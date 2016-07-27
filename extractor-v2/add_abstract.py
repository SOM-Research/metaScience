__author__ = 'valerio cosentino'

import mysql.connector
from mysql.connector import errorcode
import db_config

#downloaded from https://aminer.org/citation
SOURCE_PATH = "../data/citation-acm-v8.txt"


def select_db(cnx):
    cursor = cnx.cursor()
    cursor.execute("USE " + db_config.DB_NAME)
    cursor.close()


def establish_connection():
    return mysql.connector.connect(**db_config.CONFIG)


def get_paper_id(cnx, title):
    paper_id = None
    cursor = cnx.cursor()
    query = "SELECT id " \
            "FROM " + db_config.DB_NAME + ".paper p " \
            "WHERE p.title = %s AND abstract IS NULL"
    arguments = [title]
    cursor.execute(query, arguments)

    row = cursor.fetchone()
    if row:
        paper_id = row[0]

    cursor.close()

    return paper_id


def insert_abstract(cnx, paper_id, abstract):
    cursor = cnx.cursor()
    query = "UPDATE " + db_config.DB_NAME + ".paper SET abstract = %s WHERE id = %s"
    arguments = [abstract, paper_id]
    cursor.execute(query, arguments)
    cnx.commit()
    cursor.close()


def get_paper_abstract(list):
    abstract = ""
    in_abstract = False
    for e in list:
        if e.startswith("#!"):
            abstract = e.replace("#!", "")
            in_abstract = True
        else:
            if in_abstract:
                abstract += e

    return abstract


def collect_abstract_information(cnx):
    block = []

    with open(SOURCE_PATH, "r") as f:
        for line in f:
            if line in ['\n', '\r\n']:
                paper_title = block[0].replace("#*", "").strip()
                abstract = get_paper_abstract(block)

                if abstract:
                    paper_id = get_paper_id(cnx, paper_title)
                    if paper_id:
                        insert_abstract(cnx, paper_id, abstract)
                del block[:]
            else:
                block.append(line)


def main():
    cnx = establish_connection()
    select_db(cnx)
    collect_abstract_information(cnx)
    cnx.close()


if __name__ == "__main__":
    main()
