-- phpMyAdmin SQL Dump
-- version 5.0.2
-- https://www.phpmyadmin.net/
--
-- 主機： 127.0.0.1:3306
-- 產生時間： 2022-04-11 04:18:56
-- 伺服器版本： 5.7.31
-- PHP 版本： 7.3.21

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- 資料庫： `fyp2`
--

-- --------------------------------------------------------

--
-- 資料表結構 `notice`
--

DROP TABLE IF EXISTS `notice`;
CREATE TABLE IF NOT EXISTS `notice` (
  `noticeID` int(11) NOT NULL AUTO_INCREMENT,
  `userID` varchar(255) NOT NULL,
  `sportname` varchar(255) NOT NULL,
  PRIMARY KEY (`noticeID`,`userID`) USING BTREE,
  KEY `fk_notice_userID` (`userID`),
  KEY `fk_notice_sportName` (`sportname`)
) ENGINE=MyISAM AUTO_INCREMENT=10 DEFAULT CHARSET=utf8;

--
-- 傾印資料表的資料 `notice`
--

INSERT INTO `notice` (`noticeID`, `userID`, `sportname`) VALUES
(7, '5e364454048b8b039629a49a6e090795', '上肢綜合運動'),
(8, '5e364454048b8b039629a49a6e090795', '協調運動'),
(9, '5e364454048b8b039629a49a6e090795', '抬腿運動');

-- --------------------------------------------------------

--
-- 資料表結構 `sport`
--

DROP TABLE IF EXISTS `sport`;
CREATE TABLE IF NOT EXISTS `sport` (
  `sportID` int(11) NOT NULL AUTO_INCREMENT,
  `sportname` varchar(255) NOT NULL,
  `engname` varchar(255) NOT NULL,
  `sdescribe` varchar(255) DEFAULT NULL,
  `difficulty` varchar(255) DEFAULT NULL,
  `imgpath` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`sportID`,`sportname`) USING BTREE
) ENGINE=MyISAM AUTO_INCREMENT=4 DEFAULT CHARSET=utf8;

--
-- 傾印資料表的資料 `sport`
--

INSERT INTO `sport` (`sportID`, `sportname`, `engname`, `sdescribe`, `difficulty`, `imgpath`) VALUES
(1, '上肢綜合運動', 'handlift', '可以讓你保持關節彈性、改善水腫與改善上肢無力的狀況！\r\n\r\n', 'low', 'handlift.jpeg'),
(2, '協調運動', 'legCoordination', '改善身體平衡性和協調性', 'low', 'legCoordination.jpeg'),
(3, '抬腿運動', 'leglift', '激人體分泌激素，進而達到解毒、排毒的功能。 運動時也會刺激大小腸的蠕動，促進腸胃的消化功能。 高抬腿運動進行時必須維持上半身的筆直與穩定性\r\n\r\n', 'low', 'leglift.jpeg');

-- --------------------------------------------------------

--
-- 資料表結構 `userinfo`
--

DROP TABLE IF EXISTS `userinfo`;
CREATE TABLE IF NOT EXISTS `userinfo` (
  `userID` varchar(255) NOT NULL,
  `ack` varchar(255) NOT NULL,
  `inheritCode` varchar(255) DEFAULT NULL,
  `inheritDate` datetime DEFAULT CURRENT_TIMESTAMP,
  `weekNotice` varchar(255) NOT NULL DEFAULT '0000000',
  `createDate` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`userID`) USING BTREE
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

--
-- 傾印資料表的資料 `userinfo`
--

INSERT INTO `userinfo` (`userID`, `ack`, `inheritCode`, `inheritDate`, `weekNotice`, `createDate`) VALUES
('5e364454048b8b039629a49a6e090795', '38f99de83c70a0bbef19310b8e6bf64c', '5705a93290377747adbbcc3820e1b0f6', '2022-04-11 00:53:27', '0011110', '2022-04-11 00:53:27');

-- --------------------------------------------------------

--
-- 資料表結構 `userlog`
--

DROP TABLE IF EXISTS `userlog`;
CREATE TABLE IF NOT EXISTS `userlog` (
  `logID` int(11) NOT NULL AUTO_INCREMENT,
  `userID` varchar(255) NOT NULL,
  `sportName` varchar(255) NOT NULL,
  `startdate` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `enddate` datetime DEFAULT NULL,
  PRIMARY KEY (`logID`,`userID`) USING BTREE,
  KEY `fk_userlog_userID` (`userID`),
  KEY `fk_userlog_sportName` (`sportName`)
) ENGINE=MyISAM AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;

--
-- 傾印資料表的資料 `userlog`
--

INSERT INTO `userlog` (`logID`, `userID`, `sportName`, `startdate`, `enddate`) VALUES
(1, '5e364454048b8b039629a49a6e090795', 'handlift', '2022-04-11 01:01:55', NULL);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
