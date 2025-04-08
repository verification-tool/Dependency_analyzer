use sem6;
drop table if exists bugs;

CREATE TABLE bugs (
    project_id INT NOT NULL,
    priority_id INT NOT NULL,
    no_of_bugs INT NOT NULL,
    assigned_to INT
);

INSERT INTO bugs (project_id, priority_id,  no_of_bugs, assigned_to) VALUES
(1, 1, 40, , 101),
(2, 3, 25,  102),
(3, 2, 35, 103);