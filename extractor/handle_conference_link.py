__author__ = 'atlanmod'

import logging
import mysql.connector
from mysql.connector import errorcode
import os
import database_connection_config as dbconnection

LOG_FILENAME = 'logger_handle_conference_link.log'


def create_conference_link_table(cnx):
    cursor = cnx.cursor()
    create_conference_link_table = "CREATE TABLE IF NOT EXISTS " + dbconnection.DATABASE_NAME + "._conference_link" \
                                         "(" \
                                         "source_id varchar(150), " \
                                         "link varchar(150), " \
                                         "primary key (source_id), " \
                                         "index _link (link)" \
                                         ");"
    cursor.execute(create_conference_link_table)

    cnx.commit()
    cursor.close()


def update_conference_link_table(cnx):
    cursor = cnx.cursor()
    insert = "INSERT IGNORE INTO " + dbconnection.DATABASE_NAME + "._conference_link " \
             "(source_id, link)" \
             "VALUES " \
             "('uml', 'now_models')," \
             "('models', 'now_models');"
    cursor.execute(insert)
    cnx.commit()
    cursor.close()

def main():
    logging.basicConfig(filename=LOG_FILENAME, level=logging.WARNING)
    with open(LOG_FILENAME, "w") as log_file:
        log_file.write('\n')
    cnx = mysql.connector.connect(**dbconnection.CONFIG)
    #create conference link table
    create_conference_link_table(cnx)
    #update conference link table
    update_conference_link_table(cnx)

if __name__ == "__main__":
    main()
