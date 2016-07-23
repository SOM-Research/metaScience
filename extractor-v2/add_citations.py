__author__ = 'valerio cosentino'

import mysql.connector
from mysql.connector import errorcode
import db_config

#downloaded from https://aminer.org/citation
SOURCE_PATHS = ["../data/dblp.txt", "../data/citation-acm-v8.txt"]

def select_db(cnx):
    cursor = cnx.cursor()
    cursor.execute("USE " + db_config.DB_NAME)
    cursor.close()


def establish_connection():
    return mysql.connector.connect(**db_config.CONFIG)


def drop_temp_tables(cnx):
    cursor = cnx.cursor()
    cursor.execute("DROP TABLE IF EXISTS " + db_config.DB_NAME + ".temp_paper_mapper")
    cursor.execute("DROP TABLE IF EXISTS " + db_config.DB_NAME + ".temp_paper_citations")
    cursor.close()


def create_citations_tables_for_citations(cnx):
    drop_temp_tables(cnx)
    cursor = cnx.cursor()
    create_table_paper_mapper = "CREATE TABLE " + db_config.DB_NAME + ".temp_paper_mapper( " \
                                      "aimer_id VARCHAR(512) PRIMARY KEY, " \
                                      "title VARCHAR(255), " \
                                      "metascience_id BIGINT(20), " \
                                      "INDEX mi (metascience_id) " \
                                      ") ENGINE=InnoDB DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC;"

    create_table_citations = "CREATE TABLE " + db_config.DB_NAME + ".temp_paper_citations( " \
                                      "paper_id VARCHAR(512), " \
                                      "cited_paper VARCHAR(255), " \
                                      "PRIMARY KEY (paper_id, cited_paper) " \
                                      ") ENGINE=InnoDB DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC;"

    cursor.execute(create_table_paper_mapper)
    cursor.execute(create_table_citations)
    cursor.close()


def populate_mapper(cnx, paper_id, paper_title):
    cursor = cnx.cursor()
    query = "INSERT IGNORE INTO " + db_config.DB_NAME + ".temp_paper_mapper VALUES(%s, %s, %s)"
    arguments = [paper_id, paper_title.strip("."), None]
    cursor.execute(query, arguments)
    cnx.commit()
    cursor.close()


def populate_citations(cnx, paper_id, cited_paper_ids):
    cursor = cnx.cursor()

    for cited_paper_id in cited_paper_ids:
        query = "INSERT IGNORE INTO " + db_config.DB_NAME + ".temp_paper_citations VALUES(%s, %s)"
        arguments = [paper_id, cited_paper_id]
        cursor.execute(query, arguments)
        cnx.commit()
    cursor.close()


def populate_temp_tables(cnx, paper_id, paper_title, cited_paper_ids):
    populate_mapper(cnx, paper_id, paper_title)
    populate_citations(cnx, paper_id, cited_paper_ids)


def get_paper_id(list):
    paper_id = None
    for e in list:
        if e.startswith("#index"):
            paper_id = e.replace("#index", "").strip()
            break

    return paper_id


def get_cited_papers(list):
    cited_papers = []
    for e in list:
        if e.startswith("#%"):
            citing_id = e.replace("#%", "").strip()
            cited_papers.append(citing_id)

    return cited_papers


def collect_citations_information(cnx, source_path):
    block = []

    with open(source_path, "r") as f:
        for line in f:
            if line in ['\n', '\r\n']:
                paper_title = block[0].replace("#*", "").strip().rstrip('.')
                paper_id = get_paper_id(block)
                cited_paper_ids = get_cited_papers(block)
                populate_temp_tables(cnx, paper_id, paper_title, cited_paper_ids)
                del block[:]
            else:
                block.append(line)


def perform_mapping(cnx):
    cursor = cnx.cursor()
    query = "UPDATE " + db_config.DB_NAME + ".temp_paper_mapper pm, " + db_config.DB_NAME + ".paper p " \
            "SET pm.metascience_id = p.id WHERE pm.title = p.title;"
    cursor.execute(query)
    cnx.commit()
    cursor.close()


def populate_paper_is_cited_table(cnx):
    cursor = cnx.cursor()
    query = "INSERT IGNORE INTO " + db_config.DB_NAME + ".paper_is_cited " \
            "SELECT reference.metascience_id AS paper_cites, paper.metascience_id AS paper_is_cited " \
            "FROM " + db_config.DB_NAME + ".temp_paper_mapper paper JOIN " + db_config.DB_NAME + ".temp_paper_citations cit ON paper.aimer_id = cit.paper_id " \
            "JOIN " + db_config.DB_NAME + ".temp_paper_mapper reference ON reference.aimer_id = cit.cited_paper " \
            "WHERE paper.metascience_id IS NOT NULL AND reference.metascience_id IS NOT NULL;"
    cursor.execute(query)
    cnx.commit()
    cursor.close()


def main():
    cnx = establish_connection()
    select_db(cnx)

    for sp in SOURCE_PATHS:
        create_citations_tables_for_citations(cnx)
        collect_citations_information(cnx, sp)
        perform_mapping(cnx)
        populate_paper_is_cited_table(cnx)
        drop_temp_tables(cnx)

    cnx.close()


if __name__ == "__main__":
    main()
