CREATE DATABASE IF NOT EXISTS sem6;
USE sem6;

DROP TABLE IF EXISTS editorials;

-- Create editorials table
CREATE TABLE editorials (
    article_id INT PRIMARY KEY AUTO_INCREMENT,
    article_title VARCHAR(200) NOT NULL,
    article_desc TEXT,
    editorials_cat_id INT NOT NULL,
    item_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert sample data for dependency demonstration
INSERT INTO editorials (article_title, editorials_cat_id, item_id) VALUES
('Breaking News', 1, 101),       -- Will be deleted (cat_id <= 2)
('Tech Review', 2, 102),         -- Will be deleted (cat_id <= 2)
('Industry Report', 5, 103),     -- Will be updated (cat_id >=5)
('Market Analysis', 5, 101),     -- Will be updated (cat_id >=5)
('Product Launch', 6, 102),      -- Will be updated (cat_id >=5)
('Case Study', 3, 103),          -- Unaffected
('White Paper', 4, 101),         -- Unaffected
('Research Brief', 1, 102),      -- Will be deleted (cat_id <=2)
('Trend Forecast', 5, 103),      -- Will be updated (cat_id >=5)
('Annual Review', 2, 101);       -- Will be deleted (cat_id <=2)