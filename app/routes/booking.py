from app import (
    app,
    restricted,
    create_connection,
    get_customer_id,
    get_customer_type,
    get_booking,
    booking_exists,
    booking_is_inactive,
    fake,
)
from flask import render_template, session, request, redirect, flash, url_for, abort
from datetime import datetime


@app.route("/booking/new-booking", methods=["POST"])
def new_booking():
    customer_id = get_customer_id()
    form = request.form
    is_roundtrip = form.get("isRoundtrip") == "True"

    flight_info = {
        "depart_flight_id": form.get("DepartFlightID"),
        "return_flight_id": form.get("ReturnFlightID", None),
        "depart_flight_date": form.get("DepartDate"),
        "return_flight_date": form.get("ReturnDate", None),
        "flight_class": form.get("flightClass"),
        "type": "Roundtrip" if is_roundtrip else "Oneway",
        "total_passengers": int(form.get("numPassenger")),
        "price_per_passenger": form.get("pricePerPassenger"),
        "total_price": form.get("totalPrice"),
    }

    flight_info["depart_flight_date"] = datetime.strptime(
        flight_info["depart_flight_date"], "%d %b %Y"
    ).date()

    if flight_info["return_flight_date"]:
        flight_info["return_flight_date"] = datetime.strptime(
            flight_info["return_flight_date"], "%d %b %Y"
        ).date()

    query = """
    SELECT booking_id 
    FROM booking
    WHERE booking_id=%s"""

    cnx = create_connection()
    cursor = cnx.cursor()

    booking_id = fake.lexify(
        text="??????", letters="ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    )
    cursor.execute(query, booking_id)
    result = cursor.fetchone()
    while result is not None:
        booking_id = fake.lexify(
            text="??????", letters="ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
        )
        cursor.execute(query, booking_id)
        result = cursor.fetchone()
    cursor.close()

    current_date = datetime.today().date()
    passenger_info = []
    for i in range(flight_info["total_passengers"]):
        first_name = "firstNamePassenger-{num}".format(num=i + 1)
        last_name = "lastNamePassenger-{num}".format(num=i + 1)
        identifier = "idPassenger-{num}".format(num=i + 1)
        seat = "seatPassenger-{num}".format(num=i + 1)
        seat_class = "seatClassPassenger-{num}".format(num=i + 1)
        seat_price = "seatPricePassenger-{num}".format(num=i + 1)

        passenger = {
            "id": form.get(identifier),
            "first_name": form.get(first_name),
            "last_name": form.get(last_name),
            "seat": form.get(seat),
            "seat_class": form.get(seat_class),
            "seat_price": form.get(seat_price),
        }

        passenger_info.append(passenger)

    contact_info = {
        "first_name": form.get("contactFirstName"),
        "last_name": form.get("contactLastName"),
        "email": form.get("contactEmail"),
        "mobile": form.get("contactMobile"),
    }

    booking = {
        "booking_id": booking_id,
        "customer_id": customer_id,
        "depart_flight_id": flight_info["depart_flight_id"],
        "return_flight_id": flight_info["return_flight_id"],
        "depart_flight_date": flight_info["depart_flight_date"],
        "return_flight_date": flight_info["return_flight_date"],
        "flight_class": flight_info["flight_class"],
        "first_name": contact_info["first_name"],
        "last_name": contact_info["last_name"],
        "email": contact_info["email"],
        "mobile": contact_info["mobile"],
        "booking_date": current_date,
        "last_modify_date": current_date,
        "total_passengers": flight_info["total_passengers"],
        "price_per_passenger": flight_info["price_per_passenger"],
        "total_price": flight_info["total_price"],
        "flight_type": flight_info["type"],
        "status": "Upcoming",
    }

    fields = []
    values = []
    for key in booking.keys():
        fields.append(key)
        values.append("%({key})s".format(key=key))

    fields = ", ".join(fields)
    values = ", ".join(values)
    query = "INSERT INTO booking ({fields}) VALUES ({values})".format(
        fields=fields, values=values
    )
    cursor = cnx.cursor()
    cursor.execute(query, booking)
    cursor.close()

    query = """
    UPDATE flight 
    SET occupied_capacity=occupied_capacity+%s 
    WHERE flight_id=%s
    """

    cursor = cnx.cursor()
    cursor.execute(
        query, (flight_info["total_passengers"], flight_info["depart_flight_id"])
    )
    if is_roundtrip:
        cursor.execute(
            query, (flight_info["total_passengers"], flight_info["return_flight_id"])
        )
    cursor.close()

    query_p = """
    INSERT INTO passenger (passenger_id, first_name, last_name) 
    VALUE(%s, %s, %s)
    """

    query_pb = """
    INSERT INTO pass_has_booking (passenger_id, booking_id, seat, seat_class, seat_price) 
    VALUE(%s, %s, %s, %s, %s)
    """

    for passenger in passenger_info:
        try:
            cursor = cnx.cursor()
            cursor.execute(
                query_p,
                (passenger["id"], passenger["first_name"], passenger["last_name"]),
            )
            cursor.close()
        except:
            print("Passenger with id={id} exists".format(id=passenger["id"]))
        cursor = cnx.cursor()
        cursor.execute(
            query_pb,
            (
                passenger["id"],
                booking_id,
                passenger["seat"],
                passenger["seat_class"],
                passenger["seat_price"],
            ),
        )
        cursor.close()

    cnx.commit()
    cnx.close()

    return redirect(
        url_for(
            "view_booking",
            booking_id=booking_id,
            booking_last_name=contact_info["last_name"],
            go_back=False,
        )
    )


@app.route("/customer/my-bookings.html")
@restricted(access_level="USER")
def my_bookings():
    customer_id = get_customer_id()

    query = """
    SELECT b.booking_id as id, b.last_name as last_name, a1.city as from_city, a2.city as to_city, DATE_FORMAT(b.booking_date, "%%d %%b %%Y") as date, b.flight_type as flight_type, b.status as status 
    FROM booking as b, flight as f, airport as a1, airport as a2 
    WHERE b.customer_id=%s and b.status in (%s, %s) and f.flight_id=b.depart_flight_id and f.dep_date=b.depart_flight_date and f.class=b.flight_class and a1.airport_code=f.from_airport and a2.airport_code=f.to_airport
    ORDER BY date DESC 
    """

    cnx = create_connection()
    cursor = cnx.cursor()
    cursor.execute(query, (customer_id, "Active", "Upcoming"))
    upcoming_bookings = cursor.fetchall()
    cursor.close()

    cursor = cnx.cursor()
    cursor.execute(query, (customer_id, "Passed", "Canceled"))
    passed_bookings = cursor.fetchall()
    cursor.close()
    cnx.close()

    return render_template(
        "customer/my-bookings.html",
        upcoming_bookings=upcoming_bookings,
        passed_bookings=passed_bookings,
    )


@app.route("/booking/manage-booking.html")
@restricted(access_level="GUEST")
def manage_booking_page():
    messages = {
        "not_found": "We are unable to find the booking reference you provided. Please validate that your information is correct and try again.",
        "inactive": "We are unable unable to perform the task you have asked. The booking may be inactive or canceled.",
        "canceled": "Your booking has been successfully canceled.",
    }

    error = session.pop("error", None)
    success = session.pop("success", None)

    message = (
        messages[success]
        if success is not None
        else messages[error]
        if error is not None
        else False
    )
    show_alert = True if message else False

    alert = {"type": "success" if success is not None else "error", "message": message}

    return render_template(
        "/booking/manage-booking.html", show_alert=show_alert, alert=alert
    )


@app.route("/booking/manage-booking", methods=["POST"])
def manage_booking():
    form = request.form
    booking_id = form.get("bookingID")
    booking_last_name = form.get("lastName")
    go_back = False if get_customer_id() == 0 else True

    if get_customer_type() == "GUEST" and not booking_exists(
        booking_id, booking_last_name
    ):
        session["error"] = "not_found"
        return redirect(url_for("manage_booking_page"))

    btn_state = form.get("btnState")
    if btn_state == "view":
        return redirect(
            url_for(
                "view_booking",
                booking_id=booking_id,
                booking_last_name=booking_last_name,
                go_back=go_back,
            )
        )
    else:
        if get_customer_type() == "GUEST" and booking_is_inactive(
            booking_id, booking_last_name
        ):
            session["error"] = "inactive"
            return redirect(url_for("manage_booking_page"))

        if btn_state == "modify":
            return redirect(
                url_for(
                    "modify_booking",
                    booking_id=booking_id,
                    booking_last_name=booking_last_name,
                    go_back=True,
                )
            )
        elif btn_state == "cancel":
            return redirect(
                url_for(
                    "cancel_booking",
                    booking_id=booking_id,
                    booking_last_name=booking_last_name,
                )
            )

    return abort(500)


@app.route("/booking/view-booking/<booking_id>&<booking_last_name>&<go_back>")
def view_booking(booking_id="", booking_last_name="", modify=False, go_back=False):
    go_back_address = "my_bookings"
    data = get_booking(booking_id, booking_last_name)

    return render_template(
        "booking/get-booking.html",
        booking=data["booking_info"],
        picked_flight=data["flight"],
        passenger_info=data["passenger_info"],
        contact_info=data["contact_info"],
        go_back=go_back == "True",
        go_back_address=url_for(go_back_address),
    )


@app.route("/modify-booking/<booking_id>&<booking_last_name>&<go_back>")
def modify_booking(booking_id="", booking_last_name="", modify=False, go_back=False):
    go_back_address = "index" if get_customer_type() == "GUEST" else "my_bookings"
    data = get_booking(booking_id, booking_last_name)

    return render_template(
        "booking/modify-booking.html",
        booking=data["booking_info"],
        picked_flight=data["flight"],
        passenger_info=data["passenger_info"],
        contact_info=data["contact_info"],
        go_back=go_back == "True",
        go_back_address=url_for(go_back_address),
    )


@app.route("/booking/modify-booking", methods=["POST"])
def modify_booking_post():
    form = request.form
    booking_id = form.get("bookingID")
    total_passengers = int(form.get("numPassengers"))
    first_name = form.get("contactFirstName")
    last_name = form.get("contactLastName")
    email = form.get("contactEmail")
    mobile = form.get("contactMobile")
    old_last_name = form.get("oldContactLastName")
    addtional_price = int(form.get("totalPrice"))
    customer_type = get_customer_type()

    passenger_info = []
    for i in range(total_passengers):
        identifier = "idPassenger-{num}".format(num=i + 1)
        seat = "seatPassenger-{num}".format(num=i + 1)
        seat_class = "seatClassPassenger-{num}".format(num=i + 1)
        seat_price = "seatPricePassenger-{num}".format(num=i + 1)

        passenger = {
            "id": form.get(identifier),
            "seat": form.get(seat),
            "seat_class": form.get(seat_class),
            "seat_price": form.get(seat_price),
        }

        passenger_info.append(passenger)

    query = """
    UPDATE booking 
    SET first_name=%s, last_name=%s, email=%s, mobile=%s, total_price=total_price+%s, last_modify_date=CURRENT_DATE 
    WHERE booking_id=%s and last_name=%s
    """

    cnx = create_connection()
    cursor = cnx.cursor()
    cursor.execute(
        query,
        (
            first_name,
            last_name,
            email,
            mobile,
            addtional_price,
            booking_id,
            old_last_name,
        ),
    )
    cursor.close()

    query = """
    UPDATE pass_has_booking 
    SET seat=%s, seat_class=%s, seat_price=%s 
    WHERE passenger_id=%s and booking_id=%s
    """

    for passenger in passenger_info:
        cursor = cnx.cursor()
        cursor.execute(
            query,
            (
                passenger["seat"],
                passenger["seat_class"],
                passenger["seat_price"],
                passenger["id"],
                booking_id,
            ),
        )
        cursor.close()

    cnx.commit()
    cnx.close()

    go_back = False if customer_type == "GUEST" else True

    return redirect(
        url_for(
            "view_booking",
            booking_id=booking_id,
            booking_last_name=last_name,
            go_back=go_back,
        )
    )


@app.route("/booking/cancel-booking/<booking_id>&<booking_last_name>")
def cancel_booking(booking_id="", booking_last_name=""):
    customer_type = get_customer_type()

    query = """
    UPDATE booking 
    SET status=%s 
    WHERE booking_id=%s and last_name=%s
    """

    cnx = create_connection()
    cursor = cnx.cursor()
    cursor.execute(query, ("Canceled", booking_id, booking_last_name))
    cursor.close()

    query = """
    SELECT depart_flight_id, return_flight_id, total_passengers, flight_type
    FROM booking
    WHERE booking_id=%s and last_name=%s
    """

    cursor = cnx.cursor()
    cursor.execute(query, (booking_id, booking_last_name))
    booking_info = cursor.fetchone()
    cursor.close()

    query = """
    UPDATE flight 
    SET occupied_capacity=occupied_capacity-%s 
    WHERE flight_id=%s
    """

    cursor = cnx.cursor()
    cursor.execute(
        query, (booking_info["total_passengers"], booking_info["depart_flight_id"])
    )
    if booking_info["flight_type"] == "Roundtrip":
        cursor.execute(
            query, (booking_info["total_passengers"], booking_info["return_flight_id"])
        )
    cursor.close()
    cnx.commit()
    cnx.close()

    if customer_type == "GUEST":
        session["success"] = "canceled"
    else:
        flash("The booking has been successfully canceled", "success")

    return redirect(
        url_for("manage_booking_page")
        if customer_type == "GUEST"
        else url_for("my_bookings")
    )


@app.route("/booking/add-booking", methods=["POST"])
@restricted(access_level="USER")
def add_booking():
    form = request.form

    booking_id = form.get("bookingID")
    first_name = form.get("firstName")
    last_name = form.get("lastName")

    query = """
    SELECT *
    FROM booking
    WHERE booking_id=%s and first_name=%s and last_name=%s
    """

    cnx = create_connection()
    cursor = cnx.cursor()
    cursor.execute(query, (booking_id, first_name, last_name))
    booking = cursor.fetchone()
    cursor.close()
    cnx.close()

    if booking is None:
        flash("The booking you are trying to add doesn't exists!", "error")
        return redirect(url_for("my_bookings"))

    if booking_exists(booking_id, last_name):
        flash("The booking you are trying to add already exists!", "error")
        return redirect(url_for("my_bookings"))

    cnx = create_connection()
    booking["customer_id"] = session["customer_id"]

    fields = []
    values = []
    for key in booking.keys():
        fields.append(key)
        values.append("%({key})s".format(key=key))

    fields = ", ".join(fields)
    values = ", ".join(values)
    query = "INSERT INTO booking ({fields}) VALUES ({values})".format(
        fields=fields, values=values
    )
    cursor = cnx.cursor()
    cursor.execute(query, booking)
    cnx.commit()
    cursor.close()
    cnx.close()

    flash("The booking has been successfully added to your account", "success")
    return redirect(url_for("my_bookings"))

