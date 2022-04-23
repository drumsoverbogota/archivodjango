-- phpMyAdmin SQL Dump
-- version 4.9.5deb2
-- https://www.phpmyadmin.net/
--
-- Host: localhost:3306
-- Generation Time: Aug 18, 2021 at 10:23 PM
-- Server version: 8.0.26-0ubuntu0.20.04.2
-- PHP Version: 7.4.3

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `archivopunk`
--

-- --------------------------------------------------------

--
-- Table structure for table `banda`
--

CREATE TABLE `banda` (
  `id` int NOT NULL,
  `nombre` varchar(100) NOT NULL,
  `nombrecorto` varchar(30) NOT NULL,
  `otros` text NOT NULL,
  `integrantes` text,
  `comentarios` text,
  `imagen` text,
  `imagen_thumbnail` text CHARACTER SET utf8 COLLATE utf8_general_ci,
  `extranjera` tinyint(1) NOT NULL,
  `fecha_creacion` datetime DEFAULT NULL,
  `fecha_modificacion` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;

-- --------------------------------------------------------

--
-- Table structure for table `banda_lanzamiento`
--

CREATE TABLE `banda_lanzamiento` (
  `id` int NOT NULL,
  `banda_id` int NOT NULL,
  `lanzamiento_id` int NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;

-- --------------------------------------------------------

--
-- Table structure for table `entrada`
--

CREATE TABLE `entrada` (
  `id` int NOT NULL,
  `titulo` varchar(100) NOT NULL,
  `contenido` text NOT NULL,
  `resumen` text NOT NULL,
  `tipo` varchar(10) NOT NULL DEFAULT '0',
  `fecha` date NOT NULL
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `lanzamiento`
--

CREATE TABLE `lanzamiento` (
  `id` int NOT NULL,
  `nombre` text NOT NULL,
  `nombrecorto` varchar(30) NOT NULL,
  `referencia` text,
  `formato` enum('CD','Digipack','12"','10"','7"','Flexi','Cassette','Digital','Mini CD','DVD','Otros','Bootleg') DEFAULT NULL,
  `anho` text,
  `tracklist` text NOT NULL,
  `creditos` text,
  `notas` text,
  `link` text,
  `link_youtube` text,
  `indice_referencia` text,
  `imagen` text,
  `imagen_thumbnail` text CHARACTER SET utf8 COLLATE utf8_general_ci,
  `fecha_creacion` datetime DEFAULT NULL,
  `fecha_modificacion` datetime DEFAULT NULL,
  `visible` tinyint(1) NOT NULL DEFAULT '1',
  `disponible` tinyint(1) NOT NULL DEFAULT '1'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;

-- --------------------------------------------------------

--
-- Table structure for table `publicacion`
--

CREATE TABLE `publicacion` (
  `id` int NOT NULL,
  `nombre` text NOT NULL,
  `nombrecorto` varchar(30) NOT NULL,
  `fecha` text,
  `numero` int DEFAULT NULL,
  `notas` text,
  `link` text,
  `indice_referencia` text,
  `imagen` text,
  `imagen_thumbnail` text CHARACTER SET utf8 COLLATE utf8_general_ci,
  `fecha_creacion` datetime DEFAULT NULL,
  `fecha_modificacion` datetime DEFAULT NULL,
  `visible` tinyint(1) NOT NULL DEFAULT '1'
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb3;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `banda`
--
ALTER TABLE `banda`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `nombrecorto` (`nombrecorto`);

--
-- Indexes for table `banda_lanzamiento`
--
ALTER TABLE `banda_lanzamiento`
  ADD PRIMARY KEY (`id`),
  ADD KEY `banda_lanzamiento_ibfk_1` (`banda_id`),
  ADD KEY `lanzamiento_id` (`lanzamiento_id`);

--
-- Indexes for table `entrada`
--
ALTER TABLE `entrada`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `lanzamiento`
--
ALTER TABLE `lanzamiento`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `nombrecorto` (`nombrecorto`);

--
-- Indexes for table `publicacion`
--
ALTER TABLE `publicacion`
  ADD PRIMARY KEY (`id`),
  ADD KEY `nombrecorto` (`nombrecorto`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `banda`
--
ALTER TABLE `banda`
  MODIFY `id` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `banda_lanzamiento`
--
ALTER TABLE `banda_lanzamiento`
  MODIFY `id` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `entrada`
--
ALTER TABLE `entrada`
  MODIFY `id` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `lanzamiento`
--
ALTER TABLE `lanzamiento`
  MODIFY `id` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `publicacion`
--
ALTER TABLE `publicacion`
  MODIFY `id` int NOT NULL AUTO_INCREMENT;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `banda_lanzamiento`
--
ALTER TABLE `banda_lanzamiento`
  ADD CONSTRAINT `banda_lanzamiento_ibfk_1` FOREIGN KEY (`banda_id`) REFERENCES `banda` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `banda_lanzamiento_ibfk_2` FOREIGN KEY (`lanzamiento_id`) REFERENCES `lanzamiento` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;

--- Añadidos después de la migración

ALTER TABLE `lanzamiento` ADD `portadas` TINYINT(1) NOT NULL DEFAULT '1' AFTER `disponible`, ADD `disco_digitalizado` TINYINT(1) NOT NULL DEFAULT '1' AFTER `portadas`;

ALTER TABLE `lanzamiento` ADD `nota_digitalizacion` text NOT NULL AFTER `disco_digitalizado`;

ALTER TABLE `lanzamiento` ADD `lanzamiento` TINYINT(1) NOT NULL DEFAULT '1' AFTER `fecha_modificacion`; 

-- --------------------------------------------------------

--
-- Table structure for table `conciertos`
--

CREATE TABLE `conciertos` (
  `id` int NOT NULL,
  `nombre` text NOT NULL,
  `nombrecorto` varchar(30) NOT NULL,
  `fecha_grabacion` date,
  `notas` text,
  `link` text,
  `imagen` text,
  `imagen_thumbnail` text,
  `fecha_creacion` datetime DEFAULT NULL,
  `fecha_modificacion` datetime DEFAULT NULL,
  `visible` tinyint NOT NULL DEFAULT '1'
) ENGINE=MyISAM DEFAULT CHARSET=UTF8MB4;

ALTER TABLE `conciertos`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `nombrecorto` (`nombrecorto`);

  ALTER TABLE `conciertos`
  MODIFY `id` int NOT NULL AUTO_INCREMENT;