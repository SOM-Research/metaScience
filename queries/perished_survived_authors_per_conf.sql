USE dblp;
DROP PROCEDURE IF EXISTS perished_survived_authors_between_two_conf_editions;
DROP PROCEDURE IF EXISTS calculate_perished_survived_authors_in_conf;
DROP PROCEDURE IF EXISTS calculate_perished_survived_authors;
DROP PROCEDURE IF EXISTS get_perished_survived_authors;

DROP TABLE IF EXISTS _perished_survived_authors_per_conf;

CREATE TABLE _perished_survived_authors_per_conf (
	id int(11) primary key auto_increment,
	author numeric(8),
	author_name varchar(70),
	status varchar(10),
	conf varchar(256),
	period varchar(10),
	span numeric(2),
	index conf (conf),
	index period (period)
);

DELIMITER //
CREATE PROCEDURE perished_survived_authors_between_two_conf_editions (IN year_x numeric(4), IN year_y numeric(4), IN conf varchar(255), IN span numeric(2))
BEGIN
	insert into _perished_survived_authors_per_conf
	select NULL, author_x_year as author, author_name, if(author_y_year IS NULL,'perished', 'survived') as status, conf as conf, CONCAT(year_x, '-', year_y) as period, span
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
	(select auth.author_id as author_y_year
		from dblp_pub_new pub
		join
		dblp_authorid_ref_new auth
		on pub.id = auth.id
		where type = 'inproceedings' and year > year_x and year <= year_y and source = conf
		group by author_id
	) as authors_year_y
	on author_x_year = author_y_year;

END //

CREATE PROCEDURE calculate_perished_survived_authors_in_conf(IN conf varchar(255), IN _range NUMERIC(2))
BEGIN
	DECLARE exit_loop BOOLEAN;
	DECLARE _year NUMERIC(10);
	DECLARE year_plus_range NUMERIC(10);
	DECLARE advanced_year NUMERIC(10);
	DECLARE to_advance NUMERIC(2) DEFAULT _range;
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
		IF (SELECT year_plus_range IS NOT NULL) THEN
			SET _year = year_plus_range;
		END IF;

		advance: LOOP
		    IF to_advance > 0 THEN
		        SET to_advance = to_advance - 1;
		        FETCH year_cursor INTO advanced_year;
		        SET year_plus_range = advanced_year;
            ELSE
				LEAVE advance;
            END IF;

		END LOOP advance;

		IF exit_loop THEN
			CLOSE year_cursor;
			LEAVE get_pair_years;
		END IF;

		CALL perished_survived_authors_between_two_conf_editions(_year, year_plus_range, conf, _range);
		SET to_advance = _range;

	END LOOP get_pair_years;

END //

CREATE PROCEDURE get_perished_survived_authors(IN c varchar(255), IN _r NUMERIC(2))
BEGIN
	DECLARE perished_survived_number_of_rows INTEGER;

	SELECT count(*) INTO perished_survived_number_of_rows
	FROM _perished_survived_authors_per_conf
	WHERE conf = c and span = _r;

	IF perished_survived_number_of_rows = 0 THEN
		CALL calculate_perished_survived_authors_in_conf(c, _r);
	END IF;

	SELECT *
	FROM _perished_survived_authors_per_conf
	WHERE conf = c AND span = _r;


END //

CREATE PROCEDURE calculate_perished_survived_authors(IN _range NUMERIC(2))
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

		CALL calculate_perished_survived_authors_in_conf(var_source, _range);

		IF (exit_loop) THEN
			CLOSE source_cursor;
			LEAVE get_source;
		END IF;
	END LOOP get_source;
END //

DELIMITER ;