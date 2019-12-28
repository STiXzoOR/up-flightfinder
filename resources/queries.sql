--------------------------------------------------------------------
-- The "?" indicates values provided by user for a specific query --
--------------------------------------------------------------------

------------------------------------------------------------------------------------------------------------------------
-- GET FLIGHTS --
-----------------

-- ONEWAY --

SELECT
    f.flight_id,
    f.airline,
    al.airline_name,
    f.dep_date,
    f.from_airport,
    aprt1.city,
    f.dep_time,
    f.to_airport,
    aprt2.city,
    f.arr_time,
    f.price,
    f.class,
    f.duration,
    ap.airplane_name
FROM
    flight AS f,
    airline AS al,
    airplane AS ap,
    airport AS aprt1,
    airport AS aprt2
WHERE
    al.airline_code = f.airline AND ap.airplane_model = f.airplane AND aprt1.airport_code = f.from_airport AND aprt2.airport_code = f.to_airport AND f.from_airport = "?" AND f.to_airport = "?" AND f.dep_date = "?" AND IF(
        f.dep_date = CURRENT_DATE,
        f.dep_time >= CURRENT_TIME,
        1
    ) AND f.occupied_capacity <=(ap.capacity - ?) AND f.class = "?" AND f.status = "Upcoming"
ORDER BY
    f.price;

-- ROUNDTRIP --

SELECT
    f1.flight_id,
    f1.airline,
    al1.airline_name,
    f1.dep_date,
    f1.from_airport,
    aprt1.city,
    f1.dep_time,
    f1.to_airport,
    aprt2.city,
    f1.arr_time,
    f1.price,
    f1.class,
    f1.duration,
    ap1.airplane_name,
    f2.flight_id,
    f2.airline,
    al2.airline_name,
    f2.dep_date,
    f2.from_airport,
    aprt3.city,
    f2.dep_time,
    f2.to_airport,
    aprt4.city,
    f2.arr_time,
    f2.price,
    f2.class,
    f2.duration,
    ap2.airplane_name
FROM
    flight AS f1,
    flight AS f2,
    airline AS al1,
    airline AS al2,
    airplane AS ap1,
    airplane AS ap2,
    airport AS aprt1,
    airport AS aprt2,
    airport AS aprt3,
    airport AS aprt4
WHERE
    al1.airline_code = f1.airline AND ap1.airplane_model = f1.airplane AND aprt1.airport_code = f1.from_airport AND aprt2.airport_code = f1.to_airport AND f1.from_airport = "?" AND f1.to_airport = "?" AND f1.dep_date = "?" AND IF(
        f1.dep_date = CURRENT_DATE,
        f1.dep_time >= CURRENT_TIME,
        1
    ) AND f1.occupied_capacity <=(ap1.capacity - "?") AND f1.class = "?" AND f1.status = "Upcoming" AND al2.airline_code = f2.airline AND ap2.airplane_model = f2.airplane AND aprt3.airport_code = f2.from_airport AND aprt4.airport_code = f2.to_airport AND f2.from_airport = "?" AND f2.to_airport = "?" AND f2.dep_date = "?" AND f2.occupied_capacity <=(ap2.capacity - "?") AND f2.class = "?" AND f2.status = "Upcoming"
ORDER BY
    f1.price + f2.price;

------------------------------------------------------------------------------------------------------------------------
-- GET ROUTES --
----------------

-- AIRPORTS --

SELECT city, airport_code
FROM airport;

-- ROUTES PER AIRPORT --

SELECT DISTINCT from_airport, GROUP_CONCAT(DISTINCT to_airport ORDER BY to_airport SEPARATOR ",") AS to_airports
FROM flight
WHERE from_airport = "?"
GROUP BY from_airport;

------------------------------------------------------------------------------------------------------------------------
-- MANAGE BOOKING --
--------------------

-- BOOKING EXISTS --

SELECT booking_id 
FROM booking
WHERE booking_id="?" AND last_name="?";

-- BOOKING IS ACTIVE --

SELECT status 
FROM booking 
WHERE booking_id="?" AND last_name="?" AND status="Active";

-- BOOKING IS INACTIVE --

SELECT status 
FROM booking 
WHERE booking_id="?" AND last_name="?" AND status in ("Canceled", "Passed");

-- BASIC BOOKING INFO --

SELECT booking_id, depart_flight_id, return_flight_id, booking_date, total_passengers, price_per_passenger, total_price, flight_type, status
FROM booking
WHERE booking_id="?" AND last_name="?";

-- BOOKING PASSENGER INFO --

SELECT p.passenger_id, p.first_name, p.last_name, phb.seat, phb.seat_class
FROM passenger as p, pass_has_booking as phb
WHERE p.passenger_id=phb.passenger_id AND phb.booking_id="?";

-- BOOKING CONTACT INFO --

SELECT first_name, last_name, email, mobile
FROM booking
WHERE booking_id="?" AND last_name="?";

-- ALL CUSTOMER BOOKINGS --

SELECT b.booking_id, b.last_name, a1.city, a2.city, b.booking_date, b.flight_type, b.status
FROM customer as c, booking as b, flight as f, airport as a1, airport as a2 
WHERE c.email="?" AND b.customer_id=c.customer_id AND f.flight_id=b.depart_flight_id AND a1.airport_code=f.from_airport AND a2.airport_code=f.to_airport 
ORDER BY b.booking_date DESC;

-- ADD BOOKING --
INSERT INTO booking 
VALUES ("?","?","?","?","?","?","?","?","?","?","?","?","?","?","Active");

-- MODIFY BOOKING --
UPDATE booking 
SET first_name="?", last_name="?", email="?", mobile="?", last_modify_date=CURRENT_DATE 
WHERE booking_id="?" and last_name="?";

-- CANCEL BOOKING --
UPDATE booking 
SET status="Canceled" 
WHERE booking_id="?" and last_name="?";

------------------------------------------------------------------------------------------------------------------------
-- MANAGE USER --
-----------------

-- USER EXISTS --

SELECT * 
FROM customer 
WHERE email="?"

-- GET USER INFO BY EMAIL --

SELECT customer_id, first_name, last_name, mobile, gender, joined_date, customer_type 
FROM customer 
WHERE email="?"

-- ADD USER --

INSERT INTO customer 
VALUES ("?", "?", "?", "?", "?", "?", "?", "?", "Active", "USER")

-- EDIT USER --

UPDATE customer 
SET first_name="?", last_name="?", mobile="?" 
WHERE customer_id="?" and email="?"

-- CHANGE USER PASSWORD --

UPDATE customer 
SET password="?" 
WHERE customer_id="?" and email="?"

-- DELETE USER --

DELETE FROM customer 
WHERE customer_id="?" and email="?"