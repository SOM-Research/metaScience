import logging
import mysql.connector
from mysql.connector import errorcode
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
import time
import cross_module_variables as shared
import re
import database_connection_config as dbconnection

LOG_FILENAME = 'logger_conference_title.log'
driver = webdriver.PhantomJS()

# This script gathers (via Selenium) the TITLE for each proceedings in DBLP
# and add them to the table AUX_DBLP_PROCEEDINGS.
#
# The table AUX_DBLP_PROCEEDINGS is derived from DBLP_PUB_NEW

def update_title_conference(cnx, dblp_key, id):
    title = get_dblp_full_name_conference(dblp_key)

    cursor = cnx.cursor()
    query = "UPDATE aux_dblp_proceedings SET title = %s WHERE id = %s"
    arguments = [title, id]
    cursor.execute(query, arguments)
    cnx.commit()
    cursor.close()


def get_dblp_full_name_conference(dblp_key):
    title = ""
    conf_info = dblp_key.split("/")
    link = "db/" + conf_info[0] + "/" + conf_info[1] + "/" + "index.html"
    driver.get(shared.DBLP + "/" + link)
    try:
        title = re.sub("\(.*\)", "", driver.find_element_by_id("headline").find_element_by_tag_name("h1").text)
    except NoSuchElementException:
        logging.info("title for " + link + " not found!")

    return title


def add_proceedings_info(cnx, id):
    conf_cursor = cnx.cursor()
    query = "SELECT id, dblp_key, url " \
            "FROM aux_dblp_proceedings " \
            "WHERE dblp_key IS NOT NULL AND " \
            "title IS NULL AND " \
            "location IS NULL AND " \
            "type IS NULL AND " \
            "month IS NULL AND " \
            "rank IS NULL AND " \
            "id > %s "
    arguments = [id]
    conf_cursor.execute(query, arguments)
    row = conf_cursor.fetchone()
    proceedings = "empty"
    while row is not None:
        id = row[0]
        dblp_key = row[1]
        proceedings = row[2]
        update_title_conference(cnx, dblp_key, id)
        row = conf_cursor.fetchone()
        logging.warning("last conf analysed " + str(proceedings))

    conf_cursor.close()


# This method is used to recover an execution that went wrong.
# It restart the extraction process from the last id entered in the database
# To activate the recover process, just activate the flag "RECOVER_PROCESS"
def get_id_to_start(cnx):
    conf_cursor = cnx.cursor()
    query = "SELECT MAX(id) " \
            "FROM aux_dblp_proceedings " \
            "WHERE title IS NOT NULL"
    conf_cursor.execute(query)
    row = conf_cursor.fetchone()
    return row[0]

RECOVER_PROCESS = True

def main():
    logging.basicConfig(filename=LOG_FILENAME, level=logging.WARNING)
    with open(LOG_FILENAME, "w") as log_file:
        log_file.write('\n')
    cnx = mysql.connector.connect(**dbconnection.CONFIG)
    #set the row id from the table 'aux_dblp_proceedings' to start extracting the conference information
    id_to_start = 0
    if RECOVER_PROCESS:
        id = get_id_to_start(cnx)
        if id is not None:
            id_to_start = int(id)

    add_proceedings_info(cnx, id_to_start)
    driver.close()

if __name__ == "__main__":
    main()