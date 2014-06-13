__author__ = 'atlanmod'

import logging
import mysql.connector
from mysql.connector import errorcode
from selenium import webdriver
import time

COMPUTER_SCIENCE_CONFERENCE_RANK = 'http://lipn.univ-paris13.fr/~bennani/CSRank.html'

LOG_FILENAME = 'logger_conference_rank.log'

CONFIG = {
    'user': 'root',
    'password': 'coitointerrotto',
    'host': 'atlanmodexp.info.emn.fr',
    'port': '13506',
    'database': 'dblp',
    'raise_on_warnings': False,
    'buffered': True
}

driver = webdriver.Chrome(executable_path='C:\Program Files (x86)\Google\Chrome\chromedriver.exe')


def get_ranked_conferences_core():
    driver.get(COMPUTER_SCIENCE_CONFERENCE_RANK)
    time.sleep(5)
    ranks = driver.find_elements_by_tag_name("table")
    return ranks


def add_proceedings_rank(cnx):
    cursor = cnx.cursor()
    ranks = get_ranked_conferences_core()
    for rank in ranks:
        conferences = rank.find_elements_by_tag_name("tr")
        for conf in conferences:
            try:
                core_acronym = conf.find_element_by_xpath("./td[1]").text
                core_rank = conf.find_element_by_xpath("./td[3]").text
                query = "UPDATE aux_dblp_proceedings SET rank = %s WHERE source = %s " \
                        "AND type IN ('conference', 'symposium')"
                arguments = [core_rank, core_acronym]
                cursor.execute(query, arguments)
                cnx.commit()
            except:
                continue
    cursor.close()
    driver.close()


def main():
    logging.basicConfig(filename=LOG_FILENAME, level=logging.WARNING)
    with open(LOG_FILENAME, "w") as log_file:
        log_file.write('\n')
    cnx = mysql.connector.connect(**CONFIG)
    add_proceedings_rank(cnx)

if __name__ == "__main__":
    main()