USE metascience;
DROP PROCEDURE IF EXISTS calculate_turnover_between_editions;
DROP PROCEDURE IF EXISTS calculate_turnover_for_conference;
DROP PROCEDURE IF EXISTS get_turnover_information;
DROP PROCEDURE IF EXISTS calculate_turnover_information;

DROP TABLE IF EXISTS aux_conference_turnover;

CREATE TABLE aux_conference_turnover (
	researcher_id bigint(20),
	researcher_name varchar(255),
	status varchar(255),
	time_interval numeric(2),
	period varchar(255),
	conference_id bigint(20),
	INDEX c (conference_id),
	INDEX p (period),
	PRIMARY KEY pk (conference_id, researcher_id, period)
);

DELIMITER //
CREATE PROCEDURE calculate_turnover_between_editions (IN year_x numeric(4), IN year_y numeric(4), IN target_conference_id bigint(20), IN time_interval numeric(2))
BEGIN
	insert into aux_conference_turnover
	select 
	author_x_year as researcher_id, 
	author_name as researcher_name, 
	if(author_y_year IS NULL,'perished', 'survived') as status,
	time_interval,
	CONCAT(year_x, '-', year_y) as period,
	target_conference_id as conference_id
	FROM (
		SELECT r.id as author_x_year, r.name as author_name
		FROM conference_edition ce join paper p on ce.id = p.published_in
		JOIN authorship a ON a.paper_id = p.id JOIN researcher r ON r.id = a.researcher_id
		WHERE p.type = 1 AND year = year_x AND conference_id = target_conference_id) AS authors_year_x
	LEFT JOIN
	(SELECT r.id as author_y_year, r.name as author_name
	FROM conference_edition ce join paper p on ce.id = p.published_in
	JOIN authorship a ON a.paper_id = p.id JOIN researcher r ON r.id = a.researcher_id
	WHERE p.type = 1 AND year > year_x AND year <= year_y AND conference_id = target_conference_id) AS authors_year_y
	ON author_x_year = author_y_year;

END //

CREATE PROCEDURE calculate_turnover_for_conference(IN target_conference_id bigint(20), IN _range NUMERIC(2))
BEGIN
	DECLARE exit_loop BOOLEAN;
	DECLARE _year NUMERIC(10);
	DECLARE year_plus_range NUMERIC(10);
	DECLARE advanced_year NUMERIC(10);
	DECLARE to_advance NUMERIC(2) DEFAULT _range;
	DECLARE year_cursor CURSOR FOR
									SELECT year
									FROM conference_edition ce
									WHERE ce.conference_id = target_conference_id
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

		CALL calculate_turnover_between_editions(_year, year_plus_range, target_conference_id, _range);
		SET to_advance = _range;

	END LOOP get_pair_years;

END //

CREATE PROCEDURE get_turnover_information(IN target_conference_id bigint(20), IN _r NUMERIC(2))
BEGIN
	DECLARE perished_survived_number_of_rows INTEGER;

	SELECT count(*) INTO perished_survived_number_of_rows
	FROM aux_conference_turnover
	WHERE conference_id = target_conference_id and time_interval = _r;

	IF perished_survived_number_of_rows = 0 THEN
		CALL calculate_turnover_for_conference(target_conference_id, _r);
	END IF;

	SELECT *
	FROM aux_conference_turnover
	WHERE conference_id = target_conference_id AND time_interval = _r;


END //

CREATE PROCEDURE calculate_turnover_information(IN _range NUMERIC(2))
BEGIN
	DECLARE exit_loop BOOLEAN;
	DECLARE target_conference_id BIGINT(20);
	DECLARE id_cursor CURSOR FOR
									SELECT id
									FROM conference;
	DECLARE CONTINUE HANDLER FOR NOT FOUND SET exit_loop = TRUE;

	OPEN id_cursor;
	FETCH id_cursor INTO target_conference_id;
	get_conference_id: LOOP

		CALL calculate_turnover_for_conference(target_conference_id, _range);

		IF (exit_loop) THEN
			CLOSE id_cursor;
			LEAVE get_conference_id;
		END IF;
	END LOOP get_conference_id;
END //

DELIMITER ;