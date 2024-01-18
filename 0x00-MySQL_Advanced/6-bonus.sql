-- script that creates a stored procedure AddBonus that adds a new correction for a student.
DROP PROCEDURE IF EXISTS AddBonus;
DELIMITER $$
CREATE PROCEDURE AddBonus(
    IN user_id INT, 
    IN project_name VARCHAR(255), 
    IN score FLOAT)
BEGIN
    DECLARE project_id INT;

    -- Use INSERT IGNORE to handle the case where the project already exists
    INSERT IGNORE INTO projects (name) VALUES (project_name);

    SET project_id = (SELECT id FROM projects WHERE name = project_name LIMIT 1);
    INSERT INTO corrections (user_id, project_id, score) VALUES(user_id, project_id, score);
END
$$
DELIMITER ;
