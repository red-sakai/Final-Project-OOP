-- MySQL dump 10.13  Distrib 8.0.42, for Win64 (x86_64)
--
-- Host: localhost    Database: hh_support_tickets_db
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
-- Table structure for table `support_tickets`
--

DROP TABLE IF EXISTS `support_tickets`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `support_tickets` (
  `ticket_id` varchar(50) NOT NULL,
  `user_email` varchar(255) DEFAULT NULL,
  `ticket_title` varchar(255) DEFAULT NULL,
  `ticket_description` text,
  `error_code` varchar(50) DEFAULT NULL,
  `tracking_id` varchar(50) DEFAULT NULL,
  `timestamp` datetime DEFAULT NULL,
  `admin_reply` text,
  `reply_timestamp` datetime DEFAULT NULL,
  `attachments` varchar(255) DEFAULT NULL,
  `status` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`ticket_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `support_tickets`
--

LOCK TABLES `support_tickets` WRITE;
/*!40000 ALTER TABLE `support_tickets` DISABLE KEYS */;
INSERT INTO `support_tickets` VALUES ('78f74f42-b123-4d87-b67e-35013cb00788','jheredtest@gmail.com','testetsteqwe','123123123123123','','','2025-06-06 12:10:43','hello there','2025-06-06 12:54:56','','done'),('d11c018c-51e5-4ca2-b6db-96ddf3c58b15','jheredtest@gmail.com','test1231231231231231','1312312312312313123123123123','','','2025-06-06 12:20:10','sdsfgdsfgsdfgsdgfdggds','2025-06-06 12:42:31','support_attachments/36cf2d58-e8f3-4c8d-b668-00d4bd2b0ad6_1749183607_Wooden_Table_in_Blurred_Classroom_Setting.jpg','done'),('db7e72f7-9592-4bed-aa71-5ef808a64f15','jheredmiguelrepublica14@gmail.com','Test email 123','test email 123','','','2025-06-06 13:59:48','cute dog','2025-06-06 14:00:22','support_attachments/252e5bc7-3ea2-4382-bd3a-67364136cfc4_1749189585_golden_goldenretrieverlife_.jpg','done'),('e447436d-c4cb-451a-989a-0ead5ecebbe4','jheredmiguelrepublica14@gmail.com','Booking does not append yet','fix it plz','','','2025-06-06 13:05:31','it fixed olready noob','2025-06-06 13:06:05','support_attachments/21c3bc7e-1926-4c0b-8649-495b57c78e29_1749186328_ChatGPT_Image_Jun_1_2025_10_02_01_PM.png','done');
/*!40000 ALTER TABLE `support_tickets` ENABLE KEYS */;
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
