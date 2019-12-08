import csv
import os
import json
from faker import Faker
from datetime import datetime, timedelta
fake = Faker()

current_dir = os.getcwd()
durations = {}
time_multiplier = 3
classes = ['Economy', 'Business', 'First Class']
date_start = today = datetime.now().date()
date_end = date_start + timedelta(days=30)

flight_ids = []


def random_time():
    hours = fake.random_int(1, 24)
    minutes = fake.random_int(0, 55, step=5)

    hours = hours if hours > 9 else '0{}'.format(hours)
    minutes = minutes if minutes > 9 else '0{}'.format(minutes)

    return '{H}:{M}'.format(H=hours, M=minutes)


with open(current_dir + '/csv_data/routes_durations.json', mode='r') as file:
    durations = json.load(file)

with open(current_dir + '/csv_data/routes.csv', mode='r') as input_csv, open(current_dir + '/csv_data/flights.csv', mode='w') as output_csv:
    csv_reader = csv.DictReader(input_csv,
                                delimiter=';',
                                fieldnames=['airline', 'from', 'to', 'airplane'])
    csv_writer = csv.DictWriter(output_csv,
                                fieldnames=['flight_id', 'airline', 'airplane', 'from_airport', 'to_airport',
                                            'dep_date', 'dep_time', 'arr_date', 'arr_time', 'duration',
                                            'class', 'price', 'change_fee', 'cancel_fee', 'discount',
                                            'occupied_capacity', 'status'],
                                quoting=csv.QUOTE_ALL)

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

                    flight_id = airline + fake.numerify(text="####")
                    while flight_id in flight_ids:
                        flight_id = airline + fake.numerify(text="####")

                    flight_ids.append(flight_id)

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

                    csv_writer.writerow(flight_record)
                    dep_date += timedelta(days=1)
                    date_start += timedelta(days=1)
