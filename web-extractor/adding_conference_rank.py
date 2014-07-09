__author__ = 'atlanmod'

import logging
import mysql.connector
from mysql.connector import errorcode
from selenium import webdriver
import time

#This script gathers (via Selenium) the CONFERENCE RANK for the proceedings in AUX_DBLP_PROCEEDINGS
#and add them to the table.
#The RANK is retrieved from the link pointed by COMPUTER_SCIENCE_CONFERENCE_RANK
#
#The table AUX_DBLP_PROCEEDINGS is derived from DBLP_PUB_NEW
#Below the mysql script to generate the AUX_DBLP_PROCEEDINGS is shown
# create table dblp.aux_dblp_proceedings as
# select id as dblp_id, dblp_key, url, source, year
# from dblp.dblp_pub_new where type = 'proceedings';
#
# alter table dblp.aux_dblp_proceedings
# add column id int(11) primary key auto_increment first,
# add column location varchar(256),
# add column type varchar(25),
# add column month varchar(25),
# add column rank varchar(10),
# add index dblp_key (dblp_key);

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