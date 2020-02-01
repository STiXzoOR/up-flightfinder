from app import (
    app,
    create_connection,
    get_customer_id,
    get_customer_type,
    get_flights,
    build_flights,
    build_selected_flights,
    redirect_guest,
)
from flask import render_template, session, request, redirect, flash, url_for, jsonify
from datetime import datetime


@app.route("/flights/search-flights", methods=["GET"])
def search_flights():
    is_roundtrip = False

    WHERE = """
    al.airline_code=f.airline and ap.airplane_model=f.airplane and aprt1.airport_code=f.from_airport and aprt2.airport_code=f.to_airport and f.from_airport=%s and f.to_airport=%s and f.dep_date=%s and IF(f.dep_date=CURRENT_DATE, f.dep_time>=CURRENT_TIME, 1) and f.occupied_capacity <= (ap.capacity-%s) and f.class=%s and f.status="Upcoming"
    """

    ORDER_BY = "f.price"

    counter = start_limit = int(request.args.get("startLimit"))
    LIMIT = "{start},5".format(start=start_limit)

    from_airport_code = request.args.get("fromAirport")
    to_airport_code = request.args.get("toAirport")
    passenger_num = int(request.args.get("numPassengers"))
    flight_class = request.args.get("flightClass")

    temp_depart_date = request.args.get("departDate")
    depart_date = datetime.strptime(temp_depart_date, "%d %b %Y").date()
    return_date = request.args.get("returnDate")

    params = (
        from_airport_code,
        to_airport_code,
        depart_date,
        passenger_num,
        flight_class,
    )

    if return_date != "One Way":
        is_roundtrip = True

        WHERE = """
        al1.airline_code=f1.airline and ap1.airplane_model=f1.airplane and aprt1.airport_code=f1.from_airport and aprt2.airport_code=f1.to_airport and f1.from_airport=%s and f1.to_airport=%s and f1.dep_date=%s and IF(f1.dep_date=CURRENT_DATE, f1.dep_time>=CURRENT_TIME, 1) and f1.occupied_capacity <= (ap1.capacity-%s) and f1.class=%s and f1.status="Upcoming" and al2.airline_code=f2.airline and ap2.airplane_model=f2.airplane and aprt3.airport_code=f2.from_airport and aprt4.airport_code=f2.to_airport and f2.from_airport=%s and f2.to_airport=%s and f2.dep_date=%s and f2.occupied_capacity <= (ap2.capacity-%s) and f2.class=%s and f2.status="Upcoming" and %s and %s
        """

        ORDER_BY = "f1.price+f2.price"

        dep_time = (
            'f2.dep_time>=ADDTIME(f1.arr_time, "05:00:00")'
            if return_date == temp_depart_date
            else 1
        )
        arr_date = "f1.arr_date=f1.dep_date" if return_date == temp_depart_date else 1
        return_date = datetime.strptime(return_date, "%d %b %Y").date()

        params = (
            from_airport_code,
            to_airport_code,
            depart_date,
            passenger_num,
            flight_class,
            to_airport_code,
            from_airport_code,
            return_date,
            passenger_num,
            flight_class,
            dep_time,
            arr_date,
        )

    data = get_flights(
        is_roundtrip=is_roundtrip,
        params=params,
        WHERE=WHERE,
        ORDER_BY=ORDER_BY,
        LIMIT=LIMIT,
    )

    if not len(data):
        return jsonify(message="no_result", content="")

    flights = ""
    for flight in data:
        counter += 1
        depart_flight_id = flight["departFlightID"]
        return_flight_id = flight["returnFlightID"] if is_roundtrip else "None"
        price = (
            flight["departPrice"] + flight["returnPrice"]
            if is_roundtrip
            else flight["departPrice"]
        )
        post_url = url_for(
            "picked_flight",
            depart_flight_id=depart_flight_id,
            return_flight_id=return_flight_id,
            depart_date=depart_date,
            return_date=return_date if is_roundtrip else "None",
            passenger_num=passenger_num,
            price=price,
            flight_class=flight_class,
            is_roundtrip=is_roundtrip,
        )

        flights += """  <div id="flight-{id}" class="my-4">
                            <form id="pickedFlightForm-{id}" action="{post_url}">
                                <div class="row justify-content-center">
                                    <div class="flight-row col-12 col-sm-8 col-md-9 col-lg-8 col-xl-6 flight-card-padding-right">
                                        <div id="flightInfo" class="flight card rounded-3x flight-card-sm shadow-1 small h-100">
                                            <div class="card-body">""".format(
            id=counter, post_url=post_url
        )

        depart_flight, return_flight = build_flights(flight, is_roundtrip)

        flights += depart_flight
        if return_flight is not None:
            flights += '<hr class="my-2">'
            flights += return_flight

        flights += """                      </div>
                                            <div class="d-block d-sm-none">
                                                <button class="btn btn-sm btn-primary btn-block process-form" type="submit">Select - €{price}</button>
                                            </div>
                                        </div>
                                    </div>
                                    <div class="d-none d-sm-block col-sm-4 col-md-3 col-lg-2 flight-card-padding-left">
                                        <div id="flightPrice" class="price card rounded-3x shadow-1 text-center h-100">
                                            <div class="price-body card-body d-flex flex-column justify-content-center align-items-center">""".format(
            id=counter, price=price
        )
        if is_roundtrip:
            flights += """                      <div class="font-weight-bold font-size-lg mb-2">€{price}</div>
                                                <button class="btn btn-primary process-form" type="submit">Select</button>""".format(
                id=counter, price=price
            )
        else:
            flights += """                       <button class="btn btn-primary btn-block process-form" type="submit" style="white-space: normal;">
                                                    Select (€{price})                                    
                                                </button>
                                                """.format(
                id=counter, price=price
            )

        flights += """                       </div>
                                        </div>
                                    </div>
                                </div>
                            </form>
                        </div>""".format(
            price=price
        )

    if len(data) == 5:
        flights += """  <div id="loadMoreBtn" class="row justify-content-center">
                            <input type="hidden" name="startLimitMore" value="{start}">
                            <a id="loadMoreFlights" class="load-more-flights btn btn-primary" href="#"><i class="fas fa-spinner fa-fw mr-2"></i>Load More</a>
                        </div>""".format(
            start=start_limit + 5
        )

    return jsonify(message="result", content=flights)


@app.route(
    "/booking/new_booking?depart_flight_id=<depart_flight_id>&return_flight_id=<return_flight_id>&depart_date=<depart_date>&return_date=<return_date>&passenger_num=<passenger_num>&price=<price>&flight_class=<flight_class>&is_roundtrip=<is_roundtrip>"
)
@redirect_guest
def picked_flight(
    depart_flight_id="",
    return_flight_id="",
    depart_date="",
    return_date="",
    passenger_num=0,
    price=0,
    flight_class="",
    is_roundtrip=False,
):
    session.pop("is_guest", None)
    customer_id = get_customer_id()
    customer_type = get_customer_type()
    is_roundtrip = is_roundtrip == "True"

    if customer_type == "USER":
        query = """
        SELECT status 
        FROM booking 
        WHERE customer_id=%s and depart_flight_id=%s and status in ("Active", "Upcoming")
        """

        cnx = create_connection()
        cursor = cnx.cursor()
        cursor.execute(query, (customer_id, depart_flight_id))
        result = cursor.fetchone()
        cursor.close()
        cnx.close()

        if result is not None:
            flash("You have already booked this flight route!", "error")
            return redirect(url_for("index"))

    WHERE = """
    f.flight_id=%s and f.dep_date=%s and f.class=%s and al.airline_code=f.airline and ap.airplane_model=f.airplane and aprt1.airport_code=f.from_airport and aprt2.airport_code=f.to_airport
    """

    params = (
        depart_flight_id,
        depart_date,
        flight_class,
    )

    if is_roundtrip:
        WHERE = """
        f1.flight_id=%s and f1.dep_date=%s and f1.class=%s and f2.flight_id=%s and f2.dep_date=%s and f2.class=%s and al1.airline_code=f1.airline and ap1.airplane_model=f1.airplane and aprt1.airport_code=f1.from_airport and aprt2.airport_code=f1.to_airport and al2.airline_code=f2.airline and ap2.airplane_model=f2.airplane and aprt3.airport_code=f2.from_airport and aprt4.airport_code=f2.to_airport
        """

        params += (
            return_flight_id,
            return_date,
            flight_class,
        )

    flight = get_flights(
        is_roundtrip=is_roundtrip, params=params, WHERE=WHERE, FETCH_ALL=False
    )

    price = int(price)
    passenger_num = int(passenger_num)
    total_price = price * passenger_num

    depart_flight, return_flight = build_selected_flights(
        flight=flight, is_roundtrip=is_roundtrip
    )

    picked_flight = depart_flight

    if return_flight is not None:
        picked_flight += '<hr class="my-2">'
        picked_flight += return_flight

    return render_template(
        "booking/new-booking.html",
        picked_flight=picked_flight,
        flight_class=flight_class,
        num_passenger=passenger_num,
        price=price,
        total_price=total_price,
        is_roundtrip=is_roundtrip,
    )

