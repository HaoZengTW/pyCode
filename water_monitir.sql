-- MySQL dump 10.13  Distrib 8.0.38, for macos14 (x86_64)
--
-- Host: localhost    Database: water_monitor
-- ------------------------------------------------------
-- Server version	9.0.1

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
-- Table structure for table `log_table`
--

DROP TABLE IF EXISTS `log_table`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `log_table` (
  `log_id` int NOT NULL AUTO_INCREMENT,
  `station_name` varchar(45) DEFAULT NULL,
  `notify_time` datetime DEFAULT NULL,
  `status` tinyint DEFAULT NULL,
  `rainfall_condition` float DEFAULT NULL,
  `rainfall_10min` float DEFAULT NULL,
  `error_msg` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`log_id`)
) ENGINE=InnoDB AUTO_INCREMENT=110 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `rainfall_web`
--

DROP TABLE IF EXISTS `rainfall_web`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `rainfall_web` (
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
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `valve_table`
--

DROP TABLE IF EXISTS `valve_table`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `valve_table` (
  `valve_id` int NOT NULL AUTO_INCREMENT,
  `valve_close_time` datetime DEFAULT NULL,
  `before_size` int DEFAULT NULL,
  `before_flow` int DEFAULT NULL,
  `after_size` int DEFAULT NULL,
  `after_flow` int DEFAULT NULL,
  `current_time` datetime DEFAULT NULL,
  PRIMARY KEY (`valve_id`)
) ENGINE=InnoDB AUTO_INCREMENT=77 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2024-12-19 14:21:07