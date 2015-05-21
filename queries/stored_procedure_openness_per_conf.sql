USE dblp;
DROP PROCEDURE IF EXISTS openness_conference_at_year;
DROP PROCEDURE IF EXISTS calculate_openness_conf;
DROP PROCEDURE IF EXISTS get_openness_conf;

DROP TABLE IF EXISTS _openness_conf;

CREATE TABLE _openness_conf (
	id int(11) primary key auto_increment,
	number_of_papers numeric(8),
	from_outsiders numeric(8),
	from_community numeric(8),
	new_authors numeric(8),
	perc_new_authors decimal(8,2),
	conf varchar(256),
	year numeric(4),
	index conf(conf),
	index year(year)
);

DELIMITER //
CREATE PROCEDURE openness_conference_at_year (IN year_x numeric(4), IN conf varchar(255))
BEGIN
	insert into _openness_conf
	select NULL, count(*) as papers,
	sum(if (num_of_previous_authors = 0, 1, 0)) as outsiders,
	sum(if (num_of_authors = num_of_previous_authors, 1, 0)) as from_community,
	x_authors - previous_authors as new_authors,
	truncate((((x_authors - previous_authors) / x_authors) * 100),2) as perc_new_authors,
	conf, year_x
    from (
        select paper_id, count(x_year.author_id) as num_of_authors, count(previous_years.author_id) as num_of_previous_authors, year
            from (
            select auth.id as paper_id, auth.author_id, year
            from dblp_pub_new pub
            join
            dblp_authorid_ref_new auth
            on pub.id = auth.id
            where type = 'inproceedings' and year = year_x and source = conf) as x_year
        left join
            (select auth.author_id
            from dblp_pub_new pub
            join
            dblp_authorid_ref_new auth
            on pub.id = auth.id
            where type = 'inproceedings' and year < year_x and source = conf
            group by auth.author_id) as previous_years
        on x_year.author_id = previous_years.author_id
    group by paper_id) as openness
    join
        (select count(distinct x_year.author_id) as x_authors, count(distinct previous_years.author_id) as previous_authors
           from (
            select auth.id as paper_id, auth.author_id, year
            from dblp_pub_new pub
            join
            dblp_authorid_ref_new auth
            on pub.id = auth.id
            where type = 'inproceedings' and year = year_x and source = conf) as x_year
        left join
            (select auth.author_id
            from dblp_pub_new pub
            join
            dblp_authorid_ref_new auth
            on pub.id = auth.id
            where type = 'inproceedings' and year < year_x and source = conf
            group by auth.author_id) as previous_years
        on x_year.author_id = previous_years.author_id) as authors_info
    on 1 = 1;

END //

CREATE PROCEDURE calculate_openness_conf(IN conf varchar(255))
BEGIN
	DECLARE exit_loop BOOLEAN;
	DECLARE _year NUMERIC(10);
	DECLARE year_cursor CURSOR FOR
									SELECT year
									FROM dblp_pub_new
									WHERE type = 'inproceedings' and source = conf
									GROUP BY year
									ORDER BY year;
	DECLARE CONTINUE HANDLER FOR NOT FOUND SET exit_loop = TRUE;

	OPEN year_cursor;

	_iterate: LOOP
		FETCH year_cursor INTO _year;

		IF exit_loop THEN
			CLOSE year_cursor;
			LEAVE _iterate;
		END IF;

		CALL openness_conference_at_year(_year, conf);

	END LOOP _iterate;

END //

CREATE PROCEDURE get_openness_conf(IN c varchar(255))
BEGIN
	DECLARE _rows INTEGER;

	SELECT count(*) INTO _rows
	FROM _openness_conf
	WHERE conf = c;

	IF _rows = 0 THEN
		CALL calculate_openness_conf(c);
	END IF;

	SELECT *
	FROM _openness_conf
	WHERE conf = c;


END //

DELIMITER ;