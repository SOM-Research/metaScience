__author__ = 'atlanmod'

import logging
import mysql.connector
from mysql.connector import errorcode
import json
import codecs
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import db_config
import time
import re

#This script gathers (via Selenium) the PROGRAM COMMITTEE CHAIR and MEMBERS
#for the editions from 2003 of the conferences defined in the pc_info.json
#Currently, we track
#ICSE, FSE, ESEC, ASE, SPLASH, OOPSLA, ECOOP, ISSTA, FASE,
#MODELS, WCRE, CSMR, ICMT, COMPSAC, APSEC, VISSOFT, ICSM, SOFTVIS,
#SCAM, TOOLS, CAISE, ER, ECMFA, ECMDA-FA, MSR
#The configuration of the json file is explained clearly in the main()

EXCEPTION_NAMES_PATH = '../data/program-committee-exceptions.json'
EXCEPTION_NAMES = None

WAIT_TIME = 5
LOG_FILENAME = 'logger_program_committee.log'
GOOGLE = 'http://www.google.com'
DBLP = 'dblp.uni-trier.de/pers/'
SCHOLAR = 'scholar.google'

INPUT = "../data/er_pc_members.txt"
driver = webdriver.Chrome(executable_path='C:\Program Files (x86)\Google\Chrome\chromedriver.exe')


def calculate_query(cnx, query, arguments):
    cursor = cnx.cursor()
    cursor.execute(query, arguments)
    data = cursor.fetchone()
    cursor.close()
    return data


def check_data_returned(data, member):
    if len(data) == 0:
        logging.warning("insertion - member not found in dblp: " + member)
    elif len(data) > 1:
        logging.warning("insertion - multiple entries for member: " + member + "! ids:" + ','.join([str(d[0]) for d in data]))


def query_metascience(cnx, member):
    researcher_id = None
    data = None

    query_researcher = "SELECT id FROM `" + db_config.DB_NAME + "`.researcher WHERE name = %s;"
    query_researcher_alias = "SELECT researcher_id FROM `" + db_config.DB_NAME + "`.researcher_alias WHERE alias = %s;"

    queries = [query_researcher, query_researcher_alias]
    pos = 0
    while data is None and len(queries)-1 >= pos:
        arguments = [member]
        data = calculate_query(cnx, queries[pos], arguments)
        if data:
            check_data_returned(data, member)
            researcher_id = data[0]
            break
        pos += 1

    return researcher_id


def insert_new_alias(cnx, researcher_id, alias):
    cursor = cnx.cursor()
    insert = "INSERT IGNORE INTO `" + db_config.DB_NAME + "`.researcher_alias VALUES (%s, %s)"
    arguments = [researcher_id, alias]
    cursor.execute(insert, arguments)
    cnx.commit()
    cursor.close()


def get_name_on_scholar_via_google(cnx, venue, name, year, role):
    data = []
    driver.get(GOOGLE)
    search_box = driver.find_element_by_name("q")

    search_box.send_keys(name + " scholar " + venue + Keys.RETURN)

    #wait
    time.sleep(WAIT_TIME)
    google_hits = driver.find_elements_by_xpath("//*[@class='g']//h3/a")
    for hit in google_hits:
        if SCHOLAR in hit.text and 'citations' in hit.text:
            name = re.sub('- Google.*', '', hit.text).strip()

            query_dblp_author = "SELECT DISTINCT id FROM `" + db_config.DB_NAME + "`.researcher WHERE name = %s UNION " \
                                "SELECT researcher_id FROM `" + db_config.DB_NAME + "`.researcher_alias WHERE alias = %s"
            arguments = [name, name]
            data = calculate_query(cnx, query_dblp_author, arguments)
            if data:
                insert_new_alias(cnx, data[0], name)
                logging.warning("insertion - the researcher: (" + name + "," + str(data[0]) + ") has been matched to: " + name + " role/venue/year " + role + "/" + venue + "/" + str(year))
                break
            else:
                get_name_on_dblp_via_google(cnx, venue, name)

    if data:
        found = data[0]
    else:
        found = None

    return found


def get_name_on_dblp_via_google(cnx, venue, name, year, role):
    data = []
    driver.get(GOOGLE)
    search_box = driver.find_element_by_name("q")

    search_box.send_keys(name + " dblp " + venue + Keys.RETURN)

    #wait
    time.sleep(WAIT_TIME)
    google_hits = driver.find_elements_by_xpath("//*[@class='g']//h3/a")
    for hit in range(len(google_hits)):
        link = google_hits[hit].get_attribute("href")
        if DBLP in link and 'pers' in link:
            google_hits[hit].click()
            time.sleep(WAIT_TIME)
            try:
                dblp_name = driver.find_element_by_id("headline").find_element_by_tag_name("h1").text.strip()
            except:
                dblp_name = driver.find_element_by_xpath("//h1[contains(@id,'homepages')]").text

            query_dblp_author = "SELECT DISTINCT id FROM `" + db_config.DB_NAME + "`.researcher WHERE name = %s UNION " \
                                "SELECT researcher_id FROM `" + db_config.DB_NAME + "`.researcher_alias WHERE alias = %s"
            arguments = [dblp_name, dblp_name]
            data = calculate_query(cnx, query_dblp_author, arguments)
            if data:
                insert_new_alias(cnx, data[0], name)
                logging.warning("matched - the researcher: (" + name + "," + str(data[0]) + ") has been matched to: " + dblp_name +
                                " role/venue/year " + role + "/" + venue + "/" + str(year))
                break
            else:
                driver.back()
                time.sleep(2)
                google_hits = driver.find_elements_by_xpath("//*[@class='g']//h3/a")

    if data:
        found = data[0]
    else:
        found = None

    return found


def get_researcher_id(cnx, venue, name, year, role):
    if EXCEPTION_NAMES.has_key(name):
        logging.warning("changing - the researcher: " + name + " has been changed to " + EXCEPTION_NAMES.get(name) +
                        " role/venue/year " + role + "/" + venue + "/" + str(year))
        name = EXCEPTION_NAMES.get(name)

    researcher_id = query_metascience(cnx, name)

    if not researcher_id:
        researcher_id = get_name_on_dblp_via_google(cnx, venue, name, year, role)

    if not researcher_id:
        researcher_id = get_name_on_scholar_via_google(cnx, venue, name, year, role)

    return researcher_id


def get_conference_id(cnx, venue, year):
    conference_edition_id = None
    cursor = cnx.cursor()
    query = "SELECT ce.id " \
            "FROM `" + db_config.DB_NAME + "`.conference c JOIN `" + db_config.DB_NAME + "`.conference_edition ce " \
            "ON c.id = ce.conference_id " \
            "WHERE acronym = '" + venue + "' AND year = %s"
    arguments = [year]
    cursor.execute(query, arguments)

    row = cursor.fetchone()
    if row:
        conference_edition_id = row[0]

    cursor.close()

    return conference_edition_id


def insert_program_committe_member(cnx, conference_edition_id, researcher_id, is_chair):
    cursor = cnx.cursor()
    query = "INSERT IGNORE INTO `" + db_config.DB_NAME + "`.program_committee VALUES(%s, %s, %s)"
    arguments = [researcher_id, is_chair, conference_edition_id]
    cursor.execute(query, arguments)
    cnx.commit()
    cursor.close()


def is_chair(role):
    flag = 0
    if role == "chair":
        flag = 1
    return flag


def digest_name(name):
    no_parenthesis = re.sub("\(.*\)", "", name)
    no_alpha = re.sub(r"^\W+|\W+$", "", no_parenthesis)
    return no_alpha.strip()


def insert_in_db(cnx, members, role, venue, year):
    conference_edition_id = get_conference_id(cnx, venue, year)

    if conference_edition_id:
        for member in members:
            digested = digest_name(member)
            researcher_id = get_researcher_id(cnx, venue, digested, year, role)
            if researcher_id:
                insert_program_committe_member(cnx, conference_edition_id, researcher_id, is_chair(role))
            else:
                #TODO if a researcher is not found, what do we do?
                logging.warning("insertion - the researcher " + digested + " has not been found for role/venue/year " + role + "/" + venue + "/" + str(year))


def establish_connection():
    return mysql.connector.connect(**db_config.CONFIG)


def init_global_variables():
    global EXCEPTION_NAMES
    with open(EXCEPTION_NAMES_PATH) as data_file:
        EXCEPTION_NAMES = json.load(data_file, "utf-8")


def main():
    logging.basicConfig(filename=LOG_FILENAME, level=logging.WARNING)
    with open(LOG_FILENAME, "w") as log_file:
        log_file.write('\n')
    cnx = establish_connection()
    init_global_variables()
    json_file = codecs.open(INPUT, 'r', 'utf-8')
    json_lines = json_file.read()
    for line in json_lines.split('\n'):
        if line.strip() != '':
            if not line.startswith("#") and len(line.strip()) > 0:
                json_entry = json.loads(line)

                role = json_entry.get("role")
                venue = json_entry.get("venue")
                year = json_entry.get("year")
                members = json_entry.get("members")

                insert_in_db(cnx, members, role, venue, year)

    json_file.close()
    cnx.close()
    driver.close()


if __name__ == "__main__":
    main()