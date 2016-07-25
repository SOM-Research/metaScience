__author__ = 'valerio cosentino'

import csv
import mysql.connector
from mysql.connector import errorcode
import re
import db_config
import mysql.connector
from mysql.connector import errorcode
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
import time

CVS_PATH = "../data/CORE.csv"

driver = webdriver.Chrome(executable_path='C:\Program Files (x86)\Google\Chrome\chromedriver.exe')
WAITING_TIME = 3 #in secs
URL = 'https://www.google.com'


def process_name(name):
    return re.sub('\(.*\)', '', name)


def get_rank_id(rank):
    id = None
    if rank == 'A*': id = 1
    elif rank == 'A': id = 2
    elif rank == 'B': id = 3
    elif rank == 'C': id = 4

    return id


def find_match_by_title_acronym(cnx, acronym, title):
    conference_id = None
    cursor = cnx.cursor()
    query = "SELECT id " \
            "FROM `" + db_config.DB_NAME + "`.conference " \
            "WHERE acronym = %s or name = %s"
    arguments = [acronym, title]
    cursor.execute(query, arguments)
    row = cursor.fetchone()

    if row:
        conference_id = row[0]

    cursor.close()

    return conference_id


def find_match_by_url(cnx, reference):
    conference_id = None
    cursor = cnx.cursor()
    query = "SELECT id " \
            "FROM `" + db_config.DB_NAME + "`.conference " \
            "WHERE url LIKE '%" + reference + "'"
    cursor.execute(query)
    row = cursor.fetchone()

    if row:
        conference_id = row[0]

    cursor.close()

    return conference_id


def find_match_in_website(cnx, title):
    conference_id = None
    driver.get(URL)
    time.sleep(WAITING_TIME)
    query_field = [i for i in driver.find_elements_by_tag_name("input") if i.get_attribute("id") == "lst-ib"][0]
    query_field.send_keys(title + " dblp" + Keys.ENTER)
    time.sleep(WAITING_TIME)
    hits_container = driver.find_element_by_id('rso')
    hits = hits_container.find_elements_by_class_name('g')
    time.sleep(WAITING_TIME)

    for h in hits:
        try:
            link = h.find_element_by_class_name("rc").find_element_by_tag_name("a").get_attribute("href")
        except:
            link = None

        if link:
            if 'uni-trier' in link and '/db/conf/' in link and (link.endswith('/index.html') or link.endswith('/')):
                reference = '/db/conf/' + '/'.join(link.split('/db/conf/')[1].split('/')[:-1])
                conference_id = find_match_by_url(cnx, reference)
                break

    return conference_id


def find_match(cnx, acronym, title, rank):
    conference_id = find_match_by_title_acronym(cnx, acronym, title)
    if not conference_id:
        conference_id = find_match_in_website(cnx, title)

    if not conference_id:
        print 'no match for ' + title + '(' + acronym + ') ' + rank
    else:
        rank_id = get_rank_id(rank)
        cursor_update = cnx.cursor()
        update = "UPDATE `" + db_config.DB_NAME + "`.conference SET rank_id = %s WHERE id = %s"
        arguments = [rank_id, conference_id]
        cursor_update.execute(update, arguments)
        cnx.commit()
        cursor_update.close()


def select_db(cnx):
    cursor = cnx.cursor()
    cursor.execute("USE " + db_config.DB_NAME)
    cursor.close()


def establish_connection():
    return mysql.connector.connect(**db_config.CONFIG)


def main():
    input = open(CVS_PATH, 'rb')
    reader = csv.reader(input)

    cnx = establish_connection()
    select_db(cnx)

    for row in reader:
        name = process_name(row[1])
        acronym = row[2]
        rank = row[4]

        find_match(cnx, acronym, name, rank)

    input.close()
    cnx.close()

if __name__ == "__main__":
    main()
