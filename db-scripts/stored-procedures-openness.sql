USE metascience;
DROP PROCEDURE IF EXISTS get_openness_information_for_edition;
DROP PROCEDURE IF EXISTS get_openness_information_for_conference;
DROP PROCEDURE IF EXISTS get_openness_information_for_all_conferences;

DROP TABLE IF EXISTS aux_conference_openness;
CREATE TABLE aux_conference_openness (
	total_papers bigint(20),
	papers_from_outsiders bigint(20),
	papers_from_community bigint(20),
	total_authors bigint(20),
	existing_authors bigint(20),
	new_authors bigint(20),
	year_edition numeric(4),
	time_interval numeric(2),
	conference_edition_id bigint(20),
	conference_id bigint(20),
	PRIMARY KEY pk (conference_id, year_edition, time_interval)
);

DELIMITER //

/* calculate the number of new authors, old ones and their sum for an edition of a given conference with respect to a time interval */
CREATE DEFINER=`root`@`localhost` PROCEDURE `get_openness_information_for_edition`(IN target_conference_id BIGINT(20), IN target_year NUMERIC(4), IN span NUMERIC(2))
BEGIN
	insert ignore into aux_conference_openness
	select 
papers.total_papers,
papers.from_outsiders,
papers.from_community,
researchers.*
from (
	select *
		from (
			select 
			count(author_edition_x) as total_authors,
			sum(if (author_edition_x = author_previous_y_editions, 1, 0)) as old_authors,
			sum(if (author_previous_y_editions is null, 1, 0)) as new_authors,
			edition,
			span as time_interval,
			conference_edition_id,
			conference_id
			from (
				select 
				unique_authors_edition_x.unique_author as author_edition_x, 
				unique_authors_previous_y_editions.unique_author as author_previous_y_editions, 
				unique_authors_edition_x.year as edition,
				span as time_interval,
				unique_authors_edition_x.conference_edition_id,
				unique_authors_edition_x.conference_id
				from (
					/* unique authors for edition X */
					select ce.conference_id, ce.id as conference_edition_id, ce.year, a.researcher_id as unique_author
					from 
						conference_edition ce join paper p on ce.id = p.published_in 
						join authorship a on a.paper_id = p.id
					where ce.year = target_year and ce.conference_id = target_conference_id
					group by a.researcher_id) as unique_authors_edition_x
				left join
					(
					/* unique authors for editions [X-Y,X) */
					select a.researcher_id as unique_author
					from 
						conference_edition ce join paper p on ce.id = p.published_in 
						join authorship a on a.paper_id = p.id
					where ce.conference_id = target_conference_id and ce.year >= (target_year-span) and ce.year < target_year
					group by a.researcher_id) as unique_authors_previous_y_editions
				on unique_authors_edition_x.unique_author = unique_authors_previous_y_editions.unique_author) as info_edition_x) as all_editions
		where conference_id is not null) as researchers
join
(select
	count(*) as total_papers,
	sum(if (num_of_previous_authors = 0, 1, 0)) as from_outsiders,
	sum(if (num_of_authors = num_of_previous_authors, 1, 0)) as from_community,
	conference_id, conference_edition_id, year
	from (
		select 
		paper_id, target_edition.conference_id, target_edition.conference_edition_id, target_edition.year,
		count(target_edition.researcher_id) as num_of_authors, 
		count(previous_x_editions.researcher_id) as num_of_previous_authors
		from (
			/* papers and authors for editions X */
			select paper_id, researcher_id, year, conference_id, ce.id as conference_edition_id
			from authorship a join paper p on a.paper_id = p.id
			join conference_edition ce on ce.id = p.published_in
			where ce.conference_id = target_conference_id and year = target_year) as target_edition
		left join
			/* unique authors for editions [X-Y,X) */
			(select a.researcher_id, conference_id, ce.id as conference_edition_id
			from 
				conference_edition ce join paper p on ce.id = p.published_in 
				join authorship a on a.paper_id = p.id
			where ce.conference_id = target_conference_id and ce.year >= (target_year-span) and ce.year < target_year
			group by a.researcher_id) as previous_x_editions
		on target_edition.researcher_id = previous_x_editions.researcher_id
		group by paper_id) as info_edition_x) as papers
on papers.conference_edition_id = researchers.conference_edition_id;
END //

CREATE DEFINER=`root`@`localhost` PROCEDURE `get_openness_information_for_conference`(IN target_conference_id BIGINT(20), IN span NUMERIC(2))
BEGIN
	DECLARE exit_loop BOOLEAN;
	DECLARE current_year NUMERIC(10);
	DECLARE year_cursor CURSOR FOR
									SELECT year
									FROM conference_edition
									WHERE conference_id = target_conference_id
									ORDER BY year ASC;
	DECLARE CONTINUE HANDLER FOR NOT FOUND SET exit_loop = TRUE;

	OPEN year_cursor;

	_iterate: LOOP
		FETCH year_cursor INTO current_year;

		IF exit_loop THEN
			CLOSE year_cursor;
			LEAVE _iterate;
		END IF;
		

		CALL get_openness_information_for_edition(target_conference_id, current_year, span);

	END LOOP _iterate;

END //

CREATE DEFINER=`root`@`localhost` PROCEDURE `get_openness_information_for_all_conferences`(IN span NUMERIC(2))
BEGIN
	DECLARE exit_loop BOOLEAN;
	DECLARE current_conference BIGINT(20);
	DECLARE cur CURSOR FOR 	
							SELECT id
							FROM conference;
	DECLARE CONTINUE HANDLER FOR NOT FOUND SET exit_loop = TRUE;

	OPEN cur;

	_iterate: LOOP
		FETCH cur INTO current_conference;

		IF exit_loop THEN
			CLOSE cur;
			LEAVE _iterate;
		END IF;
		

		CALL get_openness_information_for_conference(current_conference, span);

	END LOOP _iterate;

END //