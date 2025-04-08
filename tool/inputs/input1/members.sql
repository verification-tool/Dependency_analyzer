use sem6;
drop table if exists members;
drop table if exists audit_log;
-- Create members table
CREATE TABLE members (
    id INT PRIMARY KEY AUTO_INCREMENT,
    phno_day INT,
    mem_age INT
);

-- Insert sample data for dependency triggers
INSERT INTO members (phno_day, mem_age) VALUES
(105, 60),   -- Will be updated by stmt1 (+2) and deleted by stmt4
(85, 55),    -- Will be updated by stmt3 (+1) and deleted by stmt8
(95, 62),    -- Will be updated by stmt1/stmt3 and deleted by stmt4
(72, 58),    -- Will trigger INSERT in stmt5 and deleted by stmt8
(65, 50),    -- Will be updated by stmt6 (+1 mem_age)
(115, 60),   -- Will be updated by stmt1 (+2)
(78, 59);    -- Will be deleted by stmt8

-- Create audit_log table for INSERT...SELECT example
CREATE TABLE audit_log (
    log_id INT PRIMARY KEY AUTO_INCREMENT,
    message VARCHAR(255)
);