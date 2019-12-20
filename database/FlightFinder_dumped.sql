-- phpMyAdmin SQL Dump
-- version 4.9.0.1
-- https://www.phpmyadmin.net/
--
-- Host: localhost:8889
-- Generation Time: Dec 18, 2019 at 06:35 PM
-- Server version: 5.7.26
-- PHP Version: 7.3.8

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";

--
-- Database: `FlightFinderDB`
--

-- --------------------------------------------------------

--
-- Table structure for table `AIRLINE`
--

CREATE TABLE `AIRLINE` (
  `airline_code` varchar(2) NOT NULL,
  `airline_name` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `AIRLINE`
--

INSERT INTO `AIRLINE` (`airline_code`, `airline_name`) VALUES
('4U', 'Germanwings'),
('7G', 'Star Flyer'),
('9C', 'China SSS'),
('A3', 'Aegean Airlines'),
('AA', 'American Airlines'),
('AB', 'Air Berlin'),
('AC', 'Air Canada'),
('AF', 'Air France'),
('AI', 'Air India Limited'),
('AS', 'Alaska Airlines'),
('AY', 'Finnair'),
('AZ', 'Alitalia'),
('B6', 'JetBlue Airways'),
('BA', 'British Airways'),
('BC', 'Skymark Airlines'),
('BY', 'TUI Airways'),
('CA', 'Air China'),
('CY', 'Cyprus Airways'),
('CZ', 'China Southern Airlines'),
('DL', 'Delta Air Lines'),
('EB', 'Wamos Air'),
('EL', 'Air Nippon'),
('ET', 'Ethiopian Airlines'),
('FM', 'Shanghai Airlines'),
('FR', 'Ryanair'),
('GF', 'Gulf Air Bahrain'),
('HO', 'Juneyao Airlines'),
('IB', 'Iberia Airlines'),
('JL', 'Japan Airlines'),
('KL', 'KLM Royal Dutch Airlines'),
('KU', 'Kuwait Airways'),
('LA', 'LAN Airlines'),
('LH', 'Lufthansa'),
('LS', 'Jet2.com'),
('MH', 'Malaysia Airlines'),
('MT', 'Thomas Cook Airlines'),
('MU', 'China Eastern Airlines'),
('NH', 'All Nippon Airways'),
('NZ', 'Air New Zealand'),
('OA', 'Olympic Airlines'),
('PK', 'Pakistan International Airlines'),
('QR', 'Qatar Airways'),
('S7', 'S7 Airlines'),
('SQ', 'Singapore Airlines'),
('SU', 'Aeroflot Russian Airlines'),
('TO', 'Transavia France'),
('U2', 'easyJet'),
('U6', 'Ural Airlines'),
('UA', 'United Airlines'),
('UN', 'Transaero Airlines'),
('US', 'US Airways'),
('UX', 'Air Europa'),
('VN', 'Vietnam Airlines'),
('VS', 'Virgin Atlantic Airways'),
('VX', 'Virgin America'),
('VY', 'Formosa Airlines'),
('ZB', 'Air Bourbon'),
('ZH', 'Shenzhen Airlines');

-- --------------------------------------------------------

--
-- Table structure for table `AIRPLANE`
--

CREATE TABLE `AIRPLANE` (
  `airplane_model` varchar(3) NOT NULL,
  `airplane_name` varchar(100) NOT NULL,
  `capacity` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `AIRPLANE`
--

INSERT INTO `AIRPLANE` (`airplane_model`, `airplane_name`, `capacity`) VALUES
('319', 'Airbus A319', 134),
('320', 'Airbus A320', 150),
('321', 'Airbus A321', 185),
('32A', 'Airbus A320 (Sharklet)', 210),
('32B', 'Airbus A321 (Sharklet)', 180),
('32S', 'Airbus (A318/A318/A320/A321)', 222),
('330', 'Airbus A330', 293),
('332', 'Airbus A330-200', 225),
('333', 'Airbus A330-300', 283),
('346', 'Airbus A340-600', 342),
('388', 'Airbus A380-800', 525),
('733', 'Boeing 737-300', 148),
('735', 'Boeing 737-500', 140),
('737', 'Boeing 737', 210),
('738', 'Boeing 737-800', 175),
('73H', 'Boeing 737-800 (73H)', 160),
('744', 'Boeing 747-400', 416),
('752', 'Boeing 757-200', 228),
('757', 'Boeing 757', 240),
('75W', 'Boeing 757-200 (75W)', 230),
('763', 'Boeing 767-300', 210),
('764', 'Boeing 767-400', 243),
('767', 'Boeing 767', 174),
('76W', 'Boeing 767-300ER (76W)', 208),
('772', 'Boeing 777-200', 313),
('773', 'Boeing 777-300', 370),
('777', 'Boeing 777', 300),
('77W', 'Boeing 777-300ER', 370),
('787', 'Boeing 787', 267),
('788', 'Boeing 787-8', 325),
('AR8', 'Avro RJ85', 112),
('CR9', 'Canadair Regional Jet 900', 88),
('CRK', 'Canadair Regional Jet 1000', 100),
('E90', 'Embraer 190', 95);

-- --------------------------------------------------------

--
-- Table structure for table `AIRPORT`
--

CREATE TABLE `AIRPORT` (
  `airport_code` varchar(3) NOT NULL,
  `airport_name` varchar(50) NOT NULL,
  `city` varchar(50) NOT NULL,
  `country` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `AIRPORT`
--

INSERT INTO `AIRPORT` (`airport_code`, `airport_name`, `city`, `country`) VALUES
('ATH', 'Eleftherios Venizelos International Airport', 'Athens', 'Greece'),
('BCN', 'Barcelona International Airport', 'Barcelona', 'Spain'),
('CAN', 'Guangzhou Baiyun International Airport', 'Guangzhou', 'China'),
('DME', 'Domodedovo International Airport', 'Moscow', 'Russia'),
('FRA', 'Frankfurt am Main Airport', 'Frankfurt', 'Germany'),
('FUK', 'Fukuoka Airport', 'Fukuoka', 'Japan'),
('HND', 'Tokyo Haneda International Airport', 'Tokyo', 'Japan'),
('JFK', 'John F Kennedy International Airport', 'New York', 'United States'),
('LCA', 'Larnaca International Airport', 'Larnaca', 'Cyprus'),
('LHR', 'London Heathrow Airport', 'London', 'United Kingdom'),
('MAD', 'Adolfo Suarez Madrid-Barajas Airport', 'Madrid', 'Spain'),
('MAN', 'Manchester Airport', 'Manchester', 'United Kingdom'),
('ORY', 'Paris-Orly Airport', 'Paris', 'France'),
('PFO', 'Paphos International Airport', 'Paphos', 'Cyprus'),
('SFO', 'San Francisco International Airport', 'San Francisco', 'United States'),
('SHA', 'Shanghai Hongqiao International Airport', 'Shanghai', 'China'),
('SKG', 'Thessaloniki Macedonia International Airport', 'Thessaloniki', 'Greece'),
('STR', 'Stuttgart Airport', 'Stuttgart', 'Germany'),
('SVO', 'Sheremetyevo International Airport', 'Moscow', 'Russia'),
('TLS', 'Toulouse-Blagnac Airport', 'Toulouse', 'France');

-- --------------------------------------------------------

--
-- Table structure for table `BOOKING`
--

CREATE TABLE `BOOKING` (
  `booking_id` varchar(6) NOT NULL,
  `customer_id` int(11) NOT NULL,
  `depart_flight_id` varchar(10) NOT NULL,
  `return_flight_id` varchar(10),
  `first_name` varchar(50) NOT NULL,
  `last_name` varchar(50) NOT NULL,
  `email` varchar(255) NOT NULL,
  `mobile` varchar(10) NOT NULL,
  `booking_date` date NOT NULL,
  `last_modify_date` date NOT NULL,
  `total_passengers` int(11) NOT NULL,
  `price_per_passenger` int(11) NOT NULL,
  `total_price` int(11) NOT NULL,
  `flight_type` varchar(50) NOT NULL,
  `status` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Table structure for table `CUSTOMER`
--

CREATE TABLE `CUSTOMER` (
  `customer_id` int(11) NOT NULL,
  `email` varchar(255) NOT NULL,
  `password` binary(60) DEFAULT NULL,
  `first_name` varchar(50) DEFAULT NULL,
  `last_name` varchar(50) DEFAULT NULL,
  `mobile` varchar(10) DEFAULT NULL,
  `gender` varchar(6) DEFAULT NULL,
  `joined_date` date DEFAULT NULL,
  `status` varchar(50) DEFAULT NULL,
  `customer_type` varchar(10) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `CUSTOMER`
--

INSERT INTO `CUSTOMER` (`customer_id`, `email`, `password`, `first_name`, `last_name`, `mobile`, `gender`, `joined_date`, `status`, `customer_type`) VALUES
(0, 'None', NULL, NULL, NULL, NULL, NULL, NULL, 'Active', 'GUEST');

-- --------------------------------------------------------

--
-- Table structure for table `FLIGHT`
--

CREATE TABLE `FLIGHT` (
  `flight_id` varchar(10) NOT NULL,
  `airline` varchar(2) NOT NULL,
  `airplane` varchar(3) NOT NULL,
  `from_airport` varchar(3) NOT NULL,
  `to_airport` varchar(3) NOT NULL,
  `dep_date` date NOT NULL,
  `dep_time` time NOT NULL,
  `arr_date` date NOT NULL,
  `arr_time` time NOT NULL,
  `duration` time NOT NULL,
  `class` varchar(50) NOT NULL,
  `price` int(11) NOT NULL,
  `change_fee` int(11) NOT NULL,
  `cancel_fee` int(11) NOT NULL,
  `discount` decimal(5,0) NOT NULL,
  `occupied_capacity` int(11) NOT NULL,
  `status` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Table structure for table `PASSENGER`
--

CREATE TABLE `PASSENGER` (
  `passenger_id` varchar(10) NOT NULL,
  `first_name` varchar(50) NOT NULL,
  `last_name` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Table structure for table `PASS_HAS_BOOKING`
--

CREATE TABLE `PASS_HAS_BOOKING` (
  `passenger_id` varchar(10) NOT NULL,
  `booking_id` varchar(6) NOT NULL,
  `seat` varchar(5) NOT NULL,
  `seat_class` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `AIRLINE`
--
ALTER TABLE `AIRLINE`
  ADD PRIMARY KEY (`airline_code`);

--
-- Indexes for table `AIRPLANE`
--
ALTER TABLE `AIRPLANE`
  ADD PRIMARY KEY (`airplane_model`);

--
-- Indexes for table `AIRPORT`
--
ALTER TABLE `AIRPORT`
  ADD PRIMARY KEY (`airport_code`);

--
-- Indexes for table `BOOKING`
--
ALTER TABLE `BOOKING`
  ADD PRIMARY KEY (`booking_id`,`customer_id`,`depart_flight_id`),
  ADD KEY `BOOKING_fk0` (`customer_id`),
  ADD KEY `BOOKING_fk1` (`depart_flight_id`),
  ADD KEY `BOOKING_fk2` (`return_flight_id`);

--
-- Indexes for table `CUSTOMER`
--
ALTER TABLE `CUSTOMER`
  ADD PRIMARY KEY (`customer_id`,`email`);

--
-- Indexes for table `FLIGHT`
--
ALTER TABLE `FLIGHT`
  ADD PRIMARY KEY (`flight_id`),
  ADD KEY `FLIGHT_fk0` (`airline`),
  ADD KEY `FLIGHT_fk1` (`airplane`),
  ADD KEY `FLIGHT_fk2` (`from_airport`),
  ADD KEY `FLIGHT_fk3` (`to_airport`);

--
-- Indexes for table `PASSENGER`
--
ALTER TABLE `PASSENGER`
  ADD PRIMARY KEY (`passenger_id`);

--
-- Indexes for table `PASS_HAS_BOOKING`
--
ALTER TABLE `PASS_HAS_BOOKING`
  ADD PRIMARY KEY (`passenger_id`,`booking_id`),
  ADD KEY `PASS_HAS_BOOKING_fk1` (`booking_id`);

--
-- Constraints for dumped tables
--

--
-- Constraints for table `BOOKING`
--
ALTER TABLE `BOOKING`
  ADD CONSTRAINT `BOOKING_fk0` FOREIGN KEY (`customer_id`) REFERENCES `CUSTOMER` (`customer_id`) ON UPDATE CASCADE ON DELETE CASCADE,
  ADD CONSTRAINT `BOOKING_fk1` FOREIGN KEY (`depart_flight_id`) REFERENCES `FLIGHT` (`flight_id`) ON DELETE CASCADE,
  ADD CONSTRAINT `BOOKING_fk2` FOREIGN KEY (`return_flight_id`) REFERENCES `FLIGHT`(`flight_id`) ON DELETE CASCADE;

--
-- Constraints for table `FLIGHT`
--
ALTER TABLE `FLIGHT`
  ADD CONSTRAINT `FLIGHT_fk0` FOREIGN KEY (`airline`) REFERENCES `airline` (`airline_code`) ON UPDATE CASCADE,
  ADD CONSTRAINT `FLIGHT_fk1` FOREIGN KEY (`airplane`) REFERENCES `airplane` (`airplane_model`) ON UPDATE CASCADE,
  ADD CONSTRAINT `FLIGHT_fk2` FOREIGN KEY (`from_airport`) REFERENCES `airport` (`airport_code`) ON UPDATE CASCADE,
  ADD CONSTRAINT `FLIGHT_fk3` FOREIGN KEY (`to_airport`) REFERENCES `airport` (`airport_code`) ON UPDATE CASCADE;

--
-- Constraints for table `PASS_HAS_BOOKING`
--
ALTER TABLE `PASS_HAS_BOOKING`
  ADD CONSTRAINT `PASS_HAS_BOOKING_fk0` FOREIGN KEY (`passenger_id`) REFERENCES `PASSENGER` (`passenger_id`) ON DELETE CASCADE,
  ADD CONSTRAINT `PASS_HAS_BOOKING_fk1` FOREIGN KEY (`booking_id`) REFERENCES `BOOKING` (`booking_id`) ON DELETE CASCADE;

DELIMITER $$
--
-- Events
--
CREATE DEFINER=`root`@`localhost` EVENT `clean_inactive_flights` ON SCHEDULE EVERY 15 DAY STARTS (TIMESTAMP(CURRENT_DATE) + INTERVAL 1 DAY + INTERVAL 1 HOUR) ON COMPLETION NOT PRESERVE ENABLE COMMENT 'Clean up inactive flights after 15 days' DO DELETE FROM flight
    WHERE dep_date < CURRENT_DATE()$$

CREATE DEFINER=`root`@`localhost` EVENT `update_booking_status` ON SCHEDULE EVERY 1 DAY STARTS (TIMESTAMP(CURRENT_DATE) + INTERVAL 1 DAY + INTERVAL 1 HOUR) ON COMPLETION NOT PRESERVE ENABLE COMMENT 'Update booking status to inactive' DO UPDATE booking SET status="Passed"
    WHERE flight.dep_date < CURRENT_DATE()$$

DELIMITER ;
