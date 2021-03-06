from flask import session, request, redirect, g, url_for, abort, flash
from itsdangerous import URLSafeTimedSerializer, URLSafeSerializer
from pymysql.cursors import DictCursor
from datetime import datetime
from functools import wraps
from faker import Faker
import requests
import pymysql
import platform
import json
import os


WINDOWS = platform.system() == "Windows"
OSX = platform.system() == "Darwin"
fake = Faker()


def restricted(access_level):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not get_customer_type() == access_level:
                return abort(403)
            return func(*args, **kwargs)

        return wrapper

    return decorator


def redirect_when(_type):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if get_customer_type() == _type:
                return redirect(url_for("index"))
            return func(*args, **kwargs)

        return wrapper

    return decorator


def redirect_guest(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if get_customer_type() == "GUEST" and session.get("is_guest") is None:
            session["is_guest"] = True
            return redirect(url_for("guest_detected", next=request.path))
        return func(*args, **kwargs)

    return wrapper


def check_unconfirmed(by="", TIMED=True):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            arg = request.values.get(by)
            arg = arg if arg else request.view_args.get(by)

            if arg is None:
                return abort(404)
            else:
                email = arg if by == "email" else confirm_token(token=arg, TIMED=TIMED)
                if not email:
                    flash("The requested link is invalid or has expired.", "error")
                    return redirect(url_for("index"))

                if user_is_confirmed(email):
                    flash(
                        "Your account is already confirmed. Please sign in!", "warning"
                    )
                    return redirect(url_for("index"))

            return func(*args, **kwargs)

        return wrapper

    return decorator


def create_connection():
    options = {
        "host": os.getenv("DB_HOST"),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD"),
        "db": os.getenv("DB_NAME"),
        "charset": "utf8mb4",
        "cursorclass": DictCursor,
    }

    if OSX:
        options.update({"unix_socket": "/Applications/MAMP/tmp/mysql/mysql.sock"})

    return pymysql.connect(**options)


def get_customer_id():
    return g.current_customer.get("id")


def get_customer_type():
    return g.current_customer.get("type")


def set_session_user(info={}):
    return session.update(info)


def clear_session_user():
    for field in [
        "customer_id",
        "email",
        "customer_type",
        "first_name",
        "last_name",
        "full_name",
    ]:
        session.pop(field, None)


def user_is_confirmed(email):
    if email is None:
        return True

    query = """
    SELECT status
    FROM customer
    WHERE email=%s and status="Confirmed"
    """

    cnx = create_connection()
    cursor = cnx.cursor()
    cursor.execute(query, (email))
    result = cursor.fetchone()
    cursor.close()
    cnx.close()

    return result is not None


def get_user_fullname(email=None):
    if not email:
        return None

    query = """
    SELECT first_name, last_name
    FROM customer
    WHERE email=%s
    """

    cnx = create_connection()
    cursor = cnx.cursor()
    cursor.execute(query, (email))
    result = cursor.fetchone()
    cursor.close()
    cnx.close()

    return (
        email.split("@")[0]
        if "first_name" not in result
        else "{fname} {lname}".format(
            fname=result["first_name"], lname=result["last_name"]
        )
    )


def build_flight_card(
    airline_logo="",
    airline_name="",
    from_airport="",
    time_from="",
    to_airport="",
    time_to="",
):
    return """  <div class="form-row justify-content-center align-items-center">
                    <div class="col-2 px-0 px-md-2 px-lg-0 px-xl-2 text-center">
                        <img src="../../static/images/airlines/{airline_logo}.png" class="img-fluid h-75 w-75" alt="{airline_name}"/>
                        <p class="d-picked-none font-size-90 font-weight-bold text-muted mb-0 mt-1">{airline_name}</p>
                    </div>
                    <div class="col-3 col-sm-2">
                        <div class="text-right font-weight-bold font-size-lg">{time_from}</div>
                        <div class="text-right text-muted font-size-lg">{from_airport}</div>
                    </div>
                    <div class="col-4 col-sm-6">
                        <hr data-content="" class="hr-text hr-icon">
                    </div>
                    <div class="col-3 col-sm-2">
                        <div class="text-left font-weight-bold font-size-lg">{time_to}</div>
                        <div class="text-left text-muted font-size-lg">{to_airport}</div>
                    </div>
                </div>""".format(
        airline_logo=airline_logo,
        airline_name=airline_name,
        from_airport=from_airport,
        time_from=time_from,
        to_airport=to_airport,
        time_to=time_to,
    )


def build_selected_flight_card(
    id="",
    flight="",
    flight_id="",
    airline_name="",
    from_airport="",
    from_city="",
    to_airport="",
    to_city="",
    date="",
    klass="",
    airplane="",
    duration="",
    flight_type="",
):
    card = """  <div id="{flight_type}Flight" class="card rounded-3x shadow-none">
                    <a aria-controls="picked{flight_type}Flight" aria-expanded="false" class="small accordion-toggler text-body collapsed" data-toggle="collapse" href="#picked{flight_type}Flight">
                        <div class="form-row justify-content-center align-items-center">
                            <div class="col-11 px-0">""".format(
        flight_type=flight_type
    )
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
                                    <input type="hidden" id="{flight_type}FlightID" name="{flight_type}FlightID" value="{flight_id}">
                                    <input type="hidden" id="{flight_type}Date" name="{flight_type}Date" value="{date}">
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
                </div>""".format(
        flight_id=flight_id,
        airline_name=airline_name,
        from_airport=from_airport,
        from_city=from_city,
        to_airport=to_airport,
        to_city=to_city,
        date=date,
        klass=klass,
        airplane=airplane,
        hours=duration.hour,
        minutes=duration.minute,
        flight_type=flight_type,
    )

    return card


def build_flights(flight="", is_roundtrip=False):
    depart_flight = build_flight_card(
        airline_logo=flight["departAirlineCode"],
        airline_name=flight["departAirlineName"],
        from_airport=flight["departFromAirport"],
        time_from=flight["departTime"],
        to_airport=flight["departToAirport"],
        time_to=flight["departArrivalTime"],
    )
    return_flight = None
    if is_roundtrip:
        return_flight = build_flight_card(
            airline_logo=flight["returnAirlineCode"],
            airline_name=flight["returnAirlineName"],
            from_airport=flight["returnFromAirport"],
            time_from=flight["returnTime"],
            to_airport=flight["returnToAirport"],
            time_to=flight["returnArrivalTime"],
        )

    return depart_flight, return_flight


def build_selected_flights(picked_flight_index=0, flight="", is_roundtrip=False):
    depart_flight, return_flight = build_flights(
        flight=flight, is_roundtrip=is_roundtrip
    )

    duration = flight["departDuration"]
    depart_duration = datetime.strptime(duration, "%H:%M").time()

    depart_flight = build_selected_flight_card(
        id=picked_flight_index + 1,
        flight=depart_flight,
        flight_id=flight["departFlightID"],
        airline_name=flight["departAirlineName"],
        from_airport=flight["departFromAirport"],
        from_city=flight["departFromCity"],
        to_airport=flight["departToAirport"],
        to_city=flight["departToCity"],
        date=flight["departDate"],
        klass=flight["departClass"],
        airplane=flight["departAirplaneName"],
        duration=depart_duration,
        flight_type="Depart",
    )

    if is_roundtrip:
        duration = flight["returnDuration"]
        return_duration = datetime.strptime(duration, "%H:%M").time()

        return_flight = build_selected_flight_card(
            id=picked_flight_index + 1,
            flight=return_flight,
            flight_id=flight["returnFlightID"],
            airline_name=flight["returnAirlineName"],
            from_airport=flight["returnFromAirport"],
            from_city=flight["returnFromCity"],
            to_airport=flight["returnToAirport"],
            to_city=flight["returnToCity"],
            date=flight["returnDate"],
            klass=flight["returnClass"],
            airplane=flight["returnAirplaneName"],
            duration=return_duration,
            flight_type="Return",
        )

    return depart_flight, return_flight


def get_airports():
    query = """
    SELECT city, airport_code as code 
    FROM airport
    """

    cnx = create_connection()
    cursor = cnx.cursor()
    cursor.execute(query)
    result = cursor.fetchall()
    cursor.close()
    cnx.close()

    return result


def get_popular_destinations():
    query = """
    SELECT CASE WHEN ap.airport_code IN ("ATH", "LCA", "SHA") THEN ap.country ELSE ap.city END as name, MIN(f.price) as price 
    FROM FLIGHT as f, AIRPORT as ap 
    WHERE f.dep_date = CURRENT_DATE and ap.airport_code = f.from_airport and f.from_airport in ( "ATH", "LCA", "DME", "HND", "JFK", "LHR", "ORY", "MAD", "SHA" ) 
    GROUP BY ap.city, ap.country, ap.airport_code
    """

    cnx = create_connection()
    cursor = cnx.cursor()
    cursor.execute(query)
    result = cursor.fetchall()
    cursor.close()
    cnx.close()

    return result


def get_flights(
    is_roundtrip=False, params=(), WHERE="", ORDER_BY="", LIMIT="", FETCH_ALL=True
):
    query = """
    SELECT f.flight_id as departFlightID, f.airline as departAirlineCode, al.airline_name as departAirlineName, DATE_FORMAT(f.dep_date, "%%d %%b %%Y") as departDate, f.from_airport as departFromAirport, aprt1.city as departFromCity, TIME_FORMAT(f.dep_time, "%%H:%%i") as departTime, f.to_airport as departToAirport, aprt2.city as departToCity, TIME_FORMAT(f.arr_time, "%%H:%%i") as departArrivalTime, f.price as departPrice, f.class as departClass, TIME_FORMAT(f.duration, "%%H:%%i") as departDuration, ap.airplane_name as departAirplaneName
    FROM flight as f, airline as al, airplane as ap, airport as aprt1, airport as aprt2
    """

    count_query = """
    SELECT COUNT(*) as totalRows
    FROM flight as f, airline as al, airplane as ap, airport as aprt1, airport as aprt2
    """

    if is_roundtrip:
        query = """
        SELECT f1.flight_id as departFlightID, f1.airline as departAirlineCode, al1.airline_name as departAirlineName, DATE_FORMAT(f1.dep_date, "%%d %%b %%Y") as departDate, f1.from_airport as departFromAirport, aprt1.city as departFromCity, TIME_FORMAT(f1.dep_time, "%%H:%%i") as departTime, f1.to_airport as departToAirport, aprt2.city as departToCity, TIME_FORMAT(f1.arr_time, "%%H:%%i") as departArrivalTime, f1.price as departPrice, f1.class as departClass, TIME_FORMAT(f1.duration, "%%H:%%i") as departDuration, ap1.airplane_name as departAirplaneName, f2.flight_id as returnFlightID, f2.airline as returnAirlineCode, al2.airline_name as returnAirlineName, DATE_FORMAT(f2.dep_date, "%%d %%b %%Y") as returnDate, f2.from_airport as returnFromAirport, aprt3.city as returnFromCity, TIME_FORMAT(f2.dep_time, "%%H:%%i") as returnTime, f2.to_airport as returnToAirport, aprt4.city as returnToCity, TIME_FORMAT(f2.arr_time, "%%H:%%i") as returnArrivalTime, f2.price as returnPrice, f2.class as returnClass, TIME_FORMAT(f2.duration, "%%H:%%i") as returnDuration, ap2.airplane_name as returnAirplaneName
        FROM flight as f1, flight as f2, airline as al1, airline as al2, airplane as ap1, airplane as ap2, airport as aprt1, airport as aprt2, airport as aprt3, airport as aprt4
        """

        count_query = """
        SELECT COUNT(*) as totalRows
        FROM flight as f1, flight as f2, airline as al1, airline as al2, airplane as ap1, airplane as ap2, airport as aprt1, airport as aprt2, airport as aprt3, airport as aprt4
        """

    if WHERE:
        query += " WHERE {where}".format(where=WHERE)
        count_query += " WHERE {where}".format(where=WHERE)

    if ORDER_BY:
        query += " ORDER BY {order}".format(order=ORDER_BY)

    if LIMIT:
        query += " LIMIT {limit}".format(limit=LIMIT)

    cnx = create_connection()
    cursor = cnx.cursor()
    cursor.execute(count_query, params)
    total_rows = cursor.fetchone()["totalRows"]
    cursor.close()

    cursor = cnx.cursor()
    cursor.execute(query, params)
    data = cursor.fetchall() if FETCH_ALL else cursor.fetchone()
    cursor.close()
    cnx.close()

    return total_rows, data


def booking_exists(booking_id, last_name):
    customer_id = get_customer_id()
    customer_type = get_customer_type()

    query = """
    SELECT booking_id 
    FROM booking
    WHERE booking_id=%s and (last_name=%s {operator} customer_id=%s)
    """.format(
        operator="or" if customer_type == "GUEST" else "and"
    )

    cnx = create_connection()
    cursor = cnx.cursor()
    cursor.execute(query, (booking_id, last_name, customer_id))
    result = cursor.fetchone()
    cursor.close()
    cnx.close()

    return result is not None


def booking_is_active(booking_id, last_name):
    query = """
    SELECT status 
    FROM booking 
    WHERE booking_id=%s and last_name=%s and status in ("Active", "Upcoming")
    """

    cnx = create_connection()
    cursor = cnx.cursor()
    cursor.execute(query, (booking_id, last_name))
    result = cursor.fetchone()
    cursor.close()
    cnx.close()

    return result is not None


def booking_is_inactive(booking_id, last_name):
    query = """
    SELECT status 
    FROM booking 
    WHERE booking_id=%s and last_name=%s and status in ("Canceled", "Passed")
    """

    cnx = create_connection()
    cursor = cnx.cursor()
    cursor.execute(query, (booking_id, last_name))
    result = cursor.fetchone()
    cursor.close()
    cnx.close()

    return result is not None


def get_booking(booking_id="", booking_last_name=""):
    customer_id = get_customer_id()
    customer_type = get_customer_type()
    is_roundtrip = False

    query = """
    SELECT booking_id as id, depart_flight_id, depart_flight_date, return_flight_id, return_flight_date, flight_class, DATE_FORMAT(booking_date, "%%d %%b %%Y") as date, total_passengers, price_per_passenger, total_price, flight_type, status
    FROM booking
    WHERE booking_id=%s and (last_name=%s {operator} customer_id=%s) 
    """.format(
        operator="or" if customer_type == "GUEST" else "and"
    )

    cnx = create_connection()
    cursor = cnx.cursor()
    cursor.execute(query, (booking_id, booking_last_name, customer_id))
    booking_info = cursor.fetchone()
    cursor.close()

    WHERE = """
    f.flight_id=%s and f.dep_date=%s and f.class=%s and al.airline_code=f.airline and ap.airplane_model=f.airplane and aprt1.airport_code=f.from_airport and aprt2.airport_code=f.to_airport
    """

    params = (
        booking_info["depart_flight_id"],
        booking_info["depart_flight_date"],
        booking_info["flight_class"],
    )

    if booking_info["flight_type"] == "Roundtrip":
        is_roundtrip = True

        WHERE = """
        f1.flight_id=%s and f1.dep_date=%s and f1.class=%s and f2.flight_id=%s and f2.dep_date=%s and f2.class=%s and al1.airline_code=f1.airline and ap1.airplane_model=f1.airplane and aprt1.airport_code=f1.from_airport and aprt2.airport_code=f1.to_airport and al2.airline_code=f2.airline and ap2.airplane_model=f2.airplane and aprt3.airport_code=f2.from_airport and aprt4.airport_code=f2.to_airport
        """

        params += (
            booking_info["return_flight_id"],
            booking_info["return_flight_date"],
            booking_info["flight_class"],
        )

    _, flight = get_flights(
        is_roundtrip=is_roundtrip, params=params, WHERE=WHERE, FETCH_ALL=False
    )
    depart_flight, return_flight = build_selected_flights(
        flight=flight, is_roundtrip=is_roundtrip
    )

    picked_flight = depart_flight

    if return_flight is not None:
        picked_flight += '<hr class="my-2">'
        picked_flight += return_flight

    query = """
    SELECT p.passenger_id as id, p.first_name as first_name, p.last_name as last_name, phb.seat as seat, phb.seat_class as seat_class, phb.seat_price as seat_price
    FROM passenger as p, pass_has_booking as phb
    WHERE p.passenger_id=phb.passenger_id and phb.booking_id=%s
    """

    cursor = cnx.cursor()
    cursor.execute(query, (booking_id))
    passenger_info = cursor.fetchall()
    cursor.close()

    query = """
    SELECT first_name, last_name, email, mobile
    FROM booking
    WHERE booking_id=%s and (last_name=%s {operator} customer_id=%s)
    """.format(
        operator="or" if customer_type == "GUEST" else "and"
    )

    cursor = cnx.cursor()
    cursor.execute(query, (booking_id, booking_last_name, customer_id))
    contact_info = cursor.fetchone()
    cursor.close()
    cnx.close()

    data = {
        "booking_info": booking_info,
        "flight": picked_flight,
        "passenger_info": passenger_info,
        "contact_info": contact_info,
    }

    return data


def send_email_mailgun(data={}):
    api_key = os.getenv("MAILGUN_API_KEY")
    api_base_url = os.getenv("MAILGUN_API_BASE_URL")
    api_domain = os.getenv("MAILGUN_API_DOMAIN")
    api_email = os.getenv("MAILGUN_API_SENDER_EMAIL")

    api_url = "{base_url}/{domain}/messages".format(
        base_url=api_base_url, domain=api_domain
    )
    sender = "Flight Finder <{email}>".format(email=api_email)

    return requests.post(
        api_url,
        auth=("api", api_key),
        data={
            "from": sender,
            "to": data.get("recipient"),
            "subject": data.get("subject"),
            "template": data.get("template"),
            "h:X-Mailgun-Variables": json.dumps({"action_url": data.get("action_url")}),
        },
    )


def generate_token(email="", TIMED=True):
    if TIMED:
        serializer = URLSafeTimedSerializer(os.getenv("SECRET_KEY"))
        salt = os.getenv("SECURITY_PASSWORD_SALT")
    else:
        serializer = URLSafeSerializer(os.getenv("SECRET_KEY"))
        salt = os.getenv("SECURITY_EMAIL_SALT")

    return serializer.dumps(email, salt=salt)


def confirm_token(token="", expiration=600, TIMED=True):
    try:
        if TIMED:
            serializer = URLSafeTimedSerializer(os.getenv("SECRET_KEY"))
            salt = os.getenv("SECURITY_PASSWORD_SALT")
            email = serializer.loads(token, salt=salt, max_age=expiration)
        else:
            serializer = URLSafeSerializer(os.getenv("SECRET_KEY"))
            salt = os.getenv("SECURITY_EMAIL_SALT")
            email = serializer.loads(token, salt=salt)
    except:
        return False

    return email


def send_confirm_account_email(email="", next_url=None):
    token = generate_token(email)
    confirm_url = url_for("confirm_email", token=token, next=next_url, _external=True)
    recipient = "{fullname} <{email}>".format(
        fullname=get_user_fullname(email), email=email,
    )

    data = {
        "recipient": recipient,
        "subject": "Confirm your acount",
        "template": "confirm_account",
        "action_url": confirm_url,
    }

    return send_email_mailgun(data=data)


def send_reset_password_email(email="", token=""):
    reset_url = url_for("reset_password", token=token, _external=True)
    recipient = "{fullname} <{email}>".format(
        fullname=get_user_fullname(email), email=email,
    )

    data = {
        "recipient": recipient,
        "subject": "Forgot your password?",
        "template": "reset_password",
        "action_url": reset_url,
    }

    return send_email_mailgun(data=data)
