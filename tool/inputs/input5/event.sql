-- database_setup.sql
CREATE DATABASE IF NOT EXISTS sem6;
USE sem6;

DROP TABLE IF EXISTS events;

-- Create events table
CREATE TABLE events (
    no_of_days INT NOT NULL,
    no_of_presenters INT NOT NULL
);

-- Insert sample data
INSERT INTO events (no_of_days, no_of_presenters) VALUES
( 3, 25),
( 2, 12),
( 5, 8),
( 4, 3),
( 3, 18),
( 2, 22);

-- Sample data explanation:
-- 2 events with presenters >=20 (25,22) - will get +1 day
-- 3 events with presenters <=14 (12,8,3) - will get -1 day
-- 1 event with presenters <=4 (3) - will be deleted
-- Final SELECT will show all remaining events with presenters >=1