__author__ = 'atlanmod'

import logging
import mysql.connector
from mysql.connector import errorcode
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
import re
import time
import nltk.metrics
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import database_connection_config as dbconnection


SCHOLAR = 'http://scholar.google.com'
LOG_FILENAME = 'logger_paper_abstract.log'
WAIT_TIME = 10
driver = webdriver.Chrome(executable_path='C:\Program Files (x86)\Google\Chrome\chromedriver.exe')


IEEEXPLORE = "ieeexplore"
SPRINGER = "springer"
DL_ACM = "dl.acm"
SCIENCEDIRECT = "sciencedirect"
COMPUTER_SOCIETY = "computer.org"


def get_abstract_from_ieeexplore():

    abstract = ""
    try:
        abstract_container = WebDriverWait(driver, WAIT_TIME).until(EC.presence_of_all_elements_located((By.XPATH, "//div[@class='article']/p")))
        if abstract_container:
            abstract = abstract_container[0].text
        else:
            logging.info("abstract not found for: " + driver.current_url)
    except TimeoutException:
        logging.info("timeout for: " + driver.current_url)
    return abstract


def get_abstract_from_springer():
    abstract = ""
    try:
        abstract_container = WebDriverWait(driver, WAIT_TIME).until(EC.presence_of_all_elements_located((By.XPATH, "//div[starts-with(@class, 'abstract-content')]/p")))
        if abstract_container:
            abstract = abstract_container[0].text
        else:
            logging.info("abstract not found for: " + driver.current_url)
    except TimeoutException:
        logging.info("timeout for: " + driver.current_url)
    return abstract


def get_abstract_from_acm():
    abstract = ""
    try:
        abstract_container = WebDriverWait(driver, WAIT_TIME).until(EC.presence_of_all_elements_located((By.ID, "abstract")))
        if abstract_container:
            abstract = abstract_container[0].text
        else:
            logging.info("abstract not found for: " + driver.current_url)
    except TimeoutException:
        logging.info("timeout for: " + driver.current_url)
    return abstract


def get_abstract_from_sciencedirect():
    abstract = ""
    try:
        abstract_container = WebDriverWait(driver, WAIT_TIME).until(EC.presence_of_all_elements_located((By.XPATH, "//div[starts-with(@class, 'abstract')]/p")))
        if abstract_container:
            abstract = abstract_container[0].text
        else:
            logging.info("abstract not found for: " + driver.current_url)
    except TimeoutException:
        logging.info("timeout for: " + driver.current_url)
    return abstract


def get_abstract_from_computersociety():
    abstract = ""
    try:
        abstract_container = WebDriverWait(driver, WAIT_TIME).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "abs-articlesummary")))
        if abstract_container:
            abstract = abstract_container[0].text
        else:
            logging.info("abstract not found for: " + driver.current_url)
    except TimeoutException:
        logging.info("timeout for: " + driver.current_url)
    return abstract


def add_abstract_to_paper(hit, cnx, key):
    hit.click()
    time.sleep(1)
    url = driver.current_url

    abstract = ""

    if IEEEXPLORE in url:
        abstract = get_abstract_from_ieeexplore()
    elif SPRINGER in url:
        abstract = get_abstract_from_springer()
    elif DL_ACM in url:
        abstract = get_abstract_from_acm()
    elif SCIENCEDIRECT in url:
        abstract = get_abstract_from_sciencedirect()
    elif COMPUTER_SOCIETY in url:
        abstract = get_abstract_from_computersociety()
    else:
        logging.info("define a parser for " + url)

    insert_paper_abstract_info(cnx, key, abstract)


def find_paper_in_scholar(cnx, title, key):
    driver.get(SCHOLAR)
    try:
        search_box = WebDriverWait(driver, WAIT_TIME).until(EC.presence_of_element_located((By.ID, "gs_hp_tsi")))
        search_box.send_keys(title + Keys.RETURN)

        scholar_hits = driver.find_elements_by_class_name("gs_ri")

        for hit in scholar_hits:
            info_hit = hit.find_element_by_class_name("gs_rt")
            try:
                hit_link = info_hit.find_element_by_tag_name("a")
                title_hit = hit_link.text
                leveh_distance = nltk.metrics.edit_distance(re.sub(r'\s+', '', title_hit.lower()), re.sub(r'\s+', '', title.lower()))
                if leveh_distance <= 6:
                    if leveh_distance > 1:
                        logging.warning("match: " + title_hit + " ******* " + title + "  ******* " + str(leveh_distance))
                    add_abstract_to_paper(hit_link, cnx, key)

                    break
            except NoSuchElementException:
                continue
    except TimeoutException:
        logging.info("Google Scholar not loaded")



def insert_paper_abstract_info(cnx, key, abstract):
    cursor = cnx.cursor()
    query = "INSERT aux_dblp_inproceedings_abstract VALUES (%s, %s)"
    arguments = [key, abstract]
    cursor.execute(query, arguments)
    cnx.commit()
    cursor.close()


def add_abstract_info(cnx):
    conf_cursor = cnx.cursor()
    query = "SELECT dblp_key, title " \
            "FROM aux_dblp_inproceedings_tracks " \
            "WHERE dblp_key NOT IN (SELECT dblp_key FROM aux_dblp_inproceedings_abstract)"
    conf_cursor.execute(query)
    row = conf_cursor.fetchone()
    while row is not None:
        key = row[0]
        title = row[1]
        find_paper_in_scholar(cnx, title, key)
        row = conf_cursor.fetchone()
    conf_cursor.close()


def main():
    logging.basicConfig(filename=LOG_FILENAME, level=logging.WARNING)
    with open(LOG_FILENAME, "w") as log_file:
        log_file.write('\n')
    cnx = mysql.connector.connect(**dbconnection.CONFIG)

    add_abstract_info(cnx)
    driver.close()
    cnx.close()

if __name__ == "__main__":
    main()