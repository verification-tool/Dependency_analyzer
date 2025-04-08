use sem6;
drop table if exists projects;

CREATE TABLE projects (
    project_id INT PRIMARY KEY,
    employee_id INT NOT NULL,
    duration INT NOT NULL,
    no_of_worker INT NOT NULL,
    cost INT NOT NULL
);

-- Insert sample projects covering all operation scenarios
INSERT INTO projects (project_id,employee_id, duration, no_of_worker, cost) VALUES
(101, 1, 12, 5, 4500),   
(102, 2, 24, 8, 4976),        
(103,  3, 6, 3, 2400),     
(104,1, 3, 10, 6500),       
(105, 2, 1, 2, 1500);