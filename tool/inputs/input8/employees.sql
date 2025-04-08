use sem6;
drop table if exists employees;

CREATE TABLE employees (
    emp_id INT PRIMARY KEY,
    performance_rate INT NOT NULL,
    work_experience INT NOT NULL,
    security_level INT
);

INSERT INTO employees (emp_id, performance_rate, work_experience,security_level) VALUES
(101, 85, 5 , 1),    -- performance+exp=90 (security_level+1)
(102,35, 6 ,3), -- performance+exp=41 (no change)
(103, 30, 2,1),   -- performance+exp=32 (security_level-1)
(104,5, 1,3); -- performance_rate=5 (will be deleted)