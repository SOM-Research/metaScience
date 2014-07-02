__author__ = 'atlanmod'

import logging
import mysql.connector
from mysql.connector import errorcode
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import json
import re
import csv
import time

LOG_FILENAME = 'logger_program_committee.log'
CONFIG = {
    'user': 'root',
    'password': 'coitointerrotto',
    'host': 'atlanmodexp.info.emn.fr',
    'port': '13506',
    'database': 'dblp',
    'raise_on_warnings': False,
    'buffered': True
}
# CONFIG = {
#     'user': 'root',
#     'password': 'root',
#     'host': '127.0.0.1',
#     'port': '3306',
#     'database': 'test',
#     'raise_on_warnings': False,
#     'buffered': True
# }

JSON_FILE = "./program_committee_info.json"
JSON_ENTRY_ATTRIBUTES_FOR_HTML = 16
JSON_ENTRY_ATTRIBUTES_FOR_TEXT = 7
JSON_ENTRY_ATTRIBUTES_FOR_TEXT_IN_HTML = 13
driver = webdriver.Chrome(executable_path='C:\Program Files (x86)\Google\Chrome\chromedriver.exe')
GOOGLE = "http://www.google.com"
DBLP = "www.informatik.uni-trier.de"

CONFERENCE = ''
YEAR = ''
ROLE = ''


def calculate_query(cnx, query, arguments):
    cursor = cnx.cursor()
    cursor.execute(query, arguments)
    data = cursor.fetchall()
    cursor.close()
    return data


def recover_id_by_querying_google(cnx, member):
    data = []
    google_driver = webdriver.Chrome(executable_path='C:\Program Files (x86)\Google\Chrome\chromedriver.exe')
    google_driver.get(GOOGLE)
    search_box = google_driver.find_element_by_name("q")
    search_box.send_keys(member + " dblp " + Keys.RETURN)
    #wait
    time.sleep(2)
    google_hits = google_driver.find_elements_by_xpath("//*[@id='rso']//h3/a")
    for hit in google_hits:
        link = hit.get_attribute("href")
        if DBLP in link:
            hit.click()
            dblp_name = google_driver.find_element_by_id("headline").find_element_by_tag_name("h1").text.strip()
            query_dblp_author = "SELECT DISTINCT author_id FROM dblp_authorid_ref_new WHERE author = %s"
            arguments = [dblp_name]
            data = calculate_query(cnx, query_dblp_author, arguments)
            break
    google_driver.close()
    return data


def get_dblp_id(data, member):
    id = None
    if len(data) == 0:
        logging.warning("member not found in dblp: " + member)
    if len(data) == 1:
        id = data[0][0]
    else:
        id = -1
        auths = ''
        for d in data:
            auths = auths + ',' + d
        logging.warning("multiple entries for member: " + auths)

    return id


def find_dblp_id(cnx, member):
    id = 0
    data = []
    query_scholar_authors = "SELECT dblp_author_id FROM aux_scholar_authors WHERE name = %s"
    query_program_committee = "SELECT DISTINCT dblp_author_id FROM aux_program_committee WHERE name = %s"
    query_dblp_author = "SELECT DISTINCT author_id FROM dblp_authorid_ref_new WHERE author = %s"
    query_dblp_aliases = "SELECT DISTINCT author_id FROM dblp.dblp_aliases_new WHERE authorAlias = %s;"
    queries = [query_scholar_authors, query_program_committee, query_dblp_author, query_dblp_aliases]
    pos = 0
    while len(data) == 0 and len(queries)-1 >= pos:
        arguments = [member]
        data = calculate_query(cnx, queries[pos], arguments)
        pos += 1

    #if the member is not found, we try to get his id by querying dblp with google
    if len(data) == 0:
        data = recover_id_by_querying_google(cnx, member)

    id = get_dblp_id(data, member)
    return id


def invert_name(name):
    names = name.split(',')
    return (names[1].strip() + ' ' + names[0].strip())


def insert_members_in_db(cnx, members):
    cursor = cnx.cursor()
    for member in members:
        if member != '':
            member_id = find_dblp_id(cnx, member)
            query = "INSERT IGNORE INTO aux_program_committee " \
                    "SET name = %s, conference = %s, year = %s, role = %s, dblp_author_id = %s"
            arguments = [member, CONFERENCE, int(YEAR), ROLE, member_id]
            cursor.execute(query, arguments)
            cnx.commit()
    cursor.close()


def get_selection_web_elements(start_word, tag_start_word, tag_filter, stop_word, tag_stop_word):
    # if the tag filter is defined, it will select the elements after the start word according to the filter tag
    if tag_filter == 'NULL':
        #collect elements after the stop word, relying or not on the start word tag selected.
        if tag_start_word != 'NULL':
            after_start_word = driver.find_elements_by_xpath(
                "//" + tag_start_word + "/descendant-or-self::*[contains(text(),'" + start_word + "')][1]/following::*")
        else:
            after_start_word = driver.find_elements_by_xpath("//*/descendant-or-self::*[contains(text(),'" + start_word + "')][1]/following::*")
    else:
        if tag_start_word != 'NULL':
            after_start_word = driver.find_elements_by_xpath(
                "//" + tag_start_word + "/descendant-or-self::*[contains(text(),'" + start_word + "')][1]"
                "/following::*[contains(@id,'" + tag_filter + "') or contains(@class,'" + tag_filter + "')]"
                "/descendant-or-self::*")
        else:
            after_start_word = driver.find_elements_by_xpath(
                "//*/descendant-or-self::*[contains(text(),'" + start_word + "')][1]"
                "/following::*[contains(@id,'" + tag_filter + "') or contains(@class,'" + tag_filter + "')]"
                "/descendant-or-self::*")

    #collect elements before the stop word, relying or not on the stop word tag selected.
    #if the stop word is not defined ("NULL"),
    #the selection will contain all the web elements from the start_word until the end of the page
    if stop_word != "NULL":
        if tag_stop_word != 'NULL':
            before_stop_word = driver.find_elements_by_xpath("//" + tag_stop_word + ""
                    "/descendant-or-self::*[contains(text(),'" + stop_word + "')][1]/preceding::*")
        else:
            before_stop_word = driver.find_elements_by_xpath("//*"
                   "/descendant-or-self::*[contains(text(),'" + stop_word + "')][1]/preceding::*")
    else:
        before_stop_word = after_start_word

    selection = set(after_start_word).intersection(set(before_stop_word))
    return selection


def define_replacement(member_name_separator):
    replacement = member_name_separator + '.*'
    if member_name_separator == '(':
        replacement = '\(.*'

    return replacement


def extract_member_name(mixed, member_name_separator, inverted_name, text):
    name = ''
    #the member_name_separator should be contained in text,
    #this should avoid recognizing as member something that is not
    if member_name_separator == '':
        name = text
    elif member_name_separator in text:
        replacement = define_replacement(member_name_separator)

        if mixed == 'yes':
            if ROLE == 'chair':
                if 'chair' in text.lower():
                    name = re.sub(replacement, '', text)
            else:
                if 'chair' not in text.lower():
                    name = re.sub(replacement, '', text)
        else:
            name = re.sub(replacement, '', text)

    if inverted_name == 'yes':
        if name != '':
            name = invert_name(name)
    return name


def add_name_to_list(members, name):
    if name != '':
        if u"\uFFFD" in name:
            logging.warning(name + " has been discarded due to unrecognized character!"
                            + " conf/year/role: " + CONFERENCE + "/" + YEAR + "/" + ROLE)
        else:
            members.add(name)


def collect_members_from_web_elements(selected_web_elements, member_tag,
                                      single_or_all, member_name_separator, inverted_name, mixed):
    members = set()
    for element in selected_web_elements:
        text = element.text.strip()
        #do not analyse empty text
        if text != '':
            if element.tag_name == member_tag:
                if single_or_all == "single":
                    name = extract_member_name(mixed, member_name_separator, inverted_name, text)
                    add_name_to_list(members, name)
                else:
                    lines = text.split('\n')
                    for l in lines:
                        name = extract_member_name(mixed, member_name_separator, inverted_name, l)
                        add_name_to_list(members, name)
    return members


def extract_members_from_html(url, start_word, tag_start_word, tag_filter, stop_word, tag_stop_word,
                    member_tag, single_or_all, member_name_separator, inverted_name, mixed):
    driver.get(url)

    selected_web_elements = get_selection_web_elements(start_word, tag_start_word, tag_filter, stop_word, tag_stop_word)
    members = collect_members_from_web_elements(selected_web_elements, member_tag,
                                                single_or_all, member_name_separator, inverted_name, mixed)
    return members


def extract_members_from_text_in_html(url, target_tag, start_text, stop_text, mixed, inverted_name,
                                      member_separator, member_name_separator):
    driver.get(url)
    members = set()

    element = driver.find_element_by_xpath("//" + target_tag + "[contains(.,'" + start_text + "')]")
    content = element.text
    content = re.sub('^.*' + start_text, '', content, flags=re.DOTALL)
    content = re.sub(stop_text + '.*$', '', content, flags=re.DOTALL)
    member_entries = content.split(member_separator)
    for me in member_entries:
        if me != '':
            name = extract_member_name(mixed, member_name_separator, inverted_name, me)
            members.add(name.strip())

        # name = re.sub(member_name_separator + '.*', '', me)
        # if name != '':
        #     members.add(name.strip())

    return members


def extract_program_committee_info_from_html(cnx, url,
                                   start_word, tag_start_word, tag_filter, stop_word, tag_stop_word,
                                   members_tag, single_or_all, inverted_name,
                                   member_name_separator, mixed):
    members = extract_members_from_html(url, start_word, tag_start_word, tag_filter, stop_word, tag_stop_word,
                              members_tag, single_or_all, member_name_separator, inverted_name, mixed)
    if len(members) == 0:
        logging.warning("members not found! conf/year/role: " + CONFERENCE + "/" + YEAR + "/" + ROLE)
    ##debug
    # for m in members:
    #     print m
    insert_members_in_db(cnx, members)


def extract_program_committee_info_from_text(cnx, text, entry_separator):
    members = set()
    if entry_separator == '':
        entries = [text]
    else:
        entries = text.split(entry_separator)

    for e in entries:
        if e != '':
            members.add(e.strip())
    ##debug
    # for m in members:
    #     print m
    insert_members_in_db(cnx, members)


def extract_program_committee_info_from_text_in_html(cnx, url, target_tag, start_text, stop_text, mixed, inverted_name,
                                                     member_separator, member_name_separator):
    members = extract_members_from_text_in_html(url, target_tag, start_text, stop_text, mixed, inverted_name,
                                                member_separator, member_name_separator)
    ##debug
    # for m in members:
    #     print m
    insert_members_in_db(cnx, members)


def get_separator(separator):
    s = separator
    if separator.lower() == "new_line":
        s = '\n'
    elif separator.lower() == "comma":
        s = ','
    elif separator.lower() == "empty_string":
        s = ''
    elif separator.lower() == "left_par":
        s = '('
    return s


def check_value(attribute, text, allowed):
    check = text.lower() in allowed and text.lower().strip() != ''

    if check is False:
        logging.warning("wrong attribute for " + attribute + " .Value: " + text + " is not allowed."
                        + " conf/year/role: " + CONFERENCE + "/" + YEAR + "/" + ROLE)

    return check


def check_type(text, attribute):
    check = True
    if attribute == 'year':
        matchObj = re.match("\d\d\d\d", text)
        if matchObj is None:
            check = False
            logging.warning("wrong attribute for " + attribute + " . Value: " + text + " is not a four-digit year."
                            + " conf/year/role: " + CONFERENCE + "/" + YEAR + "/" + ROLE)
    else:
        check = False

    return check


def check_input(json_entry, parser):
    passed = False

    if check_value('parser', parser, ['html', 'text', 'text_in_html']):
        if parser == "html":
            passed = (len(json_entry) == JSON_ENTRY_ATTRIBUTES_FOR_HTML and
                      check_type(json_entry.get('year'), 'year') and
                      check_value('action', json_entry.get("action"), ['proc', 'skip']) and
                      check_value('containment', json_entry.get("containment"), ['single', 'all']) and
                      check_value('inverted_member_name', json_entry.get("inverted_member_name"), ['yes', 'no']) and
                      check_value('extract_role', json_entry.get("extract_role"), ['member', 'chair']) and
                      check_value('mixed_roles',json_entry.get("mixed_roles"), ['yes', 'no']))
        elif parser == "text":
            passed = (len(json_entry) == JSON_ENTRY_ATTRIBUTES_FOR_TEXT and
                      check_type(json_entry.get('year'), 'year') and
                      check_value('extract_role', json_entry.get("extract_role"), ['member', 'chair']))
        elif parser == "text_in_html":
            passed = (len(json_entry) == JSON_ENTRY_ATTRIBUTES_FOR_TEXT_IN_HTML and
                      check_type(json_entry.get('year'), 'year') and
                      check_value('mixed_roles',json_entry.get("mixed_roles"), ['yes', 'no']) and
                      check_value('inverted_member_name', json_entry.get("inverted_member_name"), ['yes', 'no']) and
                      check_value('extract_role', json_entry.get("extract_role"), ['member', 'chair']))
    else:
        logging.warning("parser " + parser + " unknown!"
                        +" conf/year/role: " + CONFERENCE + "/" + YEAR + "/" + ROLE)
    return passed


def main():
    logging.basicConfig(filename=LOG_FILENAME, level=logging.WARNING)
    with open(LOG_FILENAME, "w") as log_file:
        log_file.write('\n')
    cnx = mysql.connector.connect(**CONFIG)
    line_counter = 1
    #Each JSON data per line
    json_file = open(JSON_FILE)
    json_lines = json_file.read()
    for line in json_lines.split('\n'):
        if line != '':
            line_unicoded = unicode(line, errors='ignore')
            json_entry = json.loads(line_unicoded)
            try:
                global ROLE, CONFERENCE, YEAR
                parser = json_entry.get("parser").lower()
                ROLE = json_entry.get("extract_role").lower() #The role to extract: MEMBER or CHAIR
                CONFERENCE = json_entry.get("conference") #The acronym of the conference to analyse
                YEAR = json_entry.get("year") #The year of the conference to analyse
                if check_input(json_entry, parser):
                    action = json_entry.get("action").lower()
                    #action can be "PROC" or "SKIP". The former tells the program to process a JSON line,
                    #while the latter is used to skip that line
                    if action == "proc":
                        #HTML parser. It is used to collect text in one or more HTML tags
                        if parser == 'html':
                            #URL. The url of the program committee or organizers
                            url = json_entry.get("url")
                            #START_TEXT. The starting point to parse the page
                            start_text = json_entry.get("start_text")
                            #TAG_START_TEXT. The tag that contains the START TEXT
                            tag_start_text = json_entry.get("tag_start_text")
                            #TAG_SELECTOR. It used to select only tags with a given id or class attributes
                            #that follow the TAG_START_TEXT.
                            tag_selector = json_entry.get("id_or_class_selector")
                            #STOP_TEXT. The end point to parse the page
                            stop_text = json_entry.get("stop_text")
                            #TAG_STOP_TEXT. The tag that contains the STOP_TEXT
                            tag_stop_text = json_entry.get("tag_stop_text")
                            #MEMBERS_TAG. The tag that contains the members
                            members_tag = json_entry.get("members_tag")
                            #CONTAINMENT. SINGLE or ALL.
                            #It tells the program whether the MEMBERS_TAG contains one member or all
                            single_or_all = json_entry.get("containment").lower()
                            #MIXED_ROLES. YES or NO.
                            #It tells the program whether MEMBERS_TAG are only of one type (MEMBER or CHAIR) or are mixed
                            mixed = json_entry.get("mixed_roles").lower()
                            #INVERTED_MEMBER_NAME. YES or NO
                            #It tells the program whether the names are inverted (ex.: Gates, Bill) or not (Bill Gates)
                            inverted_name = json_entry.get("inverted_member_name").lower()
                            #MEMBER_NAME_SEPARATOR. COMMA, NEW_LINE, LEFT PAR, EMPTY_STRING or user defined separators
                            #It tells the program how for each member, its name is separated from the remaining information
                            #ex.: Bill Gates, Microsoft  --> COMMA
                            #     Bill Gates (Microsoft) --> LEFT_PAR
                            #     Bill Gates - Microsoft --> -
                            member_name_separator = get_separator(json_entry.get("member_name_separator")).lower()

                            extract_program_committee_info_from_html(cnx, url,
                                                           start_text, tag_start_text, tag_selector, stop_text, tag_stop_text,
                                                           members_tag, single_or_all, inverted_name,
                                                           member_name_separator, mixed)
                        #TEXT_IN_HTML. It is used when all the information are contained in only one HTML tag.
                        elif parser == "text_in_html":
                            #URL. The url of the program committee or organizers
                            url = json_entry.get("url")
                            #TARGET_TAG. The tag to analyse
                            target_tag = json_entry.get("target_tag")
                            #START_TEXT. Remove everything that is before the START_TEXT (included)
                            start_text = json_entry.get("start_text")
                            #STOP_TEXT. Remove everything that is after the STOP_TEXT (included)
                            stop_text = json_entry.get("stop_text")
                            #MEMBER_SEPARATOR.
                            #It defines how members are separated between each other (generally is NEW_LINE)
                            member_separator = get_separator(json_entry.get("member_separator")).lower()
                            #MIXED_ROLES. YES or NO.
                            #It tells the program whether MEMBERS_TAG are only of one type (MEMBER or CHAIR) or are mixed
                            mixed = json_entry.get("mixed_roles").lower()
                            #INVERTED_MEMBER_NAME. YES or NO
                            #It tells the program whether the names are inverted (ex.: Gates, Bill) or not (Bill Gates)
                            inverted_name = json_entry.get("inverted_member_name").lower()
                            #MEMBER_NAME_SEPARATOR. COMMA, NEW_LINE, LEFT PAR, EMPTY_STRING or user defined separators
                            #It tells the program how for each member, its name is separated from the remaining information
                            member_name_separator = get_separator(json_entry.get("member_name_separator")).lower()
                            extract_program_committee_info_from_text_in_html(cnx, url, target_tag, start_text, stop_text,
                                                                             mixed, inverted_name,
                                                                             member_separator, member_name_separator)
                        #TEXT. It is used when the preceding parsers can't do the job.
                        #It expects a text with a list of members
                        elif parser == 'text':
                            #TEXT. It contains a list of members
                            text = json_entry.get("text")
                            #ENTRY_SEPARATOR. It defines how the members (entries) are separated in the text
                            entry_separator = get_separator(json_entry.get("entry_separator")).lower()
                            extract_program_committee_info_from_text(cnx, text, entry_separator)
            except:
                logging.warning("json line " + str(line_counter) + " is not valid!")
        line_counter += 1
    json_file.close()
    driver.close()
    cnx.close()


if __name__ == "__main__":
    main()