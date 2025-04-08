-- database_setup.sql
CREATE DATABASE IF NOT EXISTS sem6;
USE sem6;

DROP TABLE IF EXISTS deps;

CREATE TABLE deps (
    depid INT PRIMARY KEY,
    no_of_emp INT NOT NULL,
    max_capacity INT NOT NULL
);

-- Insert sample data with multiple attributes
INSERT INTO deps (depid, no_of_emp, max_capacity) VALUES
(1001, 10, 15),   -- Will be affected by capacity update rules
(1002, 8, 10),    -- Meets max_capacity - no_of_emp = 2 threshold
(1003, 5, 5),     -- At full capacity
(1004, 0, 3),     -- Candidate for deletion (max_capacity < 5)
(1005, 12, 15),   -- Will trigger multi-column update
(1006, 3, 20),    -- Meets SELECT criteria (capacity > 20, employees < 10)
(1007, 7, 25),    -- Valid for complex queries
(1008, 15, 18),   -- Will be reset by no_of_emp = 0 update
(1009, 2, 5),     -- Borderline case for capacity rules
(1010, 0, 4);  