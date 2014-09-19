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

#Launch this script in debug mode and put a break point on the instruction "print "redirected to captcha"

#This script looks for paper abstracts
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
        abstract_container = WebDriverWait(driver, WAIT_TIME).until(EC.presence_of_element_located((By.XPATH, "(//div[@class='article'])[1]/p")))
        if abstract_container:
            abstract = abstract_container.text
        else:
            logging.info("abstract not found for: " + driver.current_url)
    except TimeoutException:
        logging.info("timeout for: " + driver.current_url)

    if abstract == "":
        logging.info("abstract not loaded for: " + driver.current_url)
    return abstract


def get_abstract_from_springer():
    abstract = ""
    try:
        abstract_container = WebDriverWait(driver, WAIT_TIME).until(EC.presence_of_element_located((By.XPATH, "(//div[starts-with(@class, 'abstract-content')])[1]/p")))
        if abstract_container:
            abstract = abstract_container.text
        else:
            logging.info("abstract not found for: " + driver.current_url)
    except TimeoutException:
        logging.info("timeout for: " + driver.current_url)

    if abstract == "":
        logging.info("abstract not loaded for: " + driver.current_url)
    return abstract


def get_abstract_from_acm():
    abstract = ""
    try:
        abstract_container = WebDriverWait(driver, WAIT_TIME).until(EC.visibility_of_element_located((By.ID, "abstract")))
        if abstract_container:
            abstract = abstract_container.text
        else:
            logging.info("abstract not found for: " + driver.current_url)
    except TimeoutException:
        logging.info("timeout for: " + driver.current_url)

    if abstract == "":
        logging.info("abstract not loaded for: " + driver.current_url)
    return abstract


def get_abstract_from_sciencedirect():
    abstract = ""
    try:
        abstract_container = WebDriverWait(driver, WAIT_TIME).until(EC.presence_of_element_located((By.XPATH, "(//div[starts-with(@class, 'abstract')])[1]/p")))
        if abstract_container:
            abstract = abstract_container.text
        else:
            logging.info("abstract not found for: " + driver.current_url)
    except TimeoutException:
        logging.info("timeout for: " + driver.current_url)

    if abstract == "":
        logging.info("abstract not loaded for: " + driver.current_url)
    return abstract


def get_abstract_from_computersociety():
    abstract = ""
    try:
        abstract_container = WebDriverWait(driver, WAIT_TIME).until(EC.presence_of_element_located((By.CLASS_NAME, "abs-articlesummary")))
        if abstract_container:
            abstract = abstract_container.text
        else:
            logging.info("abstract not found for: " + driver.current_url)
    except TimeoutException:
        logging.info("timeout for: " + driver.current_url)

    if abstract == "":
        logging.info("abstract not loaded for: " + driver.current_url)
    return abstract


def add_abstract_to_paper(hit, cnx, id, key):
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

    insert_paper_abstract_info(cnx, id, key, abstract)


def in_captcha_page():
    time.sleep(1)
    flag = True
    try:
        capcha = driver.find_element_by_id("gs_captcha_ccl")
    except:
        flag = False

    if not flag:
        try:
            capcha = driver.find_element_by_xpath("form/input[name='captcha']")
        except:
            flag = False

    return flag


def find_paper_in_scholar(cnx, title, id, key):
    driver.get(SCHOLAR)
    try:
        search_box = WebDriverWait(driver, WAIT_TIME).until(EC.presence_of_element_located((By.ID, "gs_hp_tsi")))
        search_box.send_keys(title + Keys.RETURN)

        if in_captcha_page():
            print "redirected to captcha"

        try:
            #wait
            scholar_hits = WebDriverWait(driver, WAIT_TIME).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "gs_ri")))
            time.sleep(2)

            for hit in scholar_hits:
                info_hit = hit.find_element_by_class_name("gs_rt")
                try:
                    hit_link = info_hit.find_element_by_tag_name("a")
                    title_hit = hit_link.text
                    leveh_distance = nltk.metrics.edit_distance(re.sub(r'\s+', '', title_hit.lower()), re.sub(r'\s+', '', title.lower()))
                    if leveh_distance <= 6:
                        if leveh_distance > 1:
                            logging.warning("match: " + title_hit + " ******* " + title + "  ******* " + str(leveh_distance))
                        add_abstract_to_paper(hit_link, cnx, id, key)

                        break
                except NoSuchElementException:
                    continue
        except TimeoutException:
            logging.warning("abstract not found for " + title)

    except TimeoutException:
        logging.info("Google Scholar not loaded")



def insert_paper_abstract_info(cnx, id, key, abstract):
    cursor = cnx.cursor()
    query = "INSERT aux_dblp_inproceedings_abstract VALUES (NULL, %s, %s, %s)"
    arguments = [id, key, abstract]
    cursor.execute(query, arguments)
    cnx.commit()
    cursor.close()


def add_abstract_info(cnx):
    conf_cursor = cnx.cursor()

    query = "SELECT dblp_id, dblp_key, title " \
            "FROM aux_dblp_inproceedings_tracks " \
            "WHERE SUBSTRING_INDEX(SUBSTRING_INDEX(crossref, '/', 2), '/', -1) = 'msr'"
    # query = "SELECT dblp_id, dblp_key, title " \
    #         "FROM aux_dblp_inproceedings_tracks " \
    #         "WHERE dblp_id NOT IN (SELECT dblp_id FROM aux_dblp_inproceedings_abstract)"

    conf_cursor.execute(query)
    row = conf_cursor.fetchone()
    while row is not None:
        id = row[0]
        key = row[1]
        title = row[2]
        find_paper_in_scholar(cnx, title, id, key)
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