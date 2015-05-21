USE dblp;
DROP PROCEDURE IF EXISTS fill_pc_coauthored_papers_rate_table;
DROP PROCEDURE IF EXISTS insert_pc_coauthored_papers_rate_for_conf;

DROP TABLE IF EXISTS _pc_coauthored_papers_rate;

DELIMITER //
CREATE PROCEDURE fill_pc_coauthored_papers_rate_table(IN dblp_source varchar(256), IN conference_name varchar(256))
BEGIN
	DECLARE not_found BOOLEAN;
	DECLARE _exists_table VARCHAR(256);
	DECLARE _exists_entry VARCHAR(256);
	DECLARE _cursor CURSOR FOR
								SELECT TABLE_NAME 
								FROM information_schema.tables 
								WHERE TABLE_NAME = "_pc_coauthored_papers_rate";	
	DECLARE _cursor_table CURSOR FOR
								SELECT conf
								FROM _pc_coauthored_papers_rate
								WHERE conf = dblp_source; 
	DECLARE CONTINUE HANDLER FOR NOT FOUND SET not_found = TRUE;
	OPEN _cursor;
	FETCH _cursor INTO _exists_table;
	IF (not_found) THEN
		CLOSE _cursor;
		CREATE TABLE _pc_coauthored_papers_rate (num_of_papers NUMERIC(11), 
												num_of_coauthored_papers_pc_members NUMERIC(11), 
												perc_of_coauthored_papers_pc_members DECIMAL(5,2),
												perc_of_no_coauthored_papers_pc_members DECIMAL(5,2),
												pub_year NUMERIC(11),
												conf VARCHAR(256));
		CALL insert_pc_coauthored_papers_rate_for_conf(dblp_source, conference_name);
	ELSE 
		CLOSE _cursor;
		
		OPEN _cursor_table;
		FETCH _cursor_table INTO _exists_entry;
		IF (not_found) THEN
			CALL insert_pc_coauthored_papers_rate_for_conf(dblp_source, conference_name);
		END IF;
	END IF;
END //

CREATE PROCEDURE insert_pc_coauthored_papers_rate_for_conf(IN dblp_source varchar(256), IN conference_name varchar(256))
BEGIN
	INSERT _pc_coauthored_papers_rate
	SELECT num_of_papers, num_of_coauthored_papers_pc_members, 
	round((num_of_coauthored_papers_pc_members/num_of_papers) * 100, 2) as perc_of_coauthored_papers_pc_members, 
	round(((num_of_papers - num_of_coauthored_papers_pc_members)/num_of_papers) * 100, 2) as perc_of_no_coauthored_papers_pc_members, 
	pub_year,
	source
	FROM 
	(SELECT count(*) as num_of_papers, year, source
	FROM dblp_pub_new pub
	WHERE source = dblp_source and type = 'inproceedings'
	group by year) as total_papers
	JOIN
	(SELECT count(distinct paper_id) as num_of_coauthored_papers_pc_members, pub_year
	FROM
	(SELECT pub.id as paper_id, title, author_id, pub.year as pub_year 
	FROM dblp_pub_new pub
	JOIN dblp_authorid_ref_new auth
	ON pub.id = auth.id
	WHERE pub.source = dblp_source and pub.type = 'inproceedings') as authors
	JOIN
	(
	SELECT name, dblp_author_id, year as pc_member_year 
	FROM aux_program_committee 
	WHERE conference = conference_name AND dblp_author_id <> -1) as pc_members
	ON authors.author_id = pc_members.dblp_author_id
	WHERE pc_member_year = pub_year
	group by pub_year) as coauthored_papers
	ON total_papers.year = coauthored_papers.pub_year;
END //


DELIMITER ;