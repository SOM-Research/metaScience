__author__ = 'valerio cosentino'

import mysql.connector
from mysql.connector import errorcode
import db_config

DBLP_DATABASE = "dblp-2016-02-13"


def establish_connection():
    return mysql.connector.connect(**db_config.CONFIG)


def add_new_researchers(cnx):
    cursor = cnx.cursor()
    query = "INSERT IGNORE INTO `" + db_config.DB_NAME + "`.researcher " \
            "SELECT dblp.id, dblp.author FROM `" + DBLP_DATABASE + "`.dblp_author_ref_new dblp " \
            "LEFT JOIN `" + db_config.DB_NAME + "`.researcher r ON dblp.id = r.id " \
            "WHERE r.id IS NULL"
    cursor.execute(query)
    cnx.commit()
    cursor.close()


def add_new_researcher_aliases(cnx):
    cursor = cnx.cursor()
    query = "INSERT IGNORE INTO `" + db_config.DB_NAME + "`.researcher_alias " \
            "SELECT dblp.author_id, dblp.authorAlias FROM `" + DBLP_DATABASE + "`.dblp_aliases_new dblp"
    cursor.execute(query)
    cnx.commit()
    cursor.close()

#TODO
def add_new_conferences(cnx):
    cursor = cnx.cursor()
    query = "INSERT IGNORE INTO `" + db_config.DB_NAME + "`.conference " \
            "SELECT NULL, NULL, source_id, CONCAT('dblp.uni-trier.de/db/conf/', source_id), NULL, NULL " \
            "FROM `" + DBLP_DATABASE + "`.dblp_pub_new dblp " \
            "WHERE dblp_key LIKE 'conf%' " \
            "GROUP BY SUBSTRING_INDEX(dblp_key, '/', 2)"
    cursor.execute(query)
    cnx.commit()
    cursor.close()


#TODO
def add_new_conference_editions(cnx):
    cursor = cnx.cursor()
    query = "INSERT IGNORE INTO `" + db_config.DB_NAME + "`.conference_edition " \
            "SELECT NULL, dblp_selection.year, title, NULL, meta.id, NULL " \
            "FROM (SELECT year, source, source_id, title " \
                  "FROM `" + DBLP_DATABASE + "`.dblp_pub_new " \
                  "WHERE dblp_key LIKE 'conf%' AND (source = source_id OR source IS NULL) AND type = 'proceedings' " \
                  "GROUP BY source, source_id, year) " \
            "AS dblp_selection " \
            "JOIN `" + db_config.DB_NAME + "`.conference meta " \
            "ON dblp_selection.source_id = meta.acronym"
    cursor.execute(query)
    cnx.commit()
    cursor.close()


def add_new_papers(cnx):
    cursor_edition = cnx.cursor()
    cursor_paper = cnx.cursor()
    query_edition_info = "SELECT acronym, ce.id as conference_edition_id, ce.year " \
            "FROM `" + db_config.DB_NAME + "`.conference_edition ce JOIN `" + db_config.DB_NAME + "`.conference c " \
            "ON ce.conference_id = c.id;"
    cursor_edition.execute(query_edition_info)

    row = cursor_edition.fetchone()
    while row:
        acronym = row[0]
        edition_id = row[1]
        year = row[2]
        query = "INSERT IGNORE INTO `" + db_config.DB_NAME + "`.paper " \
                "SELECT id, doi, NULL, `" + db_config.DB_NAME + "`.calculate_num_of_pages(pages), title, url, " + str(edition_id) + ", NULL " \
                "FROM `" + DBLP_DATABASE + "`.dblp_pub_new " \
                "WHERE dblp_key LIKE 'conf%' AND (source = source_id OR source IS NULL) AND type = 'inproceedings' " \
                "AND source_id = '" + acronym + "' AND year = " + str(year) + ";"
        cursor_paper.execute(query)
        cnx.commit()

        row = cursor_edition.fetchone()

    cursor_paper.close()
    cursor_edition.close()


def add_new_authorships(cnx):
    cursor_paper = cnx.cursor()
    cursor_authorship = cnx.cursor()
    query_paper_id = "SELECT id " \
                     "FROM `" + db_config.DB_NAME + "`.paper;"
    cursor_paper.execute(query_paper_id)

    row = cursor_paper.fetchone()
    while row:
        paper_id = row[0]
        query = "INSERT IGNORE INTO `" + db_config.DB_NAME + "`.authorship " \
                "SELECT a.id, a.author_id, b.author_num " \
                "FROM `" + DBLP_DATABASE + "`.dblp_authorid_ref_new a JOIN `" + DBLP_DATABASE + "`.dblp_author_ref_new b " \
                "ON a.author = b.author AND a.id = b.id " \
                "WHERE a.id = %s;"
        arguments = [paper_id]
        cursor_authorship.execute(query, arguments)
        cnx.commit()

        row = cursor_paper.fetchone()

    cursor_paper.close()


def main():
    cnx = establish_connection()
    add_new_researchers(cnx)
    add_new_researcher_aliases(cnx)
    add_new_conferences(cnx)
    add_new_conference_editions(cnx)
    add_new_papers(cnx)
    add_new_authorships(cnx)
    cnx.close()

if __name__ == "__main__":
    main()
