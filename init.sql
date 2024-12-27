CREATE DATABASE IF NOT EXISTS water_monitor;

USE water_monitor;

CREATE TABLE IF NOT EXISTS `log_table` (
  `log_id` int NOT NULL AUTO_INCREMENT,
  `station_name` varchar(45) DEFAULT NULL,
  `notify_time` datetime DEFAULT NULL,
  `status` tinyint DEFAULT NULL,
  `rainfall_condition` float DEFAULT NULL,
  `rainfall_10min` float DEFAULT NULL,
  `error_msg` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`log_id`)
) ENGINE=InnoDB AUTO_INCREMENT=110 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS `rainfall_web` (
  `primary_num` int NOT NULL AUTO_INCREMENT,
  `station_name` varchar(45) DEFAULT NULL,
  `region_name` varchar(45) DEFAULT NULL,
  `rainfall_10min` float DEFAULT NULL,
  `rainfall_1hr` float DEFAULT NULL,
  `rainfall_3hr` float DEFAULT NULL,
  `rainfall_6hr` float DEFAULT NULL,
  `rainfall_12hr` float DEFAULT NULL,
  `rainfall_24hr` float DEFAULT NULL,
  `rainfall_2days` float DEFAULT NULL,
  `data_time` datetime DEFAULT NULL,
  `current_time` datetime DEFAULT NULL,
  PRIMARY KEY (`primary_num`)
) ENGINE=InnoDB AUTO_INCREMENT=20747 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS `valve_table` (
  `valve_id` int NOT NULL AUTO_INCREMENT,
  `valve_close_time` datetime DEFAULT NULL,
  `before_size` int DEFAULT NULL,
  `before_flow` int DEFAULT NULL,
  `after_size` int DEFAULT NULL,
  `after_flow` int DEFAULT NULL,
  `current_time` datetime DEFAULT NULL,
  PRIMARY KEY (`valve_id`)
) ENGINE=InnoDB AUTO_INCREMENT=77 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

