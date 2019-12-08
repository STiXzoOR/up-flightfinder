# -*- coding:utf-8 -*-

from flask import Flask, render_template, session, request, redirect, flash, g, jsonify, send_file

from DBLib import DBHelper
from collections import OrderedDict, defaultdict
from faker import Faker
from datetime import datetime, timedelta
from pymysql.cursors import DictCursor, Cursor
import pymysql
import platform
import base64
import json
import io
import re
import os

WINDOWS = platform.system() == 'Windows'
OSX = platform.system() == 'Darwin' 


fake = Faker()
app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key = 'FlightRadar19'

# DB = DBHelper(db='feiflight', host='localhost', user='root',
#                   password='root', socket='/Applications/MAMP/tmp/mysql/mysql.sock')

search_result = []
passenger_num = 0
order_id = 0
is_roundtrip = False

def create_connection():
    if WINDOWS:
        return pymysql.connect(host='localhost',
                            user='root',
                            password='',
                            db='FlightRadar',
                            charset='utf8mb4',
                            cursorclass=DictCursor)

    return pymysql.connect(host='localhost',
                            user='root',
                            password='root',
                            db='FlightRadar',
                            unix_socket='/Applications/MAMP/tmp/mysql/mysql.sock',
                            charset='utf8mb4',
                            cursorclass=DictCursor)

def build_flight_card(airline_logo='', airline_name='', from_airport='', time_from='', to_airport='', time_to=''):
    return """  <div class="form-row justify-content-center align-items-center">
                    <div class="col-2 col-lg-1 col-xl-2 px-0 px-md-2 px-lg-0 px-xl-2 text-center">
                        <!-- <img src="data:image/png;base64,{airline_logo}" class="float-left" alt="{airline_name}"/> -->
                        <img src="../static/images/airlines/{airline_logo}.png" class="img-fluid h-75 w-75" alt="{airline_name}"/>
                    </div>
                    <div class="col-3 col-sm-2">
                        <div class="text-right font-weight-bold font-size-lg">{time_from}</div>
                        <div class="text-right text-muted font-size-lg">{from_airport}</div>
                    </div>
                    <div class="col-4 col-sm-6">
                        <!-- <div class="flight-line text-center">
                            <span class="d-inline-block align-middle horizontal-line"></span>
                            <span class="d-inline-block align-middle fas fa-plane mx-1 text-muted" aria-hidden="true"></span>
                            <span class="d-inline-block align-middle horizontal-line"></span>
                        </div> -->
                        <hr data-content="" class="hr-text hr-icon">
                    </div>
                    <div class="col-3 col-sm-2">
                        <div class="text-left font-weight-bold font-size-lg">{time_to}</div>
                        <div class="text-left text-muted font-size-lg">{to_airport}</div>
                    </div>
                </div>""".format(airline_logo=airline_logo, airline_name=airline_name, from_airport=from_airport, time_from=time_from, to_airport=to_airport, time_to=time_to)

def build_selected_flight_card(id='', flight='', flight_id='', airline_name='', from_airport='', from_city='', to_airport='', to_city='', date='', klass='', airplane='', duration='', flight_type=''):
    card = """  <div id="{flight_type}Flight" class="card rounded-3x shadow-none">
                    <a aria-controls="picked{flight_type}Flight" aria-expanded="false" class="small accordion-toggler text-body collapsed" data-toggle="collapse" href="#picked{flight_type}Flight">
                        <div class="form-row justify-content-center align-items-center">
                            <div class="col-11 px-0">""".format(flight_type=flight_type)
    card += flight
    card += """             </div>
                            <div class="col-1 expansion-panel-icon text-black-secondary text-right ml-0">
                                <i class="collapsed-show material-icons">keyboard_arrow_down</i>
                                <i class="collapsed-hide material-icons">keyboard_arrow_up</i>
                            </div>
                        </div>
                    </a>
                    <div id="picked{flight_type}Flight" class="font-size-90 card-footer p-0 mt-2 collapse" aria-labelledby="picked{flight_type}Flight" data-parent="#{flight_type}Flight">
                        <div class="card-body p-0">
                            <div class="form-row justify-content-center align-items-center">
                                <div class="col-4 col-lg-4 col-xl-4 pl-3 pl-sm-4 pl-lg-3 pr-0 text-muted">
                                    <input type="hidden" name="{flight_type}FlightID" value="{flight_id}">
                                    <div class="font-size-xl mb-3">{flight_id}</div>
                                    <div>{date}</div>
                                    <div>{airline_name}</div>
                                    <div>{klass}</div>
                                    <div>{airplane}</div>
                                </div>
                                <div class="col text-muted pl-0">
                                    <div class="flight-legend float-right pr-1">
                                        <div class="flight-legend-point">
                                            <div class="flight-point-icon">
                                                <span class="fas fa-map-marker-alt fa-fw"></span>
                                            </div>
                                            <span>International {from_city} Airport</span>
                                        </div>
                                        <div class="flight-legend-point">
                                            <div class="flight-point-icon">
                                                <span class="fas fa-plane fa-rotate-90 fa-fw"></span>
                                            </div>
                                            <span>{hours} Hour(s) and {minutes} Minute(s)</span>
                                        </div>
                                        <div class="flight-legend-point">
                                            <div class="flight-point-icon">
                                                <span class="fas fa-map-marker-alt fa-fw"></span>
                                            </div>
                                            <span>International {to_city} Airport</span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>""".format(flight_id=flight_id, airline_name=airline_name, from_airport=from_airport, from_city=from_city, to_airport=to_airport, to_city=to_city, date=date, klass=klass, airplane=airplane, hours=duration.hour, minutes=duration.minute, flight_type=flight_type)
    
    return card

def build_flights(flight='', is_roundtrip=False):
    depart_time = str(flight['departTime'])
    arrival_time = str(flight['departArrivalTime'])

    depart_time_from = "{time:0>8}".format(time=depart_time)[:-3]
    depart_time_to = "{time:0>8}".format(time=arrival_time)[:-3]

    depart_flight = build_flight_card(airline_logo=flight['departAirlineCode'],
                                        airline_name=flight['departAirlineName'], 
                                        from_airport=flight['departFromAirport'], 
                                        time_from=depart_time_from, 
                                        to_airport=flight['departToAirport'], 
                                        time_to=depart_time_to)
    return_flight = None                                  
    if is_roundtrip:
        depart_time = str(flight['returnTime'])
        arrival_time = str(flight['returnArrivalTime'])

        return_time_from = "{time:0>8}".format(time=depart_time)[:-3]
        return_time_to = "{time:0>8}".format(time=arrival_time)[:-3]

        return_flight = build_flight_card(airline_logo=flight['returnAirlineCode'],
                                            airline_name=flight['returnAirlineName'], 
                                            from_airport=flight['returnFromAirport'], 
                                            time_from=return_time_from, 
                                            to_airport=flight['returnToAirport'], 
                                            time_to=return_time_to)
        
    return depart_flight, return_flight

def build_selected_flights(picked_flight_index=0, flight='', is_roundtrip=False):
    depart_flight, return_flight = build_flights(flight=flight, is_roundtrip=is_roundtrip)

    duration = str(flight['departDuration'])
    depart_duration = datetime.strptime(duration[:-3], "%H:%M").time()
    depart_date = flight['departDate'].strftime("%d %b %Y")

    depart_flight = build_selected_flight_card(id=picked_flight_index+1,
                                               flight=depart_flight,
                                               flight_id=flight['departFlightID'],
                                               airline_name=flight['departAirlineName'],
                                               from_airport=flight['departFromAirport'],
                                               from_city=flight['departFromCity'],
                                               to_airport=flight['departToAirport'],
                                               to_city=flight['departToCity'],
                                               date=depart_date,
                                               klass=flight['departClass'],
                                               airplane=flight['departAirplaneName'],
                                               duration=depart_duration,
                                               flight_type='Depart')
    
    if is_roundtrip:
        duration = str(flight['returnDuration'])
        return_duration = datetime.strptime(duration[:-3], "%H:%M").time()
        return_date = flight['returnDate'].strftime("%d %b %Y")

        return_flight = build_selected_flight_card(id=picked_flight_index+1, 
                                                   flight=return_flight, 
                                                   flight_id=flight['returnFlightID'], 
                                                   airline_name=flight['returnAirlineName'], 
                                                   from_airport=flight['returnFromAirport'], 
                                                   from_city=flight['returnFromCity'], 
                                                   to_airport=flight['returnToAirport'], 
                                                   to_city=flight['returnToCity'], 
                                                   date=return_date, 
                                                   klass=flight['returnClass'], 
                                                   airplane=flight['returnAirplaneName'], 
                                                   duration=return_duration,
                                                   flight_type='Return')
    
    return depart_flight, return_flight
    
def get_user(table_name, attributes):
    def func(id):
        if id is None: return None

        Connection = create_connection()
        cursor = Connection.cursor()
        query = 'SELECT {fields} FROM {table} WHERE user_id={id}'.format(fields=', '.join(attributes),
                                                                  table=table_name,
                                                                  id=id)
        cursor.execute(query)
        result = cursor.fetchall()
        cursor.close()
        Connection.close()
        
        return result[0] if result else None
    
    return func

def get_airports():
    Connection = create_connection()
    cursor = Connection.cursor()
    query = 'SELECT {fields} FROM airport'.format(fields=', '.join(['city', 'airport_code as code']))
    cursor.execute(query)
    result = cursor.fetchall()
    cursor.close()
    Connection.close()
        
    return result

def encode_image(img_data):
    return (base64.urlsafe_b64encode(img_data)).decode('ascii')

def get_image(img_id):
    Connection = create_connection()
    cursor = Connection.cursor()
    query = 'SELECT logo FROM airline WHERE airline_code="{id}"'.format(id=img_id)
    cursor.execute(query)
    result = cursor.fetchall()
    cursor.close()
    Connection.close()
        
    return result[0]['logo']

get_current_user = get_user('users', ['user_id', 'first_name', 'last_name', 'email', 'password', 'user_type'])

@app.before_request
def before_request():
    g.authedUser = get_current_user(session.get('user_id', None))
    # g.authedUser['name'] = g.authedUser['first_name'] + ' ' + g.authedUser['last_name']
    g.url_path = request.path

@app.route('/')
@app.route('/index.html')
def index():
    airports = get_airports()
    return render_template('index.html', airports=airports)

@app.route('/_get_airports', methods=['POST'])
def return_airports():
    data = request.get_json()
    airport = str(data['airport'])

    if not airport:
        return 'OK'

    airports = data['airports'][1:]

    air = {}
    for source in airports:
        air[source] = airports[:]
        air[source].remove(source)

    return jsonify(result=air[airport])

@app.route('/search-flights', methods=["GET"])
def search_flights():
    global search_result
    global passenger_num
    global is_roundtrip
    is_roundtrip = False

    query = """
    SELECT f.flight_id as departFlightID, f.airline as departAirlineCode, al.airline_name as departAirlineName, f.dep_date as departDate, f.from_airport as departFromAirport, aprt1.city as departFromCity, f.dep_time as departTime, f.to_airport as departToAirport, aprt2.city as departToCity, f.arr_time as departArrivalTime, f.price as departPrice, f.class as departClass, f.duration as departDuration, ap.airplane_name as departAirplaneName
    FROM flight as f, airline as al, airplane as ap, airport as aprt1, airport as aprt2
    WHERE al.airline_code=f.airline and ap.airplane_model=f.airplane and aprt1.airport_code=f.from_airport and aprt2.airport_code=f.to_airport and f.from_airport=%s and f.to_airport=%s and f.dep_date=%s and f.dep_time>=CURRENT_TIME and f.occupied_capacity <= (ap.capacity-%s) and f.class=%s and f.status="Upcoming"
    ORDER BY f.price
    """

    from_airport_code = re.sub(r'[\(\)]', "", request.args.get('fromAirport')).rsplit(' ', 1)[1]
    to_airport_code = re.sub(r'[\(\)]', "", request.args.get('toAirport')).rsplit(' ', 1)[1]
    num_passengers = request.args.get('numPassengers')
    flight_class = request.args.get('flightClass')
    
    temp_depart_date = request.args.get('departDate')
    depart_date = datetime.strptime(temp_depart_date, '%d %b %Y').date()
    temp_return_date = return_date = request.args.get('returnDate')
    
    params = (from_airport_code, to_airport_code, depart_date, num_passengers, flight_class)

    if return_date != 'One Way':
        is_roundtrip = True
        query = """
        SELECT f1.flight_id as departFlightID, f1.airline as departAirlineCode, al1.airline_name as departAirlineName, f1.dep_date as departDate, f1.from_airport as departFromAirport, aprt1.city as departFromCity, f1.dep_time as departTime, f1.to_airport as departToAirport, aprt2.city as departToCity, f1.arr_time as departArrivalTime, f1.price as departPrice, f1.class as departClass, f1.duration as departDuration, ap1.airplane_name as departAirplaneName, f2.flight_id as returnFlightID, f2.airline as returnAirlineCode, al2.airline_name as returnAirlineName, f2.dep_date as returnDate, f2.from_airport as returnFromAirport, aprt3.city as returnFromCity, f2.dep_time as returnTime, f2.to_airport as returnToAirport, aprt4.city as returnToCity, f2.arr_time as returnArrivalTime, f2.price as returnPrice, f2.class as returnClass, f2.duration as returnDuration, ap2.airplane_name as returnAirplaneName
        FROM flight as f1, flight as f2, airline as al1, airline as al2, airplane as ap1, airplane as ap2, airport as aprt1, airport as aprt2, airport as aprt3, airport as aprt4
        WHERE al1.airline_code=f1.airline and ap1.airplane_model=f1.airplane and aprt1.airport_code=f1.from_airport and aprt2.airport_code=f1.to_airport and f1.from_airport=%s and f1.to_airport=%s and f1.dep_date=%s and f1.dep_time>=CURRENT_TIME and f1.occupied_capacity <= (ap1.capacity-%s) and f1.class=%s and f1.status="Upcoming" and al2.airline_code=f2.airline and ap2.airplane_model=f2.airplane and aprt3.airport_code=f2.from_airport and aprt4.airport_code=f2.to_airport and f2.from_airport=%s and f2.to_airport=%s and f2.dep_date=%s and f2.dep_time>=CURRENT_TIME and f2.occupied_capacity <= (ap2.capacity-%s) and f2.class=%s and f2.status="Upcoming" and %s and %s
        ORDER BY f1.price+f2.price
        """
        
        dep_time = 'f2.dep_time>=ADDTIME(f1.arr_time, "05:00:00")' if return_date == temp_depart_date else 1
        arr_date = 'f1.arr_date=f1.dep_date' if return_date == temp_depart_date else 1
        return_date = datetime.strptime(return_date, '%d %b %Y').date()

        params = (from_airport_code, to_airport_code, depart_date, num_passengers, flight_class, to_airport_code, from_airport_code, return_date, num_passengers, flight_class, dep_time, arr_date)

    Connection = create_connection()
    cursor = Connection.cursor()
    cursor.execute(query, params)
    result = cursor.fetchall()
    cursor.close()
    Connection.close()

    if not len(result):
        return 'no_result'

    search_result = result
    passenger_num = int(num_passengers)

    flights = """   <div id="flightsContainer" class="my-3">"""

    for i, flight in enumerate(result):
        flights += """  <div id="flight-{id}" class="more-item my-3">
                            <div class="row justify-content-center align-items-center">
                                <div class="flight-row col-12 col-md-9 col-lg-8 col-xl-6 pr-md-0 mr-md-0">
                                    <div id="flightInfo" class="flight card rounded-3x small">
                                        <div class="card-body">""".format(id=i+1)

        depart_flight, return_flight = build_flights(flight, is_roundtrip)

        flights += depart_flight
        if return_flight is not None:
            flights += '<hr class="my-2">'
            flights += return_flight
        
        flights += """                  </div>
                                    </div>
                                </div>
                                <div class="d-none d-md-block col-md-3 col-lg-2 pl-md-1 ml-0">
                                    <div id="flightPrice" class="price card rounded-3x text-center">
                                        <div class="card-body">
                                            <form id="pickedFlightForm-{id}" class="my-4" method="POST" action="picked-flight">
                                                <div class="font-weight-bold font-size-lg mb-2">€{price}</div>
                                                <button class="btn btn-primary" type="submit" name="pickedFlight" value="{id}">Select</button>
                                            </form>
                                        </div>
                                    </div>
                                </div>
                                <div class="d-block d-md-none col-12 mt-1">
                                    <div id="flightPriceSmall" class="price-small card rounded-3x">
                                        <div class="card-body">
                                            <form id="pickedFlightForm-{id}" method="POST" action="picked-flight">
                                                <button class="btn btn-primary btn-block" type="submit" name="pickedFlight" value="{id}">Select - €{price}</button>
                                            </form>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>""".format(id=i+1, price=int(flight['departPrice'])+int(flight['returnPrice']) if is_roundtrip else flight['departPrice'])
        
        # if i < len(result):
        #     flights += '<hr class="more-item my-2">'

    flights += """      <div class="row justify-content-center">
                            <a id="loadMore" class="btn btn-primary load-more__btn" href="#"><i class="fas fa-spinner"></i> Load More </a>
                        </div>
                    </div>
                </div>
            </div>
        </div>"""
    
    return flights

@app.route('/picked-flight', methods=["POST"])
def picked_flight():
    picked_flight_index = int(request.form.get('pickedFlight'))
    flight = search_result[picked_flight_index-1]

    check_query = """
    SELECT status 
    FROM booking 
    WHERE customer_id=%s and flight_id=%s and status="Active"
    """

    Connection = create_connection()
    cursor = Connection.cursor()
    cursor.execute(check_query, (session['user_id'], flight['departFlightID']))
    result = cursor.fetchone()
    cursor.close()
    Connection.close()

    if result is not None:
        flash(u"You have already booked this flight route!", 'error')
        return redirect('/index.html')

    price = int(flight['departPrice'])+int(flight['returnPrice']) if is_roundtrip else int(flight['departPrice'])
    total_price = price*passenger_num

    depart_flight, return_flight = build_selected_flights(picked_flight_index=picked_flight_index,
                                                          flight=flight, 
                                                          is_roundtrip=is_roundtrip)

    picked_flight = depart_flight

    if return_flight is not None:
        picked_flight += '<hr class="my-2">'
        picked_flight += return_flight
    
    return render_template('new-booking.html', picked_flight=picked_flight, num_passenger=passenger_num, price=price, total_price=total_price)

@app.route('/new-booking', methods=["POST"])
def new_booking():
    Connection = create_connection()

    flight_type = 'Oneway'
    flight_info = [{'flightID': request.form.get('DepartFlightID')}]
    if is_roundtrip:
        flight_type = 'Roundtrip'
        flight_info.append({'flightID': request.form.get('ReturnFlightID')})

    cursor = Connection.cursor(Cursor)
    cursor.execute('SELECT booking_id FROM booking')
    result = cursor.fetchall()
    cursor.close()

    booking_ids = list(result)

    booking_id = fake.lexify(text="??????", letters="ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789")
    while booking_id in booking_ids:
        booking_id = fake.lexify(text="??????", letters="ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789")

    current_date = str(datetime.today().date())
    passenger_info = []
    for i in range(passenger_num):
        first_name = 'firstNamePassenger-{num}'.format(num=i+1)
        last_name = 'lastNamePassenger-{num}'.format(num=i+1)
        identifier = 'idPassenger-{num}'.format(num=i+1)
        seat = 'seatPassenger-{num}'.format(num=i+1)
        seat_class = 'seatClassPassenger-{num}'.format(num=i+1)

        passenger = {'ID': request.form.get(identifier), 
                     'first_name': request.form.get(first_name),
                     'last_name': request.form.get(last_name),
                     'seat': request.form.get(seat),
                     'seat_class': request.form.get(seat_class)}
        
        passenger_info.append(passenger)
    
    contact_info = {'name': request.form.get('contactName'),
                    'email': request.form.get('contactEmail'),
                    'mobile': request.form.get('contactMobile')}

    price_per_passenger = request.form.get('pricePerPassenger')
    total_price = request.form.get('totalPrice')

    for flight in flight_info:
        booking = {'booking_id': booking_id,
                'customer_id': session['user_id'],
                'flight_id': flight['flightID'],	
                'name': contact_info['name'],
                'email': contact_info['email'],
                'mobile': contact_info['mobile'],
                'booking_date': current_date,
                'last_modify_date': current_date,
                'total_passengers': passenger_num,
                'price_per_passenger': price_per_passenger,
                'total_price': total_price,
                'flight_type': flight_type,
                'status': 'Active'
                }
        
        fields = []
        values = []
        for key in booking.keys():
            fields.append(key)
            values.append('%({key})s'.format(key=key))

        fields = ', '.join(fields)
        values = ', '.join(values)
        ins = 'INSERT INTO booking ({fields}) VALUES ({values})'.format(fields=fields,
                                                                        values=values)
        cursor = Connection.cursor()
        cursor.execute(ins, booking)
        Connection.commit()
        cursor.close()

        cursor = Connection.cursor()
        cursor.execute('UPDATE flight SET occupied_capacity=occupied_capacity+%s WHERE flight_id=%s', (passenger_num, flight['flightID']))
        Connection.commit()
        cursor.close()
    
    for passenger in passenger_info:
        try:
            cursor = Connection.cursor()
            cursor.execute('INSERT INTO passenger (passenger_id, first_name, last_name) VALUE(%s, %s, %s)', (passenger['ID'], passenger['first_name'], passenger['last_name']))
            Connection.commit()
            cursor.close()
        except:
            print('Passenger with id={id} exists'.format(id=passenger['ID']))
        cursor = Connection.cursor()
        cursor.execute('INSERT INTO pass_has_booking (passenger_id, booking_id, seat, seat_class) VALUE(%s, %s, "1A", "None")', (passenger['ID'], booking_id))
        Connection.commit()
        cursor.close()
    
    Connection.close()

    session['booking_id'] = booking_id
    return redirect("/get-booking")

@app.route('/get-booking')
@app.route('/get-booking-post', methods=["POST"])
def booking():
    is_roundtrip = False
    booking_id = session.get('booking_id', None)
    if booking_id is None:
        booking_id = request.form.get('bookingID')
        if booking_id is None:
            return redirect('/index.html')
    else:
        session.pop('booking_id')
    
    # booking_id ='ZWVD54'

    booking_query = """
    SELECT booking_id as ID, flight_id as flightID, booking_date as date, total_passengers as totalPassengers, price_per_passenger as pricePerPassenger, total_price as totalPrice, flight_type as flightType, status
    FROM booking
    WHERE booking_id=%s and last_name=%s
    """

    Connection = create_connection()
    cursor = Connection.cursor()
    cursor.execute(booking_query, (session['user_id'], booking_id))
    booking_info = cursor.fetchone()

    flight_query = """
    SELECT f.flight_id as departFlightID, f.airline as departAirlineCode, al.airline_name as departAirlineName, f.dep_date as departDate, f.from_airport as departFromAirport, aprt1.city as departFromCity, f.dep_time as departTime, f.to_airport as departToAirport, aprt2.city as departToCity, f.arr_time as departArrivalTime, f.price as departPrice, f.class as departClass, f.duration as departDuration, ap.airplane_name as departAirplaneName
    FROM flight as f, airline as al, airplane as ap, airport as aprt1, airport as aprt2
    WHERE f.flight_id=%s and al.airline_code=f.airline and ap.airplane_model=f.airplane and aprt1.airport_code=f.from_airport and aprt2.airport_code=f.to_airport
    """

    params = (booking_info['flightID'],)

    if booking_info['flightType'] == 'Roundtrip':
        is_roundtrip = True
        flight_query = """
        SELECT f1.flight_id as departFlightID, f1.airline as departAirlineCode, al1.airline_name as departAirlineName, f1.dep_date as departDate, f1.from_airport as departFromAirport, aprt1.city as departFromCity, f1.dep_time as departTime, f1.to_airport as departToAirport, aprt2.city as departToCity, f1.arr_time as departArrivalTime, f1.price as departPrice, f1.class as departClass, f1.duration as departDuration, ap1.airplane_name as departAirplaneName, f2.flight_id as returnFlightID, f2.airline as returnAirlineCode, al2.airline_name as returnAirlineName, f2.dep_date as returnDate, f2.from_airport as returnFromAirport, aprt3.city as returnFromCity, f2.dep_time as returnTime, f2.to_airport as returnToAirport, aprt4.city as returnToCity, f2.arr_time as returnArrivalTime, f2.price as returnPrice, f2.class as returnClass, f2.duration as returnDuration, ap2.airplane_name as returnAirplaneName
        FROM flight as f1, flight as f2, airline as al1, airline as al2, airplane as ap1, airplane as ap2, airport as aprt1, airport as aprt2, airport as aprt3, airport as aprt4
        WHERE f1.flight_id=%s and f2.flight_id=%s and al1.airline_code=f1.airline and ap1.airplane_model=f1.airplane and aprt1.airport_code=f1.from_airport and aprt2.airport_code=f1.to_airport and al2.airline_code=f2.airline and ap2.airplane_model=f2.airplane and aprt3.airport_code=f2.from_airport and aprt4.airport_code=f2.to_airport
        """

        booking_info = cursor.fetchone()
        params += (booking_info['flightID'],)
    
    cursor.close()
    booking_info['date'] = booking_info['date'].strftime("%d %b %Y")
    
    cursor = Connection.cursor()
    cursor.execute(flight_query, params)
    flight = cursor.fetchone()
    cursor.close()

    depart_flight, return_flight = build_selected_flights(flight=flight, 
                                                          is_roundtrip=is_roundtrip)

    picked_flight = depart_flight

    if return_flight is not None:
        picked_flight += '<hr class="my-2">'
        picked_flight += return_flight

    passenger_query = """
    SELECT p.passenger_id as ID, p.first_name as first_name, p.last_name as last_name, phb.seat as seat, phb.seat_class as seat_class
    FROM passenger as p, pass_has_booking as phb
    WHERE p.passenger_id=phb.passenger_id and phb.booking_id=%s
    """

    cursor = Connection.cursor()
    cursor.execute(passenger_query, (booking_id))
    passenger_info = cursor.fetchall()
    cursor.close()
    
    for passenger in passenger_info:
        first_name = passenger['first_name']
        last_name = passenger['last_name']

        name = '{fname} {lname}'.format(fname=first_name, lname=last_name)
        passenger.update({'name': name})

    contact_query = """
    SELECT name, email, mobile
    FROM booking
    WHERE customer_id=%s and booking_id=%s
    """

    cursor = Connection.cursor()
    cursor.execute(contact_query, (session['user_id'], booking_id))
    contact_info = cursor.fetchone()
    cursor.close()
    Connection.close()
    
    return render_template('booking.html', booking=booking_info, picked_flight=picked_flight, passenger_info=passenger_info, contact_info=contact_info)

@app.route('/change_order', methods=["POST"])
def change_order():
    Connection = create_connection()

    paid = request.form['change_paid']
    flight_id = request.form['flight_id']
    flight_date = request.form['flight_date']
    flight_class = request.form['flight_class']
    flight_d = datetime.datetime.strptime(flight_date, '%Y-%m-%d').date()
    print(flight_d)
    print(flight_class)
    
    if paid == 'No':
        cursor = Connection.cursor()
        cursor.execute('SELECT price, point FROM `order` WHERE id=%s', (order_id))
        result = cursor.fetchall()
        cursor.close()
        
        price = int(result[0]['price'])
        point = int(result[0]['point'])

        cursor = Connection.cursor()
        cursor.execute('UPDATE customer SET balance=balance+%s, point=point-%s WHERE user_id=%s', (price, point, session['user_id']))
        Connection.commit()
        cursor.close()
        
        cursor = Connection.cursor()
        cursor.execute('DELETE FROM order_flight WHERE order_id=%s', (order_id))
        Connection.commit()
        cursor.close()
        
        cursor = Connection.cursor()
        cursor.execute('INSERT INTO order_flight VALUE(%s, %s, %s, %s)', (order_id, flight_id, flight_d, flight_class))
        Connection.commit()
        cursor.close()
        
        cursor = Connection.cursor()
        cursor.execute('SELECT price, point FROM flight WHERE id=%s and date=%s and class=%s', (flight_id, flight_d, flight_class))
        result = cursor.fetchall()
        cursor.close()
        
        price = int(result[0]['price'])
        point = int(result[0]['point'])
        
        cursor = Connection.cursor()
        cursor.execute('SELECT passenger_id FROM order_passenger WHERE order_id=%s', (order_id))
        result = cursor.fetchall()
        cursor.close()
        
        volume = len(result)
        cursor = Connection.cursor()
        cursor.execute('UPDATE `order` SET price=%s, point=%s WHERE id=%s', (price*volume, point*volume, order_id))
        Connection.commit()
        cursor.close()
    else:
        cursor = Connection.cursor()
        cursor.execute('SELECT id FROM order_change_application')
        result = cursor.fetchall()
        cursor.close()
        
        cursor = Connection.cursor()
        cursor.execute('INSERT INTO order_change_application VALUE(%s, %s, %s, %s, %s, "Pending")', (len(result), order_id, flight_id, flight_d, flight_class))
        Connection.commit()
        cursor.close()
        
        flash(u'Please wait for the permission from flight company', 'success')
    
    Connection.close()
    return redirect('/order.html')


@app.route('/cancel_order', methods=["POST"])
def cancel_order():
    Connection = create_connection()
    
    paid = request.form['cancel_paid']
    if paid == 'No':
        cursor = Connection.cursor()
        cursor.execute('UPDATE `order` SET canceled=1 WHERE id=%s', (order_id))
        Connection.commit()
        cursor.close()
    else:
        cursor = Connection.cursor()
        cursor.execute('SELECT id FROM order_cancel_application')
        result = cursor.fetchall()
        cursor.close()
        
        cursor = Connection.cursor()
        cursor.execute('INSERT INTO order_cancel_application VALUE(%s, %s, "Pending")', (len(result), order_id))
        Connection.commit()
        cursor.close()
        
        flash(u'Please wait for the permission from flight company', 'success')
    
    Connection.close()
    return redirect('/order.html')


@app.route('/my-trips.html')
def my_trips():
    Connection = create_connection()
    cursor = Connection.cursor()
    cursor.execute('SELECT balance, point FROM customer WHERE user_id=%s', (session['user_id']))
    result = cursor.fetchall()
    cursor.close()

    balance = result[0]['balance']
    points = result[0]['point']
    
    cursor = Connection.cursor()
    cursor.execute('SELECT o.time, f.from, f.to, o.paid, o.canceled, o.price, o.id FROM `order` as o, order_flight as of, flight as f \
                    WHERE o.customer_id=%s and o.id=of.order_id and of.flight_id=f.id and of.flight_date=f.date and of.flight_class=f.class\
                    ORDER by o.id', (session['user_id']))
    result = cursor.fetchall()
    cursor.close()
    Connection.close()

    orders = []
    if len(result):
        order = [str(val) for val in result[0].values()]
        for i in range(3, 5):
            order[i] = 'Yes' if int(order[i]) else 'No'

        print(order)
        orders = [order]
        if len(result) > 1:
            for i in range(1, len(result)):
                order = [str(val) for val in result[i].values()]
                
                for j in range(3, 5):
                    order[j] = 'Yes' if int(order[j]) else 'No'

                # print(order)
                if order[6] != orders[i-1][6]:
                    orders.append(order)
        
        print(orders)

    return render_template('my-trips.html', balance=balance, points=points, orders=orders)


@app.route('/get_order', methods=["POST"])
def get_order():
    global order_id
    order_id = request.form['order_id']
    return redirect("/order.html")


@app.route('/admin-portal-order-id', methods=["POST"])
def admin_portal_order_id():
    global order_id
    order_id = request.form['order_id']
    return redirect("/order.html")


@app.route('/admin-portal-user-id', methods=["POST"])
def admin_portal_user_id():
    user_id = request.form['user_id']

    Connection = create_connection()
    cursor = Connection.cursor()
    cursor.execute('SELECT name FROM users WHERE id=%s', (user_id))
    result = cursor.fetchall()
    cursor.close()
    
    user_name = result[0]['name']
    
    cursor = Connection.cursor()
    cursor.execute('SELECT o.time, f.from, f.to, o.paid, o.canceled, o.price, o.id FROM `order` as o, order_flight as of, flight as f \
                    WHERE o.customer_id=%s and o.id=of.order_id and of.flight_id=f.id and of.flight_date=f.date and of.flight_class=f.class\
                    ORDER by o.id', (user_id))
    result = cursor.fetchall()
    cursor.close()
    Connection.close()
    
    order = [str(val) for val in result[0].values()]
    for i in range(3, 5):
        order[i] = 'Yes' if int(order[i]) else 'No'

    print(order)
    orders = [order]
    if len(result) > 1:
        for i in range(1, len(result)):
            order = [str(val) for val in result[i].values()]
            
            for j in range(3, 5):
                order[j] = 'Yes' if int(order[j]) else 'No'

            # print(order)
            if order[6] != orders[i-1][6]:
                orders.append(order)
    
    print(orders)
    return render_template('user-orders.html', orders=orders, user_name=user_name)


@app.route('/sign-in.html')
def login():
    return render_template('sign-in.html')


@app.route('/sign-in.html', methods=["POST"])
def login_post():
    email = request.form.get('email')
    password = request.form.get('password')

    Connection = create_connection()
    cursor = Connection.cursor()
    cursor.execute('SELECT user_id, first_name, last_name, password, user_type FROM users WHERE email=%s', (email))
    result = cursor.fetchone()
    cursor.close()
    Connection.close()
    
    if result is None:
        flash(u"The user does not exist!", 'error')
        return redirect('/sign-in.html')
    
    if password != result['password']:
        flash(u"Wrong password!", 'error')
        return redirect('/sign-in.html')
    
    session['user_id'] = result['user_id']
    session['user_type'] = result['user_type']
    session['name'] = '{fname} {lname}'.format(fname=result['first_name'], lname=result['last_name'])
    
    return redirect('/index.html')

@app.route('/sign-up.html')
def sign_up():
    return render_template('sign-up.html')

@app.route('/sign-up.html', methods=["POST"])
def sign_up_post():
    first_name = request.form.get('firstName')
    last_name = request.form.get('lastName')
    email = request.form.get('email')
    password = request.form.get('password')

    Connection = create_connection()
    cursor = Connection.cursor()
    cursor.execute('SELECT * FROM users WHERE email=%s', (email))
    result = cursor.fetchone()
    cursor.close()

    if result is not None:
        flash(u"The user already exists", 'error')
        return redirect('/sign-up.html')
    
    cursor = Connection.cursor()
    cursor.execute('SELECT COUNT(*) as nextID FROM users')
    result = cursor.fetchone()
    cursor.close()
    
    user_id = int(result['nextID'])
    cursor = Connection.cursor()
    cursor.execute('INSERT INTO users (user_id, first_name, last_name, email, password, user_type) VALUE(%s, %s, %s, %s, %s, "CUSTOMER")', (user_id, first_name, last_name, email, password))
    cursor.close()

    cursor = Connection.cursor()
    cursor.execute('INSERT INTO customer (customer_id, mobile, address, address2, city, state, zip_code, country) VALUE(%s, "", "", "", "", "", "", "")', (user_id))
    cursor.close()
    Connection.commit()
    Connection.close()

    session['user_id'] = user_id
    session['user_type'] = 'CUSTOMER'
    session['name'] = '{fname} {lname}'.format(fname=first_name, lname=last_name)

    return redirect('/index.html')

@app.route('/sign-out.html')
def page_logout():
    del session['user_id']
    return redirect('/index.html')

@app.route('/user-profile.html')
def profile():
    Connection = create_connection()

    user_query = """
    'SELECT u.first_name as fname, u.last_name as lname, u.email as email, c.mobile as mobile, c.address as address, c.address2 as address2, c.city as city, c.state as state, c.zip_code as zip, c.country as country 
    FROM users as u, customer as c
    WHERE u.user_id=%s and c.customer_id=u.user_id'
    """

    cursor = Connection.cursor()
    cursor.execute(user_query, (session['user_id']))
    customer_info = cursor.fetchone()
    cursor.close()

    cursor = Connection.cursor()
    cursor.execute('SELECT booking FROM customer WHERE customer_id=%s', (session['user_id']))
    customer_info = cursor.fetchone()
    cursor.close()

    return render_template('user-profile.html', user_info=customer_info)

@app.route('/user-profile.html', methods=["POST"])
def profile_post():
    name = request.form['name']
    password = request.form['password']

    Connection = create_connection()
    cursor = Connection.cursor()
    cursor.execute('UPDATE users SET name=%s, password=%s WHERE id=%s', (name, password, session['user_id']))
    cursor.close()
    Connection.commit()
    Connection.close()

    flash(u"Profile updated", 'success')
    return redirect('/profile.html')


@app.route('/admin-portal.html')
def admin_portal():
    Connection = create_connection()
    cursor = Connection.cursor()
    cursor.execute('SELECT * FROM flight_cancel_application')
    result = cursor.fetchall()
    cursor.close()
    Connection.close()

    return render_template('admin-portal.html', cancel_info=result)

@app.route('/f_cancel_accept', methods=["POST"])
def f_cancel_accept():
    cancel_id = request.form['cancel_id']
    flight_id = request.form['flight_id']
    flight_date = request.form['flight_date']
    flight_class = request.form['flight_class']

    Connection = create_connection()
    cursor = Connection.cursor()
    cursor.execute('UPDATE flight SET canceled=1 WHERE id=%s and date=%s and class=%s', (flight_id, flight_date, flight_class))
    Connection.commit()
    cursor.close()
    
    cursor = Connection.cursor()
    cursor.execute('UPDATE flight_cancel_application SET process="Accepted" WHERE id=%s', (cancel_id))
    Connection.commit()
    cursor.close()
    Connection.close()
    
    return redirect('/admin-portal.html')


@app.route('/f_cancel_reject', methods=["POST"])
def f_cancel_reject():
    cancel_id = request.form['cancel_id']

    Connection = create_connection()
    cursor = Connection.cursor()
    cursor.execute('UPDATE flight_cancel_application SET process="Rejected" WHERE id=%s', (cancel_id))
    Connection.commit()
    cursor.close()
    Connection.close()

    return redirect('/admin-portal.html')


@app.route('/add-company', methods=["POST"])
def admin_portal_add_company():
    email = request.form['email']
    password = request.form['password']
    name = request.form['name']
    mobile = request.form['mobile']

    Connection = create_connection()
    cursor = Connection.cursor()
    cursor.execute('SELECT * FROM users WHERE email=%s', (email))
    result = cursor.fetchall()
    cursor.close()

    if len(result):
        flash(u"The company already exists", 'error')
        return redirect('/admin-portal.html')

    cursor = Connection.cursor()
    cursor.execute('SELECT * FROM users')
    result = cursor.fetchall()
    cursor.close()

    number = len(result)

    cursor = Connection.cursor()
    cursor.execute('INSERT INTO users VALUE(%s, 1, %s, %s, %s, %s)', (number, password, name, email, mobile))
    cursor.close()

    cursor = Connection.cursor()
    cursor.execute('INSERT INTO company VALUE(%s)', (number))
    Connection.commit()
    cursor.close()
    Connection.close()

    flash(u"Company added", 'success')
    return redirect('/admin-portal.html')


@app.route('/company-portal.html')
def company_portal():
    Connection = create_connection()
    cursor = Connection.cursor()
    cursor.execute('SELECT * FROM order_cancel_application')
    result = cursor.fetchall()
    cursor.close()

    cancel = [[str(var) for var in item.values()] for item in result]

    cursor = Connection.cursor()
    cursor.execute('SELECT * FROM order_change_application')
    result = cursor.fetchall()
    cursor.close()
    Connection.close()

    change = [[str(var) for var in item.values()] for item in result]

    print(change)

    return render_template('company-portal.html', cancel_info=cancel, change_info=change)


@app.route('/cancel_accept', methods=["POST"])
def cancel_accept():
    cancel_id = request.form['cancel_id']
    o_id = request.form['o_id']

    Connection = create_connection()
    cursor = Connection.cursor()
    cursor.execute('UPDATE `order` SET canceled=1 WHERE id=%s', (o_id))
    Connection.commit()
    cursor.close()

    cursor = Connection.cursor()
    cursor.execute('UPDATE order_cancel_application SET process="Accepted" WHERE id=%s', (cancel_id))
    Connection.commit()
    cursor.close()

    cursor = Connection.cursor()
    cursor.execute('SELECT price, point, customer_id FROM `order` WHERE id=%s', (o_id))
    result = cursor.fetchall()
    cursor.close()
    Connection.commit()

    price = result[0]['price']
    point = result[0]['point']
    customer_id = result[0]['customer_id']
    
    cursor = Connection.cursor()
    cursor.execute('UPDATE customer SET balance=balance+%s, point=point-%s WHERE user_id=%s', (price, point, customer_id))
    cursor.close()
    Connection.commit()
    Connection.close()

    return redirect('/company-portal.html')


@app.route('/cancel_reject', methods=["POST"])
def cancel_reject():
    Connection = create_connection()
    cancel_id = request.form['cancel_id']
    cursor = Connection.cursor()
    cursor.execute('UPDATE order_cancel_application SET process="Rejected" WHERE id=%s', [cancel_id])
    Connection.commit()
    return redirect('/company-portal.html')


@app.route('/change_accept', methods=["POST"])
def change_accept():
    change_id = request.form['change_id']
    o_id = request.form['o_id']
    flight_id = request.form['flight_id']
    flight_date = request.form['flight_date']
    flight_class = request.form['flight_class']

    Connection = create_connection()
    cursor = Connection.cursor()
    cursor.execute('UPDATE order_change_application SET process="Accepted" WHERE id=%s', (change_id))
    cursor.close()
    Connection.commit()
    
    cursor = Connection.cursor()
    cursor.execute('SELECT price, point, customer_id FROM `order` WHERE id=%s', (o_id))
    result = cursor.fetchall()
    cursor.close()

    cursor = Connection.cursor()
    cursor.execute('UPDATE customer SET balance=balance+%s, point=point-%s WHERE user_id=%s',
                   [result[0][0], result[0][1], result[0][2]])
    cursor.close()
    Connection.commit()

    cursor = Connection.cursor()
    cursor.execute('DELETE FROM order_flight WHERE order_id=%s', (o_id))
    cursor.close()
    Connection.commit()

    cursor = Connection.cursor()
    cursor.execute('INSERT INTO order_flight VALUE(%s, %s, %s, %s)', (o_id, flight_id, flight_date, flight_class))
    cursor.close()
    Connection.commit()

    cursor = Connection.cursor()
    cursor.execute('SELECT price, point FROM flight WHERE id=%s and date=%s and class=%s', (flight_id, flight_date, flight_class))
    result = cursor.fetchall()
    cursor.close()

    price = result[0]['price']
    point = result[0]['point']

    cursor = Connection.cursor()
    cursor.execute('SELECT passenger_id FROM order_passenger WHERE order_id=%s', (o_id))
    result = cursor.fetchall()
    cursor.close()

    volume = len(result)

    cursor = Connection.cursor()
    cursor.execute('UPDATE `order` SET price=%s, point=%s WHERE id=%s', (price * volume, point * volume, o_id))
    cursor.close()
    Connection.commit()
    Connection.close()

    return redirect('/company-portal.html')


@app.route('/change_reject', methods=["POST"])
def change_reject():
    change_id = request.form['change_id']

    Connection = create_connection()
    cursor = Connection.cursor()
    cursor.execute('UPDATE order_change_application SET process="Rejected" WHERE id=%s', (change_id))
    cursor.close()
    Connection.commit()
    Connection.close()
    
    return redirect('/company-portal.html')


@app.route('/add_flights', methods=["POST"])
def company_portal_add_flights():
    flight_id = request.form['flight_id']
    date_begin = request.form['date_begin']
    date_end = request.form['date_end']
    From = request.form['From']
    to = request.form['to']
    cabin_class = request.form['cabin_class']
    depart_time = request.form['depart_time']
    arrival_time = request.form['arrival_time']
    price = request.form['price']
    point = request.form['point']
    cancel_fee = request.form['cancel_fee']
    change_fee = request.form['change_fee']
    seats = request.form['seats']
    date_b = datetime.datetime.strptime(date_begin, '%Y-%m-%d').date()
    date_e = datetime.datetime.strptime(date_end, '%Y-%m-%d').date()
    d_time = datetime.datetime.strptime(depart_time, '%H:%M').time()
    a_time = datetime.datetime.strptime(arrival_time, '%H:%M').time()
    Date = date_b

    ins = 'INSERT INTO flight VALUE(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
    Connection = create_connection()
    while Date <= date_e:
        cursor = Connection.cursor()
        cursor.execute(ins, (flight_id, Date, cabin_class, From, to, d_time, a_time, price, point, cancel_fee, change_fee, seats, 0, session['user_id']))
        cursor.close()
        Connection.commit()
        Date = Date + datetime.timedelta(days=1)
    Connection.close()

    flash(u"Flights added", 'success')
    return redirect('/company-portal.html')


@app.route('/flight.html', methods=["POST"])
def search_flight():
    flight_id = request.form['flight_no']
    flight_date = request.form['flight_date']
    flight_class = request.form['flight_class']

    Connection = create_connection()
    cursor = Connection.cursor()
    cursor.execute('SELECT * FROM flight WHERE id=%s and date=%s and class=%s', (flight_id, flight_date, flight_class))
    result = cursor.fetchall()
    cursor.close()

    flight = [str(val) for val in result[0].values()]
    flight[12] = 'Yes' if int(flight[12]) else 'No'

    cursor = Connection.cursor()
    cursor.execute('SELECT p.name, p.id FROM passenger as p, order_passenger as op, order_flight as of \
                    WHERE of.flight_id=%s and of.flight_date=%s and of.flight_class=%s and of.order_id=op.order_id and \
                    op.passenger_id=p.id', (flight_id, flight_date, flight_class))
    result = cursor.fetchall()
    cursor.close()
    Connection.close()

    passengers = [[str(val) for val in item.values()] for item in result]

    return render_template('/flight.html', f_info=flight, p_info=passengers)


@app.route('/modify_flight', methods=["POST"])
def modify_flight():
    flight_id = request.form['Flight_id']
    flight_date = request.form['Flight_date']
    flight_class = request.form['Flight_class']
    volume = request.form['seats']
    price = request.form['price']
    point = request.form['point']
    cancel_fee = request.form['cancel_fee']
    change_fee = request.form['change_fee']

    Connection = create_connection()
    cursor = Connection.cursor()
    cursor.execute('UPDATE flight SET volume=%s, price=%s, point=%s, cancel_rule=%s, change_rule=%s WHERE id=%s and \
                    date=%s and class=%s', (volume, price, point, cancel_fee, change_fee, flight_id, flight_date, flight_class))
    cursor.close()
    Connection.commit()
    
    cursor = Connection.cursor()
    cursor.execute('SELECT * FROM flight WHERE id=%s and date=%s and class=%s', (flight_id, flight_date, flight_class))
    result = cursor.fetchall()
    cursor.close()

    flight = [str(val) for val in result[0].values()]
    flight[12] = 'Yes' if int(flight[12]) else 'No'

    cursor = Connection.cursor()
    cursor.execute('SELECT p.name, p.id FROM passenger as p, order_passenger as op, order_flight as of \
                    WHERE of.flight_id=%s and of.flight_date=%s and of.flight_class=%s and of.order_id=op.order_id and \
                    op.passenger_id=p.id', (flight_id, flight_date, flight_class))
    result = cursor.fetchall()
    cursor.close()
    Connection.close()

    passengers = [[str(val) for val in item.values()] for item in result]

    flash(u'Flight modified', 'success')

    return render_template('/flight.html', f_info=flight, p_info=passengers)


@app.route('/cancel_flight', methods=["POST"])
def cancel_flight():
    flight_id = request.form['Flight_id']
    flight_date = request.form['Flight_date']
    flight_class = request.form['Flight_class']

    Connection = create_connection()
    cursor = Connection.cursor()
    cursor.execute('SELECT id FROM flight_cancel_application')
    result = cursor.fetchall()
    cursor.close()

    fca_id = len(result)

    cursor = Connection.cursor()
    cursor.execute('INSERT INTO flight_cancel_application VALUE(%s, %s, %s, %s, "Pending")', (fca_id, flight_id, flight_date, flight_class))
    cursor.close()
    Connection.commit()
    
    cursor = Connection.cursor()
    cursor.execute('SELECT * FROM flight WHERE id=%s and date=%s and class=%s', (flight_id, flight_date, flight_class))
    result = cursor.fetchall()
    cursor.close()

    flight = [str(val) for val in result[0].values()]
    flight[12] = 'Yes' if int(flight[12]) else 'No'

    cursor = Connection.cursor()
    cursor.execute('SELECT p.name, p.id FROM passenger as p, order_passenger as op, order_flight as of \
                    WHERE of.flight_id=%s and of.flight_date=%s and of.flight_class=%s and of.order_id=op.order_id and \
                    op.passenger_id=p.id', (flight_id, flight_date, flight_class))
    result = cursor.fetchall()
    cursor.close()
    Connection.close()

    passengers = [[str(val) for val in item.values()] for item in result]

    flash(u'Please wait for the permission from admin', 'success')
    return render_template('/flight.html', f_info=flight, p_info=passengers)


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
