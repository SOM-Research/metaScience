import logging
import mysql.connector
from mysql.connector import errorcode
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
import time
import cross_module_variables as shared
import re
import database_connection_config as dbconnection

LOG_FILENAME = 'logger_conference_type.log'
driver = webdriver.PhantomJS()

# This script gathers (via Selenium) the TITLE for each proceedings in DBLP
# and add them to the table AUX_DBLP_PROCEEDINGS.
#
# The table AUX_DBLP_PROCEEDINGS is derived from DBLP_PUB_NEW

def update_type_conference(cnx, dblp_key):
    conf_cursor = cnx.cursor()
    query = "SELECT title FROM dblp_pub_new WHERE type='proceedings' AND BINARY dblp_key = %s"
    arguments = [dblp_key]
    conf_cursor.execute(query, arguments)
    title = conf_cursor.fetchone()[0]
	
    cursor = cnx.cursor()
    type = ''
    if 'workshop' in title.lower():
        type = 'workshop'
    elif 'conference' in title.lower():
        type = 'conference'
    elif 'symposium' in title.lower():
        type = 'symposium'

    query = "UPDATE aux_dblp_proceedings SET type = %s WHERE BINARY dblp_key = %s"
    arguments = [type, dblp_key]
    cursor.execute(query, arguments)
    cnx.commit()

    cursor.close()

def add_type_info(cnx):
    conf_cursor = cnx.cursor()
    query = "SELECT id, dblp_key " \
            "FROM aux_dblp_proceedings " \
            "WHERE dblp_key IS NOT NULL AND title is not NULL"
    conf_cursor.execute(query)
    row = conf_cursor.fetchone()
    while row is not None:
        id = row[0]
        dblp_key = row[1]
        update_type_conference(cnx, dblp_key)
        row = conf_cursor.fetchone()
        logging.warning("last conf analysed " + str(dblp_key))

    conf_cursor.close()

def main():
    logging.basicConfig(filename=LOG_FILENAME, level=logging.WARNING)
    with open(LOG_FILENAME, "w") as log_file:
        log_file.write('\n')
    cnx = mysql.connector.connect(**dbconnection.CONFIG)
    add_type_info(cnx)
    driver.close()

if __name__ == "__main__":
    main()