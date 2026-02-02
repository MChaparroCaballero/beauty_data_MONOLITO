-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Servidor: 127.0.0.1
-- Tiempo de generación: 13-01-2026 a las 13:42:03
-- Versión del servidor: 10.4.32-MariaDB
-- Versión de PHP: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";

CREATE USER IF NOT EXISTS 'beauty_data'@'localhost' IDENTIFIED BY 'beauty_data';
GRANT ALL PRIVILEGES ON beauty_data.* TO 'beauty_data'@'localhost';
FLUSH PRIVILEGES;

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de datos: `beauty_data`
--
DROP DATABASE IF EXISTS beauty_data;
CREATE DATABASE  beauty_data;
USE beauty_data;
-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `productos`
--

CREATE TABLE IF NOT EXISTS `productos` (
  `cod` int(11) NOT NULL,
  `nombre` varchar(200) DEFAULT NULL,
  `categoria` varchar(200) DEFAULT NULL,
  `descripcion` varchar(200) DEFAULT NULL,
  `precio_de_compra` decimal(10,2) DEFAULT 0.00,
  `precio_de_venta` decimal(10,2) DEFAULT 0.00,
  `stock` int(11) DEFAULT 0,
  `proveedor` varchar(200) DEFAULT NULL,
  `estado` varchar(20) DEFAULT 'Activo'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `productos`
--
ALTER TABLE `productos`
  ADD PRIMARY KEY (`cod`);

--
-- AUTO_INCREMENT de las tablas volcadas
--

--
-- AUTO_INCREMENT de la tabla `productos`
--
ALTER TABLE `productos`
  MODIFY `cod` int(11) NOT NULL AUTO_INCREMENT;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;

-- Insertar productos de ejemplo
INSERT INTO `productos` (`nombre`, `categoria`, `descripcion`, `precio_de_compra`, `precio_de_venta`, `stock`, `proveedor`, `estado`) 
VALUES 
('Base de Maquillaje Matte Fit', 'Rostro', 'Base de larga duración, acabado mate, 30ml.', 8.50, 15.99, 50, 'Cosméticos Global S.A.', 'Activo'),

('Labial Líquido Red Velvet', 'Labios', 'Labial indeleble de alta pigmentación, color rojo intenso.', 4.20, 12.00, 30, 'Beauty Supply Co.', 'Activo'),

('Máscara de Pestañas Volumen Extremo', 'Ojos', 'Resistente al agua, color negro profundo.', 5.75, 10.50, 0, 'Distribuidora Estilo', 'Agotado'),

('Paleta de Sombras Nude', 'Ojos', '12 tonos neutros entre mates y brillantes.', 12.00, 25.00, 15, 'Cosméticos Global S.A.', 'Activo'),

('Corrector de Ojeras Light', 'Rostro', 'Cobertura completa con hidratación.', 3.90, 8.50, 25, 'Beauty Supply Co.', 'Activo');
