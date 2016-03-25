__author__ = 'valerio cosentino'

import mysql.connector
from mysql.connector import errorcode
import db_config
from selenium import webdriver
import time
import re


#This script gathers (via Selenium) the TRACK assigned to the paper in the DBLP web-site


LOG_FILENAME = 'logger_paper_track.log'
driver = webdriver.Chrome(executable_path='C:\Program Files (x86)\Google\Chrome\chromedriver.exe')

WAIT_TIME = 5
DBLP = 'http://dblp.uni-trier.de/'


def get_track(cnx, track):
    found = None
    cursor = cnx.cursor()
    query = "SELECT id FROM `" + db_config.DB_NAME + "`.track WHERE name = %s"
    arguments = [track]
    cursor.execute(query, arguments)

    row = cursor.fetchone()

    if row:
        found = row[0]

    cursor.close()

    return found


def insert_track(cnx, track):
    cursor = cnx.cursor()
    query = "INSERT IGNORE INTO `" + db_config.DB_NAME + "`.track VALUES (NULL, %s)"
    arguments = [track]
    cursor.execute(query, arguments)
    cnx.commit()
    cursor.close()


def insert_track_paper(cnx, track_id, paper_id):
    cursor = cnx.cursor()
    query = "INSERT IGNORE INTO `" + db_config.DB_NAME + "`.track_paper VALUES (%s, %s)"
    arguments = [track_id, paper_id]
    cursor.execute(query, arguments)
    cnx.commit()
    cursor.close()


def go_to_dblp(url):
    if driver.current_url:
        previous_conference_info = driver.current_url.split('#')[0]
        conference_info = url.split('#')[0]
        if conference_info not in previous_conference_info:
            driver.get(DBLP + url)
    else:
        driver.get(DBLP + url)


def get_title_element(url, paper_title):
    found = None

    go_to_dblp(url)

    time.sleep(WAIT_TIME)

    hits = [web_element for web_element in driver.find_elements_by_class_name("title") if web_element.text.strip(".") == paper_title.strip(".")]

    if hits:
        if len(hits) > 1:
            print "too many hits"

        found = hits[0]
    else:
        print "paper with title: " + paper_title + " not found"

    return found


def digest_text(text):
    if ':' in text:
        text = text.split(':')[1].strip()

    return text

    # index = 0
    # words = text.split(' ')
    # for i in range(len(words)):
    #     if len(words[i]) <= 2:
    #         index = i
    #         break
    # digested = ' '.join(words[index+1:]).strip()
    #
    # if digested == '':
    #     digested = None
    #
    # return digested


def find_track(url, paper_title):
    web_element = get_title_element(url, paper_title)
    precedents = [we for we in web_element.find_elements_by_xpath("./preceding::*[starts-with(name(),'h')]") if we.text != '']
    precedents.reverse()
    found = None
    for p in precedents:
        if p.tag_name in ['h1', 'h2']:
            found = p
            break

    return digest_text(found.text)


def establish_connection():
    return mysql.connector.connect(**db_config.CONFIG)


def assign_track(cnx):
    cursor = cnx.cursor()
    query = "SELECT p.id, p.title, p.url, t.track_id " \
            "FROM `" + db_config.DB_NAME + "`.paper p " \
            "LEFT JOIN `" + db_config.DB_NAME + "`.track_paper t ON p.id = t.paper_id " \
            "WHERE t.track_id IS NULL"
    cursor.execute(query)

    row = cursor.fetchone()

    while row:
        paper_id = row[0]
        paper_title = row[1]
        url = row[2]

        track = find_track(url, paper_title)

        if track:
            insert_track(cnx, track)
            track_id = get_track(cnx, track)
            insert_track_paper(cnx, track_id, paper_id)

        row = cursor.fetchone()

    cursor.close()


def main():
    cnx = establish_connection()
    assign_track(cnx)
    driver.close()


if __name__ == "__main__":
    main()
