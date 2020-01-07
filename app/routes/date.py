from app import app, create_connection
from flask import request, jsonify


@app.route("/_get_max_date", methods=["GET"])
def return_date():
    query = """
    SELECT MAX(arr_date) as date
    FROM flight
    """

    cnx = create_connection()
    cursor = cnx.cursor()
    cursor.execute(query)
    date = cursor.fetchone()["date"]
    cursor.close()
    cnx.close()

    return jsonify(date=str(date))
