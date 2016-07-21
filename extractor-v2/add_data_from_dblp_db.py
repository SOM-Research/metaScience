__author__ = 'valerio cosentino'

import mysql.connector
from mysql.connector import errorcode
import db_config

DBLP_DATABASE = "dblp-2016-02-13"


def select_db(cnx):
    cursor = cnx.cursor()
    cursor.execute("USE " + db_config.DB_NAME)
    cursor.close()


def establish_connection():
    return mysql.connector.connect(**db_config.CONFIG)


def add_new_researchers(cnx):
    cursor = cnx.cursor()
    query = "INSERT IGNORE INTO `" + db_config.DB_NAME + "`.researcher " \
            "SELECT dblp.author_id, dblp.author FROM `" + DBLP_DATABASE + "`.dblp_authorid_ref_new dblp " \
            "LEFT JOIN `" + db_config.DB_NAME + "`.researcher r ON dblp.author_id = r.id " \
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


def add_new_conferences(cnx):
    cursor = cnx.cursor()
    query = "INSERT IGNORE INTO `" + db_config.DB_NAME + "`.conference " \
            "SELECT NULL, NULL, source_id, CONCAT('dblp.uni-trier.de/db/conf/', source_id), NULL, NULL, NULL " \
            "FROM `" + DBLP_DATABASE + "`.dblp_pub_new dblp " \
            "WHERE dblp_key LIKE 'conf%' AND url IS NOT NULL " \
            "GROUP BY SUBSTRING_INDEX(dblp_key, '/', 2)"
    cursor.execute(query)
    cnx.commit()
    cursor.close()


def add_new_conference_editions(cnx):
    cursor = cnx.cursor()
    query = "INSERT IGNORE INTO `" + db_config.DB_NAME + "`.conference_edition " \
            "SELECT NULL, dblp_selection.year, title, SUBSTRING_INDEX(SUBSTRING_INDEX(dblp_selection.url, '.html#', 1), '-', 1) as url, meta.id, NULL " \
            "FROM (SELECT year, source_id, url, CONCAT(upper(source_id), ' ', year) as title " \
                  "FROM `" + DBLP_DATABASE + "`.dblp_pub_new dblp " \
                  "WHERE SUBSTRING_INDEX(crossref, '/', -1) REGEXP '^[0-9]+(-[0-9])*$' " \
                  "GROUP BY source_id, year) " \
            "AS dblp_selection " \
            "JOIN `" + db_config.DB_NAME + "`.conference meta " \
            "ON dblp_selection.source_id = meta.acronym"
    cursor.execute(query)
    cnx.commit()
    cursor.close()


#not consider internal reports (source_id <> 'corr')
def add_new_journals(cnx):
    cursor = cnx.cursor()
    query = "INSERT IGNORE INTO `" + db_config.DB_NAME + "`.journal " \
            "SELECT NULL, source, source_id, CONCAT('dblp.uni-trier.de/db/journals/', source_id), NULL " \
            "FROM `" + DBLP_DATABASE + "`.dblp_pub_new dblp " \
            "WHERE dblp_key LIKE 'journals/%' AND url IS NOT NULL AND source_id <> 'corr' " \
            "GROUP BY SUBSTRING_INDEX(dblp_key, '/', 2)"
    cursor.execute(query)
    cnx.commit()
    cursor.close()


def add_new_journal_issues(cnx):
    cursor = cnx.cursor()
    query = "INSERT IGNORE INTO `" + db_config.DB_NAME + "`.journal_issue " \
            "SELECT NULL, dblp_selection.year, volume, number, dblp_selection.url, meta.id " \
            "FROM (SELECT source_id, year, volume, number, SUBSTRING_INDEX(url, '#', 1) as url " \
                "FROM `" + DBLP_DATABASE + "`.dblp_pub_new dblp " \
                "WHERE dblp_key LIKE 'journals/%' AND url IS NOT NULL AND source_id <> 'corr' " \
                "GROUP BY volume, number, year, SUBSTRING_INDEX(url, '#', 1)) " \
            "AS dblp_selection " \
            "JOIN `" + db_config.DB_NAME + "`.journal meta " \
            "ON dblp_selection.source_id = meta.acronym"
    cursor.execute(query)
    cnx.commit()
    cursor.close()


def add_new_conference_papers(cnx):
    cursor_edition = cnx.cursor()
    cursor_paper = cnx.cursor()
    query_edition_info = "SELECT acronym, ce.id as conference_edition_id, ce.year, ce.url " \
            "FROM `" + db_config.DB_NAME + "`.conference_edition ce JOIN `" + db_config.DB_NAME + "`.conference c " \
            "ON ce.conference_id = c.id;"
    cursor_edition.execute(query_edition_info)

    row = cursor_edition.fetchone()
    while row:
        acronym = row[0]
        edition_id = row[1]
        year = row[2]
        url = row[3]
        try:
            query = "INSERT IGNORE INTO `" + db_config.DB_NAME + "`.paper " \
                    "SELECT id, doi, NULL, `" + db_config.DB_NAME + "`.calculate_num_of_pages(pages), title, url, " + str(edition_id) + ", 1 " \
                    "FROM `" + DBLP_DATABASE + "`.dblp_pub_new " \
                    "WHERE SUBSTRING_INDEX(SUBSTRING_INDEX(url, '.html#', 1), '-', 1) = '" + url + "' AND type = 'inproceedings' " \
                    "AND source_id = '" + acronym + "' AND year = " + str(year) + ";"
            cursor_paper.execute(query)
            cnx.commit()
            row = cursor_edition.fetchone()
        except:
            print acronym + " " + str(edition_id) + " " + str(year) + " " + str(url)

    cursor_paper.close()
    cursor_edition.close()


def add_new_journal_papers(cnx):
    cursor_issue = cnx.cursor()
    cursor_paper = cnx.cursor()
    query_issue_info = "SELECT acronym, ji.id as journal_issue_id, ji.url " \
            "FROM `" + db_config.DB_NAME + "`.journal_issue ji JOIN `" + db_config.DB_NAME + "`.journal j " \
            "ON ji.journal_id = j.id;"
    cursor_issue.execute(query_issue_info)

    row = cursor_issue.fetchone()
    while row:
        acronym = row[0]
        issue_id = row[1]
        url = row[2]
        try:
            query = "INSERT IGNORE INTO `" + db_config.DB_NAME + "`.paper " \
                    "SELECT id, doi, NULL, `" + db_config.DB_NAME + "`.calculate_num_of_pages(pages), title, url, " + str(issue_id) + ", 2 " \
                    "FROM `" + DBLP_DATABASE + "`.dblp_pub_new " \
                    "WHERE SUBSTRING_INDEX(url, '#', 1) = '" + url + "' AND type = 'article' " \
                    "AND source_id = '" + acronym + "'"
            cursor_paper.execute(query)
            cnx.commit()
            row = cursor_issue.fetchone()
        except:
            print acronym + " " + str(issue_id) + " " + str(url)

    cursor_paper.close()
    cursor_issue.close()


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


def add_new_paper_stats(cnx):
    cursor = cnx.cursor()
    query = "INSERT IGNORE INTO " + db_config.DB_NAME + ".aux_paper_stats " \
            "SELECT p.id as paper_id, year, MAX(position) AS co_authors, 1/(MAX(position) + 1) AS participation, pages, p.type " \
            "FROM " + db_config.DB_NAME + ".conference_edition ce JOIN ( " \
                                                                    "SELECT p.* " \
                                                                    "FROM " + db_config.DB_NAME + ".aux_paper_stats aux RIGHT JOIN " + db_config.DB_NAME + ".paper p " \
                                                                    "ON p.id = aux.paper_id " \
                                                                    "WHERE aux.paper_id IS NULL AND p.type = 1) as p " \
                                                                "ON p.published_in = ce.id " \
            "JOIN " + db_config.DB_NAME + ".authorship a ON a.paper_id = p.id WHERE p.type = 1 " \
            "GROUP BY p.id " \
            "UNION " \
            "SELECT p.id, year, MAX(position) AS co_authors, 1/(MAX(position) + 1) AS participation, pages, p.type " \
            "FROM " + db_config.DB_NAME + ".journal_issue ji JOIN ( " \
                                                                "SELECT p.* " \
                                                                "FROM " + db_config.DB_NAME + ".aux_paper_stats aux RIGHT JOIN " + db_config.DB_NAME + ".paper p " \
                                                                "ON p.id = aux.paper_id " \
                                                                "WHERE aux.paper_id IS NULL AND p.type = 2) as p " \
                                                            "ON p.published_in = ji.id " \
            "JOIN " + db_config.DB_NAME + ".authorship a ON a.paper_id = p.id WHERE p.type = 2 " \
            "GROUP BY p.id"
    cursor.execute(query)
    cnx.commit()
    cursor.close()


def main():
    cnx = establish_connection()
    select_db(cnx)
    add_new_researchers(cnx)
    add_new_researcher_aliases(cnx)
    add_new_conferences(cnx)
    add_new_conference_editions(cnx)
    add_new_journals(cnx)
    add_new_journal_issues(cnx)
    add_new_conference_papers(cnx)
    add_new_journal_papers(cnx)
    add_new_authorships(cnx)
    add_new_paper_stats(cnx)
    cnx.close()

if __name__ == "__main__":
    main()
