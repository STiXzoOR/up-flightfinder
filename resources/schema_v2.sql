-- MySQL dump 10.13  Distrib 8.0.19, for macos10.15 (x86_64)
--
-- Host: localhost    Database: FlightFinderDB
-- ------------------------------------------------------
-- Server version	5.7.26

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `AIRLINE`
--

DROP TABLE IF EXISTS `AIRLINE`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `AIRLINE` (
  `airline_code` varchar(2) NOT NULL,
  `airline_name` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`airline_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `AIRLINE`
--

LOCK TABLES `AIRLINE` WRITE;
/*!40000 ALTER TABLE `AIRLINE` DISABLE KEYS */;

INSERT INTO `AIRLINE` (`airline_code`, `airline_name`)
VALUES
	('4U','Germanwings'),
	('7G','Star Flyer'),
	('9C','China SSS'),
	('A3','Aegean Airlines'),
	('AA','American Airlines'),
	('AB','Air Berlin'),
	('AC','Air Canada'),
	('AF','Air France'),
	('AI','Air India Limited'),
	('AS','Alaska Airlines'),
	('AY','Finnair'),
	('AZ','Alitalia'),
	('B6','JetBlue Airways'),
	('BA','British Airways'),
	('BC','Skymark Airlines'),
	('BY','TUI Airways'),
	('CA','Air China'),
	('CY','Cyprus Airways'),
	('CZ','China Southern Airlines'),
	('DL','Delta Air Lines'),
	('EB','Wamos Air'),
	('EL','Air Nippon'),
	('ET','Ethiopian Airlines'),
	('FM','Shanghai Airlines'),
	('FR','Ryanair'),
	('GF','Gulf Air Bahrain'),
	('HO','Juneyao Airlines'),
	('IB','Iberia Airlines'),
	('JL','Japan Airlines'),
	('KL','KLM Royal Dutch Airlines'),
	('KU','Kuwait Airways'),
	('LA','LAN Airlines'),
	('LH','Lufthansa'),
	('LS','Jet2.com'),
	('MH','Malaysia Airlines'),
	('MT','Thomas Cook Airlines'),
	('MU','China Eastern Airlines'),
	('NH','All Nippon Airways'),
	('NZ','Air New Zealand'),
	('OA','Olympic Airlines'),
	('PK','Pakistan International Airlines'),
	('QR','Qatar Airways'),
	('S7','S7 Airlines'),
	('SQ','Singapore Airlines'),
	('SU','Aeroflot Russian Airlines'),
	('TO','Transavia France'),
	('U2','easyJet'),
	('U6','Ural Airlines'),
	('UA','United Airlines'),
	('UN','Transaero Airlines'),
	('US','US Airways'),
	('UX','Air Europa'),
	('VN','Vietnam Airlines'),
	('VS','Virgin Atlantic Airways'),
	('VX','Virgin America'),
	('VY','Formosa Airlines'),
	('ZB','Air Bourbon'),
	('ZH','Shenzhen Airlines');

/*!40000 ALTER TABLE `AIRLINE` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `AIRPLANE`
--

DROP TABLE IF EXISTS `AIRPLANE`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `AIRPLANE` (
  `airplane_model` varchar(3) NOT NULL,
  `airplane_name` varchar(100) DEFAULT NULL,
  `capacity` int(11) DEFAULT NULL,
  PRIMARY KEY (`airplane_model`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `AIRPLANE`
--

LOCK TABLES `AIRPLANE` WRITE;
/*!40000 ALTER TABLE `AIRPLANE` DISABLE KEYS */;

INSERT INTO `AIRPLANE` (`airplane_model`, `airplane_name`, `capacity`)
VALUES
	('319','Airbus A319',134),
	('320','Airbus A320',150),
	('321','Airbus A321',185),
	('32A','Airbus A320 (Sharklet)',210),
	('32B','Airbus A321 (Sharklet)',180),
	('32S','Airbus (A318/A318/A320/A321)',222),
	('330','Airbus A330',293),
	('332','Airbus A330-200',225),
	('333','Airbus A330-300',283),
	('346','Airbus A340-600',342),
	('388','Airbus A380-800',525),
	('733','Boeing 737-300',148),
	('735','Boeing 737-500',140),
	('737','Boeing 737',210),
	('738','Boeing 737-800',175),
	('73H','Boeing 737-800 (73H)',160),
	('744','Boeing 747-400',416),
	('752','Boeing 757-200',228),
	('757','Boeing 757',240),
	('75W','Boeing 757-200 (75W)',230),
	('763','Boeing 767-300',210),
	('764','Boeing 767-400',243),
	('767','Boeing 767',174),
	('76W','Boeing 767-300ER (76W)',208),
	('772','Boeing 777-200',313),
	('773','Boeing 777-300',370),
	('777','Boeing 777',300),
	('77W','Boeing 777-300ER',370),
	('787','Boeing 787',267),
	('788','Boeing 787-8',325),
	('AR8','Avro RJ85',112),
	('CR9','Canadair Regional Jet 900',88),
	('CRK','Canadair Regional Jet 1000',100),
	('E90','Embraer 190',95);

/*!40000 ALTER TABLE `AIRPLANE` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `AIRPORT`
--

DROP TABLE IF EXISTS `AIRPORT`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `AIRPORT` (
  `airport_code` varchar(3) NOT NULL,
  `airport_name` varchar(50) DEFAULT NULL,
  `city` varchar(50) DEFAULT NULL,
  `country` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`airport_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `AIRPORT`
--

LOCK TABLES `AIRPORT` WRITE;
/*!40000 ALTER TABLE `AIRPORT` DISABLE KEYS */;

INSERT INTO `AIRPORT` (`airport_code`, `airport_name`, `city`, `country`)
VALUES
	('ATH','Eleftherios Venizelos International Airport','Athens','Greece'),
	('BCN','Barcelona International Airport','Barcelona','Spain'),
	('CAN','Guangzhou Baiyun International Airport','Guangzhou','China'),
	('DME','Domodedovo International Airport','Moscow','Russia'),
	('FRA','Frankfurt am Main Airport','Frankfurt','Germany'),
	('FUK','Fukuoka Airport','Fukuoka','Japan'),
	('HND','Tokyo Haneda International Airport','Tokyo','Japan'),
	('JFK','John F Kennedy International Airport','New York','United States'),
	('LCA','Larnaca International Airport','Larnaca','Cyprus'),
	('LHR','London Heathrow Airport','London','United Kingdom'),
	('MAD','Adolfo Suarez Madrid-Barajas Airport','Madrid','Spain'),
	('MAN','Manchester Airport','Manchester','United Kingdom'),
	('ORY','Paris-Orly Airport','Paris','France'),
	('PFO','Paphos International Airport','Paphos','Cyprus'),
	('SFO','San Francisco International Airport','San Francisco','United States'),
	('SHA','Shanghai Hongqiao International Airport','Shanghai','China'),
	('SKG','Thessaloniki Macedonia International Airport','Thessaloniki','Greece'),
	('STR','Stuttgart Airport','Stuttgart','Germany'),
	('SVO','Sheremetyevo International Airport','Moscow','Russia'),
	('TLS','Toulouse-Blagnac Airport','Toulouse','France');

/*!40000 ALTER TABLE `AIRPORT` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `BOOKING`
--

DROP TABLE IF EXISTS `BOOKING`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `BOOKING` (
  `booking_id` varchar(6) NOT NULL,
  `customer_id` int(11) NOT NULL,
  `depart_flight_id` varchar(10) NOT NULL,
  `return_flight_id` varchar(10) NOT NULL,
  `depart_flight_date` date NOT NULL,
  `return_flight_date` date NOT NULL,
  `flight_class` varchar(50) NOT NULL,
  `first_name` varchar(50) DEFAULT NULL,
  `last_name` varchar(50) DEFAULT NULL,
  `email` varchar(255) DEFAULT NULL,
  `mobile` varchar(10) DEFAULT NULL,
  `booking_date` date DEFAULT NULL,
  `last_modify_date` date DEFAULT NULL,
  `total_passengers` int(11) DEFAULT NULL,
  `price_per_passenger` int(11) DEFAULT NULL,
  `total_price` int(11) DEFAULT NULL,
  `flight_type` varchar(50) DEFAULT NULL,
  `status` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`booking_id`,`customer_id`,`depart_flight_id`,`depart_flight_date`,`flight_class`),
  KEY `fk_BOOKING_CUSTOMER1_idx` (`customer_id`),
  KEY `fk_BOOKING_FLIGHT1_idx` (`depart_flight_id`,`depart_flight_date`,`flight_class`),
  KEY `fk_BOOKING_FLIGHT2_idx` (`return_flight_id`,`return_flight_date`),
  CONSTRAINT `fk_BOOKING_CUSTOMER1` FOREIGN KEY (`customer_id`) REFERENCES `CUSTOMER` (`customer_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_BOOKING_FLIGHT1` FOREIGN KEY (`depart_flight_id`, `depart_flight_date`, `flight_class`) REFERENCES `FLIGHT` (`flight_id`, `dep_date`, `class`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_BOOKING_FLIGHT2` FOREIGN KEY (`return_flight_id`, `return_flight_date`) REFERENCES `FLIGHT` (`flight_id`, `dep_date`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `BOOKING`
--

LOCK TABLES `BOOKING` WRITE;
/*!40000 ALTER TABLE `BOOKING` DISABLE KEYS */;
/*!40000 ALTER TABLE `BOOKING` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `CUSTOMER`
--

DROP TABLE IF EXISTS `CUSTOMER`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `CUSTOMER` (
  `customer_id` int(11) NOT NULL AUTO_INCREMENT,
  `email` varchar(255) DEFAULT NULL,
  `password` binary(60) DEFAULT NULL,
  `first_name` varchar(50) DEFAULT NULL,
  `last_name` varchar(50) DEFAULT NULL,
  `mobile` varchar(10) DEFAULT NULL,
  `gender` varchar(6) DEFAULT NULL,
  `joined_date` date DEFAULT NULL,
  `status` varchar(50) DEFAULT NULL,
  `customer_type` varchar(10) DEFAULT NULL,
  PRIMARY KEY (`customer_id`),
  UNIQUE KEY `email_UNIQUE` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `CUSTOMER`
--

LOCK TABLES `CUSTOMER` WRITE;
/*!40000 ALTER TABLE `CUSTOMER` DISABLE KEYS */;

INSERT INTO `CUSTOMER` (`customer_id`, `email`, `password`, `first_name`, `last_name`, `mobile`, `gender`, `joined_date`, `status`, `customer_type`)
VALUES
	(1,'None',NULL,NULL,NULL,NULL,NULL,NULL,'Confirmed','GUEST');

/*!40000 ALTER TABLE `CUSTOMER` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `FLIGHT`
--

DROP TABLE IF EXISTS `FLIGHT`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `FLIGHT` (
  `flight_id` varchar(10) NOT NULL,
  `airline` varchar(2) NOT NULL,
  `airplane` varchar(3) NOT NULL,
  `from_airport` varchar(3) NOT NULL,
  `to_airport` varchar(3) NOT NULL,
  `dep_date` date NOT NULL,
  `dep_time` time DEFAULT NULL,
  `arr_date` date DEFAULT NULL,
  `arr_time` time DEFAULT NULL,
  `duration` time DEFAULT NULL,
  `class` varchar(50) NOT NULL,
  `price` int(11) DEFAULT NULL,
  `change_fee` int(11) DEFAULT NULL,
  `cancel_fee` int(11) DEFAULT NULL,
  `discount` decimal(5,0) DEFAULT NULL,
  `occupied_capacity` int(11) DEFAULT NULL,
  `status` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`flight_id`,`dep_date`,`class`),
  KEY `fk_FLIGHT_AIRLINE1_idx` (`airline`),
  KEY `fk_FLIGHT_AIRPLANE1_idx` (`airplane`),
  KEY `fk_FLIGHT_AIRPORT1_idx` (`from_airport`),
  KEY `fk_FLIGHT_AIRPORT2_idx` (`to_airport`),
  CONSTRAINT `fk_FLIGHT_AIRLINE1` FOREIGN KEY (`airline`) REFERENCES `AIRLINE` (`airline_code`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `fk_FLIGHT_AIRPLANE1` FOREIGN KEY (`airplane`) REFERENCES `AIRPLANE` (`airplane_model`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `fk_FLIGHT_AIRPORT1` FOREIGN KEY (`from_airport`) REFERENCES `AIRPORT` (`airport_code`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `fk_FLIGHT_AIRPORT2` FOREIGN KEY (`to_airport`) REFERENCES `AIRPORT` (`airport_code`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `FLIGHT`
--

LOCK TABLES `FLIGHT` WRITE;
/*!40000 ALTER TABLE `FLIGHT` DISABLE KEYS */;
/*!40000 ALTER TABLE `FLIGHT` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `PASSENGER`
--

DROP TABLE IF EXISTS `PASSENGER`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `PASSENGER` (
  `passenger_id` int(11) NOT NULL,
  `first_name` varchar(50) DEFAULT NULL,
  `last_name` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`passenger_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `PASSENGER`
--

LOCK TABLES `PASSENGER` WRITE;
/*!40000 ALTER TABLE `PASSENGER` DISABLE KEYS */;
/*!40000 ALTER TABLE `PASSENGER` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `PASS_HAS_BOOKING`
--

DROP TABLE IF EXISTS `PASS_HAS_BOOKING`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `PASS_HAS_BOOKING` (
  `booking_id` varchar(6) NOT NULL,
  `passenger_id` int(11) NOT NULL,
  `seat` varchar(5) DEFAULT NULL,
  `seat_class` varchar(50) DEFAULT NULL,
  `seat_price` int(11) DEFAULT NULL,
  PRIMARY KEY (`booking_id`,`passenger_id`),
  KEY `fk_PASS_HAS_BOOKING_PASSENGER_idx` (`passenger_id`),
  KEY `fk_PASS_HAS_BOOKING_BOOKING1_idx` (`booking_id`),
  CONSTRAINT `fk_PASS_HAS_BOOKING_BOOKING1` FOREIGN KEY (`booking_id`) REFERENCES `BOOKING` (`booking_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_PASS_HAS_BOOKING_PASSENGER` FOREIGN KEY (`passenger_id`) REFERENCES `PASSENGER` (`passenger_id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `PASS_HAS_BOOKING`
--

LOCK TABLES `PASS_HAS_BOOKING` WRITE;
/*!40000 ALTER TABLE `PASS_HAS_BOOKING` DISABLE KEYS */;
/*!40000 ALTER TABLE `PASS_HAS_BOOKING` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2020-02-01 17:49:45
