__author__ = 'atlanmod'

import logging
import mysql.connector
from mysql.connector import errorcode
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import json
import re
import codecs
import time
from unidecode import unidecode
import cross_module_variables as shared
import database_connection_config as dbconnection

#This script gathers (via Selenium) the TOPICS
#for the editions from 2003 of the venue defined in the topic_info.json
#Currently, we track
#MODELS, ASE, ICSE
#we plan to add
#ICSE, FSE, ESEC, ASE, SPLASH, OOPSLA, ECOOP, ISSTA, FASE,
#WCRE, CSMR, ICMT, COMPSAC, APSEC, VISSOFT, ICSM, SOFTVIS,
#SCAM, TOOLS, CAISE, ER, ECMFA, ECMDA-FA, MSR
#The configuration of the json file is explained clearly in the main()


LOG_FILENAME = 'logger_topic_info.log'

JSON_FILE = "./topic_info.json"
JSON_ENTRY_ATTRIBUTES_FOR_HTML = 13
JSON_ENTRY_ATTRIBUTES_FOR_TEXT = 7
JSON_ENTRY_ATTRIBUTES_FOR_TEXT_IN_HTML = 10
driver = webdriver.Chrome(executable_path='C:\Program Files (x86)\Google\Chrome\chromedriver.exe')

VENUE = ''
YEAR = ''
TYPE = ''


def insert_topics_in_db(cnx, topics):
    cursor = cnx.cursor()
    for topic in topics:
        if u"\uFFFD" in topic:
            topic = topic.replace(u"\uFFFD", '?')
            logging.warning(topic + " detected unrecognized character(s)!"
                            + " venue/year: " + VENUE + "/" + YEAR)
        #TODO, member_decoded = re.sub('\s+', ' ', unidecode(member).decode('utf-8').strip().strip(','))
        topic_decoded = unidecode(topic).decode('utf-8').strip().strip(',').lower()

        query = "INSERT IGNORE INTO aux_topics " \
                "SET name = %s, venue = %s, type=%s, year = %s"
        arguments = [topic_decoded, VENUE, TYPE, int(YEAR)]
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
        if tag_start_word != 'NULL' and tag_filter.lower() != 'all_first_columns':
            after_start_word = driver.find_elements_by_xpath(
                "//" + tag_start_word + "/descendant-or-self::*[contains(text(),'" + start_word + "')][1]"
                "/following::*[contains(@id,'" + tag_filter + "') or contains(@class,'" + tag_filter + "')]"
                "/descendant-or-self::*")
        elif tag_start_word != 'NULL' and tag_filter.lower() == 'all_first_columns':
            after_start_word = driver.find_elements_by_xpath(
                "//" + tag_start_word + "/descendant-or-self::*[contains(text(),'" + start_word + "')][1]"
                "/following::tr/td[1]/descendant-or-self::*")
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


def extract_member_name(text):
    #this method can evolve in case some topics contain brackets
    return text


def add_name_to_list(members, name):
    stripped = re.sub(r'^\W+', '', name.strip())
    if len(stripped) > 3:
        members.add(stripped)


def collect_members_from_web_elements(selected_web_elements, member_tag, single_or_all):
    members = set()
    for element in selected_web_elements:
        text = element.text.strip()
        #do not analyse empty text
        if text != '':
            if element.tag_name == member_tag:
                if single_or_all == "single":
                    name = extract_member_name(text)
                    if name.strip() != '':
                        add_name_to_list(members, name)
                else:
                    lines = text.split('\n')
                    for l in lines:
                        name = extract_member_name(l.strip())
                        if name.strip() != '':
                            add_name_to_list(members, name)
    return members


def extract_members_from_html(url, start_word, tag_start_word, tag_filter, stop_word, tag_stop_word,
                    member_tag, single_or_all):
    driver.get(url)
    time.sleep(5)
    selected_web_elements = get_selection_web_elements(start_word, tag_start_word, tag_filter, stop_word, tag_stop_word)
    members = collect_members_from_web_elements(selected_web_elements, member_tag, single_or_all)
    return members


def extract_members_from_text_in_html(url, target_tag, start_text, stop_text, member_separator):
    driver.get(url)
    time.sleep(5)
    members = set()

    element = driver.find_element_by_xpath("//" + target_tag + "[contains(.,'" + start_text + "')]")
    content = element.text
    content = re.sub('^.*' + start_text, '', content, flags=re.DOTALL)
    content = re.sub(stop_text + '.*$', '', content, flags=re.DOTALL)
    member_entries = content.split(member_separator)
    for me in member_entries:
        stripped = re.sub(r'^\W+', '', me.strip())
        if len(stripped) > 3:
            members.add(stripped)

    return members


def extract_topic_info_from_html(cnx, url,
                                   start_word, tag_start_word, tag_filter, stop_word, tag_stop_word,
                                   members_tag, single_or_all):
    members = extract_members_from_html(url, start_word, tag_start_word, tag_filter, stop_word, tag_stop_word,
                              members_tag, single_or_all)
    if len(members) == 0:
        logging.warning("members not found! venue/year/type: " + VENUE + "/" + YEAR + "/" + TYPE)
    insert_topics_in_db(cnx, members)


def extract_topic_info_from_text(cnx, text, entry_separator):
    members = set()
    if entry_separator == '':
        entries = [text]
    else:
        entries = text.split(entry_separator)

    for e in entries:
        stripped = re.sub(r'^\W+', '', e.strip())
        if len(stripped) > 3:
            members.add(stripped)
    insert_topics_in_db(cnx, members)


def extract_topic_info_from_text_in_html(cnx, url, target_tag, start_text, stop_text, member_separator):
    members = extract_members_from_text_in_html(url, target_tag, start_text, stop_text, member_separator)
    insert_topics_in_db(cnx, members)


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
    elif separator.lower() == "dash":
        s = '-'
    elif separator.lower() == "vertical_bar":
        s = '|'
    return s


def check_value(attribute, text, allowed):
    check = text.lower() in allowed and text.lower().strip() != ''

    if check is False:
        logging.warning("wrong attribute for " + attribute + " .Value: " + text + " is not allowed."
                        + " venue/year/type: " + VENUE + "/" + YEAR + "/" + TYPE)

    return check


def check_type(text, attribute):
    check = True
    if attribute == 'year':
        matchObj = re.match("\d\d\d\d", text)
        if matchObj is None:
            check = False
            logging.warning("wrong attribute for " + attribute + " . Value: " + text + " is not a four-digit year."
                            + " venue/year/type: " + VENUE + "/" + YEAR + "/" + TYPE)
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
                      check_value('containment', json_entry.get("containment"), ['single', 'all']))
        elif parser == "text":
            passed = (len(json_entry) == JSON_ENTRY_ATTRIBUTES_FOR_TEXT and
                      check_type(json_entry.get('year'), 'year'))
        elif parser == "text_in_html":
            passed = (len(json_entry) == JSON_ENTRY_ATTRIBUTES_FOR_TEXT_IN_HTML and
                      check_type(json_entry.get('year'), 'year'))
    else:
        logging.warning("parser " + parser + " unknown!"
                        +" venue/year/type: " + VENUE + "/" + YEAR + "/" + TYPE)
    return passed


def main():
    logging.basicConfig(filename=LOG_FILENAME, level=logging.WARNING)
    with open(LOG_FILENAME, "w") as log_file:
        log_file.write('\n')
    cnx = mysql.connector.connect(**dbconnection.CONFIG)
    line_counter = 1
    #Each JSON data per line
    json_file = codecs.open(JSON_FILE, 'r', 'utf-8')
    json_lines = json_file.read()
    for line in json_lines.split('\r\n'):
        if line.strip() != '':
            json_entry = json.loads(line)
            try:
                global VENUE, YEAR, TYPE
                parser = json_entry.get("parser").lower()
                VENUE = json_entry.get("venue") #The acronym of the venue to analyse
                YEAR = json_entry.get("year") #The year of the venue to analyse
                TYPE = json_entry.get("type") #The type of the topics (applications, industrial, etc.)
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
                            #that follow the START_TEXT/TAG_START_TEXT. In addition, you can use the keyword ALL_FIRST_COLUMNS
                            # and the parser will select all the first columns that follow the START_TEXT/TAG_START_TEXT
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
                            extract_topic_info_from_html(cnx, url,
                                                           start_text, tag_start_text, tag_selector, stop_text, tag_stop_text,
                                                           members_tag, single_or_all)
                        #TEXT_IN_HTML. It is used when all the information are contained in only one HTML tag.
                        elif parser == "text_in_html":
                            #URL. The url of the program committee or organizers
                            url = json_entry.get("url")
                            #TARGET_TAG. The tag to analyse
                            target_tag = json_entry.get("target_tag")
                            #START_TEXT. Remove everything that is before the START_TEXT (included)
                            start_text = json_entry.get("start_text")
                            #STOP_TEXT. Remove everything that is after the STOP_TEXT (included)
                            #Note that, if the content of STOP_TEXT is not found, the parser will return all the content
                            #in the TARGET_TAG from the START_TEXT till the end.
                            stop_text = json_entry.get("stop_text")
                            #MEMBER_SEPARATOR.
                            #It defines how members are separated between each other.
                            #Possible separators are COMMA, NEW_LINE, LEFT PAR, DASH, EMPTY_STRING
                            #or user defined separators
                            member_separator = get_separator(json_entry.get("member_separator")).lower()
                            extract_topic_info_from_text_in_html(cnx, url, target_tag, start_text, stop_text, member_separator)
                        #TEXT. It is used when the previous parsers can't do the job.
                        #It expects a text with a list of members
                        #Note that, the the text could contain unrecognized characters
                        #(mostly when copying text from pdf files or old web-sites),
                        #that cause errors in the json decoder
                        elif parser == 'text':
                            #TEXT. It contains a list of members
                            text = json_entry.get("text")
                            #ENTRY_SEPARATOR. It defines how the members (entries) are separated in the text
                            entry_separator = get_separator(json_entry.get("entry_separator")).lower()
                            extract_topic_info_from_text(cnx, text, entry_separator)
            except Exception as e:
                logging.warning("error on json line " + str(line_counter) + "!" + str(e.message))
        line_counter += 1
    json_file.close()
    driver.close()
    cnx.close()


if __name__ == "__main__":
    main()