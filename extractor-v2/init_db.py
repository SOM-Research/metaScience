__author__ = 'valerio cosentino'

import mysql.connector
from mysql.connector import errorcode
import db_config


def establish_connection():
    return mysql.connector.connect(**db_config.CONFIG)


def create_schema(cnx, replace):
    cursor = cnx.cursor()

    cursor.execute("set global innodb_file_format = BARRACUDA")
    cursor.execute("set global innodb_file_format_max = BARRACUDA")
    cursor.execute("set global innodb_large_prefix = ON")
    cursor.execute("set global character_set_server = utf8")

    if replace:
        drop_database_if_exists = "DROP DATABASE IF EXISTS " + db_config.DB_NAME
        cursor.execute(drop_database_if_exists)

    create_database = "CREATE DATABASE " + db_config.DB_NAME
    cursor.execute(create_database)

    cursor.execute("USE " + db_config.DB_NAME)

    cursor.close()


def create_table_researcher(cnx):
    cursor = cnx.cursor()

    create_table_researcher = "CREATE TABLE " + db_config.DB_NAME + ".researcher( " \
                              "id bigint(20) PRIMARY KEY, " \
                              "name varchar(255) NOT NULL," \
                              "UNIQUE INDEX n (name) " \
                              ") ENGINE=InnoDB DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC;"

    cursor.execute(create_table_researcher)
    cursor.close()


def create_table_researcher_alias(cnx):
    cursor = cnx.cursor()

    create_table_researcher_alias = "CREATE TABLE " + db_config.DB_NAME + ".researcher_alias( " \
                              "researcher_id bigint(20), " \
                              "alias varchar(255) NOT NULL," \
                              "PRIMARY KEY pk (researcher_id, alias) " \
                              ") ENGINE=InnoDB DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC;"

    cursor.execute(create_table_researcher_alias)
    cursor.close()


def create_table_social_profile(cnx):
    cursor = cnx.cursor()

    create_table_social_profile = "CREATE TABLE " + db_config.DB_NAME + ".social_profile( " \
                                  "researcher_id bigint(20), " \
                                  "type varchar(255) NOT NULL, " \
                                  "url varchar(255)," \
                                  "PRIMARY KEY pk (researcher_id, type)," \
                                  "INDEX t (type) " \
                                  ") ENGINE=InnoDB DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC;"

    cursor.execute(create_table_social_profile)
    cursor.close()


def create_table_category(cnx):
    cursor = cnx.cursor()

    create_table_category = "CREATE TABLE " + db_config.DB_NAME + ".category( " \
                            "id bigint(20) AUTO_INCREMENT PRIMARY KEY, " \
                            "name varchar(255) NOT NULL," \
                            "UNIQUE INDEX n (name) " \
                            ") ENGINE=InnoDB DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC;"

    cursor.execute(create_table_category)
    cursor.close()


def create_table_track(cnx):
    cursor = cnx.cursor()

    create_table_track = "CREATE TABLE " + db_config.DB_NAME + ".track( " \
                            "id bigint(20) AUTO_INCREMENT PRIMARY KEY, " \
                            "name varchar(255) NOT NULL," \
                            "UNIQUE INDEX n (name) " \
                            ") ENGINE=InnoDB DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC;"

    cursor.execute(create_table_track)
    cursor.close()


def create_track_paper(cnx):
    cursor = cnx.cursor()
    create_track_paper = "CREATE TABLE " + db_config.DB_NAME + ".track_paper( " \
                         "track_id bigint(20) NOT NULL, " \
                         "paper_id bigint(20) NOT NULL, " \
                         "PRIMARY KEY (track_id, paper_id), " \
                         "INDEX p (paper_id), " \
                         "INDEX t (track_id)" \
                         ") ENGINE=InnoDB DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC;"

    cursor.execute(create_track_paper)

    cursor.close()


def create_table_paper_type(cnx):
    cursor = cnx.cursor()

    create_table_paper_type = "CREATE TABLE " + db_config.DB_NAME + ".paper_type( " \
                        "id bigint(20) AUTO_INCREMENT PRIMARY KEY, " \
                        "name varchar(255) NOT NULL," \
                        "UNIQUE INDEX n (name) " \
                        ") ENGINE=InnoDB DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC;"

    cursor.execute(create_table_paper_type)

    insert_types =  "INSERT INTO " + db_config.DB_NAME + ".paper_type " \
                    "VALUES(NULL, 'conference'), (NULL, 'journal');"

    cursor.execute(insert_types)
    cnx.commit()
    cursor.close()


def create_table_paper(cnx):
    cursor = cnx.cursor()

    create_table_paper = "CREATE TABLE " + db_config.DB_NAME + ".paper( " \
                         "id bigint(20) PRIMARY KEY, " \
                         "doi varchar(255), " \
                         "abstract longblob, " \
                         "pages int(11), " \
                         "title varchar(255) NOT NULL, " \
                         "url varchar(255), " \
                         "published_in bigint(20), " \
                         "type bigint(20), " \
                         "UNIQUE INDEX tp (title, published_in, type), " \
                         "INDEX venue (published_in, type), " \
                         "INDEX t (type) " \
                         ") ENGINE=InnoDB DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC;"

    cursor.execute(create_table_paper)
    cursor.close()


def create_table_category_paper(cnx):
    cursor = cnx.cursor()

    create_table_category_paper = "CREATE TABLE " + db_config.DB_NAME + ".category_paper( " \
                              "category_id bigint(20) NOT NULL, " \
                              "paper_id bigint(20) NOT NULL, " \
                              "PRIMARY KEY pk (category_id, paper_id), " \
                              "INDEX p (category_id), " \
                              "INDEX r (paper_id) " \
                              ") ENGINE=InnoDB DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC;"

    cursor.execute(create_table_category_paper)
    cursor.close()


def create_table_authorship(cnx):
    cursor = cnx.cursor()

    create_table_authorship = "CREATE TABLE " + db_config.DB_NAME + ".authorship( " \
                              "paper_id bigint(20) NOT NULL, " \
                              "researcher_id bigint(20) NOT NULL, " \
                              "position int(11) NOT NULL, " \
                              "PRIMARY KEY pk (paper_id, researcher_id)," \
                              "INDEX p (paper_id), " \
                              "INDEX r (researcher_id) " \
                              ") ENGINE=InnoDB DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC;"

    cursor.execute(create_table_authorship)
    cursor.close()


def create_table_country(cnx):
    cursor = cnx.cursor()

    create_table_country = "CREATE TABLE " + db_config.DB_NAME + ".country( " \
                           "id bigint(20) AUTO_INCREMENT PRIMARY KEY, " \
                           "name varchar(255) NOT NULL," \
                           "UNIQUE INDEX n (name) " \
                           ") ENGINE=InnoDB DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC;"

    cursor.execute(create_table_country)
    cursor.close()


def create_table_institution(cnx):
    cursor = cnx.cursor()

    create_table_institution = "CREATE TABLE " + db_config.DB_NAME + ".institution( " \
                            "id bigint(20) AUTO_INCREMENT PRIMARY KEY, " \
                            "name varchar(255) NOT NULL," \
                            "country_id bigint(20) NOT NULL, " \
                            "UNIQUE INDEX n (name), " \
                            "INDEX country (country_id) " \
                            ") ENGINE=InnoDB DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC;"

    cursor.execute(create_table_institution)
    cursor.close()


def create_table_authorship_institution(cnx):
    cursor = cnx.cursor()

    create_table_authorship_institution = "CREATE TABLE " + db_config.DB_NAME + ".authorship_institution( " \
                                          "paper_id bigint(20) NOT NULL, " \
                                          "researcher_id bigint(20) NOT NULL," \
                                          "institution_id bigint(20) NOT NULL, " \
                                          "PRIMARY KEY pk (paper_id, researcher_id, institution_id)," \
                                          "INDEX institution (institution_id) " \
                                          ") ENGINE=InnoDB DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC;"

    cursor.execute(create_table_authorship_institution)
    cursor.close()


def create_table_rank(cnx):
    cursor = cnx.cursor()

    create_table_rank = "CREATE TABLE " + db_config.DB_NAME + ".rank( " \
                        "id bigint(20) AUTO_INCREMENT PRIMARY KEY, " \
                        "name varchar(255) NOT NULL," \
                        "UNIQUE INDEX n (name) " \
                        ") ENGINE=InnoDB DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC;"

    cursor.execute(create_table_rank)

    insert_ranks =  "INSERT INTO " + db_config.DB_NAME + ".rank " \
                    "VALUES(NULL, 'A*'), (NULL, 'A'), (NULL, 'B'), (NULL, 'C');"

    cursor.execute(insert_ranks)
    cnx.commit()
    cursor.close()


def create_table_domain(cnx):
    cursor = cnx.cursor()
    create_table_domain = "CREATE TABLE " + db_config.DB_NAME + ".domain( " \
                          "id bigint(20) AUTO_INCREMENT PRIMARY KEY, " \
                          "name varchar(255) NOT NULL " \
                          ") ENGINE=InnoDB DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC;"

    cursor.execute(create_table_domain)

    cursor.close()


def create_table_conference(cnx):
    cursor = cnx.cursor()
    create_table_conference = "CREATE TABLE " + db_config.DB_NAME + ".conference( " \
                              "id bigint(20) AUTO_INCREMENT PRIMARY KEY, " \
                              "name varchar(255), " \
                              "acronym varchar(255), " \
                              "url varchar(255), " \
                              "is_satellite bigint(20), " \
                              "is_merged bigint(20), " \
                              "rank_id bigint(20), " \
                              "UNIQUE INDEX a (acronym), " \
                              "INDEX rank (rank_id) " \
                              ") ENGINE=InnoDB DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC;"

    cursor.execute(create_table_conference)

    cursor.close()


def create_table_conference_edition(cnx):
    cursor = cnx.cursor()
    create_table_conference_edition = "CREATE TABLE " + db_config.DB_NAME + ".conference_edition( " \
                                      "id bigint(20) AUTO_INCREMENT PRIMARY KEY, " \
                                      "year int(4), " \
                                      "name varchar(255) NOT NULL, " \
                                      "url varchar(255), " \
                                      "conference_id bigint(20) NOT NULL, " \
                                      "institution_id bigint(20), " \
                                      "UNIQUE INDEX nc (year, conference_id), " \
                                      "INDEX y (year), " \
                                      "INDEX c (conference_id), " \
                                      "INDEX i (institution_id)" \
                                      ") ENGINE=InnoDB DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC;"

    cursor.execute(create_table_conference_edition)

    cursor.close()


def create_table_conference_domain(cnx):
    cursor = cnx.cursor()
    create_table_conference_domain = "CREATE TABLE " + db_config.DB_NAME + ".conference_domain( " \
                                      "domain_id bigint(20), " \
                                      "conference_id bigint(20), " \
                                      "PRIMARY KEY pk (domain_id, conference_id), " \
                                      "INDEX p (domain_id), " \
                                      "INDEX r (conference_id) " \
                                      ") ENGINE=InnoDB DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC;"

    cursor.execute(create_table_conference_domain)

    cursor.close()


def create_table_journal_domain(cnx):
    cursor = cnx.cursor()
    create_table_journal_domain = "CREATE TABLE " + db_config.DB_NAME + ".journal_domain( " \
                                      "domain_id bigint(20), " \
                                      "journal_id bigint(20), " \
                                      "PRIMARY KEY pk (domain_id, journal_id), " \
                                      "INDEX p (domain_id), " \
                                      "INDEX r (journal_id) " \
                                      ") ENGINE=InnoDB DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC;"

    cursor.execute(create_table_journal_domain)

    cursor.close()


def create_table_journal(cnx):
    cursor = cnx.cursor()
    create_table_journal = "CREATE TABLE " + db_config.DB_NAME + ".journal( " \
                              "id bigint(20) AUTO_INCREMENT PRIMARY KEY, " \
                              "name varchar(255), " \
                              "acronym varchar(255), " \
                              "url varchar(255), " \
                              "impact_factor float(5,3), " \
                              "UNIQUE INDEX a (acronym), " \
                              "INDEX im (impact_factor) " \
                              ") ENGINE=InnoDB DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC;"

    cursor.execute(create_table_journal)

    cursor.close()


def create_table_journal_issue(cnx):
    cursor = cnx.cursor()
    create_table_journal_issue = "CREATE TABLE " + db_config.DB_NAME + ".journal_issue( " \
                                      "id bigint(20) AUTO_INCREMENT PRIMARY KEY, " \
                                      "year int(4), " \
                                      "volume int(4), " \
                                      "number int(2), " \
                                      "url varchar(255), " \
                                      "journal_id bigint(20) NOT NULL, " \
                                      "UNIQUE INDEX nc (year, volume, number, journal_id), " \
                                      "INDEX y (year), " \
                                      "INDEX j (journal_id) " \
                                      ") ENGINE=InnoDB DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC;"

    cursor.execute(create_table_journal_issue)

    cursor.close()


def create_table_program_committee(cnx):
    cursor = cnx.cursor()
    create_table_program_committee = "CREATE TABLE " + db_config.DB_NAME + ".program_committee( " \
                                     "researcher_id bigint(20) NOT NULL, " \
                                     "is_chair int(1)," \
                                     "conference_edition_id bigint(20) NOT NULL, " \
                                     "PRIMARY KEY (researcher_id, conference_edition_id), " \
                                     "INDEX ce (conference_edition_id), " \
                                     "INDEX r (researcher_id)" \
                                     ") ENGINE=InnoDB DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC;"

    cursor.execute(create_table_program_committee)

    cursor.close()


def create_paper_is_cited(cnx):
    cursor = cnx.cursor()
    create_table_paper_is_cited = "CREATE TABLE " + db_config.DB_NAME + ".paper_is_cited( " \
                                  "paper_cites bigint(20), " \
                                  "paper_is_cited bigint(20), " \
                                  "PRIMARY KEY (paper_cites, paper_is_cited), " \
                                  "INDEX pc (paper_cites), " \
                                  "INDEX pi (paper_is_cited)" \
                                  ") ENGINE=InnoDB DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC;"

    cursor.execute(create_table_paper_is_cited)

    cursor.close()


def create_table_topic(cnx):
    cursor = cnx.cursor()
    create_table_topic = "CREATE TABLE " + db_config.DB_NAME + ".topic( " \
                         "id bigint(20) AUTO_INCREMENT PRIMARY KEY, " \
                         "name varchar(255) NOT NULL," \
                         "UNIQUE INDEX t (name) " \
                         ") ENGINE=InnoDB DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC;"

    cursor.execute(create_table_topic)

    cursor.close()


def create_conference_edition_topic(cnx):
    cursor = cnx.cursor()
    create_topic_conference_edition = "CREATE TABLE " + db_config.DB_NAME + ".topic_conference_edition( " \
                                      "topic_id bigint(20) NOT NULL, " \
                                      "conference_edition_id bigint(20) NOT NULL, " \
                                      "PRIMARY KEY (topic_id, conference_edition_id), " \
                                      "INDEX t (topic_id), " \
                                      "INDEX ce (conference_edition_id)" \
                                      ") ENGINE=InnoDB DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC;"

    cursor.execute(create_topic_conference_edition)

    cursor.close()


def create_topic_paper(cnx):
    cursor = cnx.cursor()
    create_topic_paper = "CREATE TABLE " + db_config.DB_NAME + ".topic_paper( " \
                         "topic_id bigint(20) NOT NULL, " \
                         "paper_id bigint(20) NOT NULL, " \
                         "PRIMARY KEY (topic_id, paper_id), " \
                         "INDEX p (paper_id), " \
                         "INDEX t (topic_id)" \
                         ") ENGINE=InnoDB DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC;"

    cursor.execute(create_topic_paper)

    cursor.close()


def create_steering_committee(cnx):
    cursor = cnx.cursor()
    create_steering_committee = "CREATE TABLE " + db_config.DB_NAME + ".steering_committee( " \
                                "researcher_id bigint(20) NOT NULL, " \
                                "conference_edition_id bigint(20) NOT NULL, " \
                                "PRIMARY KEY (researcher_id, conference_edition_id), " \
                                "INDEX r (researcher_id), " \
                                "INDEX ce (conference_edition_id)" \
                                ") ENGINE=InnoDB DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC;"

    cursor.execute(create_steering_committee)

    cursor.close()


def create_function_from_roman(cnx):
    cursor = cnx.cursor()
    from_roman = """
    CREATE DEFINER=`root`@`localhost` FUNCTION `from_roman`(in_roman varchar(15)) RETURNS int(11)
        DETERMINISTIC
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
    END
    """

    cursor.execute(from_roman)
    cursor.close()


def create_function_calculate_num_of_pages(cnx):
    cursor = cnx.cursor()
    calculate_num_of_pages = """
    CREATE DEFINER=`root`@`localhost` FUNCTION `calculate_num_of_pages`(pages varchar(100)) RETURNS int(11)
    DETERMINISTIC
    BEGIN
        DECLARE page_number INTEGER;

        DECLARE occ_dash INTEGER DEFAULT (INSTR(pages, '-'));
        DECLARE left_part VARCHAR(256);
        DECLARE right_part VARCHAR(256);
        DECLARE left_part_int INTEGER;
        DECLARE right_part_int INTEGER;

        /* if a '-' is found */
        IF occ_dash >= 1 THEN
            SET left_part = SUBSTRING(pages, 1, occ_dash - 1);
            SET right_part = SUBSTRING(pages, occ_dash + 1);
            /* check that the two parts are not empty */
            IF right_part = '' OR left_part = '' THEN
                SET page_number = 1;
            /* check that the two parts contain only digits */
            ELSEIF right_part REGEXP '^[[:digit:]]+$' AND left_part REGEXP '^[[:digit:]]+$' THEN
                SET left_part_int = CONVERT(SUBSTRING(pages, 1, occ_dash - 1), SIGNED INTEGER);
                SET right_part_int =  CONVERT(SUBSTRING(pages, occ_dash + 1), SIGNED INTEGER);
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
                    IF from_roman(right_part) > from_roman(left_part) THEN
                        SET page_number = from_roman(right_part) - from_roman(left_part);
                    ELSE
                        SET page_number = from_roman(left_part) - from_roman(right_part);
                    END IF;
                ELSE
                    IF left_part REGEXP '^[[:digit:]]+:[[:digit:]]+$' AND right_part REGEXP '^[[:digit:]]+:[[:digit:]]+$' THEN
                        SET left_part_int =  CONVERT(SUBSTRING(left_part, INSTR(left_part, ':') + 1), SIGNED INTEGER);
                        SET right_part_int =  CONVERT(SUBSTRING(right_part, INSTR(right_part, ':') + 1), SIGNED INTEGER);

                        IF right_part_int > left_part_int THEN
                            SET page_number = right_part_int - left_part_int;
                        ELSE
                            SET page_number = left_part_int - right_part_int;
                        END IF;

                        IF page_number = 0 THEN
                            SET page_number = 1;
                        END IF;
                    ELSE
                        SET page_number = NULL;
                    END IF;
                END IF;
            END IF;
        /* if a '-' is not found*/
        ELSE
            /* check that pages contain only digits */
            IF pages REGEXP '^[[:digit:]]+$' or UPPER(pages) REGEXP '^(M{0,4})?(CM|CD|D?C{0,3})?(XC|XL|L?X{0,3})?(IX|IV|V?I{0,3})?$' THEN
                SET page_number = 1;
            ELSE
                SET page_number = NULL;
            END IF;
        END IF;

        IF page_number <> 1 THEN
            SET page_number = page_number + 1;
        END IF;

        RETURN page_number;

    END
    """
    cursor.execute(calculate_num_of_pages)
    cursor.close()


def create_stored_procedures_for_turnover(cnx):
    cursor = cnx.cursor()

    cursor.execute("USE metascience;")
    cursor.execute("DROP PROCEDURE IF EXISTS calculate_turnover_between_editions;")
    cursor.execute("DROP PROCEDURE IF EXISTS calculate_turnover_for_conference;")
    cursor.execute("DROP PROCEDURE IF EXISTS get_turnover_information_for_conference;")
    cursor.execute("DROP PROCEDURE IF EXISTS calculate_turnover_information_for_all_conferences;")

    cursor.execute("DROP TABLE IF EXISTS aux_conference_turnover;")

    create_aux_conference_turnover_table = """
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
    """

    create_calculate_turnover_between_editions_stored_procedure = """
    CREATE PROCEDURE calculate_turnover_between_editions (IN year_x numeric(4), IN year_y numeric(4), IN target_conference_id bigint(20), IN time_interval numeric(2))
    BEGIN
        insert into aux_conference_turnover
        select
        author_x_year as researcher_id,
        authors_year_x.author_name as researcher_name,
        if(author_y_year IS NULL,'perished', 'survived') as status,
        time_interval,
        CONCAT(year_x, '-', year_y) as period,
        target_conference_id as conference_id
        FROM (
            SELECT r.id as author_x_year, r.name as author_name
            FROM conference_edition ce join paper p on ce.id = p.published_in
            JOIN authorship a ON a.paper_id = p.id JOIN researcher r ON r.id = a.researcher_id
            WHERE p.type = 1 AND year = year_x AND conference_id = target_conference_id
            GROUP BY r.id) AS authors_year_x
        LEFT JOIN
        (SELECT r.id as author_y_year, r.name as author_name
        FROM conference_edition ce join paper p on ce.id = p.published_in
        JOIN authorship a ON a.paper_id = p.id JOIN researcher r ON r.id = a.researcher_id
        WHERE p.type = 1 AND year > year_x AND year <= year_y AND conference_id = target_conference_id
        GROUP BY r.id) AS authors_year_y
        ON author_x_year = author_y_year;

    END
    """

    create_calculate_turnover_for_conference_stored_procedure = """
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

    END
    """

    create_get_turnover_information_for_conference_stored_procedure = """
    CREATE PROCEDURE get_turnover_information_for_conference(IN target_conference_id bigint(20), IN _r NUMERIC(2))
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


    END
    """

    create_calculate_turnover_information_for_all_conferences_stored_procedure = """
    CREATE PROCEDURE calculate_turnover_information_for_all_conferences(IN _range NUMERIC(2))
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
    END
    """

    cursor.execute(create_aux_conference_turnover_table)
    cursor.execute(create_calculate_turnover_between_editions_stored_procedure)
    cursor.execute(create_calculate_turnover_for_conference_stored_procedure)
    cursor.execute(create_get_turnover_information_for_conference_stored_procedure)
    cursor.execute(create_calculate_turnover_information_for_all_conferences_stored_procedure)
    cursor.close()


def create_stored_procedures_for_openness(cnx):
    cursor = cnx.cursor()
    cursor.execute("USE metascience")
    cursor.execute("DROP PROCEDURE IF EXISTS get_openness_information_for_edition;")
    cursor.execute("DROP PROCEDURE IF EXISTS get_openness_information_for_conference_by_id;")
    cursor.execute("DROP PROCEDURE IF EXISTS get_openness_information_for_conference_by_name;")
    cursor.execute("DROP PROCEDURE IF EXISTS get_openness_information_for_all_conferences;")

    cursor.execute("DROP TABLE IF EXISTS aux_conference_openness;")
    create_aux_conference_openness_table = """
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
    """

    create_get_openness_information_for_edition_stored_procedure = """
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
                        where ce.year = target_year and ce.conference_id = target_conference_id and p.type = 1
                        group by a.researcher_id) as unique_authors_edition_x
                    left join
                        (
                        /* unique authors for editions [X-Y,X) */
                        select a.researcher_id as unique_author
                        from
                            conference_edition ce join paper p on ce.id = p.published_in
                            join authorship a on a.paper_id = p.id
                        where ce.conference_id = target_conference_id and ce.year >= (target_year-span) and ce.year < target_year and p.type = 1
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
                where ce.conference_id = target_conference_id and year = target_year and p.type = 1) as target_edition
            left join
                /* unique authors for editions [X-Y,X) */
                (select a.researcher_id, conference_id, ce.id as conference_edition_id
                from
                    conference_edition ce join paper p on ce.id = p.published_in
                    join authorship a on a.paper_id = p.id
                where ce.conference_id = target_conference_id and p.type = 1 and ce.year >= (target_year-span) and ce.year < target_year
                group by a.researcher_id) as previous_x_editions
            on target_edition.researcher_id = previous_x_editions.researcher_id
            group by paper_id) as info_edition_x) as papers
    on papers.conference_edition_id = researchers.conference_edition_id;
    END
    """

    create_get_openness_information_for_conference_by_id_stored_procedure = """
    CREATE DEFINER=`root`@`localhost` PROCEDURE `get_openness_information_for_conference_by_id`(IN target_conference_id BIGINT(20), IN span NUMERIC(2))
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

    END
    """

    create_get_openness_information_for_conference_by_name_stored_procedure = """
    CREATE DEFINER=`root`@`localhost` PROCEDURE `get_openness_information_for_conference_by_name`(IN target_conference_acronym VARCHAR(255), IN span NUMERIC(2))
    BEGIN
        DECLARE exit_loop BOOLEAN;
        DECLARE target_conference_id BIGINT(20);
        DECLARE id_cursor CURSOR FOR
                                        SELECT id
                                        FROM conference c
                                        WHERE c.acronym = target_conference_acronym;
        DECLARE CONTINUE HANDLER FOR NOT FOUND SET exit_loop = TRUE;

        OPEN id_cursor;

        _iterate: LOOP
            FETCH id_cursor INTO target_conference_id;

            IF exit_loop THEN
                CLOSE id_cursor;
                LEAVE _iterate;
            END IF;


            CALL get_openness_information_for_conference_by_id(target_conference_id, span);

        END LOOP _iterate;

    END
    """

    create_get_openness_information_for_all_conferences_stored_procedure = """
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

    END
    """

    cursor.execute(create_aux_conference_openness_table)
    cursor.execute(create_get_openness_information_for_edition_stored_procedure)
    cursor.execute(create_get_openness_information_for_conference_by_id_stored_procedure)
    cursor.execute(create_get_openness_information_for_conference_by_name_stored_procedure)
    cursor.execute(create_get_openness_information_for_all_conferences_stored_procedure)
    cursor.close()


def create_table_paper_stats(cnx):
    cursor = cnx.cursor()
    create_table_paper_stats =  "CREATE TABLE " + db_config.DB_NAME + ".aux_paper_stats ( " \
                                "paper_id bigint(20) PRIMARY KEY, " \
                                "year int(4), " \
                                "co_authors int(2), " \
                                "participation decimal(5,4), " \
                                "pages int(11), " \
                                "type bigint(20) " \
                              ") ENGINE=InnoDB DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC;"
    cursor.execute(create_table_paper_stats)
    cursor.close()


def create_tables(cnx):
    create_table_researcher(cnx)
    create_table_social_profile(cnx)
    create_table_researcher_alias(cnx)
    create_table_category(cnx)
    create_table_track(cnx)
    create_table_paper_type(cnx)
    create_table_paper(cnx)
    create_table_category_paper(cnx)
    create_table_authorship(cnx)
    create_table_country(cnx)
    create_table_institution(cnx)
    create_table_authorship_institution(cnx)
    create_table_rank(cnx)
    create_table_domain(cnx)
    create_table_conference(cnx)
    create_table_conference_edition(cnx)
    create_table_conference_domain(cnx)
    create_table_program_committee(cnx)
    create_paper_is_cited(cnx)
    create_table_topic(cnx)
    create_conference_edition_topic(cnx)
    create_topic_paper(cnx)
    create_track_paper(cnx)
    create_steering_committee(cnx)

    create_table_journal(cnx)
    create_table_journal_issue(cnx)
    create_table_journal_domain(cnx)

    create_table_paper_stats(cnx)


def create_functions(cnx):
    create_function_from_roman(cnx)
    create_function_calculate_num_of_pages(cnx)


def create_stored_procedures(cnx):
    create_stored_procedures_for_openness(cnx)
    create_stored_procedures_for_turnover(cnx)


def main():
    cnx = establish_connection()
    create_schema(cnx, replace=True)
    create_tables(cnx)
    create_functions(cnx)
    create_stored_procedures(cnx)

    cnx.close()

if __name__ == "__main__":
    main()