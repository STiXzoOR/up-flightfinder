from app import app, create_connection
from flask import request, jsonify

@app.route('/_get_seats', methods=["GET"])
def return_seats():
    depart_flight_id = request.args.get('departFlightID')
    return_flight_id = request.args.get('returnFlightID')

    depart_flight_id = depart_flight_id if depart_flight_id is not None else ''
    return_flight_id = return_flight_id if return_flight_id is not None else ''

    query = """
    SELECT phb.seat as id
    FROM booking as b, pass_has_booking as phb
    WHERE (b.depart_flight_id=%s or b.return_flight_id=%s) and phb.booking_id=b.booking_id
    """

    cnx = create_connection()
    cursor = cnx.cursor()
    cursor.execute(query, (depart_flight_id, return_flight_id))
    seats = cursor.fetchall()
    cursor.close()
    cnx.close()

    return jsonify(result=seats)