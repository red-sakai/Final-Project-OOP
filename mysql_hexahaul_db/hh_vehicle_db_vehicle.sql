-- MySQL dump 10.13  Distrib 8.0.42, for Win64 (x86_64)
--
-- Host: localhost    Database: hh_vehicle_db
-- ------------------------------------------------------
-- Server version	8.0.42

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
-- Table structure for table `vehicle`
--

DROP TABLE IF EXISTS `vehicle`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `vehicle` (
  `Employee Id` int DEFAULT NULL,
  `unit_name` varchar(100) DEFAULT NULL,
  `unit_brand` varchar(50) DEFAULT NULL,
  `year` int DEFAULT NULL,
  `km_driven` int DEFAULT NULL,
  `min_weight` float DEFAULT NULL,
  `max_weight` float DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `vehicle`
--

LOCK TABLES `vehicle` WRITE;
/*!40000 ALTER TABLE `vehicle` DISABLE KEYS */;
INSERT INTO `vehicle` VALUES (201,'Honda Civic','Honda',2016,63463,25,350),(202,'Yamaha Mio Sporty','Yamaha',2011,164606,0.1,20),(203,'Yamaha NMAX','Yamaha',2024,85484,25,80),(204,'Toyota Vios','Toyota',2018,84126,20,300),(205,'Toyota Vios','Toyota',2016,89033,20,300),(206,'Honda Click 125i','Honda',2016,152252,0.1,25),(207,'Honda Click 125i','Honda',2018,9142,0.1,25),(208,'Yamaha Mio Sporty','Yamaha',2011,171637,0.1,20),(209,'Honda Click 125i','Honda',2009,195747,0.1,25),(210,'Honda Click 125i','Honda',2020,41700,0.1,25),(211,'Honda Civic','Honda',2008,194958,25,350),(212,'MG 5','SAIC',2019,20036,25,350),(213,'Toyota Vios','Toyota',2015,84817,20,300),(214,'Yamaha Mio Sporty','Yamaha',2010,156259,0.1,20),(215,'Yamaha Mio Sporty','Yamaha',2013,154282,0.1,20),(216,'Honda Civic','Honda',2014,190389,25,350),(217,'Honda Click 125i','Honda',2014,131976,0.1,25),(218,'Honda Click 125i','Honda',2016,156245,0.1,25),(219,'Toyota Vios','Toyota',2022,58374,20,300),(220,'Toyota Vios','Toyota',2023,189369,20,300),(221,'Honda Click 125i','Honda',2016,62991,0.1,25),(222,'Toyota Vios','Toyota',2016,192182,20,300),(223,'Yamaha NMAX','Yamaha',2007,175346,25,80),(224,'Honda Civic','Honda',2022,2370,25,350),(225,'Yamaha Mio Sporty','Yamaha',2007,194306,0.1,20),(226,'Yamaha Mio Sporty','Yamaha',2018,56233,0.1,20),(227,'Yamaha NMAX','Yamaha',2024,64226,25,80),(228,'Honda Click 125i','Honda',2023,110436,0.1,25),(229,'Toyota Vios','Toyota',2021,31281,20,300),(230,'Honda Civic','Honda',2019,155815,25,350),(231,'Honda Civic','Honda',2011,46693,25,350),(232,'Yamaha Mio Sporty','Yamaha',2021,27082,0.1,20),(233,'Honda Civic','Honda',2010,34565,25,350),(234,'Yamaha NMAX','Yamaha',2021,123187,25,80),(235,'Mitsubishi Fuso Fighter','Mitsubishi',2020,16768,3000,7000),(236,'Hino 700 Series Dump Truck','Hino',2022,56336,7000,15000),(237,'Isuzu ELF NHR 55','Isuzu',2009,151604,350,3000),(238,'Mitsubishi Fuso Fighter','Mitsubishi',2008,12040,3000,7000),(239,'Hino 700 Series Dump Truck','Hino',2022,93217,7000,15000),(240,'Isuzu ELF NHR 55','Isuzu',2015,85225,350,3000);
/*!40000 ALTER TABLE `vehicle` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-06-07  8:26:34
