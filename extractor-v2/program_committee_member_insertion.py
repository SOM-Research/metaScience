__author__ = 'atlanmod'

import logging
import mysql.connector
from mysql.connector import errorcode
import json
import codecs
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import db_config
import time
import re

#This script gathers (via Selenium) the PROGRAM COMMITTEE CHAIR and MEMBERS
#for the editions from 2003 of the conferences defined in the pc_info.json
#Currently, we track
#ICSE, FSE, ESEC, ASE, SPLASH, OOPSLA, ECOOP, ISSTA, FASE,
#MODELS, WCRE, CSMR, ICMT, COMPSAC, APSEC, VISSOFT, ICSM, SOFTVIS,
#SCAM, TOOLS, CAISE, ER, ECMFA, ECMDA-FA, MSR
#The configuration of the json file is explained clearly in the main()

EXCEPTION_NAMES = {
                'Ernesto Pimentel Sanchez':'Ernesto Pimentel',
                'Rob Pettit': 'Robert G. Pettit IV',
                'Aswin A. van den Berg': 'Aswin van den Berg',
                'Albert Zuendorf': 'Albert Zundorf',
                'Issy Ben-Shaul': 'Israel Ben-Shaul ',
                'Brad Martin': 'Bradley C. Martin',
                'James Larus': 'James R. Larus',
                'Chandra Boyapati': 'Chandrasekhar Boyapati',
                'R Venkatesh': 'R. Venkatesh',
                'Dany Yankelevich': 'Daniel Yankelevich',
                'Annie Anton': 'Annie I. Anton',
                'Julia Lawall': 'Julia L. Lawall',
                'Lenore Zuck': 'Lenore D. Zuck',
                'Julie McCann': 'Julie A. McCann',
                'Joe Loyall': 'Joseph P. Loyall',
                'Todd Proebsting': 'Todd A. Proebsting',
                'Bart Jacobs': 'Bart Jacobs 0002',
                'Laurie Tratt': 'Laurence Tratt',
                'Todd Veldhuizen': 'Todd L. Veldhuizen',
                'Atushi Ohori': 'Atsushi Ohori',
                'Kapil Vaswani': 'Kapil Vaswani',
                'Dimitra Giannakopolou': 'Dimitra Giannakopoulou',
                'Jan ?yvind Aagedal': 'Jan Oyvind Aagedal',
                'Andr?s Pataricza': 'Andras Pataricza',
                'Alfred W. Strohmeier' : 'Alfred Strohmeier',
                'Istvan Forgas': 'Istvan Forgacs',
                'Jorge Figeiredo': 'Jorge C. A. de Figueiredo',
                'Mohammady El-Ramly': 'Mohammad El-Ramly',
                'Panos Linos': 'Panagiotis K. Linos',
                'Tobias Roetschke': 'Tobias Rotschke',
                'Manny Lehman': 'Meir M. Lehman',
                'Jesus G. Molina': 'Jesus Garcia Molina',
                'Shigeru Miyake Hitachi': 'Shigeru Miyake',
                'Bill Claycomb': 'William Claycomb',
                'Sandra Stincic Clarke': 'Sandra Stincic',
                'Y. T. Yu ': 'Yuen-Tak Yu',
                'Shahani Markus Weerawarana':'Sanjiva Weerawarana',
                'David C. Kung' : 'David Chenho Kung',
                'Nakife Yasemin Topaloglu': 'N. Yasemin Topaloglu',
                'Tulin Berber-Atmaca': 'Tulin Atmaca',
                'Tsong Y. Chen': 'T. Y. Chen',
                'RamA3n LA3pez-CA3zar Delgado': 'Ramon Lopez-Cozar',
                'Koichi Katsurada': 'Kouichi Katsurada',
                'Sebastian MAPeller': 'Sebastian Muller',
                'Y. C. Chen': 'Y. C. Chen',
                'Yann-GaA<<l GuA(c)hA(c)neuc': 'Yann-Gael Gueheneuc',
                'Sergey N. Baranov': 'Sergey Baranov',
                'Bob Horgan': 'Joseph Robert Horgan',
                'Peter In': 'Hoh Peter In',
                'Y.T. Yu': 'Yuen-Tak Yu',
                'Y. T. Yu': 'Yuen-Tak Yu',
                'Y TYu': 'Yuen-Tak Yu',
                'Y.C. Chen': 'Y. C. Chen',
                'Lujie Jiang': 'Jie Jiang',
                'Jun Sun': 'Jun Sun 0001',
                'Tamaii Tetsuo': 'Tetsuo Tamai',
                'D. Zowghi': 'Didar Zowghi',
                'Pornsiri Muenchaisr': 'Pornsiri Muenchaisri',
                'Bob Fuhrer': 'Robert M. Fuhrer',
                'Kostas Kontagiannis': 'Kostas Kontogiannis',
                'Matthias Hauswith' : 'Matthias Hauswirth',
                'Sophia Drossopolou': 'Sophia Drossopoulou',
                'Nyekyne Gaizler Judit': 'Judit Nyeki-Gaizler',
                'Claude R. Baudoi': 'Claude Baudoin',
                'Viktor Gergel': 'Victor P. Gergel',
                'Peri Loucopoulos': 'Pericles Loucopoulos',
                'Pericles Locoupolous': 'Pericles Loucopoulos',
                'Renata Guizardi': 'Renata S. S. Guizzardi',
                'Kenji Taguchi': 'Kenji Taguchi 0001',
                'Ahmad Barfourosh': 'Ahmad Abdollahzadeh Barforoush',
                'Marite Kirkova': 'Marite Kirikova',
                'Havard Jorgensen': 'Havard D. Jorgensen',
                'Mart Roantree': 'Mark Roantree',
                'Regina Laleau': 'Regine Laleau',
                'Klaus D. Schewe': 'Klaus-Dieter Schewe',
                'Steve Liddle': 'Stephen W. Liddle',
                'Vadim Ermoleyev': 'Vadim Ermolayev',
                'Benk Wangler': 'Benkt Wangler',
                'Sutcliffe A.': 'Alistair G. Sutcliffe',
                'Leonard M.': 'Michel Leonard',
                'Rabinovich M.': 'Michael Rabinovich',
                'Kangassalo H.': 'Hannu Kangassalo',
                'Catarci T.': 'Tiziana Catarci',
                'Yu E.': 'Eric S. K. Yu',
                'Wangler B.': 'Benkt Wangler',
                'Rabitti F.': 'Fausto Rabitti',
                'Geppert A.': 'Andreas Geppert',
                'Siau K.': 'Keng Siau',
                'Alberto Leander': 'Alberto H. F. Laender',
                'Ryan U Leong Hou': 'Leong Hou U',
                'Iris Reinhertz': 'Iris Reinhartz-Berger',
                'X.Sean Wang': 'Xiaoyang Sean Wang',
                'Tosiyasu Laurence Kunii': 'Tosiyasu L. Kunii',
                'Srinath Srinivasan': 'Srinath Srinivasa',
                'Ray Liuzzi': 'Raymond A. Liuzzi',
                'Wen Lei Mao': 'Mao Lin Huang',
                'Marcela Fabiana Genero Bocco': 'Marcela Genero',
                'Paulo C. Masiero': 'Paulo Cesar Masiero',
                'Chris Verhoef Vrije': 'Chris Verhoef',
                'Pankoj Jalote': 'Pankaj Jalote',
                'Laurent Balmeli': 'Laurent Balmelli',
                'Urs Hoelzle': 'Urs Holzle',
                'Susan Sim': 'Susan Elliott Sim',
                'Jesus M. Gonzales': 'Jesus M. Gonzalez-Barahona',
                'Yamaoka Katsunori': 'Katsunori Yamaoka',
                'Dave Kung': 'David Chenho Kung',
                'W. Jumpamule': 'Watcharee Jumpamule',
                'Cerulo Luigi': 'Luigi Cerulo',
                'Judit Nyekyne Gaizler': 'Judit Nyeki-Gaizler',
                'Havard D. Jorgensen': 'Havard D. Jorgensen',
                'Miryun Kim': 'Miryung Kim ',
                'James Steel': 'Jim Steel',
                'Carsten Goerg': 'Carsten Gorg',
                'Laurent Safa': '',
                'Peggy Aravantinou': '',
                'Vasilis Chrisikopoulos': '',
                'Jean-Claude Asselborn': '',
                'Juris Roberts Kalnins': '',
                'David Frankel': '',
                'Daryl J. Martin': '',
                'Fernando Alcantara': '',
                'Bhaskar Harita': '',
                'Edward Zou': '',
                'Tingyue Li': '',
                'Wanchai Rivebipoon': '',
                'Qiangxiang Wang': '',
                'Torsten Layda': '',
                'Yossi Raanan': '',
                'Chang-Kang Fan': '',
                'Terry Bailey': ''
            }

WAIT_TIME = 10
LOG_FILENAME = 'logger_program_committee.log'
GOOGLE = 'http://www.google.com'
DBLP = 'dblp.uni-trier.de/pers/'

INPUT = "../data/program_committee_member_extracted.txt"
driver = webdriver.Chrome(executable_path='C:\Program Files (x86)\Google\Chrome\chromedriver.exe')


def calculate_query(cnx, query, arguments):
    cursor = cnx.cursor()
    cursor.execute(query, arguments)
    data = cursor.fetchone()
    cursor.close()
    return data


def check_data_returned(data, member):
    if len(data) == 0:
        logging.warning("insertion - member not found in dblp: " + member)
    elif len(data) > 1:
        logging.warning("insertion - multiple entries for member: " + member + "! ids:" + ','.join([str(d[0]) for d in data]))


def query_metascience(cnx, member):
    researcher_id = None
    data = None

    query_researcher = "SELECT id FROM `" + db_config.DB_NAME + "`.researcher WHERE name = %s;"
    query_researcher_alias = "SELECT researcher_id FROM `" + db_config.DB_NAME + "`.researcher_alias WHERE alias = %s;"

    queries = [query_researcher, query_researcher_alias]
    pos = 0
    while data is None and len(queries)-1 >= pos:
        arguments = [member]
        data = calculate_query(cnx, queries[pos], arguments)
        if data:
            check_data_returned(data, member)
            researcher_id = data[0]
            break
        pos += 1

    return researcher_id


def insert_new_alias(cnx, researcher_id, alias):
    cursor = cnx.cursor()
    insert = "INSERT IGNORE INTO `" + db_config.DB_NAME + "`.researcher_alias VALUES (%s, %s)"
    arguments = [researcher_id, alias]
    cursor.execute(insert, arguments)
    cnx.commit()
    cursor.close()


def query_dblp_via_google(cnx, name):
    data = []
    driver.get(GOOGLE)
    search_box = driver.find_element_by_name("q")
    search_box.send_keys(name + " dblp " + Keys.RETURN)
    #wait
    time.sleep(2)
    google_hits = driver.find_elements_by_xpath("//*[@id='rso']//h3/a")
    for hit in google_hits:
        link = hit.get_attribute("href")
        if DBLP in link and 'pers' in link:
            hit.click()
            try:
                dblp_name = driver.find_element_by_id("headline").find_element_by_tag_name("h1").text.strip()
            except:
                dblp_name = driver.find_element_by_xpath("//h1[contains(@id,'homepages')]").text

            query_dblp_author = "SELECT DISTINCT id FROM `" + db_config.DB_NAME + "`.researcher WHERE name = %s"
            arguments = [dblp_name]
            data = calculate_query(cnx, query_dblp_author, arguments)
            if data:
                insert_new_alias(cnx, data[0], name)
                logging.warning("insertion - the researcher: (" + name + "," + str(data[0]) + ") has been matched to: " + dblp_name)
                break
    return data


def get_researcher_id(cnx, name):
    researcher_id = query_metascience(cnx, name)

    if not researcher_id:
        researcher_id = query_dblp_via_google(cnx, name)

    return researcher_id


def get_conference_id(cnx, venue, year):
    conference_edition_id = None
    cursor = cnx.cursor()
    query = "SELECT ce.id " \
            "FROM `" + db_config.DB_NAME + "`.conference c JOIN `" + db_config.DB_NAME + "`.conference_edition ce " \
            "ON c.id = ce.conference_id " \
            "WHERE acronym = '" + venue + "' AND year = %s"
    arguments = [year]
    cursor.execute(query, arguments)

    row = cursor.fetchone()
    if row:
        conference_edition_id = row[0]

    cursor.close()

    return conference_edition_id


def insert_program_committe_member(cnx, conference_edition_id, researcher_id, is_chair):
    cursor = cnx.cursor()
    query = "INSERT IGNORE INTO `" + db_config.DB_NAME + "`.program_committee VALUES(%s, %s, %s)"
    arguments = [researcher_id, is_chair, conference_edition_id]
    cursor.execute(query, arguments)
    cnx.commit()
    cursor.close()


def is_chair(role):
    flag = 0
    if role == "chair":
        flag = 1
    return flag


def digest_name(name):
    no_parenthesis = re.sub("\(.*\)", "", name)
    no_alpha = re.sub(r"^\W+|\W+$", "", no_parenthesis)
    return no_alpha.strip()


def insert_in_db(cnx, members, role, venue, year):
    conference_edition_id = get_conference_id(cnx, venue, year)

    if conference_edition_id:
        for member in members:
            digested = digest_name(member)
            researcher_id = get_researcher_id(cnx, digested)
            if researcher_id:
                insert_program_committe_member(cnx, conference_edition_id, researcher_id, is_chair(role))
            else:
                print "researcher not found: " + digested


def establish_connection():
    return mysql.connector.connect(**db_config.CONFIG)


def main():
    logging.basicConfig(filename=LOG_FILENAME, level=logging.WARNING)
    with open(LOG_FILENAME, "w") as log_file:
        log_file.write('\n')
    cnx = establish_connection()
    json_file = codecs.open(INPUT, 'r', 'utf-8')
    json_lines = json_file.read()
    for line in json_lines.split('\n'):
        if line.strip() != '':
            if not line.startswith("#") and len(line.strip()) > 0:
                json_entry = json.loads(line)

                role = json_entry.get("role")
                venue = json_entry.get("venue")
                year = json_entry.get("year")
                members = json_entry.get("members")

                insert_in_db(cnx, members, role, venue, year)

    json_file.close()
    cnx.close()


if __name__ == "__main__":
    main()