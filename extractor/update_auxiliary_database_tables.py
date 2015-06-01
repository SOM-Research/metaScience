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

CREATE_DUMP_DB = 0
UPDATE_DBLP_TABLES = 0
UPDATE_AUX_TABLES = 1
EXTRACT_ABSTRACTS = 0
EXTRACT_PROGRAM_COMMITTEES = 0

#activate manual/automatic process
MANUAL = 0

#parameters for the automatic process
#select the minum number of editions per conference
MIN_NUMBER_OF_EDITIONS = 2
#select the starting year to collect the conferences
DEFAULT_STARTING_YEAR = 1936

#parameters for the manual process
#select the acronyms of the conferences to analyse
CONFERENCES = "'ICSE', 'SIGSOFT FSE', 'ESEC/SIGSOFT FSE', 'ASE', 'SPLASH', 'OOPSLA', 'ECOOP', 'ISSTA', 'FASE', " \
              "'MODELS', 'WCRE', 'CSMR', 'CSMR-WCRE', 'ICMT', 'COMPSAC', 'MSR', 'APSEC', 'VISSOFT', 'ICSM', 'SOFTVIS', " \
              "'SCAM', 'TOOLS', 'CAISE', 'ER', 'ECMFA', 'ECMDA-FA', 'MSR'"
#select the starting year to collect the conferences
STARTING_YEAR = 2003

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


def update_aux_dblp_proceedings(cnx, starting_year):
    cursor = cnx.cursor()
    query = "INSERT INTO dblp.aux_dblp_proceedings " \
            "SELECT NULL, id as dblp_id, dblp_key, url, source, year, NULL, NULL, NULL, NULL, NULL " \
            "FROM dblp.dblp_pub_new where type = 'proceedings' " \
            "AND id NOT IN (SELECT dblp_id FROM dblp.aux_dblp_proceedings) " \
            "AND year >= " + str(starting_year) + " " \
            "AND source IN (" + CONFERENCES + ")"
    cursor.execute(query)
    cnx.commit()
    cursor.close()


def update_aux_dblp_inproceedings_tracks(cnx, starting_year):

    cursor = cnx.cursor()
    query = "INSERT INTO dblp.aux_dblp_inproceedings_tracks " \
            "SELECT NULL, id as dblp_id, dblp_key, crossref, url, CONVERT(CONVERT(title USING ascii) USING utf8), NULL, NULL, NULL, NULL,NULL " \
            "FROM dblp.dblp_pub_new where type = 'inproceedings' " \
            "AND id NOT IN (SELECT dblp_id FROM dblp.aux_dblp_inproceedings_tracks) " \
            "AND year >= " + str(starting_year) + " " \
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


def select_conferences_and_starting_year(cnx):
    #if the variable MANUAL is set to 0
    #collect in the variable CONFERENCES all the sources for the conferences that have more than x editions.
    #The value of x is stored in MIN_NUMBER_OF_EDITIONS
    #if the variable MANUAL is set to 1, the process will load the conferences that have their source in the variable CONFERENCES

    if not MANUAL:
        cursor = cnx.cursor()
        query = "SELECT source FROM " \
                    "(" \
                    "SELECT source, count(*) as num_of_editions " \
                    "FROM dblp.dblp_pub_new " \
                    "WHERE source is not null AND type = 'proceedings' group by source" \
                    ") as x " \
                "WHERE num_of_editions >= %s"
        arguments = [MIN_NUMBER_OF_EDITIONS]
        cursor.execute(query, arguments)

        result = cursor.fetchall()

        global CONFERENCES
        CONFERENCES = ""

        starting_year = DEFAULT_STARTING_YEAR

        for r in result:
            if result[-1][0] == r[0]:
                CONFERENCES += "\"" + r[0] + "\""
            else:
                CONFERENCES += "\"" + r[0] + "\"" + ","

        cursor.close()
    else:
        starting_year = STARTING_YEAR

    return starting_year


def main():
    logging.basicConfig(filename=LOG_FILENAME, level=logging.WARNING)
    with open(LOG_FILENAME, "w") as log_file:
        log_file.write('\n')
    cnx = mysql.connector.connect(**dbconnection.CONFIG)

    if CREATE_DUMP_DB:
        #create a dump of the current database
        create_dblp_dump(dbconnection.CONFIG.get("database"))

    #select conferences to update..manual or automatic
    starting_year = select_conferences_and_starting_year(cnx)

    if UPDATE_DBLP_TABLES:
        #update dblp tables (download the latest dump and substitute the old tables)
        update_dblp_tables(dbconnection.DATABASE_NAME)

    if UPDATE_AUX_TABLES:
        #update aux tables
        update_aux_dblp_proceedings(cnx, starting_year)
        update_aux_dblp_inproceedings_tracks(cnx, starting_year)

        #execute scripts
        ##adding_conference_rank script should not be executed every time,
        ## since a conference rank does not change from one month to the next
        os.system("adding_conference_rank.py")

        os.system("adding_conference_info.py")
        os.system("adding_paper_track_info.py")
        os.system("adding_paper_citations.py")

    if EXTRACT_ABSTRACTS:
        os.system("adding_paper_abstract.py")

    if EXTRACT_PROGRAM_COMMITTEES:
        ##note that the script that updates the program committee can be executed separately,
        ##since it mainly relies on the information contained into the program_committee_info.json
        os.system("extracting_program_committee.py")

if __name__ == "__main__":
    main()
