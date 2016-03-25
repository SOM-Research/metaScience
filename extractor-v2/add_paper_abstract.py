__author__ = 'valerio cosentino'

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
import db_config

#Launch this script in debug mode and put a break point on the instruction "print "redirected to captcha"
LOG_FILENAME = 'logger_paper_abstract.log'

#This script looks for paper abstracts
MAS = 'https://academic.microsoft.com/'
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
        abstract_container = WebDriverWait(driver, WAIT_TIME).until(EC.visibility_of_element_located((By.XPATH, "(//div[@class='article'])[1]/p")))
        if abstract_container:
            abstract = abstract_container.text
        else:
            logging.info("ieeexplore - abstract not found for: " + driver.current_url)
    except TimeoutException:
        logging.info("timeout for: " + driver.current_url)

    if abstract == "":
        logging.info("ieeexplore - abstract not loaded for: " + driver.current_url)
    return abstract


def get_abstract_from_springer():
    abstract = ""
    try:
        abstract_container = WebDriverWait(driver, WAIT_TIME).\
            until(EC.presence_of_element_located((By.XPATH, "(//div[starts-with(@class, 'abstract-content')])[1]/p")))
        if abstract_container:
            abstract = abstract_container.text
        else:
            logging.info("springer - abstract not found for: " + driver.current_url)
    except TimeoutException:
        logging.info("timeout for: " + driver.current_url)

    if abstract == "":
        logging.info("springer - abstract not loaded for: " + driver.current_url)
    return abstract


def get_abstract_from_acm():
    abstract = ""
    try:
        WebDriverWait(driver, WAIT_TIME).until(EC.presence_of_element_located((By.ID, "citationdetails")))
        WebDriverWait(driver, WAIT_TIME).until(EC.presence_of_element_located((By.CLASS_NAME, "tabbody")))
        time.sleep(1)
        abstract_container = driver.find_element_by_id("abstract")
        if abstract_container:
            abstract = abstract_container.text
        else:
            logging.info("acm - abstract not found for: " + driver.current_url)
    except TimeoutException:
        logging.info("timeout for: " + driver.current_url)

    if abstract == "":
        logging.info("acm -abstract not loaded for: " + driver.current_url)

    return abstract


def get_abstract_from_sciencedirect():
    abstract = ""
    try:
        abstract_container = WebDriverWait(driver, WAIT_TIME).until(EC.presence_of_element_located((By.XPATH, "(//div[starts-with(@class, 'abstract')])[1]/p")))
        if abstract_container:
            abstract = abstract_container.text
        else:
            logging.info("sciencedirect - abstract not found for: " + driver.current_url)
    except TimeoutException:
        logging.info("timeout for: " + driver.current_url)

    if abstract == "":
        logging.info("sciencedirect - abstract not loaded for: " + driver.current_url)
    return abstract


def get_abstract_from_computersociety():
    abstract = ""
    try:
        abstract_container = WebDriverWait(driver, WAIT_TIME).until(EC.presence_of_element_located((By.CLASS_NAME, "abs-articlesummary")))
        if abstract_container:
            abstract = abstract_container.text
        else:
            logging.info("computersociety - abstract not found for: " + driver.current_url)
    except TimeoutException:
        logging.info("timeout for: " + driver.current_url)

    if abstract == "":
        logging.info("computersociety - abstract not loaded for: " + driver.current_url)
    return abstract


def get_abstract(hit):
    abstract = None
    hit.click()
    time.sleep(1)

    sources = driver.find_element_by_class_name("sources-list").find_elements_by_tag_name("li")

    found = False
    for source in sources:
        text = source.text
        if IEEEXPLORE in text or SPRINGER in text or DL_ACM in text or SCIENCEDIRECT in text or COMPUTER_SOCIETY in text:
            source.find_element_by_tag_name("a").click()
            found = True
            time.sleep(2)
            break

    if found:
        #change tab
        driver._switch_to.window(window_name=driver.window_handles[-1])
        url = driver.current_url

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
        sources_text = ','.join([s.text for s in sources])
        logging.error("unknown sources: " + sources_text)

    #close tab
    driver.close()
    #return to main tab
    driver._switch_to.window(window_name=driver.window_handles[0])
    return abstract


def find_abstract(title):
    driver.get(MAS)
    try:
        search_box = WebDriverWait(driver, WAIT_TIME).until(EC.presence_of_element_located((By.ID, "searchControl")))
        search_box.send_keys(title + Keys.RETURN)
        time.sleep(WAIT_TIME)
        try:
            #wait
            hits = WebDriverWait(driver, WAIT_TIME).until(EC.presence_of_all_elements_located((By.TAG_NAME, "article")))
            time.sleep(2)

            for hit in hits:
                title_hit = hit.find_element_by_class_name("title-bar")
                try:
                    hit_link = title_hit.find_element_by_tag_name("a")
                    leveh_distance = nltk.metrics.edit_distance(re.sub(r'\s+', '', title_hit.text.lower()), re.sub(r'\s+', '', title.lower()))
                    if leveh_distance <= 6:
                        if leveh_distance > 1:
                            logging.warning("match: " + title_hit + " ******* " + title + "  ******* " + str(leveh_distance))
                        abstract = get_abstract(hit_link)
                        break
                except NoSuchElementException:
                    continue

        except TimeoutException:
            logging.warning("abstract not found for " + title)

    except TimeoutException:
        logging.info("MAS not loaded")

    return abstract



def add_abstract_info(cnx):
    cursor = cnx.cursor()
    cursor_update = cnx.cursor()
    query = "SELECT id, title " \
            "FROM `" + db_config.DB_NAME + "`.paper " \
            "WHERE abstract IS NULL " \
            "LIMIT 10"

    cursor.execute(query)
    row = cursor.fetchone()
    while row is not None:
        id = row[0]
        title = row[1].strip('.')
        abstract = find_abstract(title)
        query_update = "UPDATE `" + db_config.DB_NAME + "`.paper SET abstract = %s WHERE id = %s"
        arguments = [abstract, id]
        cursor_update.execute(query_update, arguments)
        cnx.commit()
        row = cursor.fetchone()
    cursor_update.close()
    cursor.close()


def establish_connection():
    return mysql.connector.connect(**db_config.CONFIG)


def main():
    logging.basicConfig(filename=LOG_FILENAME, level=logging.WARNING)
    with open(LOG_FILENAME, "w") as log_file:
        log_file.write('\n')
    cnx = establish_connection()
    add_abstract_info(cnx)
    driver.close()
    cnx.close()

if __name__ == "__main__":
    main()