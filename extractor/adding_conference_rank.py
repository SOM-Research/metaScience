__author__ = 'atlanmod'

import logging
import mysql.connector
from mysql.connector import errorcode
from selenium import webdriver
import time
import database_connection_config as dbconnection

#This script gathers (via Selenium) the CONFERENCE RANK for the proceedings in AUX_DBLP_PROCEEDINGS
#and add them to the table.
#The RANK is retrieved from the link pointed by COMPUTER_SCIENCE_CONFERENCE_RANK
#
#The table AUX_DBLP_PROCEEDINGS is derived from DBLP_PUB_NEW

#Note that this script will be removed in the next version



LOG_FILENAME = 'logger_conference_rank.log'
COMPUTER_SCIENCE_CONFERENCE_RANK = 'http://lipn.univ-paris13.fr/~bennani/CSRank.html'
driver = webdriver.Chrome(executable_path='C:\Program Files (x86)\Google\Chrome\chromedriver.exe')


def add_proceedings_rank(cnx):
    cursor = cnx.cursor()
    driver.get(COMPUTER_SCIENCE_CONFERENCE_RANK)
    #iterate over the conferences of rank A* (0), A (1), B (2), C (3)
    for i in [0, 1, 2, 3]:
        driver.find_elements_by_tag_name("li")[i].find_element_by_partial_link_text("Rank").click()
        rank = driver.find_elements_by_tag_name("table")[i]
        conferences = rank.find_elements_by_tag_name("tr")
        for conf in conferences:
            try:
                core_acronym = conf.find_element_by_xpath("./td[1]").text
                core_rank = conf.find_element_by_xpath("./td[3]").text

                #exceptions
                if core_acronym == "FSE":
                    core_acronym = "'SIGSOFT FSE', 'ESEC/SIGSOFT FSE'"

                query = "UPDATE aux_dblp_proceedings SET rank = %s WHERE source IN (%s) "
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
    cnx = mysql.connector.connect(**dbconnection.CONFIG)
    add_proceedings_rank(cnx)

if __name__ == "__main__":
    main()