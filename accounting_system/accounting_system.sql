-- MySQL dump 10.13  Distrib 8.0.42, for Win64 (x86_64)
--
-- Host: localhost    Database: accounting_system
-- ------------------------------------------------------
-- Server version	8.0.42

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `ai_analysis`
--

DROP TABLE IF EXISTS `ai_analysis`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ai_analysis` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `analysis_type` enum('账单分析','财务规划','智能问答') NOT NULL,
  `user_input` text,
  `ai_response` text,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_ai_user` (`user_id`,`created_at`),
  CONSTRAINT `ai_analysis_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ai_analysis`
--

LOCK TABLES `ai_analysis` WRITE;
/*!40000 ALTER TABLE `ai_analysis` DISABLE KEYS */;
INSERT INTO `ai_analysis` VALUES (7,1,'智能问答','我花钱太多了怎么办','看到您的问题，我理解您对支出控制的担忧。不过，根据您提供的数据，我想先给您一个积极的反馈：**您本月的储蓄率其实非常高，达到了约79%**（支出1050元 ÷ 收入5100元 ≈ 20.6%的支出比例），这是一个非常健康的财务状态。\n\n但您仍然感到“花钱太多”，这通常意味着支出可能超出了您内心的预算或预期。我们可以从以下几个步骤来优化您的财务习惯，让您更有掌控感：\n\n### 1. **先分析钱花在了哪里**\n   - 您最近的4条记录是关键。请回顾这些支出：它们是**必要开销**（如房租、饮食、通勤），还是**非必要消费**（如娱乐、购物、冲动消费）？\n   - 如果是必要开销，可以思考是否有节省空间（比如更换更实惠的套餐）；如果是非必要消费，可以评估这些花费是否带来了足够的价值。\n\n### 2. **建立明确的预算框架**\n   - 建议采用 **“50/30/20” 预算法则**作为参考：\n     - **50% 用于必要支出**（您目前远低于此，很好！）\n     - **30% 用于非必要但改善生活的消费**（如聚餐、爱好）\n     - **20% 用于储蓄或投资**（您目前的储蓄部分很高，可以合理分配一部分到消费或投资中）\n   - 根据您的收入（5100元），可以设定一个更符合您心理预期的月度支出上限，比如将非必要消费控制在1000-1500元以内。\n\n### 3. **追踪每一笔支出**\n   - 继续记录每笔花费，可以使用记账APP或简单表格。每周花5分钟回顾，就能清晰看出消费趋势，避免“钱不知花哪儿了”的焦虑。\n\n### 4. **设置消费冷静期**\n   - 如果常有冲动消费，可以给自己设定一个规则：比如想买非必需品时，等待24小时再决定。很多时候，冲动感会消失。\n\n### 5. **将余额合理规划**\n   - 您本月余额有4050元，可以考虑：\n     - **紧急备用金**：存3-6个月的生活费（以您目前的支出水平，很容易积累）。\n     - **长期目标**：如学习、旅行、投资等，为余额设定具体用途，花钱会更理性。\n\n### 最后的小鼓励：\n您的财务状况其实很稳健，储蓄意识很强。感到“花钱多”可能是消费结构或心理预期的问题。**调整预算不是为了苛刻自己，而是让钱更有效地服务于您的目标和生活质量。**\n\n如果需要，我可以帮您制定一个更详细的预算表，或者聊聊您的具体消费类别。您觉得哪一部分最想优先调整呢？','2025-12-28 07:25:25'),(9,1,'智能问答','我快活不下去了怎么办','看到您的财务数据，我非常理解您此刻的焦虑和压力。本月支出高达 **100.1万元**，而收入仅为5100元，导致近 **-99.6万元** 的巨额缺口，这确实是一个极其严峻的财务危机，必须立刻、严肃地处理。\n\n请不要慌张，我们一步一步来分析和应对。现在的首要任务是 **稳住局面，避免情况进一步恶化**。\n\n### 第一步：立即止损，厘清支出\n1.  **核对账目**：请立刻检查您记录的4条支出。这100.1万的支出是否全部属实？是否存在记录错误、盗刷或误操作（例如转账时多输了位数）？这是首先要排除的。\n2.  **冻结非必要支出**：立即停止所有非生存必需的消费。审视所有订阅服务、会员、投资性支出等，能取消的立刻取消。\n\n### 第二步：分析巨额支出的性质\n这笔支出决定了后续的应对策略：\n- **如果是债务（如房贷、车贷、借款、信用卡透支）**：您需要立刻联系债权人（银行、贷款机构、个人债主），**坦诚沟通**您当前的困境，说明情况，尝试协商是否可以申请延期还款、分期还款或制定新的还款计划。逃避会让问题更严重。\n- **如果是投资亏损或生意亏损**：需要评估该投资或生意是否还有挽回余地或止损退出机制。必要时，咨询专业的法律或财务顾问。\n- **如果是大额购物或消费**：检查是否有退货退款的可能。\n\n### 第三步：紧急生存方案\n1.  **保障基本生活**：确保您手头的现金（或可用额度）能覆盖未来1-2个月最基本的食宿开销。\n2.  **寻求外部支持**：\n    - **向家人坦白**：如果可能，向最信任的家人说明情况，寻求情感和可能的临时经济支持。共同面对比独自承受要好。\n    - **寻求专业帮助**：如果债务涉及多个机构且无法处理，可以咨询正规的**债务重组顾问**或**法律援助**。\n3.  **增加收入来源**：在应对债务的同时，尽一切可能增加收入。考虑兼职、利用技能接零工等，哪怕收入微薄，也能缓解部分压力。\n\n### 第四步：长远规划与心理建设\n1.  **制定极端紧缩预算**：未来很长一段时间，您需要执行一份仅包含生存必需品的预算计划。\n2.  **信用修复**：如果此事影响了您的个人信用，在解决债务后，需要长时间通过良好记录来逐步修复。\n3.  **照顾心理健康**：这样的压力极易导致崩溃。请务必告诉自己，**财务危机是可以解决的，虽然过程艰难**。如果感到无法承受，请寻求心理咨询或向公益热线倾诉，不要独自硬扛。\n\n**总结与行动清单：**\n1.  **立即核对**：确认100.1万支出的具体项目和真实性。\n2.  **立即沟通**：如果是债务，马上联系债权人协商。\n3.  **立即节流**：停掉所有非必要开支。\n4.  **寻求支持**：不要羞于向家人或专业机构求助。\n\n您能记录下收支并意识到问题的严重性，这已经是解决问题的第一步。**财务困境虽然可怕，但它是一个可以管理的问题，不代表您个人的失败。** 请优先处理最紧急的债务和生存问题，一步一步来。\n\n如果您愿意分享更多关于这笔支出的具体情况（例如是何种类型、是否分期、债权人是谁），我可以为您提供更具针对性的建议。您不是一个人在面对，我们一起来想办法。','2025-12-28 07:37:10');
/*!40000 ALTER TABLE `ai_analysis` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `categories`
--

DROP TABLE IF EXISTS `categories`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `categories` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  `type` enum('收入','支出') NOT NULL,
  `user_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `categories_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `categories`
--

LOCK TABLES `categories` WRITE;
/*!40000 ALTER TABLE `categories` DISABLE KEYS */;
INSERT INTO `categories` VALUES (1,'餐饮','支出',NULL),(2,'交通','支出',NULL),(3,'购物','支出',NULL),(4,'娱乐','支出',NULL),(5,'工资','收入',NULL),(6,'兼职','收入',NULL);
/*!40000 ALTER TABLE `categories` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `records`
--

DROP TABLE IF EXISTS `records`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `records` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `category_id` int NOT NULL,
  `amount` decimal(10,2) NOT NULL,
  `description` text,
  `record_date` date NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  KEY `category_id` (`category_id`),
  CONSTRAINT `records_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  CONSTRAINT `records_ibfk_2` FOREIGN KEY (`category_id`) REFERENCES `categories` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `records`
--

LOCK TABLES `records` WRITE;
/*!40000 ALTER TABLE `records` DISABLE KEYS */;
INSERT INTO `records` VALUES (3,1,6,100.00,'','2025-12-28','2025-12-28 06:04:29'),(5,1,1,-1000.00,'','2025-12-28','2025-12-28 06:42:59'),(6,1,5,5000.00,'','2025-12-28','2025-12-28 06:45:58'),(8,1,1,-1000000.00,'','2025-12-28','2025-12-28 07:36:27');
/*!40000 ALTER TABLE `records` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(50) NOT NULL,
  `password` varchar(255) NOT NULL,
  `email` varchar(100) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'19942350762','ef797c8118f02dfb649607dd5d3f8c7623048c9c063d532cc95c5ed7a898a64f','','2025-12-28 06:03:30');
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-12-28 15:50:27
