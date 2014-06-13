__author__ = 'atlanmod'

__author__ = 'atlanmod'

import logging
import mysql.connector
from mysql.connector import errorcode
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
import re
import time

LOG_FILENAME = 'logger_paper_citations.log'
SCHOLAR = 'http://scholar.google.com'
driver = webdriver.Chrome(executable_path='C:\Program Files (x86)\Google\Chrome\chromedriver.exe')

CONFIG = {
    'user': 'root',
    'password': 'coitointerrotto',
    'host': 'atlanmodexp.info.emn.fr',
    'port': '13506',
    'database': 'dblp',
    'raise_on_warnings': False,
    'buffered': True
}


def get_dblp_author_id(cnx, title, author_name):
    cursor = cnx.cursor()
    query = "SELECT author_id " \
            "FROM dblp.dblp_authorid_ref_new author " \
            "JOIN dblp.dblp_pub_new pub " \
            "ON author.id = pub.id " \
            "WHERE title = %s AND author = %s"
    arguments = [title, author_name]
    cursor.execute(query, arguments)
    id = cursor.fetchone()[0]
    cursor.close()

    if id is None:
        return 0
    return id


def add_authors_citations(hit, cnx, title):
    authors = hit.find_element_by_class_name("gs_a").find_elements_by_tag_name("a")
    if authors:
        for author in authors:
            driver.get(author.get_attribute("href"))
            time.sleep(1)
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

            dblp_author_id = get_dblp_author_id(cnx, title, author_name)

            cursor = cnx.cursor()
            arguments = [author_name, all, all_y5, indexH, indexH_y5, i10, i10_y5, interests, dblp_author_id]
            query = "INSERT IGNORE INTO aux_scholar_authors " \
                    "SET name = %s, citations = %s, " \
                    "citations2009 = %s, " \
                    "indexH = %s, " \
                    "indexH2009 = %s, i10 = %s, " \
                    "i102009 = %s, " \
                    "interests = %s, " \
                    "dblp_author_id = %s"
            cursor.execute(query, arguments)
            cnx.commit()
            cursor.close()


def add_paper_citation(hit, cnx, key):
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


def add_scholar_citations(cnx, title, key):
    driver.get(SCHOLAR)
    search_box = driver.find_element_by_id("gs_hp_tsi")
    search_box.send_keys(title + Keys.RETURN)
    #wait
    time.sleep(1)

    scholar_hits = driver.find_elements_by_class_name("gs_ri")

    for hit in scholar_hits:
        info_hit = hit.find_element_by_class_name("gs_rt")
        try:
            title_hit = info_hit.find_element_by_tag_name("a").text
            if re.sub(r'\s+', '', title_hit) in re.sub(r'\s+', '', title):
                add_paper_citation(hit, cnx, key)
                add_authors_citations(hit, cnx, title)
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


def add_citation_info(cnx):
    conf_cursor = cnx.cursor()
    query = "SELECT dblp_key, title " \
            "FROM dblp_pub_new " \
            "WHERE dblp_key IS NOT NULL AND title IS NOT NULL " \
            "AND type NOT IN ('www', 'phdthesis', 'masterthesis')" \
            "AND dblp_key NOT LIKE 'dblpnote%'"
    conf_cursor.execute(query)
    row = conf_cursor.fetchone()

    while row is not None:
        key = row[0]
        title = row[1]
        add_scholar_citations(cnx, title, key)
        row = conf_cursor.fetchone()
    conf_cursor.close()


def main():
    logging.basicConfig(filename=LOG_FILENAME, level=logging.WARNING)
    with open(LOG_FILENAME, "w") as log_file:
        log_file.write('\n')
    cnx = mysql.connector.connect(**CONFIG)
    add_citation_info(cnx)
    driver.close()


if __name__ == "__main__":
    main()