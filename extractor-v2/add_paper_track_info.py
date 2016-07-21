__author__ = 'valerio cosentino'

import mysql.connector
from mysql.connector import errorcode
import db_config
from selenium import webdriver
import time

#This script gathers (via Selenium) the TRACK assigned to the paper in the DBLP web-site


LOG_FILENAME = 'logger_paper_track.log'
driver = webdriver.Chrome(executable_path='C:\Program Files (x86)\Google\Chrome\chromedriver.exe')

WAIT_TIME = 2
DBLP = 'http://dblp.uni-trier.de/'


def get_paper_id(cnx, paper_title, paper_ref):
    found = get_paper_id_from_title(cnx, paper_title)

    if not found:
        found = get_paper_id_from_ref(cnx, paper_ref)

    return found


def get_paper_id_from_ref(cnx, ref):
    cursor = cnx.cursor()
    found = None
    query = "SELECT id FROM `" + db_config.DB_NAME + "`.paper p WHERE SUBSTRING_INDEX(p.url, '#', -1) = %s"
    arguments = [ref]
    cursor.execute(query, arguments)

    row = cursor.fetchone()

    if row:
        found = row[0]

    cursor.close()
    return found


def get_paper_id_from_title(cnx, title):
    cursor = cnx.cursor()
    found = None
    query = "SELECT id FROM `" + db_config.DB_NAME + "`.paper WHERE title = %s OR title = %s"
    arguments = [title, title.strip(".")]
    cursor.execute(query, arguments)

    row = cursor.fetchone()

    if row:
        found = row[0]

    cursor.close()
    return found


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


def digest_text(text):
    if ':' in text:
        text = text.split(':')[1].strip()

    return text.lower()


def populate_db(cnx, url):
    driver.get(DBLP + url)
    time.sleep(WAIT_TIME)

    paper_titles = [web_element for web_element in driver.find_elements_by_xpath("//li[@class='entry inproceedings']")]

    for pt in paper_titles:
        track = find_track(pt)

        if track:
            paper_title = pt.find_element_by_class_name("title").text
            paper_ref = pt.get_attribute("id").split('/')[-1]

            paper_id = get_paper_id(cnx, paper_title, paper_ref)

            if paper_id:
                insert_track(cnx, track)
                track_id = get_track(cnx, track)
                insert_track_paper(cnx, track_id, paper_id)
            else:
                print 'paper not found: ' + paper_title + ' conf: ' + url


def find_track(paper_web_element):
    precedents = [we for we in paper_web_element.find_elements_by_xpath("./preceding::*[starts-with(name(),'h')]") if we.text != '']
    precedents.reverse()
    found = None
    for p in precedents:
        if p.tag_name in ['h2', 'h3']:
            found = digest_text(p.text)
            break

    return found


def select_db(cnx):
    cursor = cnx.cursor()
    cursor.execute("USE " + db_config.DB_NAME)
    cursor.close()


def establish_connection():
    return mysql.connector.connect(**db_config.CONFIG)


def assign_track2papers(cnx):
    cursor = cnx.cursor()
    query = "SELECT conference_url, id " \
            "FROM ( " \
                "SELECT p.id, SUBSTRING_INDEX(p.url, '#', 1) as conference_url, count(p.id) as total_papers, count(track_id) as papers_with_track " \
                "FROM paper p LEFT JOIN track_paper t on p.id = t.paper_id " \
                "GROUP BY SUBSTRING_INDEX(p.url, '#', 1) " \
                "ORDER BY id ASC) AS x " \
            "WHERE papers_with_track = 0"

    cursor.execute(query)

    row = cursor.fetchone()
    first_id = row[1]
    while row:
        conf_url = row[0]
        populate_db(cnx, conf_url)
        row = cursor.fetchone()
        last_id = row[1]
    cursor.close()

    print 'interval: ' + str(first_id) + ' - ' + str(last_id)


def main():
    cnx = establish_connection()
    select_db(cnx)
    assign_track2papers(cnx)
    driver.close()


if __name__ == "__main__":
    main()
