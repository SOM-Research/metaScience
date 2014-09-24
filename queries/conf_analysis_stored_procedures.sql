USE dblp;
DROP PROCEDURE IF EXISTS perished_survived_authors_between_two_conf_editions;
DROP PROCEDURE IF EXISTS calculate_perished_survived_authors_in_conf;
DROP PROCEDURE IF EXISTS calculate_perished_survived_authors;
DROP PROCEDURE IF EXISTS get_perished_survived_authors;
DROP FUNCTION IF EXISTS calculate_num_of_pages;
DROP FUNCTION IF EXISTS fill_pc_coauthored_papers_rate_table;
DROP FUNCTION IF EXISTS insert_pc_coauthored_papers_rate_for_conf;
/*
DROP TABLE IF EXISTS _perished_survived_authors_per_conf;
DROP TABLE IF EXISTS _pc_coauthored_papers_rate;
*/
CREATE TABLE _perished_survived_authors_per_conf (
	id int(11) primary key auto_increment,
	author numeric(8),
	author_name varchar(70),
	status varchar(10),
	conf varchar(256),
	period varchar(10),
	index conf (conf),
	index period (period)
);
DELIMITER //
CREATE PROCEDURE perished_survived_authors_between_two_conf_editions (IN year_x numeric(4), IN year_x_plus_1 numeric(4), IN conf varchar(255)) 
BEGIN
	insert into _perished_survived_authors_per_conf
	select NULL, author_x_year as author, author_name, if(author_x_plus_1_year IS NULL,'perished', 'survived') as status, conf as conf, CONCAT(year_x, '-', year_x_plus_1) as period
	from 
	(select auth.author_id as author_x_year, author as author_name
		from dblp_pub_new pub
		join
		dblp_authorid_ref_new auth
		on pub.id = auth.id
		where type = 'inproceedings' and year = year_x and source = conf
		group by author_id
	) as authors_year_x
	left join
	(select auth.author_id as author_x_plus_1_year
		from dblp_pub_new pub
		join
		dblp_authorid_ref_new auth
		on pub.id = auth.id
		where type = 'inproceedings' and year = year_x_plus_1 and source = conf
		group by author_id
	) as authors_year_x_plus_1
	on author_x_year = author_x_plus_1_year;

END //

CREATE PROCEDURE calculate_perished_survived_authors_in_conf(IN conf varchar(255))
BEGIN
	DECLARE exit_loop BOOLEAN; 
	DECLARE _year NUMERIC(10);
	DECLARE year_plus_1 NUMERIC(10);
	DECLARE year_cursor CURSOR FOR 
									SELECT year
									FROM dblp_pub_new 
									WHERE type = 'inproceedings' and source = conf
									GROUP BY year
									ORDER BY year;
	DECLARE CONTINUE HANDLER FOR NOT FOUND SET exit_loop = TRUE;
	
	OPEN year_cursor;

	FETCH year_cursor INTO _year;
	get_pair_years: LOOP
		IF (SELECT year_plus_1 IS NOT NULL) THEN
			SET _year = year_plus_1;
		END IF;

		
		FETCH year_cursor INTO year_plus_1;
		CALL perished_survived_authors_between_two_conf_editions(_year, year_plus_1, conf);

		IF exit_loop THEN
			CLOSE year_cursor;
			LEAVE get_pair_years;
		END IF;
		
	
	END LOOP get_pair_years;

END //

CREATE PROCEDURE get_perished_survived_authors(IN c varchar(255))
BEGIN
	DECLARE perished_survived_number_of_rows INTEGER;

	SELECT count(*) INTO perished_survived_number_of_rows
	FROM _perished_survived_authors_per_conf
	WHERE conf = c;

	IF perished_survived_number_of_rows = 0 THEN
		CALL calculate_perished_survived_authors_in_conf(c);
	END IF;

	SELECT *
	FROM _perished_survived_authors_per_conf
	WHERE conf = c;
	

END //

CREATE PROCEDURE calculate_perished_survived_authors()
BEGIN
	DECLARE exit_loop BOOLEAN;
	DECLARE var_source VARCHAR(255);
	DECLARE source_cursor CURSOR FOR 
									SELECT source
									FROM dblp_pub_new 
									WHERE type = 'inproceedings'
									GROUP BY source;
	DECLARE CONTINUE HANDLER FOR NOT FOUND SET exit_loop = TRUE;

	OPEN source_cursor;
	FETCH source_cursor INTO var_source;
	get_source: LOOP

		CALL calculate_perished_survived_authors_in_conf(var_source);
		
		IF (exit_loop) THEN
			CLOSE source_cursor;
			LEAVE get_source;
		END IF;
	END LOOP get_source;
END //


CREATE FUNCTION calculate_num_of_pages(pages varchar(100)) RETURNS INTEGER 
	DETERMINISTIC
BEGIN
	DECLARE page_number INTEGER;
	DECLARE occ_dash INTEGER DEFAULT (LENGTH(pages) - LENGTH(REPLACE(pages, '-', '')));
	DECLARE left_part INTEGER DEFAULT CONVERT(SUBSTRING_INDEX(pages, '-', 1), SIGNED INTEGER);
	DECLARE right_part INTEGER DEFAULT CONVERT(SUBSTRING_INDEX(pages, '-', -1), SIGNED INTEGER);

	IF occ_dash > 1 OR left_part = 0 OR right_part = 0 THEN
		SET page_number = 1;
	ELSE
		IF right_part > left_part THEN
			SET page_number = right_part - left_part;
		ELSE
			SET page_number = left_part - right_part;
		END IF;

        IF page_number = 0 THEN
			SET page_number = 1;
		END IF;
	END IF;

	RETURN page_number;

END //

CREATE PROCEDURE fill_pc_coauthored_papers_rate_table(IN dblp_source varchar(256), IN conference_name varchar(256))
BEGIN
	DECLARE exit_loop BOOLEAN;
	DECLARE _exists VARCHAR(256);
	DECLARE _cursor CURSOR FOR
								SELECT TABLE_NAME 
								FROM information_schema.tables 
								WHERE TABLE_NAME = "_pc_coauthored_papers_rate";
	DECLARE CONTINUE HANDLER FOR NOT FOUND SET exit_loop = TRUE;
	OPEN _cursor;
	FETCH _cursor INTO _exists;
	IF (exit_loop) THEN
		CLOSE _cursor;
		CREATE TABLE _pc_coauthored_papers_rate (num_of_papers NUMERIC(11), 
												num_of_coauthored_papers_pc_members NUMERIC(11), 
												perc_of_coauthored_papers_pc_members DECIMAL(5,2),
												perc_of_no_coauthored_papers_pc_members DECIMAL(5,2),
												pub_year NUMERIC(11),
												conf VARCHAR(256),
												primary key (pub_year, conf));
		CALL insert_pc_coauthored_papers_rate_for_conf(dblp_source, conference_name);
	ELSE 
		CLOSE _cursor;
		CALL insert_pc_coauthored_papers_rate_for_conf(dblp_source, conference_name);
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
	(SELECT count(paper_id) as num_of_coauthored_papers_pc_members, pub_year
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