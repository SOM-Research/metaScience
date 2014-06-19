__author__ = 'atlanmod'

import logging
import mysql.connector
from mysql.connector import errorcode
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
import time


GOOGLE = 'http://www.google.com'
DBLP = 'http://www.informatik.uni-trier.de/~ley/'
LOG_FILENAME = 'logger_conference_info.log'
driver = webdriver.Chrome(executable_path='C:\Program Files (x86)\Google\Chrome\chromedriver.exe')

CONFIG = {
    'user': 'root',
    'password': 'coitointerrotto',
    'host': 'atlanmodexp.info.emn.fr',
    'port': '13506',
    'database': 'dblp',
    'raise_on_warnings': False,
    'buffered': True
}


def get_proceedings_web_link(acronym, year, month, proceedings_type, city):
    driver.get(GOOGLE)
    input_element = driver.find_element_by_name("q")
    input_element.send_keys(acronym + " " + str(year) + " " + month + " " + city + " " + proceedings_type + Keys.RETURN)
    #wait
    WebDriverWait(driver, 15).until(EC.visibility_of_element_located((By.ID, "rso")))

    google_hits = driver.find_elements_by_xpath(".//*[@id='rso']//div//h3/a")

    flag = 0
    for hit in google_hits:
        link = hit.get_attribute("href")
        if (acronym in link
            or acronym.lower() in link) \
                and ('dblp' not in link
                and 'informatik.uni-trier.de' not in link
                and '.pdf' not in link
                and 'books' not in link
                and 'worldcat' not in link
                and 'amazon' not in link
                and 'researchgate' not in link):
            flag = 1
            #driver.get(link + Keys.ESCAPE)
            #link = driver.current_url
            break

    if flag == 1:
        return link.replace("%EE%80%8C", "")
    else:
        return None


def get_dblp_proceedings(url, dblp_key):
    link = ''
    if url is not None:
        link = url
    else:
        conf_info = dblp_key.split("/")
        link = "db/" + conf_info[0] + "/" + conf_info[1] + "/" + conf_info[1] + conf_info[2] + ".html"

    driver.get(DBLP + "/" + link)
    time.sleep(1)
    return driver

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

    return type


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

    type = update_type_proceedings(cnx, dblp_key, title)
    update_month_proceedings(cnx, dblp_key, title)

    return type


def update_web_link_proceedings(cnx, id, url):
    cursor = cnx.cursor()
    query = "UPDATE aux_dblp_proceedings SET web_link = %s WHERE id = %s"
    arguments = [url, id]
    cursor.execute(query, arguments)
    cnx.commit()
    cursor.close()


def get_acronym(dblp_key, dblp_acronym):
    acronym = dblp_acronym
    if dblp_acronym is None:
        acronym = dblp_key.split('/')[1]

    return acronym


def add_proceedings_info(cnx, id):
    conf_cursor = cnx.cursor()
    query = "SELECT id, dblp_key, url, source, year, month " \
            "FROM aux_dblp_proceedings " \
            "WHERE dblp_key IS NOT NULL AND " \
            "web_link IS NULL AND " \
            "id > %s " \
            "AND year >= 2003 " \
            "AND source IN " \
            "('ICSE', 'FSE', 'ESEC', 'ASE', 'SPLASH', 'OOPSLA', 'ECOOP', 'ISSTA', 'FASE')"
    arguments = [id]
    conf_cursor.execute(query, arguments)
    row = conf_cursor.fetchone()
    while row is not None:
        id = row[0]
        dblp_key = row[1]
        proceedings = row[2]
        acronym = get_acronym(dblp_key, row[3])

        if row[4] is None:
            year = ''
        else:
            year = row[4]
        if row[5] is None:
            month = ''
        else:
            month = row[5]

        proceedings_page = get_dblp_proceedings(proceedings, dblp_key)
        try:
            headline = proceedings_page.find_element_by_id("headline").text
            proceedings_type = update_proceedings(cnx, dblp_key)
            location = ''
            if ':' in headline:
                location = headline.split(':')[1]
                update_location_info(cnx, location, id)
            else:
                logging.warning("unable to extract location from " + headline)
            if proceedings_type in ('conference', 'symposium'):
                if len(location) == 0:
                    url = get_proceedings_web_link(acronym, year, month, proceedings_type, '')
                else:
                    url = get_proceedings_web_link(acronym, year, month, proceedings_type, location.split(',')[0])

                if url is not None:
                    update_web_link_proceedings(cnx, id, url)
        except NoSuchElementException:
            logging.warning(str(proceedings_page.current_url))

        row = conf_cursor.fetchone()
    conf_cursor.close()
    logging.warning("last conf analysed " + str(proceedings))


def get_id_to_start(cnx):
    conf_cursor = cnx.cursor()
    query = "SELECT MAX(id) " \
            "FROM aux_dblp_proceedings " \
            "WHERE dblp_key IS NOT NULL AND " \
            "web_link IS NOT NULL"
    conf_cursor.execute(query)
    row = conf_cursor.fetchone()
    return row[0]


def main():
    logging.basicConfig(filename=LOG_FILENAME, level=logging.WARNING)
    with open(LOG_FILENAME, "w") as log_file:
        log_file.write('\n')
    cnx = mysql.connector.connect(**CONFIG)
    #set the row id (from the table 'aux_dblp_proceedings') to start extracting the conference websites

    #get last id to start
    # id = get_id_to_start(cnx)
    # if id is None:
    #     id_to_start = 0
    # else:
    #     id_to_start = int(id)

    add_proceedings_info(cnx, 0)
    driver.close()

if __name__ == "__main__":
    main()