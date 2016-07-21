__author__ = 'valerio cosentino'

import mysql.connector
from mysql.connector import errorcode
import db_config
import time
import nltk.metrics
import re
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import unicodedata

SCHOLAR = 'http://scholar.google.com'
WAIT_TIME = 10
LEV_DISTANCE_THRESHOLD = 6
FROM_PAPER_ID = 0

driver = webdriver.Chrome(executable_path='C:\Program Files (x86)\Google\Chrome\chromedriver.exe')


def in_captcha_page():
    time.sleep(1)
    flag = True
    try:
        capcha = driver.find_element_by_id("gs_captcha_ccl")
    except:
        flag = False

    if not flag:
        try:
            capcha = driver.find_elements_by_xpath("//input[@name='captcha']")
            if capcha:
                flag = True
        except:
            flag = False
    return flag


def send_keys_to_browser(title):
    try:
        search_box = WebDriverWait(driver, WAIT_TIME).until(EC.presence_of_element_located((By.ID, "gs_hp_tsi")))
    except TimeoutException:
        search_box = WebDriverWait(driver, WAIT_TIME).until(EC.presence_of_element_located((By.ID, "gs_hdr_frm_in_txt")))

    search_box.send_keys(title + Keys.RETURN)


def normalize_text(string):
    return re.sub('\W+', '', ''.join(x for x in unicodedata.normalize('NFKD', string.lower())))


def match_title(info_hit, title):
    match = False
    title_hit = info_hit.find_element_by_tag_name("a").text
    leveh_distance = nltk.metrics.edit_distance(normalize_text(title_hit), normalize_text(title))
    if leveh_distance <= LEV_DISTANCE_THRESHOLD:
        match = True

    return match


def find_title_match(title):
    matched_paper = None
    driver.get(SCHOLAR)

    if in_captcha_page():
        print "redirected to captcha"

    send_keys_to_browser(title)

    if in_captcha_page():
        print "redirected to captcha"

    try:
        #wait
        scholar_hits = WebDriverWait(driver, WAIT_TIME).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "gs_ri")))
        time.sleep(WAIT_TIME)

        for hit in scholar_hits:
            info_hit = hit.find_element_by_class_name("gs_rt")
            try:
                if match_title(info_hit, title):
                    matched_paper = hit
                    break
            except NoSuchElementException:
                continue
    except TimeoutException:
        matched_paper = None

    return matched_paper


def get_author_positions(hit):
    positions = []
    author_positions = re.sub(" - .*", "", hit.find_element_by_class_name("gs_a").text).split(',')
    for author in author_positions:
        author = author.replace(u"\u2026", "")
        positions.append(author.strip())
    return positions


def insert_new_alias(cnx, researcher_id, alias):
    cursor = cnx.cursor()
    insert = "INSERT IGNORE INTO `" + db_config.DB_NAME + "`.researcher_alias VALUES (%s, %s)"
    arguments = [researcher_id, alias]
    cursor.execute(insert, arguments)
    cnx.commit()
    cursor.close()


def extract_author_links(scholar_hit):
    author_links = scholar_hit.find_element_by_class_name("gs_a").find_elements_by_tag_name("a")
    author_positions = get_author_positions(scholar_hit)
    position2links = {}
    if author_links:
        for author in author_links:
            position = author_positions.index(author.text.strip())
            position2links.update({position: author.get_attribute("href")})

    return position2links


def find_researcher_name_on_scholar(link):
    driver.get(link)
    #wait
    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "gsc_rsb_st")))
    time.sleep(2)
    name = driver.find_element_by_id("gsc_prf_in").text

    return name


def researcher_is_already_in_db(cnx, name):
    cursor = cnx.cursor()
    query_researcher = "SELECT id FROM `" + db_config.DB_NAME + "`.researcher WHERE name = %s;"
    query_researcher_alias = "SELECT id FROM `" + db_config.DB_NAME + "`.researcher_alias WHERE name = %s;"
    arguments = [name]

    cursor.execute(query_researcher, arguments)
    row = cursor.fetchone()

    if row is None:
        cursor.execute(query_researcher_alias, arguments)
        row = cursor.fetchone()

    cursor.close()

    return row is not None


def analyse_authors(cnx, scholar_hit, paper_id):
    position2links = extract_author_links(scholar_hit)

    if position2links:
        cursor = cnx.cursor()
        query = "SELECT res.name, researcher_id, position " \
                "FROM `" + db_config.DB_NAME + "`.authorship auth, `" + db_config.DB_NAME + "`.researcher res " \
                "WHERE auth.researcher_id = res.id AND paper_id = %s "
        arguments = [paper_id]
        cursor.execute(query, arguments)

        row = cursor.fetchone()
        while row:
            researcher_name = row[0]
            researcher_id = row[1]
            position_in_paper = row[2]

            if position2links.get(position_in_paper):
                name = find_researcher_name_on_scholar(position2links.get(position_in_paper)).strip()

                if name:
                    if not researcher_is_already_in_db(cnx, name):
                        insert_new_alias(cnx, researcher_id, name)
                        print "new alias for (" + researcher_id + "," + researcher_name + "): " + name

            row = cursor.fetchone()

        cursor.close()


def establish_connection():
    return mysql.connector.connect(**db_config.CONFIG)


def main():
    cnx = establish_connection()
    cursor = cnx.cursor()
    query = "SELECT id, title FROM `" + db_config.DB_NAME + "`.paper WHERE id >= %s LIMIT 10"
    arguments = [FROM_PAPER_ID]
    cursor.execute(query, arguments)

    row = cursor.fetchone()
    while row:
        paper_id = row[0]
        title = row[1]

        scholar_hit = find_title_match(title)
        if scholar_hit:
            analyse_authors(cnx, scholar_hit, paper_id)

        row = cursor.fetchone()

    cursor.close()
    cnx.close()


if __name__ == "__main__":
    main()
