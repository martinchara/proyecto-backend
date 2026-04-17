DROP DATABASE IF EXISTS prode_mundial;
CREATE DATABASE prode_mundial;
USE prode_mundial;

CREATE TABLE partidos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    equipo_local VARCHAR(100) NOT NULL,
    equipo_visitante VARCHAR(100) NOT NULL,
    fecha DATETIME NOT NULL,
    fase ENUM('grupos', 'dieciseisavos', 'octavos', 'cuartos', 'semis', 'final') NOT NULL,
    goles_local INT DEFAULT NULL,
    goles_visitante INT DEFAULT NULL
);
