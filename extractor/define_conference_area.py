__author__ = 'atlanmod'

import logging
import mysql.connector
from mysql.connector import errorcode
import os
import database_connection_config as dbconnection

LOG_FILENAME = 'logger_define_conference_area.log'


def create_conference_area_table(cnx):
    cursor = cnx.cursor()
    create_conference_area_table = "CREATE TABLE IF NOT EXISTS " + dbconnection.DATABASE_NAME + "._conference_area" \
                                         "(" \
                                         "source_id varchar(150), " \
                                         "area varchar(150), " \
                                         "primary key (source_id, area), " \
                                         "index _area (area)" \
                                         ");"
    cursor.execute(create_conference_area_table)

    cnx.commit()
    cursor.close()


def update_conference_area_table(cnx):
    cursor = cnx.cursor()
    insert = "INSERT IGNORE INTO " + dbconnection.DATABASE_NAME + "._conference_area " \
             "(source_id, area)" \
             "VALUES " \
             "('uml', 'modeling')," \
             "('models', 'modeling')," \
             "('ecmdafa', 'modeling')," \
             "('icmt', 'modeling')," \
             "('er', 'modeling');"
    cursor.execute(insert)
    cnx.commit()
    cursor.close()

def main():
    logging.basicConfig(filename=LOG_FILENAME, level=logging.WARNING)
    with open(LOG_FILENAME, "w") as log_file:
        log_file.write('\n')
    cnx = mysql.connector.connect(**dbconnection.CONFIG)
    #create conference link table
    create_conference_area_table(cnx)
    #update conference link table
    update_conference_area_table(cnx)

if __name__ == "__main__":
    main()
