-- script that creates a stored procedure ComputeAverageScoreForUser that computes and stores the average score for a student
DROP PROCEDURE IF EXISTS ComputeAverageScoreForUser;
DELIMITER $$
CREATE PROCEDURE ComputeAverageScoreForUser(
    IN user_id INT)
BEGIN
    DECLARE avg_score FLOAT;
    
    -- Use IFNULL to handle the case where there are no corrections for the user
    SELECT IFNULL(AVG(score), 0) INTO avg_score FROM corrections WHERE user_id = user_id;
    
    UPDATE users SET average_score = avg_score WHERE id = user_id;
END
$$
DELIMITER ;
