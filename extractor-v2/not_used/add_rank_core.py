__author__ = 'valerio cosentino'

import csv
import mysql.connector
from mysql.connector import errorcode
import re
import db_config

CVS_PATH = "data/CORE.csv"


def process_title(title):
    return re.sub('\(.*\)', '', title)


def get_rank_id(rank):
    id = None
    if rank == 'A*': id = 1
    elif rank == 'A': id = 2
    elif rank == 'B': id = 3
    elif rank == 'C': id = 4

    return id


def find_match(cnx, acronym, title, rank):
    cursor = cnx.cursor()
    query = "SELECT id " \
            "FROM `" + db_config.DB_NAME + "`.conference " \
            "WHERE acronym = %s or name = %s"
    arguments = [acronym]
    cursor.execute(query, arguments)
    row = cursor.fetchone()

    if not row:
        print 'no match for ' + title + '(' + acronym + ') ' + rank
    else:
        conference_id = row[0]
        rank_id = get_rank_id(rank)
        cursor_update = cnx.cursor()
        update = "UPDATE `" + db_config.DB_NAME + "`.conference SET rank_id = %s WHERE id = %s"
        arguments = [rank_id, conference_id]
        cursor_update.execute(update, arguments)
        cnx.commit()
        cursor_update.close()

    cursor.close()


def select_db(cnx):
    cursor = cnx.cursor()
    cursor.execute("USE " + db_config.DB_NAME)
    cursor.close()


def establish_connection():
    return mysql.connector.connect(**db_config.CONFIG)


def main():
    input = open(CVS_PATH, 'rb')
    reader = csv.reader(input)

    cnx = establish_connection()
    select_db(cnx)

    for row in reader:
        title = process_title(row[1])
        acronym = row[2]
        rank = row[4]

        if rank != 'Australasian':
            find_match(cnx, acronym, title, rank)

    input.close()
    cnx.close()

if __name__ == "__main__":
    main()
