__author__ = 'atlanmod'

import logging
import mysql.connector
from mysql.connector import errorcode
from selenium import webdriver
import requests
import gzip
from cStringIO import StringIO
import re
import os
import datetime
import database_connection_config as dbconnection

#This script updates the information stored in the database.
#In particular, it retrieves the last dump of the DBLP database (available here -> http://dblp.l3s.de/dblp++.php)
#and updates the dblp tables and the aux tables

CONFERENCES = "'ICSE', 'FSE', 'ESEC', 'ASE', 'SPLASH', 'OOPSLA', 'ECOOP', 'ISSTA', 'FASE', " \
            "'MODELS', 'WCRE', 'CSMR', 'ICMT', 'COMPSAC', 'APSEC', 'VISSOFT', 'ICSM', 'SOFTVIS', " \
            "'SCAM', 'TOOLS', 'CAISE', 'ER', 'ECMFA', 'ECMDA-FA'"
STARTING_YEAR = 2013
DBLP_DUMP = 'http://dblp.l3s.de/dblp++.php'
DUMP_LOCATION = '../facetedDBLP/'
LOG_FILENAME = 'logger_update_database.log'

def update_dblp_tables(database_name):
    driver = webdriver.Chrome(executable_path='C:\Program Files (x86)\Google\Chrome\chromedriver.exe')
    driver.get(DBLP_DUMP)
    link = driver.find_element_by_link_text("database dump")
    href = link.get_attribute('href')
    driver.close()
    dump_name = re.sub("\.gz", "", href.split('/').pop())

    try:
        response = requests.get(href, timeout=5)
        results = gzip.GzipFile(fileobj=StringIO(response.content))
        data = results.read()

    except:
        logging.warning(href + ' not found!')

    #write dump content into a file located into facetedDBLP
    dump_path = os.path.abspath(DUMP_LOCATION + dump_name)

    file = open(dump_path, "w")
    file.write(data)
    file.close()

    #import data into the database
    os.system("mysql --host=" + dbconnection.CONFIG.get('host') +
              " --user=" + dbconnection.CONFIG.get('user') +
              " --password=" + dbconnection.CONFIG.get('password') +
              " --port=" + dbconnection.CONFIG.get('port') +
              " --default-character-set=utf8 "
              " --comments "
              " --database=" + database_name + " < " + dump_path)

    #delete dump file
    os.remove(dump_path)


def update_aux_dblp_proceedings(cnx):
    cursor = cnx.cursor()
    query = "INSERT INTO dblp.aux_dblp_proceedings " \
            "SELECT NULL, id as dblp_id, dblp_key, url, source, year, NULL, NULL, NULL, NULL " \
            "FROM dblp.dblp_pub_new where type = 'proceedings' " \
            "AND dblp_key NOT IN (SELECT dblp_key FROM dblp.aux_dblp_proceedings) " \
            "AND year >= " + str(STARTING_YEAR) + " " \
            "AND source IN (" + CONFERENCES + ")"
    cursor.execute(query)
    cnx.commit()
    cursor.close()


def update_aux_dblp_inproceedings_tracks(cnx):
    cursor = cnx.cursor()
    query = "INSERT INTO dblp.aux_dblp_inproceedings_tracks " \
            "SELECT NULL, id as dblp_id, dblp_key, crossref, url, title, NULL, NULL, NULL, NULL " \
            "FROM dblp.dblp_pub_new where type = 'inproceedings' " \
            "AND dblp_key NOT IN (SELECT dblp_key FROM dblp.aux_dblp_inproceedings_tracks) " \
            "AND year >= " + str(STARTING_YEAR) + " " \
            "AND source IN (" + CONFERENCES + ")"
    cursor.execute(query)
    cnx.commit()
    cursor.close()


def create_dblp_dump(database_name):
    i = datetime.datetime.now()
    current_date = i.strftime('%Y-%m-%d')

    current_dump = DUMP_LOCATION + "conf_db_dump-" + current_date + ".sql"

    os.system("mysqldump --host=" + dbconnection.CONFIG.get('host') + " " + database_name +
              " --user=" + dbconnection.CONFIG.get('user') +
              " --password=" + dbconnection.CONFIG.get('password') +
              " --port=" + dbconnection.CONFIG.get('port') +
              " --default-character-set=utf8 "
              " > " + current_dump)


def main():
    logging.basicConfig(filename=LOG_FILENAME, level=logging.WARNING)
    with open(LOG_FILENAME, "w") as log_file:
        log_file.write('\n')
    cnx = mysql.connector.connect(**dbconnection.CONFIG)

    #create a dump of the current database
    create_dblp_dump(dbconnection.CONFIG.get("database"))
    #update tables
    update_dblp_tables(dbconnection.DATABASE_NAME)
    update_aux_dblp_proceedings(cnx)
    update_aux_dblp_inproceedings_tracks(cnx)

    #execute scripts
    ##adding_conference_rank script should not be executed every time,
    ## since a conference rank does not change from one month to the next
    os.system("adding_conference_rank.py")

    os.system("adding_conference_info.py")
    os.system("adding_paper_track_info.py")
    os.system("adding_paper_citations.py")

    ##note that the script that updates the program committee can be executed separately,
    ##since it mainly relies on the information contained into the program_committee_info.json
    os.system("extracting_program_committee.py")

if __name__ == "__main__":
    main()