-- =============================
-- =========[ ONE WAY ]=========
-- =============================
-- SEARCH
-- ============================
SELECT flight_id,airline,from_airport,to_airport,dep_date,dep_time,arr_time,duration,class,price
FROM FLIGHT
WHERE from_airport="ATH" AND to_airport="LCA" AND dep_date="2019-11-24" AND status="Active" AND class="Business"
ORDER BY price

============================
SELECT
============================
SELECT f.flight_id, f.airline, al.airline_name, f.from_airport, f.to_airport, f.dep_date, f.dep_time, f.arr_time, f.duration, f.class, f.price, ap.airplane_name, al.logo
FROM FLIGHT f, AIRLINE al, AIRPLANE ap
WHERE al.airline_code=f.airline AND ap.airplane_model=f.airplane AND f.from_airport="ATH" AND f.to_airport="LCA" AND f.dep_date="2019-11-24" AND f.status="Upcoming" AND f.class="Business"
ORDER BY f.price

============================
ROUNDTRIP
============================
SELECT f1.flight_id, f1.airline, f1.from_airport, f1.to_airport, f1.dep_date, f1.dep_time, f1.arr_date, f1.arr_time, f1.duration, f1.class, f1.price, f2.flight_id, f2.airline, f2.from_airport, f2.to_airport, f2.dep_date, f2.dep_time, f2.arr_date, f2.arr_time, f2.duration, f2.class, f2.price
FROM FLIGHT f1, FLIGHT f2
WHERE f1.from_airport="ATH" AND f1.to_airport="LCA" AND f1.dep_date="2019-11-24" AND f1.class="Economy" AND f1.status="Upcoming" AND f2.from_airport="LCA" AND f2.to_airport="ATH" AND f2.dep_date="2019-11-24" AND f2.class="First Class" AND f2.status="Upcoming" AND IF(f1.dep_date=f2.dep_date, f2.dep_time>=ADDTIME(f1.arr_time, "05:00:00"), 1) AND IF(f1.dep_date=f2.dep_date, f1.arr_date=f1.dep_date, 1)
ORDER BY f1.price+f2.price


===========================
TODAY FLIGHTS
===========================
SELECT f.* 
FROM FLIGHT f
WHERE f.dep_date=CURRENT_DATE()

===========================
ALL FLIGHTS FOR A COUNTRY
===========================
SELECT f.* 
FROM FLIGHT f, AIRPORT ap 
WHERE f.from_airport=ap.airport_code AND ap.country="xxxxx" -- where xxxxx is the country


===========================
LONGEST FLIGHT
===========================
SELECT DISTINCT, f.from_airport, f.to_airport, f.duration 
FROM FLIGHT f 
WHERE f.duration IN (
    SELECT max(duration) 
    FROM FLIGHT)
ORDER BY f.duration

===========================
FLIGHTS BETWEEN DATETIMES
===========================
SELECT *
FROM FLIGHT
WHERE dep_time BETWEEN "xx:xx:xx" AND "xx:xx:xx" OR arr_time BETWEEN "xx:xx:xx" AND "xx:xx:xx" AND dep_time >= curtime() OR arr_time >= curtime()
