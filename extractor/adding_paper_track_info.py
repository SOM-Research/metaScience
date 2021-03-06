__author__ = 'atlanmod'

import logging
import mysql.connector
from mysql.connector import errorcode
from selenium import webdriver
import time
from selenium.common.exceptions import NoSuchElementException
import cross_module_variables as shared
import database_connection_config as dbconnection

#This script gathers (via Selenium) the TRACK and SUB-TRACK(s) assigned to the paper in the conferences stored in
#AUX_DBLP_INPROCEEDINGS_TRACKS table
#
#The TRACK and SUB-TRACK(s) information is stored in AUX_DBLP_INPROCEEDINGS_TRACKS
#The table AUX_DBLP_INPROCEEDINGS_TRACKS is derived from DBLP_PUB_NEW

LOG_FILENAME = 'logger_paper_track.log'
driver = webdriver.Chrome(executable_path='C:\Program Files (x86)\Google\Chrome\chromedriver.exe')


def find_header(topic):
    for i in range(1, 6):
        try:
            topic.find_element_by_tag_name("h"+str(i))
            return i
        except:
            continue
    return 0


def collect_topics(topic, h_level, topics):
    if h_level == 2:
        return topics
    else:
        previous_topic = topic.find_element_by_xpath("preceding-sibling::header[1]")
        if h_level-1 == find_header(previous_topic):
            topics.append(previous_topic.text)
            return collect_topics(previous_topic, h_level-1, topics)
        else:
            return collect_topics(previous_topic, h_level, topics)


def get_paper_for_conf_from_url(cnx, conf):
    cursor = cnx.cursor()
    query = "SELECT dblp_key, dblp_id FROM aux_dblp_inproceedings_tracks WHERE url LIKE %s"
    arguments = [conf + '%']
    cursor.execute(query, arguments)
    data = cursor.fetchall()
    cursor.close()
    return data


def get_paper_for_conf_from_crossref(cnx, crossref):
    cursor = cnx.cursor()
    query = "SELECT dblp_key, dblp_id FROM aux_dblp_inproceedings_tracks WHERE BINARY crossref = %s"
    arguments = [crossref]
    cursor.execute(query, arguments)
    data = cursor.fetchall()
    cursor.close()
    return data


def get_page_conference_dblp(conf_url):
    driver.get(shared.DBLP + "/" + conf_url)
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


def insert_topics(cnx, paper_id, topics):
    if len(topics) == 3:
        query = "UPDATE aux_dblp_inproceedings_tracks SET track = %s, subtrack1 = %s, subtrack2 = %s WHERE dblp_id = %s"
        arguments = [topics[2], topics[1], topics[0], paper_id]
    elif len(topics) == 2:
        query = "UPDATE aux_dblp_inproceedings_tracks SET track = %s, subtrack1 = %s WHERE dblp_id = %s"
        arguments = [topics[1], topics[0], paper_id]
    elif len(topics) == 1:
        query = "UPDATE aux_dblp_inproceedings_tracks SET track = %s WHERE dblp_id = %s"
        arguments = [topics[0], paper_id]
    elif len(topics) == 0:
        query = "UPDATE aux_dblp_inproceedings_tracks SET track = 'Main' WHERE dblp_id = %s"
        arguments = [paper_id]
    else:
        print('paper_id: ' + paper_id + ' topics: ' + str(topics))

    if len(topics) <= 3:
        cursor = cnx.cursor()
        cursor.execute(query, arguments)
        cnx.commit()
        cursor.close()


def add_track_info_from_url(cnx):
    conf_cursor = cnx.cursor()
    query = "SELECT DISTINCT SUBSTRING_INDEX(url, '#', 1) " \
            "FROM aux_dblp_inproceedings_tracks " \
            "WHERE url IS NOT NULL AND track IS NULL"
    conf_cursor.execute(query)
    row = conf_cursor.fetchone()

    while row is not None:
        conference_url = row[0].split('#')[0]
        try:
            conf_page = get_page_conference_dblp(conference_url)
            papers = get_paper_for_conf_from_url(cnx, conference_url)
            for paper in papers:
                try:
                    topic = conf_page.find_element_by_id(paper[0]).find_element_by_xpath("../preceding-sibling::header[1]")
                    topics = collect_topics(topic, find_header(topic), [topic.text])
                except NoSuchElementException:
                    topics = []
                insert_topics(cnx, paper[1], topics)
            row = conf_cursor.fetchone()
        except:
            if conference_url is not None:
                logging.warning(str(conference_url))
            else:
                logging.warning("no rows from db")
    conf_cursor.close()


def add_track_info_from_crossref(cnx):
    conf_cursor = cnx.cursor()
    query = "SELECT DISTINCT crossref " \
            "FROM dblp.aux_dblp_inproceedings_tracks " \
            "WHERE crossref IS NOT NULL AND track is NULL"
    conf_cursor.execute(query)
    row = conf_cursor.fetchone()

    while row is not None:
        crossref = row[0]
        conf_info = crossref.split("/")
        conference_url = "db/" + conf_info[0] + "/" + conf_info[1] + "/" + conf_info[1] + conf_info[2] + ".html"
        try:
            conf_page = get_page_conference_dblp(conference_url)
            papers = get_paper_for_conf_from_crossref(cnx, crossref)
            for paper in papers:
                try:
                    topic = conf_page.find_element_by_id(paper[0]).find_element_by_xpath("../preceding-sibling::header[1]")
                    topics = collect_topics(topic, find_header(topic), [topic.text])
                except NoSuchElementException:
                    topics = []
                insert_topics(cnx, paper[1], topics)
            row = conf_cursor.fetchone()
        except:
            if conference_url is not None:
                logging.warning(str(conference_url))
            else:
                logging.warning("no rows from db")
    conf_cursor.close()


def main():
    logging.basicConfig(filename=LOG_FILENAME, level=logging.WARNING)
    with open(LOG_FILENAME, "w") as log_file:
        log_file.write('\n')
    cnx = mysql.connector.connect(**dbconnection.CONFIG)
    add_track_info_from_url(cnx)
    add_track_info_from_crossref(cnx)
    driver.close()

if __name__ == "__main__":
    main()