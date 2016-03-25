__author__ = 'valerio cosentino'

import mysql.connector
from mysql.connector import errorcode
from selenium import webdriver
import time
import re
import db_config


driver = webdriver.Chrome(executable_path='C:\Program Files (x86)\Google\Chrome\chromedriver.exe')
WAITING_TIME = 3 #in secs

def establish_connection():
    return mysql.connector.connect(**db_config.CONFIG)


def get_conference_name(url):
    driver.get("http://" + url)
    time.sleep(WAITING_TIME)
    headline = re.sub("\(.*\)", "", driver.find_element_by_id("headline").find_element_by_tag_name("h1").text)

    return headline


def update_conference_title(cnx):
    cursor = cnx.cursor()
    cursor_update = cnx.cursor()
    query = "SELECT id, url FROM  `" + db_config.DB_NAME + "`.conference WHERE name IS NULL;"
    cursor.execute(query)

    row = cursor.fetchone()
    while row:
        conference_id = row[0]
        dblp_url = row[1]
        conference_name = get_conference_name(dblp_url)

        query_update = "UPDATE `" + db_config.DB_NAME + "`.conference SET name = %s WHERE id = %s;"
        arguments = [conference_name,conference_id]
        cursor_update.execute(query_update, arguments)
        cnx.commit()

        row = cursor.fetchone()

    cursor_update.close()
    cursor.close()


def main():
    cnx = establish_connection()
    update_conference_title(cnx)
    cnx.close()
    driver.close()


if __name__ == "__main__":
    main()