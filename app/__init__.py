from flask import Flask, render_template, g
from dotenv import load_dotenv, find_dotenv
from app.functions.functions import *
import os

load_dotenv(find_dotenv())

app = Flask(__name__)
app.config["DEBUG"] = os.getenv("DEBUG_STATUS", False)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")


@app.before_request
def current_user():
    query = """
    SELECT customer_id as id, first_name, customer_type as type
    FROM customer
    WHERE customer_id=%s
    """

    Connection = create_connection()
    cursor = Connection.cursor()
    cursor.execute(query, (session.get("customer_id", 0)))
    result = cursor.fetchone()
    cursor.close()
    Connection.close()

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
