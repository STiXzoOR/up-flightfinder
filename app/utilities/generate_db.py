from pymysql.cursors import DictCursor, Cursor
from datetime import datetime, timedelta
from faker import Faker
import pymysql
import csv
import os
import json
import platform

DB = ''
WINDOWS = platform.system() == 'Windows'
OSX = platform.system() == 'Darwin' 
current_dir = os.getcwd()
fake = Faker()

def create_connection():
    options = {'host': 'localhost',
               'user': 'root',
               'password': '',
               'database': DB,
               'charset': 'utf8mb4',
               'cursorclass': DictCursor}
    
    if OSX:
        options['password'] = 'root'
        options.update({'unix_socket': '/Applications/MAMP/tmp/mysql/mysql.sock'})

    return pymysql.connect(**options)

def parse_sql(file):
    stmts = []
    DELIMITER = ';'
    stmt = ''

    with open(file, 'r') as db_schema:
        data = db_schema.readlines()
        for line in data:
            if not line.strip():
                continue

            if line.startswith('--'):
                continue

            if 'DELIMITER' in line:
                DELIMITER = line.split()[1]
                continue

            if (DELIMITER not in line):
                stmt += line.replace(DELIMITER, ';')
                continue

            if stmt:
                stmt += line
                stmts.append(stmt.strip())
                stmt = ''
            else:
                stmts.append(line.strip())
    
    return stmts

def create_database():
    query = """
    CREATE DATABASE IF NOT EXISTS FlightFinderDB
    """

    cnx = create_connection()
    cursor = cnx.cursor()
    cursor.execute(query)
    cursor.close()
    cnx.commit()
    cnx.close()

    return 'flightfinderdb'

def configure_database():
    stmts = parse_sql(current_dir + '/schema.sql')
    cnx = create_connection()
    
    with cnx.cursor() as cursor:
        for stmt in stmts:
            try:
                cursor.execute(stmt)
            except (pymysql.err.DatabaseError,
                pymysql.err.IntegrityError,
                pymysql.err.MySQLError) as e:
                print(e)
                print(stmt)
                exit(1)
        cnx.commit()
    
    cnx.close()


def generate_flights():
    def _generate_id(prefix=''):
        query = """
        SELECT flight_id 
        FROM flight
        WHERE flight_id=%s"""

        cursor = cnx.cursor()

        flight_id = prefix + fake.numerify(text="####")
        cursor.execute(query, flight_id)
        result = cursor.fetchone()
        while result is not None:
            flight_id = prefix + fake.numerify(text="####")
            cursor.execute(query, flight_id)
            result = cursor.fetchone()
        cursor.close()

        return flight_id
    
    durations = {}
    time_multiplier = 3
    classes = ['Economy', 'Business', 'First Class']
    date_start = today = datetime.now().date()
    date_end = date_start + timedelta(days=30)

    with open(current_dir + '/data/routes_durations.json', mode='r') as file:
        durations = json.load(file)

    with open(current_dir + '/data/routes.csv', mode='r') as input_csv:
        csv_reader = csv.DictReader(input_csv,
                                    delimiter=';',
                                    fieldnames=['airline', 'from', 'to', 'airplane'])

        cnx = create_connection()
        for row in csv_reader:
            if row['airline'] != '':
                airline = row['airline']
                from_airport = row['from']
                to_airport = row['to']
                airplane = row['airplane']
                duration = durations[from_airport][to_airport]
                duration = datetime.strptime(duration[:-3], "%H:%M")
                klass = fake.random_element(elements=classes)

                hours = []
                minutes = []
                while len(hours) < time_multiplier:
                    hour = fake.random_int(0, 23)
                    if hour not in hours:
                        hours.append(hour)

                while len(minutes) < time_multiplier:
                    minute = fake.random_int(0, 55, step=5)
                    if minute not in minutes:
                        minutes.append(minute)

                while hours and minutes:
                    hour = hours.pop(fake.random_int(0, len(hours)-1))
                    minute = minutes.pop(fake.random_int(0, len(minutes)-1))
                    date = "{Y}-{m}-{d} {H}:{M}".format(Y=today.year,
                                                        m=today.month,
                                                        d=today.day,
                                                        H=hour,
                                                        M=minute)

                    dep_date = datetime.strptime(date, "%Y-%m-%d %H:%M")
                    arr_date = dep_date + timedelta(hours=duration.hour,
                                                    minutes=duration.minute)
                    date_start = today
                    while date_start <= date_end:
                        prices = {'Economy': {'price': fake.random_int(min=70, max=300, step=1), 'change': 30, 'cancel': 60},
                                'Business': {'price': fake.random_int(min=150, max=650, step=1), 'change': 70, 'cancel': 140},
                                'First Class': {'price': fake.random_int(min=260, max=1000, step=1), 'change': 125, 'cancel': 250}
                                }
                        price = prices[klass]['price']
                        change = prices[klass]['change']
                        cancel = prices[klass]['cancel']
                        arr_date = dep_date + timedelta(hours=duration.hour,
                                                        minutes=duration.minute)

                        flight_id = _generate_id(airline)

                        flight_record = {'flight_id': flight_id,
                                        'airline': airline,
                                        'airplane': airplane,
                                        'from_airport': from_airport,
                                        'to_airport': to_airport,
                                        'dep_date': dep_date.date(),
                                        'dep_time': dep_date.time(),
                                        'arr_date': arr_date.date(),
                                        'arr_time': arr_date.time(),
                                        'duration': duration.time(),
                                        'class': klass,
                                        'price': price,
                                        'change_fee': change,
                                        'cancel_fee': cancel,
                                        'discount': 0,
                                        'occupied_capacity': 0,
                                        'status': 'Upcoming'
                                        }

                        fields = []
                        values = []
                        for key in flight_record.keys():
                            fields.append(key)
                            values.append('%({key})s'.format(key=key))

                        fields = ', '.join(fields)
                        values = ', '.join(values)
                        query = 'INSERT INTO flight ({fields}) VALUES ({values})'.format(fields=fields,
                                                                                         values=values)
                        
                        cursor = cnx.cursor()
                        cursor.execute(query, flight_record)
                        cnx.commit()
                        cursor.close()

                        dep_date += timedelta(days=1)
                        date_start += timedelta(days=1)
    cnx.close()

if __name__ == '__main__':
    print('Creating database... ', end='')
    DB = create_database()
    print('Done!')
    
    print('Importing schema file... ', end='')
    configure_database()
    print('Done!')
    
    print('Generating flights... ', end='')
    generate_flights()
    print('Done!')
