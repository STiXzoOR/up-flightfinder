CREATE TABLE `PASSENGER` (
	`passenger_id` varchar(10) NOT NULL,
	`first_name` varchar(50) NOT NULL,
	`last_name` varchar(50) NOT NULL,
	PRIMARY KEY (`passenger_id`)
);

CREATE TABLE `AIRPORT` (
	`airport_code` varchar(3) NOT NULL,
	`airport_name` varchar(50) NOT NULL,
	`city` varchar(50) NOT NULL,
	`country` varchar(50) NOT NULL,
	PRIMARY KEY (`airport_code`)
);

CREATE TABLE `BOOKING` (
	`booking_id` varchar(6) NOT NULL,
	`customer_id` INT NOT NULL,
	`depart_flight_id` varchar(10) NOT NULL,
	`return_flight_id` varchar(10),
	`first_name` varchar(50) NOT NULL,
	`last_name` varchar(50) NOT NULL,
	`email` varchar(255) NOT NULL,
	`mobile` varchar(10) NOT NULL,
	`booking_date` DATE NOT NULL,
	`last_modify_date` DATE NOT NULL,
	`total_passengers` INT NOT NULL,
	`price_per_passenger` INT NOT NULL,
	`total_price` INT NOT NULL,
	`flight_type` varchar(50) NOT NULL,
	`status` varchar(50) NOT NULL,
	PRIMARY KEY (`booking_id`,`customer_id`,`depart_flight_id`)
);

CREATE TABLE `FLIGHT` (
	`flight_id` varchar(10) NOT NULL,
	`airline` varchar(2) NOT NULL,
	`airplane` varchar(3) NOT NULL,
	`from_airport` varchar(3) NOT NULL,
	`to_airport` varchar(3) NOT NULL,
	`dep_date` DATE NOT NULL,
	`dep_time` TIME NOT NULL,
	`arr_date` DATE NOT NULL,
	`arr_time` TIME NOT NULL,
	`duration` TIME NOT NULL,
	`class` varchar(50) NOT NULL,
	`price` INT NOT NULL,
	`change_fee` INT NOT NULL,
	`cancel_fee` INT NOT NULL,
	`discount` DECIMAL(5) NOT NULL,
	`occupied_capacity` INT NOT NULL,
	`status` varchar(50) NOT NULL,
	PRIMARY KEY (`flight_id`)
);

CREATE TABLE `AIRPLANE` (
	`airplane_model` varchar(3) NOT NULL,
	`airplane_name` varchar(100) NOT NULL,
	`capacity` INT NOT NULL,
	PRIMARY KEY (`airplane_model`)
);

CREATE TABLE `CUSTOMER` (
	`customer_id` INT NOT NULL,
	`email` varchar(255) NOT NULL,
	`password` BINARY(60),
	`first_name` varchar(50),
	`last_name` varchar(50),
	`mobile` varchar(10),
	`gender` varchar(6),
	`joined_date` DATE,
	`status` varchar(50),
	`customer_type` varchar(10),
	PRIMARY KEY (`customer_id`,`email`)
);

CREATE TABLE `AIRLINE` (
	`airline_code` varchar(2) NOT NULL,
	`airline_name` varchar(50) NOT NULL,
	PRIMARY KEY (`airline_code`)
);

CREATE TABLE `PASS_HAS_BOOKING` (
	`passenger_id` varchar(10) NOT NULL,
	`booking_id` varchar(6) NOT NULL,
	`seat` varchar(5) NOT NULL,
	`seat_class` varchar(50) NOT NULL,
	PRIMARY KEY (`passenger_id`,`booking_id`)
);

ALTER TABLE `BOOKING` ADD CONSTRAINT `BOOKING_fk0` FOREIGN KEY (`customer_id`) REFERENCES `CUSTOMER`(`customer_id`) ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE `BOOKING` ADD CONSTRAINT `BOOKING_fk1` FOREIGN KEY (`depart_flight_id`) REFERENCES `FLIGHT`(`flight_id`) ON DELETE CASCADE;

ALTER TABLE `BOOKING` ADD CONSTRAINT `BOOKING_fk2` FOREIGN KEY (`return_flight_id`) REFERENCES `FLIGHT`(`flight_id`) ON DELETE CASCADE;

ALTER TABLE `FLIGHT` ADD CONSTRAINT `FLIGHT_fk0` FOREIGN KEY (`airline`) REFERENCES `AIRLINE`(`airline_code`) ON UPDATE CASCADE;

ALTER TABLE `FLIGHT` ADD CONSTRAINT `FLIGHT_fk1` FOREIGN KEY (`airplane`) REFERENCES `AIRPLANE`(`airplane_model`) ON UPDATE CASCADE;

ALTER TABLE `FLIGHT` ADD CONSTRAINT `FLIGHT_fk2` FOREIGN KEY (`from_airport`) REFERENCES `AIRPORT`(`airport_code`) ON UPDATE CASCADE;

ALTER TABLE `FLIGHT` ADD CONSTRAINT `FLIGHT_fk3` FOREIGN KEY (`to_airport`) REFERENCES `AIRPORT`(`airport_code`) ON UPDATE CASCADE;

ALTER TABLE `PASS_HAS_BOOKING` ADD CONSTRAINT `PASS_HAS_BOOKING_fk0` FOREIGN KEY (`passenger_id`) REFERENCES `PASSENGER`(`passenger_id`) ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE `PASS_HAS_BOOKING` ADD CONSTRAINT `PASS_HAS_BOOKING_fk1` FOREIGN KEY (`booking_id`) REFERENCES `BOOKING`(`booking_id`) ON UPDATE CASCADE ON DELETE CASCADE;
