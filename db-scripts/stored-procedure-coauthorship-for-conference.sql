DELIMITER //

CREATE DEFINER=`root`@`localhost` PROCEDURE `get_coauthorship_information_for_conference`(IN conf_id BIGINT(20))
BEGIN
	SELECT conference_id, source_label, source_id, target_label, target_id, connection_strength
	FROM (
		SELECT 
			conference_id, 
			source_label, source_id, 
			target_label, target_id,
			CONCAT(GREATEST(source_id, target_id), '-', LEAST(source_id, target_id)) AS connection_id,
			COUNT(*) AS connection_strength
		FROM (
			SELECT conference_id, r1.name as source_label, source.researcher_id as source_id, target.researcher_id as target_id, r2.name as target_label
			FROM authorship source JOIN paper p ON p.id = source.paper_id JOIN conference_edition ce ON ce.id = p.published_in
			JOIN authorship target ON source.paper_id = target.paper_id AND source.researcher_id <> target.researcher_id
			JOIN researcher r1 ON source.researcher_id = r1.id JOIN researcher r2 ON target.researcher_id = r2.id
			WHERE conference_id = conf_id) AS connections
		GROUP BY source_id, target_id) AS result
	GROUP BY connection_id
	ORDER BY connection_strength DESC;
END //