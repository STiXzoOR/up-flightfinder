from app import app, create_connection, get_airports
from flask import request, jsonify

@app.route('/_get_airports', methods=["GET"])
def return_airports():
    def _format_string(city, code):
        return '{city} ({code})'.format(city=city, code=code)

    airports = get_airports()
    airport = str(request.args.get('airport'))

    if not airport:
        return 'OK'

    airports = {airport['code']: airport['city'] for airport in airports}

    query = """
    SELECT DISTINCT from_airport, GROUP_CONCAT(DISTINCT to_airport ORDER BY to_airport SEPARATOR ",") as to_airport
    FROM flight
    WHERE from_airport=%s
    GROUP BY from_airport
    """

    cnx = create_connection()
    cursor = cnx.cursor()
    cursor.execute(query, airport)
    route = cursor.fetchone()
    cursor.close()
    cnx.close()

    destinations = [{'value': code, 'text': _format_string(airports[code], code)} for code in route['to_airport'].split(',')]

    return jsonify(result=destinations)