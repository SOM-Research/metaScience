USE dblp;
DROP FUNCTION IF EXISTS calculate_num_of_pages;
DROP FUNCTION IF EXISTS from_roman;

DELIMITER //

CREATE FUNCTION calculate_num_of_pages(pages varchar(100)) RETURNS int(11) DETERMINISTIC
BEGIN
	DECLARE page_number INTEGER;
	DECLARE occ_dash INTEGER DEFAULT (INSTR(pages, '-'));
	DECLARE left_part VARCHAR(256) DEFAULT SUBSTRING(pages, 1, occ_dash - 1);
	DECLARE right_part VARCHAR(256) DEFAULT SUBSTRING(pages, occ_dash + 1);
	DECLARE left_part_int INTEGER DEFAULT CONVERT(SUBSTRING(pages, 1, occ_dash - 1), SIGNED INTEGER);
	DECLARE right_part_int INTEGER DEFAULT CONVERT(SUBSTRING(pages, occ_dash + 1), SIGNED INTEGER);

	/* if a '-' is found */
	IF occ_dash >= 1 THEN
		/* check that the two parts are not empty */
		IF right_part = '' OR left_part = '' THEN
			SET page_number = 1;
		/* check that the two parts contain only digits */
        ELSEIF right_part REGEXP '[[:digit:]]+' AND left_part REGEXP '[[:digit:]]+' THEN
			IF right_part_int > left_part_int THEN
				SET page_number = right_part_int - left_part_int;
			ELSE
				SET page_number = left_part_int - right_part_int;
			END IF;

			IF page_number = 0 THEN
				SET page_number = 1;
			END IF;
		ELSE
			IF UPPER(right_part) REGEXP '^(M{0,4})?(CM|CD|(D?C{0,3}))?(XC|XL|(L?X{0,3}))?(IX|IV|(V?I{0,3}))?$' AND
				UPPER(left_part) REGEXP '^(M{0,4})?(CM|CD|(D?C{0,3}))?(XC|XL|(L?X{0,3}))?(IX|IV|(V?I{0,3}))?$' THEN
				IF from_roman(right_part_int) > from_roman(left_part_int) THEN
					SET page_number = from_roman(right_part_int) - from_roman(left_part_int);
				ELSE
					SET page_number = from_roman(left_part_int) - from_roman(right_part_int);
				END IF;
			ELSE
				SET page_number = NULL;
			END IF;
		END IF;
	/* if a '-' is not found*/
    ELSE
		/* check that pages contain only digits */
		IF pages REGEXP '[[:digit:]]+' or UPPER(pages) REGEXP '^(M{0,4})?(CM|CD|D?C{0,3})?(XC|XL|L?X{0,3})?(IX|IV|V?I{0,3})?$' THEN
			SET page_number = 1;
		ELSE
			SET page_number = NULL;
		END IF;
	END IF;

	RETURN page_number;

END //

CREATE FUNCTION from_roman(in_roman varchar(15)) RETURNS int(11) DETERMINISTIC
BEGIN

    DECLARE numeral CHAR(7) DEFAULT 'IVXLCDM';

    DECLARE digit TINYINT;
    DECLARE previous INT DEFAULT 0;
    DECLARE current INT;
    DECLARE sum INT DEFAULT 0;

    SET in_roman = UPPER(in_roman);

    WHILE LENGTH(in_roman) > 0 DO
        SET digit := LOCATE(RIGHT(in_roman, 1), numeral) - 1;
        SET current := POW(10, FLOOR(digit / 2)) * POW(5, MOD(digit, 2));
        SET sum := sum + POW(-1, current < previous) * current;
        SET previous := current;
        SET in_roman = LEFT(in_roman, LENGTH(in_roman) - 1);
    END WHILE;

    RETURN sum;
END //

DELIMITER ;