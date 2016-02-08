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
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import database_connection_config as dbconnection
import datetime
from selenium.common.exceptions import TimeoutException
import sys

#Launch this script in debug mode and put a break point on the instruction "print "redirected to captcha"
#This script performs two actions:
#1) For each paper presents in the table aux_dblp_inproceedings_tracks,
#   the script gathers (via Selenium) the current number of CITATIONS
#
#2) It finds (via Selenium) the google scholar page for each author that published in the previous conferences
#   and collects the author CITATIONS, INDEX, I10 for the past five year and the global CITATIONS, INDEX, I10.
#   In addition, it collects for each author his INTERESTS (defined in his scholar page).
#   Since the citations can change over time, the script stores also the month-year when the citations were collected

SCHOLAR = 'http://scholar.google.com'
    # 'http://www.proxybitcoin.com/browse.php?u=O7IiiS0m37iOlw6y3p9ixlhZjD69&b=5&f=norefer'
    #'http://123abcproxy.ml/browse.php?u=Oi8vc2Nob2xhci5nb29nbGUuY29t&b=5&f=norefer'
    #'http://www.webcamproxy.com/browse.php?u=http%3A%2F%2Fscholar.google.com&b=4&f=norefer'
    #'http://000111.unblock4ever.info/browse.php?u=http%3A%2F%2Fscholar.google.com&b=4&f=norefer'
    #'https://us-free-proxy.cyberghostvpn.com/go/browse.php?u=http://scholar.google.com&b=1&f=norefer'
    #'http://anonymouse.org/cgi-bin/anon-www.cgi/http://scholar.google.com'

LOG_FILENAME = 'logger_paper_citations.log'
COLLECT_PAPER_CITATIONS = True

#Build the chrome_options object specifying the locally running Privoxy as the proxy server
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--proxy-server=http://127.0.0.1:8118')

driver = webdriver.Chrome(executable_path='C:\Program Files (x86)\Google\Chrome\chromedriver.exe', chrome_options=chrome_options)
UPDATE_CITATIONS = 0
UPDATED_BEFORE = "0000-00-00"

WAIT_TIME = 10

def get_dblp_author_id_from_title(cnx, title, author_name):
    cursor = cnx.cursor()
    query = "SELECT author_id " \
            "FROM dblp.dblp_authorid_ref_new author " \
            "JOIN dblp.dblp_pub_new pub " \
            "ON author.id = pub.id " \
            "WHERE title = %s AND author = %s"
    arguments = [title, author_name]
    cursor.execute(query, arguments)
    id = cursor.fetchone()
    cursor.close()
    if id is None:
        return None
    return id[0]


def get_current_day():
    return datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%d")


def get_dblp_author_id_from_aliases(cnx, author_name):
    cursor = cnx.cursor()
    query = "SELECT author_id " \
            "FROM dblp.dblp_aliases_new aliases " \
            "WHERE author = %s OR authorAlias = %s"
    arguments = [author_name, author_name]
    cursor.execute(query, arguments)
    id = cursor.fetchone()
    cursor.close()
    if id is None:
        return None
    return id[0]


def get_dblp_author_id_from_position(cnx, title, author_pos):
    cursor = cnx.cursor()
    query = "SELECT author.id " \
            "FROM dblp_author_ref_new author " \
            "JOIN dblp_pub_new pub " \
            "ON author.id = pub.id " \
            "WHERE title = %s and author_num = %s"
    arguments = [title, author_pos]
    cursor.execute(query, arguments)
    id = cursor.fetchone()
    cursor.close()
    if id is None:
        return None
    return id[0]


def get_dblp_author_id(cnx, title, author_name, author_pos):
    author_id = get_dblp_author_id_from_title(cnx, title, author_name)
    if author_id is None:
        author_id = get_dblp_author_id_from_aliases(cnx, author_name)

    if author_id is None:
        author_id = get_dblp_author_id_from_position(cnx, title, author_pos)

    return author_id


def author_is_already_in_db(cnx, link):
    cursor = cnx.cursor()
    arguments = [link.split("&")[0]]
    query = "SELECT author_url " \
            "FROM aux_scholar_authors " \
            "WHERE author_url = %s LIMIT 1"
    cursor.execute(query, arguments)
    data = cursor.fetchone()
    cursor.close()

    found = True
    if data is None:
        found = False
    return found


def get_author_positions(hit):
    positions = []
    author_positions = re.sub(" - .*", "", hit.find_element_by_class_name("gs_a").text).split(',')
    for author in author_positions:
        author = author.replace(u"\u2026", "")
        positions.append(author.strip())
    return positions


def add_authors_citations(hit, cnx, title, paper_id):
    author_links = hit.find_element_by_class_name("gs_a").find_elements_by_tag_name("a")
    author_positions = get_author_positions(hit)
    links = {}
    if author_links:
        for author in author_links:
            position = author_positions.index(author.text.strip())
            links.update({author.get_attribute("href"): position})

    if links:
        for link in links.keys():
            if 'scholar.google' in link:
                author_link = link.split("&")[0]
            else:
                author_link = SCHOLAR + link.split("&")[0]

            if not author_is_already_in_db(cnx, author_link):
                driver.get(link)
                #wait
                WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "gsc_rsb_st")))
                time.sleep(2)

                author_name = driver.title.split('-')[0]
                stats = driver.find_element_by_id("gsc_rsb_st")
                all = stats.find_element_by_xpath("//tr[2]/td[2]").text
                all_y5 = stats.find_element_by_xpath("//tr[2]/td[3]").text
                indexH = stats.find_element_by_xpath("//tr[3]/td[2]").text
                indexH_y5 = stats.find_element_by_xpath("//tr[3]/td[3]").text
                i10 = stats.find_element_by_xpath("//tr[4]/td[2]").text
                i10_y5 = stats.find_element_by_xpath("//tr[4]/td[3]").text

                try:
                    interests = driver.find_elements_by_class_name("gsc_prf_il")[1].text
                except:
                    interests = None

                author_pos = links.get(link)
                dblp_author_id = get_dblp_author_id(cnx, title, author_name, author_pos)

                cursor = cnx.cursor()
                arguments = [author_name.strip(), all, all_y5, indexH, indexH_y5, i10, i10_y5,
                             interests, dblp_author_id, paper_id, author_link, get_current_day()]
                query = "INSERT IGNORE INTO aux_scholar_authors " \
                        "SET name = %s, " \
                        "citations = %s, " \
                        "citations_5Y = %s, " \
                        "indexH = %s, " \
                        "indexH_5Y = %s, " \
                        "i10 = %s, " \
                        "i10_5Y = %s, " \
                        "interests = %s, " \
                        "dblp_author_id = %s, " \
                        "dblp_paper_id = %s, " \
                        "author_url = %s, " \
                        "tracked_at = %s"
                cursor.execute(query, arguments)
                cnx.commit()
                cursor.close()
                driver.back()


def add_paper_citation(hit, cnx, paper_id):
    citations = 0
    try:
        citations_info = hit.find_element_by_class_name("gs_fl").find_elements_by_tag_name("a")
        for cit in citations_info:
            if cit.get_attribute("href") is not None:
                if "/scholar?cites=" in cit.get_attribute("href"):
                    citations = re.sub('\D', '', cit.text)
                    break
    except NoSuchElementException:
        citations = 0

    if citations != 0:
        update_paper_citations_info(cnx, paper_id, citations)
    else:
        update_paper_citations_info(cnx, paper_id, 0)


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


def add_scholar_citations(cnx, title, key, paper_id):
    driver.get(SCHOLAR)

    if in_captcha_page():
        print "redirected to captcha"

    send_keys_to_browser(title)

    if in_captcha_page():
        print "redirected to captcha"


    try:
        #wait
        scholar_hits = WebDriverWait(driver, WAIT_TIME).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "gs_ri")))
        time.sleep(10)

        flag = 0
        for hit in scholar_hits:
            info_hit = hit.find_element_by_class_name("gs_rt")
            try:
                title_hit = info_hit.find_element_by_tag_name("a").text
                leveh_distance = nltk.metrics.edit_distance(re.sub(r'\s+', '', title_hit.lower()), re.sub(r'\s+', '', title.lower()))
                #if re.sub(r'\s+', '', title_hit.lower()) in re.sub(r'\s+', '', title.lower()):
                if leveh_distance <= 6:
                    if leveh_distance > 1:
                        logging.warning("match: " + title_hit + " ******* " + title + "  ******* " + str(leveh_distance))
                    add_paper_citation(hit, cnx, paper_id)

                    if COLLECT_PAPER_CITATIONS:
                        add_authors_citations(hit, cnx, title, paper_id)

                    flag = 1
                    break
                elif 7 <= leveh_distance <= 12:
                    logging.warning("unmatch: " + title_hit + " ******* " + title + "  ******* " + str(leveh_distance))
            except NoSuchElementException:
                continue

        if flag == 0:
            update_paper_citations_info(cnx, paper_id, -1)

    except TimeoutException:
        logging.warning("result not found for " + title)
        update_paper_citations_info(cnx, paper_id, -1)


def update_paper_citations_info(cnx, paper_id, citations):
    cursor = cnx.cursor()
    query = "UPDATE aux_dblp_inproceedings_tracks SET citations = %s, tracked_at = %s WHERE dblp_id = %s"
    arguments = [citations, get_current_day(), paper_id]
    cursor.execute(query, arguments)
    cnx.commit()
    cursor.close()


def collect_citation_info(cnx, query, arguments):
    conf_cursor = cnx.cursor()
    if arguments:
        conf_cursor.execute(query, arguments)
    else:
        conf_cursor.execute(query)
    row = conf_cursor.fetchone()
    while row is not None:
        paper_id = row[0]
        key = row[1]
        title = row[2]
        add_scholar_citations(cnx, title, key, paper_id)
        row = conf_cursor.fetchone()
    conf_cursor.close()


#update all citation info for all conferences, real time-consuming time
def update_citation_info(cnx):
    query = "SELECT dblp_id, dblp_key, title " \
            "FROM aux_dblp_inproceedings_tracks " \
            "WHERE tracked_at <= %s"
    arguments = [UPDATED_BEFORE]
    collect_citation_info(cnx, query, arguments)


def update_citation_info_by_conference(cnx, crossref):
    if crossref is None:
        query = "SELECT dblp_id, dblp_key, title " \
                "FROM aux_dblp_inproceedings_tracks " \
                "WHERE crossref IS NULL and tracked_at <= %s"
        arguments = [UPDATED_BEFORE]
    else:
        query = "SELECT dblp_id, dblp_key, title " \
                "FROM aux_dblp_inproceedings_tracks " \
                "WHERE crossref = %s and tracked_at <= %s"
        arguments = [crossref, UPDATED_BEFORE]
    collect_citation_info(cnx, query, arguments)

#min 1376236	max 2745443
def update_citation_info_by_id_interval(cnx, min, max):
    query = "SELECT dblp_id, dblp_key, title " \
            "FROM aux_dblp_inproceedings_tracks " \
            "WHERE id >= %s and id <= %s and tracked_at <= %s"
    arguments = [min, max, UPDATED_BEFORE]
    collect_citation_info(cnx, query, arguments)


def main():
    logging.basicConfig(filename=LOG_FILENAME, level=logging.WARNING)
    with open(LOG_FILENAME, "a") as log_file:
        log_file.write('\n')
    cnx = mysql.connector.connect(**dbconnection.CONFIG)

    #update_citation_info(cnx)
    update_citation_info_by_id_interval(cnx, 2200000, 2300000)
    #update_citation_info_by_conference(cnx, "conf/icse/2006")

    driver.close()
    cnx.close()

if __name__ == "__main__":
    main()

