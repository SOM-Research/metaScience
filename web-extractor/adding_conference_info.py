__author__ = 'atlanmod'

import logging
import mysql.connector
from mysql.connector import errorcode
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
import time
import cross_module_variables as shared
import database_connection_config as dbconnection

#This script gathers (via Selenium) the LOCATION, TYPE and MONTH for each proceedings in DBLP
#and add them to the table AUX_DBLP_PROCEEDINGS.
#LOCATION is the location where the conference is settle
#TYPE can be "conference", "workshop" or "symposium"
#MONTH is the month when the conference takes place
#
#Currently, the script has been tuned to collect only the information for the following conferences from 2003:
#ICSE, FSE, ESEC, ASE, SPLASH, OOPSLA, ECOOP, ISSTA, FASE,
#MODELS, WCRE, CSMR, ICMT, COMPSAC, APSEC, VISSOFT, ICSM, SOFTVIS,
#SCAM, TOOLS, CAISE, ER, ECMFA, ECMDA-FA
#
#The table AUX_DBLP_PROCEEDINGS is derived from DBLP_PUB_NEW
#Below the mysql script to generate the AUX_DBLP_PROCEEDINGS is shown
# create table dblp.aux_dblp_proceedings as
# select id as dblp_id, dblp_key, url, source, year
# from dblp.dblp_pub_new where type = 'proceedings';
#
# alter table dblp.aux_dblp_proceedings
# add column id int(11) primary key auto_increment first,
# add column location varchar(256),
# add column type varchar(25),
# add column month varchar(25),
# add column rank varchar(10),
# add index dblp_key (dblp_key);

LOG_FILENAME = 'logger_conference_info.log'
driver = webdriver.Chrome(executable_path='C:\Program Files (x86)\Google\Chrome\chromedriver.exe')


def get_dblp_proceedings(url, dblp_key):
    if url is not None:
        link = url
    else:
        conf_info = dblp_key.split("/")
        link = "db/" + conf_info[0] + "/" + conf_info[1] + "/" + conf_info[1] + conf_info[2] + ".html"

    driver.get(shared.DBLP + "/" + link)
    time.sleep(1)
    return driver

    ##This part relies on the Selenium WebDriverWait, but it can be replace by the time.sleep(xxx) function
    # driver = webdriver.Chrome(executable_path='C:\Program Files (x86)\Google\Chrome\chromedriver.exe')
    # driver.get(GOOGLE)
    # search_box = driver.find_element_by_id("gbqfq")
    # search_box.send_keys("dblp " + url + Keys.RETURN)
    # #wait
    # WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "rso")))
    #
    # google_hits = driver.find_elements_by_xpath(".//*[@id='rso']//div//h3/a")
    #
    # for hit in google_hits:
    #     link = hit.get_attribute("href")
    #     if url in link:
    #         hit.click()
    #         break
    #
    # return driver


def update_location_info(cnx, id, conf):
    cursor = cnx.cursor()
    query = "UPDATE aux_dblp_proceedings SET location = %s WHERE id = %s"
    arguments = [id, conf]
    cursor.execute(query, arguments)
    cnx.commit()
    cursor.close()


def update_type_proceedings(cnx, dblp_key, title):
    cursor = cnx.cursor()
    type = ''
    if 'conference' in title.lower():
        type = 'conference'
    elif 'workshop' in title.lower():
        type = 'workshop'
    elif 'symposium' in title.lower():
        type = 'symposium'

    query = "UPDATE aux_dblp_proceedings SET type = %s WHERE dblp_key = %s"
    arguments = [type, dblp_key]
    cursor.execute(query, arguments)
    cnx.commit()

    cursor.close()


def update_month_proceedings(cnx, dblp_key, title):
    cursor = cnx.cursor()
    month = ''
    if 'january' in title.lower():
        month = 'january'
    elif 'february' in title.lower():
        month = 'february'
    elif 'march' in title.lower():
        month = 'march'
    elif 'april' in title.lower():
        month = 'april'
    elif 'may' in title.lower():
        month = 'may'
    elif 'june' in title.lower():
        month = 'june'
    elif 'july' in title.lower():
        month = 'july'
    elif 'august' in title.lower():
        month = 'august'
    elif 'september' in title.lower():
        month = 'september'
    elif 'october' in title.lower():
        month = 'october'
    elif 'november' in title.lower():
        month = 'november'
    elif 'december' in title.lower():
        month = 'december'

    query = "UPDATE aux_dblp_proceedings SET month = %s WHERE dblp_key = %s"
    arguments = [month, dblp_key]
    cursor.execute(query, arguments)
    cnx.commit()

    cursor.close()


def update_proceedings(cnx, dblp_key):
    cursor = cnx.cursor()
    query = "SELECT title FROM dblp_pub_new WHERE type='proceedings' AND dblp_key = %s"
    arguments = [dblp_key]
    cursor.execute(query, arguments)
    title = cursor.fetchone()[0]

    update_type_proceedings(cnx, dblp_key, title)
    update_month_proceedings(cnx, dblp_key, title)


def add_proceedings_info(cnx, id):
    conf_cursor = cnx.cursor()
    query = "SELECT id, dblp_key, url " \
            "FROM aux_dblp_proceedings " \
            "WHERE dblp_key IS NOT NULL AND " \
            "location IS NULL AND " \
            "type IS NULL AND " \
            "month IS NULL AND " \
            "rank IS NULL AND " \
            "id > %s "
    # query = "SELECT id, dblp_key, url " \
    #         "FROM aux_dblp_proceedings " \
    #         "WHERE dblp_key IS NOT NULL AND " \
    #         "id > %s " \
    #         "AND year >= 2003 " \
    #         "AND source IN (" + shared.CONFERENCES + ")"
    arguments = [id]
    conf_cursor.execute(query, arguments)
    row = conf_cursor.fetchone()
    while row is not None:
        id = row[0]
        dblp_key = row[1]
        proceedings = row[2]

        proceedings_page = get_dblp_proceedings(proceedings, dblp_key)
        try:
            headline = proceedings_page.find_element_by_id("headline").text
            update_proceedings(cnx, dblp_key)
            location = ''
            if ':' in headline:
                location = headline.split(':')[1]
                update_location_info(cnx, location, id)
            else:
                logging.warning("unable to extract location from " + headline)
        except NoSuchElementException:
            logging.warning(str(proceedings_page.current_url))

        row = conf_cursor.fetchone()
    conf_cursor.close()
    logging.warning("last conf analysed " + str(proceedings))


#This method is used to recover an execution that went wrong.
#It restart the extraction process from the last id entered in the database
#To activate the recover process, just activate the flag "RECOVER_PROCESS"
def get_id_to_start(cnx):
    conf_cursor = cnx.cursor()
    query = "SELECT MAX(id) " \
            "FROM aux_dblp_proceedings " \
            "WHERE dblp_key IS NOT NULL"
    conf_cursor.execute(query)
    row = conf_cursor.fetchone()
    return row[0]


RECOVER_PROCESS = False


def main():
    logging.basicConfig(filename=LOG_FILENAME, level=logging.WARNING)
    with open(LOG_FILENAME, "w") as log_file:
        log_file.write('\n')
    cnx = mysql.connector.connect(**dbconnection.CONFIG)
    #set the row id from the table 'aux_dblp_proceedings' to start extracting the conference information
    id_to_start = 0
    if RECOVER_PROCESS:
        if get_id_to_start(cnx) is not None:
            id_to_start = int(id)

    add_proceedings_info(cnx, id_to_start)
    driver.close()

if __name__ == "__main__":
    main()