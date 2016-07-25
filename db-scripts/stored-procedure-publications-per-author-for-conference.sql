DELIMITER //

CREATE DEFINER=`root`@`localhost` PROCEDURE `get_publications_per_author_for_conference`(IN conf_id BIGINT(20))
BEGIN
	SELECT conference_id, a.researcher_id as id, r.name as label, COUNT(a.paper_id) as pub_count
	FROM authorship a JOIN paper p ON a.paper_id = p.id JOIN conference_edition ce ON ce.id = p.published_in
	JOIN researcher r ON r.id = a.researcher_id
	WHERE ce.conference_id = conf_id
	GROUP BY a.researcher_id
	ORDER BY pub_count DESC;
END //