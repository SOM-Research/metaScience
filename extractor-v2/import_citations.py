__author__ = 'valerio cosentino'

import mysql.connector
from mysql.connector import errorcode
import db_config

#download from https://aminer.org/citation
SOURCE_PATH = "./dblp.txt"

def select_db(cnx):
    cursor = cnx.cursor()
    cursor.execute("USE " + db_config.DB_NAME)
    cursor.close()


def establish_connection():
    return mysql.connector.connect(**db_config.CONFIG)


def create_citations_tables_for_citations(cnx):
    cursor = cnx.cursor()
    cursor.execute("DROP TABLE IF EXISTS " + db_config.DB_NAME + ".temp_paper_mapper")
    cursor.execute("DROP TABLE IF EXISTS " + db_config.DB_NAME + ".temp_paper_citations")

    create_table_paper_mapper = "CREATE TABLE " + db_config.DB_NAME + ".temp_paper_mapper( " \
                                      "aimer_id VARCHAR(512) PRIMARY KEY, " \
                                      "title VARCHAR(255), " \
                                      "metascience_id BIGINT(20), " \
                                      "INDEX mi (metascience_id) " \
                                      ") ENGINE=InnoDB DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC;"

    create_table_citations = "CREATE TABLE " + db_config.DB_NAME + ".temp_paper_citations( " \
                                      "paper_id VARCHAR(512) PRIMARY KEY, " \
                                      "citing_paper VARCHAR(255), " \
                                      "INDEX cp (citing_paper) " \
                                      ") ENGINE=InnoDB DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC;"

    cursor.execute(create_table_paper_mapper)
    cursor.execute(create_table_citations)
    cursor.close()


def populate_mapper(cnx, paper_id, paper_title):
    cursor = cnx.cursor()
    query = "INSERT IGNORE INTO " + db_config.DB_NAME + ".temp_paper_mapper VALUES(%s, %s, %s)"
    arguments = [paper_id, paper_title, None]
    cursor.execute(query, arguments)
    cnx.commit()
    cursor.close()


def populate_citations(cnx, paper_id, citing_paper_ids):
    cursor = cnx.cursor()

    for paper_id in citing_paper_ids:
        query = "INSERT IGNORE INTO " + db_config.DB_NAME + ".temp_paper_citations VALUES(%s, %s)"
        arguments = [paper_id, paper_id]
        cursor.execute(query, arguments)
        cnx.commit()
    cursor.close()


def populate_temp_tables(cnx, paper_id, paper_title, citing_paper_ids):
    populate_mapper(cnx, paper_id, paper_title)
    populate_citations(cnx, paper_id, citing_paper_ids)


def get_paper_id(list):
    paper_id = None
    for e in list:
        if e.startswith("#index"):
            paper_id = e.replace("#index", "").strip()
            break

    return paper_id


def get_citing_papers(list):
    citing_papers = []
    for e in list:
        if e.startswith("#%"):
            citing_id = e.replace("#%", "").strip()
            citing_papers.append(citing_id)

    return citing_papers


def collect_citations_information(cnx):
    block = []
    with open(SOURCE_PATH, "r") as f:
        for line in f:
            if line in ['\n', '\r\n']:
                paper_title = block[0].replace("#*", "").strip()
                paper_id = get_paper_id(block)
                citing_paper_ids = get_citing_papers(block)
                populate_temp_tables(cnx, paper_id, paper_title, citing_paper_ids)
                del block[:]
            else:
                block.append(line)


def main():
    cnx = establish_connection()
    select_db(cnx)
    create_citations_tables_for_citations(cnx)
    collect_citations_information(cnx)
    cnx.close()


if __name__ == "__main__":
    main()
