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
    query = "SELECT author_id " \
            "FROM dblp_authorid_ref_new author " \
            "JOIN dblp_pub_new pub " \
            "ON author.id = pub.id " \
            "WHERE title = %s"
    arguments = [title]
    cursor.execute(query, arguments)
    ids = cursor.fetchall()
    id = ids[author_pos]
    cursor.close()
    if id is None:
        return 0
    return id[0]


def get_dblp_author_id(cnx, title, author_name, author_pos):
    author_name = get_dblp_author_id_from_title(cnx, title, author_name)
    if author_name is None:
        author_name = get_dblp_author_id_from_aliases(cnx, author_name)
    else:
        author_name = get_dblp_author_id_from_position(cnx, title, author_pos)

    return author_name


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


def add_authors_citations(hit, cnx, title, paper_id):
    authors = hit.find_element_by_class_name("gs_a").find_elements_by_tag_name("a")
    links = {}
    if authors:
        for author in authors:
            links.update({author.get_attribute("href"): authors.index(author)})

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
                arguments = [author_name, all, all_y5, indexH, indexH_y5, i10, i10_y5, interests, dblp_author_id, paper_id, author_link]
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


def add_citation_info(cnx):
    conf_cursor = cnx.cursor()
    query = "SELECT id, dblp_key, title " \
            "FROM dblp_pub_new " \
            "WHERE dblp_key IS NOT NULL AND title IS NOT NULL " \
            "AND type NOT IN ('www', 'phdthesis', 'masterthesis')" \
            "AND dblp_key NOT LIKE %s " \
            "AND id NOT IN (SELECT DISTINCT paper_id FROM aux_scholar_authors) " \
            "AND year >= 2003 " \
            "AND source IN " \
            "('ICSE', 'FSE', 'ESEC', 'ASE', 'SPLASH', 'OOPSLA', 'ECOOP', 'ISSTA', 'FASE')"
    arguments = ['dblpnote%']
    conf_cursor.execute(query, arguments)
    row = conf_cursor.fetchone()
    while row is not None:
        paper_id = row[0]
        key = row[1]
        title = row[2]
        add_scholar_citations(cnx, title, key, paper_id)
        row = conf_cursor.fetchone()
    conf_cursor.close()


def get_pos_to_start(cnx):
    conf_cursor = cnx.cursor()
    query = "SELECT MAX(paper_id) " \
            "FROM aux_scholar_authors"
    conf_cursor.execute(query)
    row = conf_cursor.fetchone()
    return row[0]


def main():
    logging.basicConfig(filename=LOG_FILENAME, level=logging.WARNING)
    with open(LOG_FILENAME, "w") as log_file:
        log_file.write('\n')
    cnx = mysql.connector.connect(**CONFIG)

    add_citation_info(cnx)
    driver.close()
    cnx.close()

if __name__ == "__main__":
    main()