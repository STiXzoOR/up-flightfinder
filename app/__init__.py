from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, render_template, g, session
from dotenv import load_dotenv, find_dotenv
from flask_maintenance import Maintenance
from app.functions.functions import *
from datetime import datetime
import atexit
import os

try:
    load_dotenv(find_dotenv())
except:
    print(
        "ERROR: Looks like you haven't generated a valid .env file. Please run: python generate_dotenv.py"
    )
    exit(1)

app = Flask(__name__)
app.config["DEBUG"] = os.getenv("DEBUG_STATUS") == "True"
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

Maintenance(app)


# EXPIREMENTAL - Real time flight status update
def change_flight_status():
    query = """
    UPDATE flight
    SET status = CASE
    WHEN (((dep_date = CURRENT_DATE and arr_date > CURRENT_DATE and dep_time <= CURRENT_TIME) or (dep_date < CURRENT_DATE and arr_date = CURRENT_DATE and arr_time >= CURRENT_TIME)) or (CURRENT_TIME >= dep_time and CURRENT_TIME <= arr_time and dep_date = CURRENT_DATE and arr_date = CURRENT_DATE)) THEN "Active" 
    WHEN ((arr_time < CURRENT_TIME and dep_date = CURRENT_DATE and arr_date = CURRENT_DATE) or (dep_date < CURRENT_DATE and arr_date <= CURRENT_DATE)) THEN "Inactive" 
    ELSE status 
    END 
    WHERE status in ("Upcoming", "Active")
    """

    cnx = create_connection()
    cursor = cnx.cursor()
    rows = cursor.execute(query)
    cursor.close()
    cnx.commit()
    cnx.close()

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(
        "[{timestamp}] LOG - Flight status changed for {number} flights.".format(
            timestamp=timestamp, number=rows
        )
    )


def remove_inactive_flights():
    query = """
    DELETE FROM flight
    WHERE status = "Inactive"
    """

    cnx = create_connection()
    cursor = cnx.cursor()
    rows = cursor.execute(query)
    cursor.close()
    cnx.commit()
    cnx.close()

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(
        "[{timestamp}] LOG - Removed fights: {number}.".format(
            timestamp=timestamp, number=rows
        )
    )


scheduler = BackgroundScheduler()
scheduler.add_job(func=change_flight_status, trigger="interval", minutes=10)
scheduler.add_job(func=remove_inactive_flights, trigger="interval", days=15)
scheduler.start()

atexit.register(lambda: scheduler.shutdown())


@app.before_request
def current_user():
    query = """
    SELECT customer_id as id, first_name, customer_type as type, status
    FROM customer
    WHERE customer_id=%s
    """

    cnx = create_connection()
    cursor = cnx.cursor()
    cursor.execute(query, (session.get("customer_id", 1)))
    result = cursor.fetchone()
    cursor.close()
    cnx.close()

    g.current_customer = result


@app.route("/")
@app.route("/index.html")
def index():
    session.pop("is_guest", None)

    return render_template(
        "index.html", airports=get_airports(), destinations=get_popular_destinations()
    )


from app.routes import error
from app.routes import guest
from app.routes import airport
from app.routes import seat
from app.routes import date
from app.routes import flight
from app.routes import customer
from app.routes import booking
