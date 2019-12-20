# -*- coding:utf-8 -*-

from flask import Flask, render_template, session, request, redirect, flash, g, jsonify, send_file, url_for, abort
from flask_bcrypt import generate_password_hash as gen_pw_hash
from flask_bcrypt import check_password_hash as chk_pw_hash

from DBLib import DBHelper
from functools import wraps
from itertools import groupby
from collections import OrderedDict, defaultdict
from faker import Faker
from datetime import datetime, timedelta
from pymysql.cursors import DictCursor, Cursor
import pymysql
import urllib.parse
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
app.config['SECRET_KEY'] = 'FlightFinder2019'

# DB = DBHelper(db='feiflight', host='localhost', user='root',
#                   password='root', socket='/Applications/MAMP/tmp/mysql/mysql.sock')

def create_connection():
    if WINDOWS:
        return pymysql.connect(host='localhost',
                            user='root',
                            password='',
                            db='FlightFinderDB',
                            charset='utf8mb4',
                            cursorclass=DictCursor)

    return pymysql.connect(host='localhost',
                            user='root',
                            password='root',
                            db='FlightFinderDB',
                            unix_socket='/Applications/MAMP/tmp/mysql/mysql.sock',
                            charset='utf8mb4',
                            cursorclass=DictCursor)

def get_customer_id():
    return g.current_customer.get('id')

def get_customer_type():
    return g.current_customer.get('type')

def build_flight_card(airline_logo='', airline_name='', from_airport='', time_from='', to_airport='', time_to=''):
    return """  <div class="form-row justify-content-center align-items-center">
                    <div class="col-2 col-lg-1 col-xl-2 px-0 px-md-2 px-lg-0 px-xl-2 text-center">
                        <img src="../static/images/airlines/{airline_logo}.png" class="img-fluid h-75 w-75" alt="{airline_name}"/>
                    </div>
                    <div class="col-3 col-sm-2">
                        <div class="text-right font-weight-bold font-size-lg">{time_from}</div>
                        <div class="text-right text-muted font-size-lg">{from_airport}</div>
                    </div>
                    <div class="col-4 col-sm-6">
                        <hr data-content="" class="flight-indicator hr-text hr-icon">
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
                                <div class="col-4 col-lg-4 col-xl-4 pl-3 pl-sm-4 pl-lg-3 pr-0">
                                    <input type="hidden" name="{flight_type}FlightID" value="{flight_id}">
                                    <div class="font-size-xl mb-3">{flight_id}</div>
                                    <div>{date}</div>
                                    <div>{airline_name}</div>
                                    <div>{klass}</div>
                                    <div>{airplane}</div>
                                </div>
                                <div class="col pl-0">
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
    depart_flight = build_flight_card(airline_logo=flight['departAirlineCode'],
                                        airline_name=flight['departAirlineName'], 
                                        from_airport=flight['departFromAirport'], 
                                        time_from=flight['departTime'], 
                                        to_airport=flight['departToAirport'], 
                                        time_to=flight['departArrivalTime'])
    return_flight = None                                  
    if is_roundtrip:
        return_flight = build_flight_card(airline_logo=flight['returnAirlineCode'],
                                            airline_name=flight['returnAirlineName'], 
                                            from_airport=flight['returnFromAirport'], 
                                            time_from=flight['returnTime'], 
                                            to_airport=flight['returnToAirport'], 
                                            time_to=flight['returnArrivalTime'])
        
    return depart_flight, return_flight

def build_selected_flights(picked_flight_index=0, flight='', is_roundtrip=False):
    depart_flight, return_flight = build_flights(flight=flight, is_roundtrip=is_roundtrip)

    duration = flight['departDuration']
    depart_duration = datetime.strptime(duration, "%H:%M").time()

    depart_flight = build_selected_flight_card(id=picked_flight_index+1,
                                               flight=depart_flight,
                                               flight_id=flight['departFlightID'],
                                               airline_name=flight['departAirlineName'],
                                               from_airport=flight['departFromAirport'],
                                               from_city=flight['departFromCity'],
                                               to_airport=flight['departToAirport'],
                                               to_city=flight['departToCity'],
                                               date=flight['departDate'],
                                               klass=flight['departClass'],
                                               airplane=flight['departAirplaneName'],
                                               duration=depart_duration,
                                               flight_type='Depart')
    
    if is_roundtrip:
        duration = flight['returnDuration']
        return_duration = datetime.strptime(duration, "%H:%M").time()

        return_flight = build_selected_flight_card(id=picked_flight_index+1, 
                                                   flight=return_flight, 
                                                   flight_id=flight['returnFlightID'], 
                                                   airline_name=flight['returnAirlineName'], 
                                                   from_airport=flight['returnFromAirport'], 
                                                   from_city=flight['returnFromCity'], 
                                                   to_airport=flight['returnToAirport'], 
                                                   to_city=flight['returnToCity'], 
                                                   date=flight['returnDate'], 
                                                   klass=flight['returnClass'], 
                                                   airplane=flight['returnAirplaneName'], 
                                                   duration=return_duration,
                                                   flight_type='Return')
    
    return depart_flight, return_flight

def get_airports():
    query = """
    SELECT city, airport_code as code 
    FROM airport
    """

    Connection = create_connection()
    cursor = Connection.cursor()
    cursor.execute(query)
    result = cursor.fetchall()
    cursor.close()
    Connection.close()
        
    return result

def get_flights(is_roundtrip=False, params=(), WHERE='', ORDER_BY='', LIMIT='', FETCH_ALL=True):
    query = """
    SELECT f.flight_id as departFlightID, f.airline as departAirlineCode, al.airline_name as departAirlineName, DATE_FORMAT(f.dep_date, "%%d %%b %%Y") as departDate, f.from_airport as departFromAirport, aprt1.city as departFromCity, TIME_FORMAT(f.dep_time, "%%H:%%i") as departTime, f.to_airport as departToAirport, aprt2.city as departToCity, TIME_FORMAT(f.arr_time, "%%H:%%i") as departArrivalTime, f.price as departPrice, f.class as departClass, TIME_FORMAT(f.duration, "%%H:%%i") as departDuration, ap.airplane_name as departAirplaneName
    FROM flight as f, airline as al, airplane as ap, airport as aprt1, airport as aprt2
    """

    if is_roundtrip:
        query = """
        SELECT f1.flight_id as departFlightID, f1.airline as departAirlineCode, al1.airline_name as departAirlineName, DATE_FORMAT(f1.dep_date, "%%d %%b %%Y") as departDate, f1.from_airport as departFromAirport, aprt1.city as departFromCity, TIME_FORMAT(f1.dep_time, "%%H:%%i") as departTime, f1.to_airport as departToAirport, aprt2.city as departToCity, TIME_FORMAT(f1.arr_time, "%%H:%%i") as departArrivalTime, f1.price as departPrice, f1.class as departClass, TIME_FORMAT(f1.duration, "%%H:%%i") as departDuration, ap1.airplane_name as departAirplaneName, f2.flight_id as returnFlightID, f2.airline as returnAirlineCode, al2.airline_name as returnAirlineName, DATE_FORMAT(f2.dep_date, "%%d %%b %%Y") as returnDate, f2.from_airport as returnFromAirport, aprt3.city as returnFromCity, TIME_FORMAT(f2.dep_time, "%%H:%%i") as returnTime, f2.to_airport as returnToAirport, aprt4.city as returnToCity, TIME_FORMAT(f2.arr_time, "%%H:%%i") as returnArrivalTime, f2.price as returnPrice, f2.class as returnClass, TIME_FORMAT(f2.duration, "%%H:%%i") as returnDuration, ap2.airplane_name as returnAirplaneName
        FROM flight as f1, flight as f2, airline as al1, airline as al2, airplane as ap1, airplane as ap2, airport as aprt1, airport as aprt2, airport as aprt3, airport as aprt4
        """

    if WHERE:
        query += ' WHERE {where}'.format(where=WHERE)
    
    if ORDER_BY:
        query += ' ORDER BY {order}'.format(order=ORDER_BY)
    
    if LIMIT:
        query += ' LIMIT {limit}'.format(limit=LIMIT)

    Connection = create_connection()
    cursor = Connection.cursor()
    cursor.execute(query, params)
    data = cursor.fetchall() if FETCH_ALL else cursor.fetchone()
    cursor.close()
    Connection.close()
    
    return data

def pick_seat():
    rows = [str(row) for row in range(1, 21)]
    cols = ['A', 'B', 'C', 'D', 'E', 'F']
    seats = [[row+col for col in cols] for row in rows]

    class_seats = {'first class': [seat for row in seats[:2] for seat in row],
                   'business': [seat for row in seats[2:4] for seat in row],
                   'economy': [seat for row in seats[4:] for seat in row]}

def booking_exists(booking_id, last_name):
    customer_id = get_customer_id()
    customer_type = get_customer_type()

    query = """
    SELECT booking_id 
    FROM booking
    WHERE booking_id=%s and (last_name=%s {operator} customer_id=%s)
    """.format(operator='or' if customer_type == 'GUEST' else 'and')

    Connection = create_connection()
    cursor = Connection.cursor()
    cursor.execute(query, (booking_id, last_name, customer_id))
    result = cursor.fetchone()
    cursor.close()
    Connection.close()

    return result is not None

def booking_is_inactive(booking_id, last_name):
    query = """
    SELECT status 
    FROM booking 
    WHERE booking_id=%s and last_name=%s and status in ("Canceled", "Passed")
    """

    Connection = create_connection()
    cursor = Connection.cursor()
    cursor.execute(query, (booking_id, last_name))
    result = cursor.fetchone()
    cursor.close()
    Connection.close()

    return result is not None

def get_booking(booking_id='', booking_last_name=''):
    customer_id = get_customer_id()
    customer_type = get_customer_type()
    is_roundtrip = False

    query = """
    SELECT booking_id as id, depart_flight_id, return_flight_id, DATE_FORMAT(booking_date, "%%d %%b %%Y") as date, total_passengers, price_per_passenger, total_price, flight_type, status
    FROM booking
    WHERE booking_id=%s and (last_name=%s {operator} customer_id=%s) 
    """.format(operator='or' if customer_type == 'GUEST' else 'and')

    Connection = create_connection()
    cursor = Connection.cursor()
    cursor.execute(query, (booking_id, booking_last_name, customer_id))
    booking_info = cursor.fetchone()
    cursor.close()

    WHERE = """
    f.flight_id=%s and al.airline_code=f.airline and ap.airplane_model=f.airplane and aprt1.airport_code=f.from_airport and aprt2.airport_code=f.to_airport
    """

    params = (booking_info['depart_flight_id'],)

    if booking_info['flight_type'] == 'Roundtrip':
        is_roundtrip = True

        WHERE = """
        f1.flight_id=%s and f2.flight_id=%s and al1.airline_code=f1.airline and ap1.airplane_model=f1.airplane and aprt1.airport_code=f1.from_airport and aprt2.airport_code=f1.to_airport and al2.airline_code=f2.airline and ap2.airplane_model=f2.airplane and aprt3.airport_code=f2.from_airport and aprt4.airport_code=f2.to_airport
        """

        params += (booking_info['return_flight_id'],)
    
    flight = get_flights(is_roundtrip=is_roundtrip, params=params, WHERE=WHERE, FETCH_ALL=False)
    depart_flight, return_flight = build_selected_flights(flight=flight, 
                                                          is_roundtrip=is_roundtrip)

    picked_flight = depart_flight

    if return_flight is not None:
        picked_flight += '<hr class="my-2">'
        picked_flight += return_flight

    query = """
    SELECT p.passenger_id as id, p.first_name as first_name, p.last_name as last_name, phb.seat as seat, phb.seat_class as seat_class
    FROM passenger as p, pass_has_booking as phb
    WHERE p.passenger_id=phb.passenger_id and phb.booking_id=%s
    """

    cursor = Connection.cursor()
    cursor.execute(query, (booking_id))
    passenger_info = cursor.fetchall()
    cursor.close()

    query = """
    SELECT first_name, last_name, email, mobile
    FROM booking
    WHERE booking_id=%s and (last_name=%s {operator} customer_id=%s)
    """.format(operator='or' if customer_type == 'GUEST' else 'and')

    cursor = Connection.cursor()
    cursor.execute(query, (booking_id, booking_last_name, customer_id))
    contact_info = cursor.fetchone()
    cursor.close()
    Connection.close()

    data = {'booking_info': booking_info,
            'flight': picked_flight,
            'passenger_info': passenger_info,
            'contact_info': contact_info}

    return data

def restricted(access_level):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if not get_customer_type() == access_level:
                abort(403)
            return fn(*args, **kwargs)
        return wrapper
    return decorator

def redirect_guest(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if get_customer_type() == 'GUEST' and session.get('is_guest') is None:
            session['is_guest'] = True
            return redirect(url_for('guest_detected', next=request.path))
        return fn(*args, **kwargs)
    return wrapper

@app.before_request
def current_user():
    query = """
    SELECT customer_id as id, first_name, customer_type as type
    FROM customer
    WHERE customer_id=%s
    """

    Connection = create_connection()
    cursor = Connection.cursor()
    cursor.execute(query, (session.get('customer_id', 0)))
    result = cursor.fetchone()
    cursor.close()
    Connection.close()

    g.current_customer = result

@app.errorhandler(403)
def access_denied(e):
    return render_template('403.html'), 403

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

@app.route('/')
@app.route('/index.html')
def index():
    return render_template('index.html', airports=get_airports())

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
    is_roundtrip = False

    WHERE = """
    al.airline_code=f.airline and ap.airplane_model=f.airplane and aprt1.airport_code=f.from_airport and aprt2.airport_code=f.to_airport and f.from_airport=%s and f.to_airport=%s and f.dep_date=%s and IF(f.dep_date=CURRENT_DATE, f.dep_time>=CURRENT_TIME, 1) and f.occupied_capacity <= (ap.capacity-%s) and f.class=%s and f.status="Upcoming"
    """

    ORDER_BY = 'f.price'

    start_limit = int(request.args.get('startLimit'))
    end_limit = int(request.args.get('endLimit'))
    LIMIT = '{start},{end}'.format(start=start_limit, end=end_limit)

    from_airport_code = re.sub(r'[\(\)]', "", request.args.get('fromAirport')).rsplit(' ', 1)[1]
    to_airport_code = re.sub(r'[\(\)]', "", request.args.get('toAirport')).rsplit(' ', 1)[1]
    passenger_num = int(request.args.get('numPassengers'))
    flight_class = request.args.get('flightClass')
    
    temp_depart_date = request.args.get('departDate')
    depart_date = datetime.strptime(temp_depart_date, '%d %b %Y').date()
    return_date = request.args.get('returnDate')
    
    params = (from_airport_code, to_airport_code, depart_date, passenger_num, flight_class)

    if return_date != 'One Way':
        is_roundtrip = True
    
        WHERE = """
        al1.airline_code=f1.airline and ap1.airplane_model=f1.airplane and aprt1.airport_code=f1.from_airport and aprt2.airport_code=f1.to_airport and f1.from_airport=%s and f1.to_airport=%s and f1.dep_date=%s and IF(f1.dep_date=CURRENT_DATE, f1.dep_time>=CURRENT_TIME, 1) and f1.occupied_capacity <= (ap1.capacity-%s) and f1.class=%s and f1.status="Upcoming" and al2.airline_code=f2.airline and ap2.airplane_model=f2.airplane and aprt3.airport_code=f2.from_airport and aprt4.airport_code=f2.to_airport and f2.from_airport=%s and f2.to_airport=%s and f2.dep_date=%s and f2.occupied_capacity <= (ap2.capacity-%s) and f2.class=%s and f2.status="Upcoming" and %s and %s
        """

        ORDER_BY = 'f1.price+f2.price'

        dep_time = 'f2.dep_time>=ADDTIME(f1.arr_time, "05:00:00")' if return_date == temp_depart_date else 1
        arr_date = 'f1.arr_date=f1.dep_date' if return_date == temp_depart_date else 1
        return_date = datetime.strptime(return_date, '%d %b %Y').date()

        params = (from_airport_code, to_airport_code, depart_date, passenger_num, flight_class, to_airport_code, from_airport_code, return_date, passenger_num, flight_class, dep_time, arr_date)

    data = get_flights(is_roundtrip=is_roundtrip, params=params, WHERE=WHERE, ORDER_BY=ORDER_BY, LIMIT=LIMIT)

    if not len(data):
        return jsonify(message='no_result', content='')

    flights = """   <div id="flightsContainer" class="mt-3 mb-4">"""

    for i, flight in enumerate(data):
        depart_flight_id = flight['departFlightID']
        return_flight_id = flight['returnFlightID'] if is_roundtrip else 'None'
        price = flight['departPrice']+flight['returnPrice'] if is_roundtrip else flight['departPrice']
        post_url = url_for('picked_flight', depart_flight_id=depart_flight_id, return_flight_id=return_flight_id, passenger_num=passenger_num, price=price, is_roundtrip=is_roundtrip)
        
        flights += """  <div id="flight-{id}" class="my-4">
                            <form id="pickedFlightForm-{id}" action="{post_url}">
                                <div class="row justify-content-center align-items-center">
                                    <div class="flight-row col-12 col-sm-8 col-md-9 col-lg-8 col-xl-6 flight-card-padding-right">
                                        <div id="flightInfo" class="flight card rounded-3x flight-card-sm shadow-1 small">
                                            <div class="card-body">""".format(id=i+1, post_url=post_url)

        depart_flight, return_flight = build_flights(flight, is_roundtrip)

        flights += depart_flight
        if return_flight is not None:
            flights += '<hr class="my-2">'
            flights += return_flight

        flights += """                      </div>
                                            <div class="d-block d-sm-none">
                                                <button class="btn btn-sm btn-primary btn-block" type="submit">Select - €{price}</button>
                                            </div>
                                        </div>
                                    </div>
                                    <div class="d-none d-sm-block col-sm-4 col-md-3 col-lg-2 flight-card-padding-left">
                                        <div id="flightPrice" class="price card rounded-3x shadow-1 text-center">
                                            <div class="price-body card-body d-flex flex-column justify-content-center align-items-center">""".format(id=i+1, price=price)
        if is_roundtrip:
            flights += """                      <div class="font-weight-bold font-size-lg mb-2">€{price}</div>
                                                <button class="btn btn-primary" type="submit">Select</button>""".format(id=i+1, price=price)
        else:
            flights += """                       <button class="btn btn-primary btn-block" type="submit">
                                                    Select (€{price})                                    
                                                </button>
                                                """.format(id=i+1, price=price)
        
        flights += """                       </div>
                                        </div>
                                    </div>
                                </div>
                            </form>
                        </div>""".format(price=price)

    # if len(data) > 5:
    #     flights += """      <div class="row justify-content-center">
    #                             <a id="loadMore" class="btn btn-primary load-more__btn" href="#"><i class="fas fa-spinner fa-fw mr-2"></i>Load More</a>
    #                         </div>
    #                     </div>
    #                 </div>
    #             </div>
    #         </div>"""

    if len(data) == 5:
        flights += """      <div id="moreFlightContent"></div>
                            <div id="loadMoreBtn" class="row justify-content-center">
                                <input type="hidden" name="startLimitMore" value="{start}">
                                <input type="hidden" name="endLimitMore" value="{end}">
                                <a id="loadMoreFlights" class="btn btn-primary" href="#"><i class="fas fa-spinner fa-fw mr-2"></i>Load More</a>
                            </div>
                        </div>
                    </div>
                </div>
            </div>""".format(start=start_limit+5, end=end_limit+5)
    
    return jsonify(message='result', content=flights)

@app.route('/guest-detected.html')
def guest_detected():
    return render_template('guest-detected.html')

@app.route('/guest-detected.html', methods=['POST'])
def guest_detected_post():
    form = request.form

    next_url = request.args.get('next')
    btn_state = form.get('btnState')
    if btn_state == 'guest':
        return redirect(urllib.parse.quote(next_url))
    elif btn_state == 'sign_in':
        return redirect(url_for('sign_in', next=next_url))
    else:
        return redirect(url_for('sign_up', next=next_url))

@app.route('/new_booking?depart_flight_id=<depart_flight_id>&return_flight_id=<return_flight_id>&passenger_num=<passenger_num>&price=<price>&is_roundtrip=<is_roundtrip>')
@redirect_guest
def picked_flight(depart_flight_id='', return_flight_id='', passenger_num=0, price=0, is_roundtrip=False):
    session.pop('is_guest', None)
    is_roundtrip = is_roundtrip == 'True'

    WHERE = """
    f.flight_id=%s and al.airline_code=f.airline and ap.airplane_model=f.airplane and aprt1.airport_code=f.from_airport and aprt2.airport_code=f.to_airport
    """

    params = (depart_flight_id,)

    if is_roundtrip:
        WHERE = """
        f1.flight_id=%s and f2.flight_id=%s and al1.airline_code=f1.airline and ap1.airplane_model=f1.airplane and aprt1.airport_code=f1.from_airport and aprt2.airport_code=f1.to_airport and al2.airline_code=f2.airline and ap2.airplane_model=f2.airplane and aprt3.airport_code=f2.from_airport and aprt4.airport_code=f2.to_airport
        """

        params += (return_flight_id,)
    
    flight = get_flights(is_roundtrip=is_roundtrip, params=params, WHERE=WHERE, FETCH_ALL=False)

    if get_customer_type() == 'USER':
        check_query = """
        SELECT status 
        FROM booking 
        WHERE customer_id=%s and depart_flight_id=%s and status="Active"
        """

        Connection = create_connection()
        cursor = Connection.cursor()
        cursor.execute(check_query, (get_customer_id(), flight['departFlightID']))
        result = cursor.fetchone()
        cursor.close()
        Connection.close()

        if result is not None:
            flash('You have already booked this flight route!', 'error')
            return redirect(url_for('index'))

    price = int(price)
    passenger_num = int(passenger_num)
    total_price = price*passenger_num

    depart_flight, return_flight = build_selected_flights(flight=flight, 
                                                          is_roundtrip=is_roundtrip)

    picked_flight = depart_flight

    if return_flight is not None:
        picked_flight += '<hr class="my-2">'
        picked_flight += return_flight
    
    return render_template('new-booking.html', picked_flight=picked_flight, num_passenger=passenger_num, price=price, total_price=total_price, is_roundtrip=is_roundtrip)

@app.route('/new-booking', methods=["POST"])
def new_booking():
    customer_id = get_customer_id()
    form = request.form
    is_roundtrip = form.get('isRoundtrip') == 'True'

    flight_info = {'depart_flight_id': form.get('DepartFlightID'),
                   'return_flight_id': form.get('ReturnFlightID') if is_roundtrip else None,
                   'type': 'Roundtrip' if is_roundtrip else 'Oneway',
                   'total_passengers': int(form.get('numPassenger')),
                   'price_per_passenger': form.get('pricePerPassenger'),
                   'total_price': form.get('totalPrice')}

    query = """
    SELECT booking_id 
    FROM booking
    WHERE booking_id=%s"""

    Connection = create_connection()
    cursor = Connection.cursor()

    # booking_ids = list(result)

    booking_id = fake.lexify(text="??????", letters="ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789")
    cursor.execute(query, booking_id)
    result = cursor.fetchone()
    while result is not None:
        booking_id = fake.lexify(text="??????", letters="ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789")
        cursor.execute(query, booking_id)
        result = cursor.fetchone()
    cursor.close()

    current_date = datetime.today().date()
    passenger_info = []
    for i in range(flight_info['total_passengers']):
        first_name = 'firstNamePassenger-{num}'.format(num=i+1)
        last_name = 'lastNamePassenger-{num}'.format(num=i+1)
        identifier = 'idPassenger-{num}'.format(num=i+1)
        seat = 'seatPassenger-{num}'.format(num=i+1)
        seat_class = 'seatClassPassenger-{num}'.format(num=i+1)

        passenger = {'id': form.get(identifier), 
                     'first_name': form.get(first_name),
                     'last_name': form.get(last_name),
                     'seat': form.get(seat),
                     'seat_class': form.get(seat_class)}
        
        passenger_info.append(passenger)
    
    contact_info = {'first_name': form.get('contactFirstName'),
                    'last_name': form.get('contactLastName'),
                    'email': form.get('contactEmail'),
                    'mobile': form.get('contactMobile')}

    booking = {'booking_id': booking_id,
               'customer_id': customer_id,
               'depart_flight_id': flight_info['depart_flight_id'], 
               'return_flight_id': flight_info['return_flight_id'],	
               'first_name': contact_info['first_name'],
               'last_name': contact_info['last_name'],
               'email': contact_info['email'],
               'mobile': contact_info['mobile'],
               'booking_date': current_date,
               'last_modify_date': current_date,
               'total_passengers': flight_info['total_passengers'],
               'price_per_passenger': flight_info['price_per_passenger'],
               'total_price': flight_info['total_price'],
               'flight_type': flight_info['type'],
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

    query = """
    UPDATE flight 
    SET occupied_capacity=occupied_capacity+%s 
    WHERE flight_id=%s
    """
    
    cursor = Connection.cursor()
    cursor.execute(query, (flight_info['total_passengers'], flight_info['depart_flight_id']))
    if is_roundtrip:
        cursor.execute(query, (flight_info['total_passengers'], flight_info['return_flight_id']))
    Connection.commit()
    cursor.close()
    
    ins_p = """
    INSERT INTO passenger (passenger_id, first_name, last_name) 
    VALUE(%s, %s, %s)
    """

    ins_pb = """
    INSERT INTO pass_has_booking (passenger_id, booking_id, seat, seat_class) 
    VALUE(%s, %s, "1A", "None")
    """

    for passenger in passenger_info:
        try:
            cursor = Connection.cursor()
            cursor.execute(ins_p, (passenger['id'], passenger['first_name'], passenger['last_name']))
            Connection.commit()
            cursor.close()
        except:
            print('Passenger with id={id} exists'.format(id=passenger['id']))
        cursor = Connection.cursor()
        cursor.execute(ins_pb, (passenger['id'], booking_id))
        Connection.commit()
        cursor.close()
    
    Connection.close()

    return redirect(url_for('view_booking', booking_id=booking_id, booking_last_name=contact_info['last_name'], go_back=False))

@app.route('/sign-in.html')
def sign_in():
    has_next = request.args.get('next') is not None
    return render_template('sign-in.html', has_next=has_next)

@app.route('/sign-in.html', methods=["POST"])
def sign_in_post():
    email = request.form.get('email')
    password = request.form.get('password')
    next_url = request.args.get('next')

    Connection = create_connection()
    cursor = Connection.cursor()
    cursor.execute('SELECT customer_id, first_name, last_name, password, customer_type FROM customer WHERE email=%s', (email))
    result = cursor.fetchone()
    cursor.close()
    Connection.close()
    
    if result is None:
        flash("The user does not exist!", 'error')
        return redirect(url_for('sign_in', next=next_url))
    
    if not chk_pw_hash(result['password'], password):
        flash("You have entered a wrong password!", 'error')
        return redirect(url_for('sign_in', next=next_url))
    
    session['customer_id'] = result['customer_id']
    session['email'] = email
    session['customer_type'] = result['customer_type']
    session['first_name'] = result['first_name']
    session['last_name'] = result['last_name']
    session['name'] = '{fname} {lname}'.format(fname=result['first_name'], lname=result['last_name'])
    
    
    return redirect(urllib.parse.quote(next_url) if next_url is not None else url_for('index'))

@app.route('/sign-up.html')
def sign_up():
    has_next = request.args.get('next') is not None
    return render_template('sign-up.html', has_next=has_next)

@app.route('/sign-up.html', methods=["POST"])
def sign_up_post():
    form = request.form

    first_name = form.get('firstName')
    last_name = form.get('lastName')
    mobile = form.get('mobile')
    gender = form.get('gender')
    email = form.get('email')
    password = gen_pw_hash(form.get('password'))
    next_url = request.args.get('next')
    current_date = datetime.now().date()

    Connection = create_connection()
    cursor = Connection.cursor()
    cursor.execute('SELECT * FROM customer WHERE email=%s', (email))
    result = cursor.fetchone()
    cursor.close()

    if result is not None:
        flash("The user already exists", 'error')
        return redirect(url_for('sign_up', next=next_url))
    
    cursor = Connection.cursor()
    cursor.execute('SELECT COUNT(*) as next_id FROM customer')
    customer_id = int(cursor.fetchone()['next_id'])
    cursor.close()
    
    ins = """
    INSERT INTO customer (customer_id, first_name, last_name, email, password, mobile, gender, joined_date, status, customer_type) 
    VALUE(%s, %s, %s, %s, %s, %s, %s, %s, "Active", "USER")
    """

    cursor = Connection.cursor()
    cursor.execute(ins, (customer_id, first_name, last_name, email, password, mobile, gender, current_date))
    cursor.close()
    Connection.commit()
    Connection.close()

    session['customer_id'] = customer_id
    session['email'] = email
    session['customer_type'] = 'USER'
    session['first_name'] = first_name
    session['last_name'] = last_name
    session['full_name'] = '{fname} {lname}'.format(fname=first_name, lname=last_name)

    return redirect(urllib.parse.quote(next_url) if next_url is not None else url_for('index'))

@app.route('/sign-out.html')
@restricted(access_level='USER')
def sign_out():
    session.clear()
    return redirect(url_for('index'))

@app.route('/user-profile.html')
@restricted(access_level='USER')
def profile():
    Connection = create_connection()

    user_query = """
    SELECT first_name, last_name, email, mobile, gender, DATE_FORMAT(joined_date, "%%d %%b %%Y") as joined_date
    FROM customer
    WHERE customer_id=%s
    """

    cursor = Connection.cursor()
    cursor.execute(user_query, (session['customer_id']))
    user_info = cursor.fetchone()
    cursor.close()
    Connection.close()

    return render_template('user-profile.html', user_info=user_info)

@app.route('/edit-info', methods=["POST"])
@restricted(access_level='USER')
def edit_info():
    form = request.form
    first_name = form.get('firstName')
    last_name = form.get('lastName')
    mobile = form.get('mobile')

    query = """
    UPDATE customer 
    SET first_name=%s, last_name=%s, mobile=%s 
    WHERE customer_id=%s and email=%s
    """

    Connection = create_connection()
    cursor = Connection.cursor()
    cursor.execute(query, (first_name, last_name, mobile, session['customer_id'], session['email']))
    cursor.close()
    Connection.commit()
    Connection.close()

    flash('Profile updated successfully', 'success')
    return redirect(url_for('profile'))

@app.route('/change-password', methods=["POST"])
@restricted(access_level='USER')
def change_password():
    form = request.form
    current_password = form.get('currentPassword')
    new_password = gen_pw_hash(form.get('newPassword'))

    Connection = create_connection()
    cursor = Connection.cursor()
    cursor.execute('SELECT password FROM customer WHERE customer_id=%s', (session['customer_id']))
    db_password = cursor.fetchone()['password']
    cursor.close()
    
    if not chk_pw_hash(db_password, current_password):
        Connection.close()
        flash('You have entered a wrong password!', 'error')
        return redirect(url_for('profile'))

    query = """
    UPDATE customer 
    SET password=%s 
    WHERE customer_id=%s and email=%s
    """

    cursor = Connection.cursor()
    cursor.execute(query, (new_password, session['customer_id'], session['email']))
    cursor.close()
    Connection.commit()
    Connection.close()

    return redirect(url_for('sign_out'))

@app.route('/delete-account', methods=["POST"])
@restricted(access_level='USER')
def delete_account():
    customer_id = get_customer_id()
    form = request.form
    current_password = form.get('currentDeletePassword')

    query = """
    SELECT password 
    FROM customer 
    WHERE customer_id=%s
    """

    Connection = create_connection()
    cursor = Connection.cursor()
    cursor.execute(query, (customer_id))
    db_password = cursor.fetchone()['password']
    cursor.close()
    
    if not chk_pw_hash(db_password, current_password):
        Connection.close()
        flash('You have entered a wrong password!', 'error')
        return redirect(url_for('profile'))
    
    query = """
    DELETE FROM customer 
    WHERE customer_id=%s and email=%s
    """

    cursor = Connection.cursor()
    cursor.execute(query, (customer_id, session['email']))
    cursor.close()
    Connection.commit()
    Connection.close()

    return redirect(url_for('sign_out'))

@app.route('/my-bookings.html')
@restricted(access_level='USER')
def my_bookings():
    customer_id = get_customer_id()

    query = """
    SELECT b.booking_id as id, b.last_name as last_name, a1.city as from_city, a2.city as to_city, DATE_FORMAT(b.booking_date, "%%d %%b %%Y") as date, b.flight_type as flight_type, b.status as status 
    FROM booking as b, flight as f, airport as a1, airport as a2 
    WHERE b.customer_id=%s and b.status in (%s, %s) and f.flight_id=b.depart_flight_id and a1.airport_code=f.from_airport and a2.airport_code=f.to_airport 
    ORDER BY date DESC 
    """

    Connection = create_connection()
    cursor = Connection.cursor()
    cursor.execute(query, (customer_id, 'Active', '""'))
    upcoming_bookings = cursor.fetchall()
    cursor.close()

    # upcoming_bookings = [next(d) for _,d in groupby(result, key=lambda _d: _d['ID'])]

    cursor = Connection.cursor()
    cursor.execute(query, (customer_id, 'Passed', 'Canceled'))
    passed_bookings = cursor.fetchall()
    cursor.close()
    Connection.close()

    # passed_bookings = [next(d) for _,d in groupby(result, key=lambda _d: _d['ID'])]

    return render_template('/my-bookings.html', upcoming_bookings=upcoming_bookings, passed_bookings=passed_bookings)

@app.route('/manage-booking.html')
@restricted(access_level='GUEST')
def manage_booking_page():
    messages = {'not_found': 'We are unable to find the booking reference you provided. Please validate that your information is correct and try again.',
                'inactive': 'We are unable unable to perform the task you have asked. The booking may be inactive or canceled.',
                'canceled': 'Your booking has been successfully canceled.'}

    error = session.pop('error', None)
    success = session.pop('success', None)
    
    message = messages[success] if success is not None else messages[error] if error is not None else False
    show_alert = True if message else False

    alert = {'type': 'success' if success is not None else 'error',
             'message': message}

    return render_template('manage-booking.html', show_alert=show_alert, alert=alert)

@app.route('/manage-booking', methods=['POST'])
def manage_booking():
    form = request.form
    booking_id = form.get('bookingID')
    booking_last_name = form.get('lastName')
    go_back = False if get_customer_id() == 0 else True
    
    if get_customer_type() == 'GUEST' and not booking_exists(booking_id, booking_last_name):
        session['error'] = 'not_found'
        return redirect(url_for('manage_booking_page'))

    btn_state = form.get('btnState')

    if btn_state == 'view':
        return redirect(url_for('view_booking', booking_id=booking_id, booking_last_name=booking_last_name, go_back=go_back))
    else:
        if get_customer_type() == 'GUEST' and booking_is_inactive(booking_id, booking_last_name):
            session['error'] = 'inactive'
            return redirect(url_for('manage_booking_page'))

        if btn_state == 'modify':
            return redirect(url_for('modify_booking', booking_id=booking_id, booking_last_name=booking_last_name, go_back=True))
        else:
            return redirect(url_for('cancel_booking', booking_id=booking_id, booking_last_name=booking_last_name))

@app.route('/view-booking/<booking_id>&<booking_last_name>&<go_back>')
def view_booking(booking_id='', booking_last_name='', modify=False, go_back=False):
    go_back_address = 'my_bookings'
    data = get_booking(booking_id, booking_last_name)

    return render_template('get-booking.html', booking=data['booking_info'], picked_flight=data['flight'], passenger_info=data['passenger_info'], contact_info=data['contact_info'], go_back=go_back == 'True', go_back_address=url_for(go_back_address))

@app.route('/modify-booking/<booking_id>&<booking_last_name>&<go_back>')
def modify_booking(booking_id='', booking_last_name='', modify=False, go_back=False):
    go_back_address = 'index' if get_customer_type() == 'GUEST' else 'my_bookings'
    data = get_booking(booking_id, booking_last_name)

    return render_template('modify-booking.html', booking=data['booking_info'], picked_flight=data['flight'], passenger_info=data['passenger_info'], contact_info=data['contact_info'], go_back=go_back == 'True', go_back_address=url_for(go_back_address))

@app.route('/modify-booking', methods=['POST'])
def modify_booking_post():
    form = request.form
    booking_id = form.get('bookingID')
    first_name = form.get('contactFirstName')
    last_name = form.get('contactLastName')
    email = form.get('contactEmail')
    mobile = form.get('contactMobile')
    old_last_name = form.get('oldContactLastName')
    customer_type = get_customer_type()
    current_date = datetime.now().date()
    
    query = """
    UPDATE booking 
    SET first_name=%s, last_name=%s, email=%s, mobile=%s, last_modify_date=%s 
    WHERE booking_id=%s and last_name=%s
    """

    Connection = create_connection()
    cursor = Connection.cursor()
    cursor.execute(query, (first_name, last_name, email, mobile, current_date, booking_id, old_last_name))
    cursor.close()
    Connection.commit()
    Connection.close()

    go_back = False if customer_type == 'GUEST' else True

    return redirect(url_for('view_booking', booking_id=booking_id, booking_last_name=last_name, go_back=go_back))

@app.route('/cancel-booking/<booking_id>&<booking_last_name>')
def cancel_booking(booking_id='', booking_last_name=''):
    customer_type = get_customer_type()

    query = """
    UPDATE booking 
    SET status=%s 
    WHERE booking_id=%s and last_name=%s
    """
    
    Connection = create_connection()
    cursor = Connection.cursor()
    cursor.execute(query, ('Canceled', booking_id, booking_last_name))
    cursor.close()
    Connection.commit()
    Connection.close()
    
    if customer_type == 'GUEST':
        session['success'] = 'canceled'
    else:
        flash('The booking has been successfully canceled', 'success')

    return redirect(url_for('manage_booking_page') if customer_type == 'GUEST' else url_for('my_bookings'))

@app.route('/add-booking', methods=['POST'])
@restricted(access_level='USER')
def add_booking():
    form = request.form

    booking_id = form.get('bookingID')
    first_name = form.get('firstName')
    last_name = form.get('lastName')

    query = """
    SELECT *
    FROM booking
    WHERE booking_id=%s and first_name=%s and last_name=%s
    """

    Connection = create_connection()
    cursor = Connection.cursor()
    cursor.execute(query, (booking_id, first_name, last_name))
    booking = cursor.fetchone()
    cursor.close()
    Connection.close()

    if booking is None:
        flash('The booking you are trying to add doesn\'t exists!', 'error')
        return redirect(url_for('my_bookings'))

    if booking_exists(booking_id, last_name):
        flash('The booking you are trying to add already exists!', 'error')
        return redirect(url_for('my_bookings'))

    Connection = create_connection()
    booking['customer_id'] = session['customer_id']
    
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
    Connection.close()

    flash('The booking has been successfully added to your account', 'success')
    return redirect(url_for('my_bookings'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
