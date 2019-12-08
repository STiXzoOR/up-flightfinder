@app.route('/search-flights', methods=["GET"])
def search_flights():
    global search_result
    global passenger_num
    global is_roundtrip
    is_roundtrip = False

    query = """
    SELECT f.flight_id as departFlightID, f.airline as departAirlineCode, al.airline_name as departAirlineName, f.dep_date as departDate, f.from_airport as departFromAirport, aprt1.city as departFromCity, f.dep_time as departTime, f.to_airport as departToAirport, aprt2.city as departToCity, f.arr_time as departArrivalTime, f.price as departPrice, f.class as departClass, f.duration as departDuration, ap.airplane_name as departAirplaneName
    FROM flight as f, airline as al, airplane as ap, airport as aprt1, airport as aprt2
    WHERE al.airline_code=f.airline and ap.airplane_model=f.airplane and aprt1.airport_code=f.from_airport and aprt2.airport_code=f.to_airport and f.from_airport=%s and f.to_airport=%s and f.dep_date=%s and f.occupied_capacity <= (ap.capacity-%s) and f.class=%s and f.status="Upcoming"
    ORDER BY f.price
    """

    from_city, from_airport_code = re.sub('[\(\)]', "", request.args.get('fromAirport')).rsplit(' ', 1)
    to_city, to_airport_code = re.sub('[\(\)]', "", request.args.get('toAirport')).rsplit(' ', 1)
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
        WHERE al1.airline_code=f1.airline and ap1.airplane_model=f1.airplane and aprt1.airport_code=f1.from_airport and aprt2.airport_code=f1.to_airport and f1.from_airport=%s and f1.to_airport=%s and f1.dep_date=%s and f1.occupied_capacity <= (ap1.capacity-%s) and f1.class=%s and f1.status="Upcoming" and al2.airline_code=f2.airline and ap2.airplane_model=f2.airplane and aprt3.airport_code=f2.from_airport and aprt4.airport_code=f2.to_airport and f2.from_airport=%s and f2.to_airport=%s and f2.dep_date=%s and f2.occupied_capacity <= (ap2.capacity-%s) and f2.class=%s and f2.status="Upcoming" and %s and %s
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
    picked_flight = ''

    flights = """   <div id="flightsContainer" class="mt-3">"""

    for i, flight in enumerate(result):
        flights += """  <div id="flight-{id}" class="my-3 moreItem">
                            <div class="flight-row row justify-content-center align-items-center">
                                <div class="col-12 col-md-8 col-lg-6 pr-md-0 mr-md-0">
                                    <div id="flightInfo" class="flight card rounded-3x">""".format(id=i+1)

        duration = str(flight['departDuration'])
        depart_duration = datetime.strptime(duration[:-3], "%H:%M").time()

        depart_flight = build_flight_card(airline_logo=flight['departAirlineCode'],
                                         airline_name=flight['departAirlineName'], 
                                         from_airport=from_airport_code, 
                                         time_from=str(flight['departTime'])[:-3], 
                                         to_airport=to_airport_code, 
                                         time_to=str(flight['departArrivalTime'])[:-3],
                                         duration=depart_duration)
        flights += depart_flight
        if is_roundtrip:
            flights += '<hr class="my-0 mx-4 flex-grow-1">'
            
            duration = str(flight['returnDuration'])
            return_duration = datetime.strptime(duration[:-3], "%H:%M").time()

            return_flight = build_flight_card(airline_logo=flight['returnAirlineCode'],
                                              airline_name=flight['returnAirlineName'], 
                                              from_airport=to_airport_code, 
                                              time_from=str(flight['returnTime'])[:-3], 
                                              to_airport=from_airport_code, 
                                              time_to=str(flight['returnArrivalTime'])[:-3],
                                              duration=return_duration)
            flights += return_flight
        
        flights += """              </div>
                                </div>
                                <div class="d-none d-md-block col-md-3 col-lg-2 pl-md-1 ml-0">
                                    <div id="flightPrice" class="price card rounded-3x justify-content-center align-items-center">
                                        <form method="POST" id="pickedFlightForm-{id}">
                                            <div class="font-weight-bold font-size-lg mb-2">€{price}</div>
                                            <!-- <button class="btn btn-primary" data-toggle="modal" href="#pickedFlightDialog-{id}">Select</button> -->
                                            <button class="btn btn-primary" type="submit" name="pickedFlight" value="{id}">Select</button>
                                        </form>
                                    </div>
                                </div>
                                <div class="d-block d-md-none col-12 mt-1">
                                    <div id="flightPriceSmall" class="price-small card rounded-3x">
                                        <div class="card-body">
                                            <form method="POST" id="pickedFlightForm-{id}">
                                                <!-- <button class="btn btn-primary btn-block" data-toggle="modal" href="#pickedFlightDialog-{id}">Select - €{price}</button> -->
                                                <button class="btn btn-primary btn-block" type="submit" name="pickedFlight" value="{id}">Select - €{price}</button>
                                            </form>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>""".format(id=i+1, price=int(flight['departPrice'])+int(flight['returnPrice']) if is_roundtrip else flight['departPrice'])

        picked_flight += """ <div class="modal fade mt-5" id="pickedFlightDialog-{id}" tabindex="-1" role="dialog" aria-labelledby="Booking-Form" aria-hidden="true">
                                <div class="modal-dialog modal-md" role="document">
                                    <div class="modal-content">
                                        <div class="modal-header">
                                            <h5 class="modal-title">Booking Form</h5>
                                            <button type="button" class="close" data-dismiss="modal" aria-label="Close">
                                                <span aria-hidden="true">&times;</span>
                                            </button>
                                        </div>
                                        <div class="modal-body">
                                            <form id="bookingForm" class="needs-validation" action="booking_review" method="POST" novalidate>
                                                <input id="pickedFlight" name="pickedFlight" type="hidden" value={id}>
                                                <div class="accordion" id="flightsInfo">""".format(id=i+1)
        
        picked_flight += build_selected_flight_card(id=i+1, 
                                                   flight=depart_flight, 
                                                   flight_id=flight['departFlightID'], 
                                                   airline_name=flight['departAirlineName'], 
                                                   from_airport=from_airport_code, 
                                                   from_city=from_city, 
                                                   to_airport=to_airport_code, 
                                                   to_city=to_city, 
                                                   date=temp_depart_date, 
                                                   klass=flight['departClass'], 
                                                   airplane=flight['departAirplaneName'], 
                                                   duration=depart_duration,
                                                   flight_type='Depart')
        if is_roundtrip:
            picked_flight += build_selected_flight_card(id=i+1, 
                                                   flight=return_flight, 
                                                   flight_id=flight['returnFlightID'], 
                                                   airline_name=flight['returnAirlineName'], 
                                                   from_airport=to_airport_code, 
                                                   from_city=from_city, 
                                                   to_airport=from_airport_code, 
                                                   to_city=to_city, 
                                                   date=temp_return_date, 
                                                   klass=flight['returnClass'], 
                                                   airplane=flight['returnAirplaneName'], 
                                                   duration=return_duration,
                                                   flight_type='Return')

        picked_flight += """</div> 
                            <div class="card rounded-3x mt-3">
                                <div class="card-body">
                                    <div class="card-title text-center font-weight-bold font-size-lg">Passenger(s) Info</div>
                                </div>
                                <div class="list-group list-group-flush" id="passengersInfo">""".format(id=i)
        
        for index in range(int(num_passengers)):
            picked_flight += """     <div class="expansion-panel list-group-item">
                                        <a aria-controls="passenger-{id}" aria-expanded="false" class="expansion-panel-toggler collapsed" data-toggle="collapse" href="#passenger-{id}" id="passengerHeading-{id}">
                                        Passenger Details #{id}
                                            <div class="expansion-panel-icon ml-3 text-black-secondary">
                                                <i class="collapsed-show material-icons">keyboard_arrow_down</i>
                                                <i class="collapsed-hide material-icons">keyboard_arrow_up</i>
                                            </div>
                                        </a>
                                        <div aria-labelledby="passenger-{id}" class="collapse" data-parent="#passengersInfo" id="passenger-{id}">
                                            <div class="expansion-panel-body">
                                                <div class="form-row mt-3">
                                                    <div class="col-12 col-md-6 col-lg-3">
                                                        <div class="floating-label">
                                                            <label for="namePassenger-{id}"> Name </label>
                                                            <input class="form-control" id="namePassenger-{id}" type="text" name="namePassenger-{id}" required data-rippleLine>
                                                            <span class="form-control-ripple"></span>
                                                        </div>
                                                        <div class="invalid-feedback">
                                                            Please enter passenger name.
                                                        </div>
                                                    </div>
                                                    <div class="col-12 col-md-6 col-lg-3">
                                                        <div class="floating-label">
                                                            <label for="idPassenger-{id}"> ID </label>
                                                            <input class="form-control" id="idPassenger-{id}" type="text" name="idPassenger-{id}" required data-rippleLine>
                                                            <span class="form-control-ripple"></span>
                                                        </div>
                                                        <div class="invalid-feedback">
                                                            Please enter passenger ID.
                                                        </div>
                                                    </div>
                                                    <div class="col-12 col-md-6 col-lg-3">
                                                        <div class="floating-label">
                                                            <label for="seatRowPassenger-{id}"> Seat Row </label>
                                                            <select class="form-control" id="seatRowPassenger-{id}" type="text" name="seatRowPassenger-{id}" required data-rippleLine>
                                                                <option></option>
                                                            <select>
                                                            <span class="form-control-ripple"></span>
                                                        </div>
                                                        <div class="invalid-feedback">
                                                            Please select a seat row.
                                                        </div>
                                                    </div>
                                                    <div class="col-12 col-md-6 col-lg-3">
                                                        <div class="floating-label">
                                                            <label for="seatColumnPassenger-{id}"> Seat Column </label>
                                                            <select class="form-control" id="seatColumnPassenger-{id}" type="text" name="seatColumnPassenger-{id}" required data-rippleLine>
                                                                <option></option>
                                                            <select>
                                                            <span class="form-control-ripple"></span>
                                                        </div>
                                                        <div class="invalid-feedback">
                                                            Please select a seat column.
                                                        </div>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                    </div>""".format(id=index+1)
        
        picked_flight += """    </div>
                            </div>
                            <div class="card rounded-3x mt-3 mb-0">
                                <div class="card-header">
                                    <div class="card-title text-center font-weight-bold font-size-lg">Contact Info</div>
                                </div>
                                <div class="card-body">
                                    <div class="form-row">
                                        <div class="col-12 col-md-4">
                                            <div class="floating-label">
                                                <label for="contactName"> Contact name </label>
                                                <input class="form-control" id="contactName" type="text" name="contactName" required data-rippleLine>
                                                <span class="form-control-ripple"></span>
                                            </div>
                                            <div class="invalid-feedback">
                                                Please enter a valid contact name.
                                            </div>
                                        </div>
                                        <div class="col-12 col-md-4">
                                            <div class="floating-label">
                                                <label for="contactMail"> Email </label>
                                                <input class="form-control" id="contactMail" type="text" name="contactMail" required data-rippleLine>
                                                <span class="form-control-ripple"></span>
                                            </div>
                                            <div class="invalid-feedback">
                                                Please enter a valid contact email.
                                            </div>
                                        </div>
                                        <div class="col-12 col-md-4">
                                            <div class="floating-label">
                                                <label for="contactMobile"> Mobile </label>
                                                <input class="form-control" id="contactMobile" type="text" name="contactMobile" required data-rippleLine>
                                                <span class="form-control-ripple"></span>
                                            </div>
                                            <div class="invalid-feedback">
                                                Please enter a valid contact mobile.
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </form>
                    </div>
                    <div class="modal-footer mt-3">
                        <button class="btn btn-primary" data-dismiss="modal" type="button">Close</button>
                        <button class="btn btn-primary" type="submit">Book Now</button>
                    </div>
                </div>
            </div>
        </div>
    </div>"""

    flights += """      <div class="row justify-content-center">
                            <a id="loadMore" class="btn btn-primary load-more__btn" href="#"><i class="fas fa-spinner"></i> Load More </a>
                        </div>
                    </div>
                </div>
            </div>
        </div>"""
    
    return flights + picked_flight