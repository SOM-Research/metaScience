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

#This script performs two actions:
#1) For each paper published from 2003 in the conferences below(*),
#   it gathers (via Selenium) the current number of CITATIONS
#(*) ICSE, FSE, ESEC, ASE, SPLASH, OOPSLA, ECOOP, ISSTA, FASE,
#    MODELS, WCRE, CSMR, ICMT, COMPSAC, APSEC, VISSOFT, ICSM, SOFTVIS,
#    SCAM, TOOLS, CAISE, ER, ECMFA, ECMDA-FA
#
#Such information is stored in AUX_DBLP_INPROCEEDINGS_TRACKS
#The table AUX_DBLP_INPROCEEDINGS_TRACKS is derived from DBLP_PUB_NEW
#Below the mysql script to generate the AUX_DBLP_INPROCEEDINGS_TRACKS is shown
# create table dblp.aux_dblp_inproceedings_tracks as
# select id as dblp_id, dblp_key, crossref, url
# from dblp.dblp_pub_new where type = 'inproceedings';
#
# alter table dblp.aux_dblp_inproceedings_tracks
# add column id int(11) primary key auto_increment first,
# add column track varchar(256),
# add column subtrack1 varchar(256),
# add column subtrack2 varchar(256),
# add column citations numeric(10),
# add index dblp_key (dblp_key);
#
#2) It finds (via Selenium) the google scholar page for each author that published in the previous conferences
#   and collects the author CITATIONS, INDEX, I10 for the past five year and the global CITATIONS, INDEX, I10.
#   In addition, it collects for each author his INTERESTS (defined in his scholar page)
#   Note that, Scholar could blocked this process, if the requests are too fast. Thereof, we strongly suggest to
#   use at least time.sleep(2) after each google scholar request
#
#Such information are stored in AUX_SCHOLAR_AUTHORS
#Below the mysql script to generate the AUX_SCHOLAR_AUTHORS is shown
# create table dblp.aux_scholar_authors (
# 	name varchar(256) primary key,
# 	citations numeric(15),
# 	citations2009 numeric(15),
# 	indexH numeric(15),
# 	indexH2009 numeric(15),
# 	i10 numeric(15),
# 	i102009 numeric(15),
# 	interests text,
#   dblp_author_id numeric(15),
#   paper_id numeric(15),
#   author_url text
# );
#
# alter table dblp.aux_scholar_authors
# add index paper_id (paper_id);

SCHOLAR = 'http://scholar.google.com'
LOG_FILENAME = 'logger_paper_citations.log'
driver = webdriver.Chrome(executable_path='C:\Program Files (x86)\Google\Chrome\chromedriver.exe')


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
        return 0
    return id[0]


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
        return 0
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
    id = cursor.fetchone()[0]
    cursor.close()
    if id is None:
        return 0
    return id


def get_dblp_author_id(cnx, title, author_name, author_pos):
    author_id = get_dblp_author_id_from_title(cnx, title, author_name)
    if author_id is None:
        author_id = get_dblp_author_id_from_aliases(cnx, author_name)
    else:
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
                WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "stats")))
                time.sleep(2)

                author_name = driver.title.split('-')[0]
                stats = driver.find_element_by_id("stats")
                all = stats.find_element_by_xpath("//tr[2]/td[2]").text
                all_y5 = stats.find_element_by_xpath("//tr[2]/td[3]").text
                indexH = stats.find_element_by_xpath("//tr[3]/td[2]").text
                indexH_y5 = stats.find_element_by_xpath("//tr[3]/td[3]").text
                i10 = stats.find_element_by_xpath("//tr[4]/td[2]").text
                i10_y5 = stats.find_element_by_xpath("//tr[4]/td[3]").text

                try:
                    interests = driver.find_element_by_id("cit-int-form").text
                except:
                    interests = None

                author_pos = links.get(link)
                dblp_author_id = get_dblp_author_id(cnx, title, author_name, author_pos)

                cursor = cnx.cursor()
                arguments = [author_name.strip(), all, all_y5, indexH, indexH_y5, i10, i10_y5, interests, dblp_author_id, paper_id, author_link]
                query = "INSERT IGNORE INTO aux_scholar_authors " \
                        "SET name = %s, citations = %s, " \
                        "citations2009 = %s, " \
                        "indexH = %s, " \
                        "indexH2009 = %s, i10 = %s, " \
                        "i102009 = %s, " \
                        "interests = %s, " \
                        "dblp_author_id = %s, " \
                        "paper_id = %s, " \
                        "author_url = %s"
                cursor.execute(query, arguments)
                cnx.commit()
                cursor.close()
                driver.back()


def add_paper_citation(hit, cnx, key):
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
        update_paper_citations_info(cnx, key, citations)
    else:
        update_paper_citations_info(cnx, key, 0)


def add_scholar_citations(cnx, title, key, paper_id):
    driver.get(SCHOLAR)
    search_box = driver.find_element_by_id("gs_hp_tsi")
    search_box.send_keys(title + Keys.RETURN)
    #wait
    time.sleep(4)

    scholar_hits = driver.find_elements_by_class_name("gs_ri")

    for hit in scholar_hits:
        info_hit = hit.find_element_by_class_name("gs_rt")
        try:
            title_hit = info_hit.find_element_by_tag_name("a").text
            leveh_distance = nltk.metrics.edit_distance(re.sub(r'\s+', '', title_hit.lower()), re.sub(r'\s+', '', title.lower()))
            #if re.sub(r'\s+', '', title_hit.lower()) in re.sub(r'\s+', '', title.lower()):
            if leveh_distance <= 3:
                if leveh_distance > 1:
                    logging.warning("match: " + title_hit + " ******* " + title + "  ******* " + str(leveh_distance))
                add_paper_citation(hit, cnx, key)
                add_authors_citations(hit, cnx, title, paper_id)
                break
        except NoSuchElementException:
            continue


def update_paper_citations_info(cnx, key, citations):
    cursor = cnx.cursor()
    query = "UPDATE aux_dblp_inproceedings_tracks SET citations = %s WHERE dblp_key = %s"
    arguments = [citations, key]
    cursor.execute(query, arguments)
    cnx.commit()
    cursor.close()

    # #check if the citations have already been set
    # cursor = cnx.cursor()
    # query = "SELECT citations FROM aux_dblp_inproceedings_tracks WHERE dblp_key = %s"
    # arguments = [key]
    # cursor.execute(query, arguments)
    # cit = cursor.fetchone()[0]
    #
    # #if citations are null
    # if cit is None:
    #     query = "UPDATE aux_dblp_inproceedings_tracks SET citations = %s WHERE dblp_key = %s"
    #     arguments = [citations, key]
    #     cursor.execute(query, arguments)
    #     cnx.commit()
    # cursor.close()
    # #TODO if citations are not null, we should update this number from one year to the next


def add_citation_info(cnx):
    conf_cursor = cnx.cursor()
    query = "SELECT id, dblp_key, title " \
            "FROM aux_dblp_inproceedings_tracks " \
            "WHERE citations IS NULL"
    conf_cursor.execute(query)
    # query = "SELECT id, dblp_key, title " \
    #         "FROM dblp_pub_new pub " \
    #         "WHERE dblp_key IS NOT NULL AND title IS NOT NULL " \
    #         "AND type NOT IN ('www', 'phdthesis', 'masterthesis')" \
    #         "AND dblp_key NOT LIKE %s " \
    #         "AND year >= 2003 " \
    #         "AND NOT EXISTS (SELECT DISTINCT dblp_key " \
    #                         "FROM aux_dblp_inproceedings_tracks " \
    #                         "WHERE pub.dblp_key = dblp_key AND citations IS NOT NULL) " \
    #         "AND NOT EXISTS (SELECT DISTINCT paper_id " \
    #                         "FROM aux_scholar_authors " \
    #                         "WHERE paper_id = pub.id) " \
    #         "AND source IN (" + shared.CONFERENCES + ")"
    #arguments = ['dblpnote%']
    #conf_cursor.execute(query, arguments)
    row = conf_cursor.fetchone()
    while row is not None:
        paper_id = row[0]
        key = row[1]
        title = row[2]
        add_scholar_citations(cnx, title, key, paper_id)
        row = conf_cursor.fetchone()
    conf_cursor.close()


def main():
    logging.basicConfig(filename=LOG_FILENAME, level=logging.WARNING)
    with open(LOG_FILENAME, "w") as log_file:
        log_file.write('\n')
    cnx = mysql.connector.connect(**dbconnection.CONFIG)

    add_citation_info(cnx)
    driver.close()
    cnx.close()

if __name__ == "__main__":
    main()