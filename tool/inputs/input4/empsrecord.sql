-- database_setup.sql
CREATE DATABASE IF NOT EXISTS sem6;
USE sem6;

DROP TABLE IF EXISTS emps;

CREATE TABLE emps (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50),
    depid INT,
    age INT,
    basic DECIMAL(10,2),
    da DECIMAL(10,2),
    hra DECIMAL(10,2),
    com DECIMAL(10,2)
);

INSERT INTO emps (name, depid, age, basic, da, hra, com) VALUES
('John', 4, 60, 18000.00, 2000.00, 3000.00, 500.00),
('Jane', 3, 62, 22000.00, 2500.00, 3500.00, 600.00),
('Bob', 5, 58, 15000.00, 1800.00, 2500.00, 400.00),
('Alice', 2, 61, 21000.00, 2200.00, 3200.00, 550.00),
('Sarah', 4, 59, 19000.00, 2100.00, 3100.00, 600.00),
('Mike', 3, 63, 24000.00, 2600.00, 3600.00, 700.00),
('Emily', 5, 58, 17000.00, 1900.00, 2700.00, 450.00),
('Dave', 6, 61, 19500.00, 2000.00, 2900.00, 500.00),
('Lisa', 2, 60, 20500.00, 2200.00, 3300.00, 580.00),
('Overlap1', 4, 61, 25000, 3000, 4000, 800), 
('Overlap2', 3, 60, 22000, 2500, 3500, 700);