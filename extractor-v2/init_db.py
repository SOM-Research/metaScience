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
                              "name varchar(255) NOT NULL " \
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
                         "category_id bigint(20), " \
                         "UNIQUE INDEX tp (title, published_in), " \
                         "INDEX conf (published_in), " \
                         "INDEX category (category_id) " \
                         ") ENGINE=InnoDB DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC;"

    cursor.execute(create_table_paper)
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
                              "domain_id bigint(20), " \
                              "rank_id bigint(20), " \
                              "UNIQUE INDEX a (acronym), " \
                              "INDEX rank (rank_id), " \
                              "INDEX domain (domain_id)" \
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
                                  "paper_cites bigint(20) NOT NULL, " \
                                  "paper_is_cited bigint(20) NOT NULL, " \
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


def create_topic_conference_edition(cnx):
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


def create_tables(cnx):
    create_table_researcher(cnx)
    create_table_social_profile(cnx)
    create_table_researcher_alias(cnx)
    create_table_category(cnx)
    create_table_track(cnx)
    create_table_paper(cnx)
    create_table_authorship(cnx)
    create_table_country(cnx)
    create_table_institution(cnx)
    create_table_authorship_institution(cnx)
    create_table_rank(cnx)
    create_table_domain(cnx)
    create_table_conference(cnx)
    create_table_conference_edition(cnx)
    create_table_program_committee(cnx)
    create_paper_is_cited(cnx)
    create_table_topic(cnx)
    create_topic_conference_edition(cnx)
    create_topic_paper(cnx)
    create_track_paper(cnx)
    create_steering_committee(cnx)

    create_function_from_roman(cnx)
    create_function_calculate_num_of_pages(cnx)


def main():
    cnx = establish_connection()
    create_schema(cnx, replace=True)
    create_tables(cnx)
    cnx.close()

if __name__ == "__main__":
    main()