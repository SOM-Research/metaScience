__author__ = 'atlanmod'

import logging
from selenium import webdriver
import json
import re
import codecs
import time

#This script gathers (via Selenium) the TOPICS
#for the editions from 2003 of the venue defined in the topic_info.json
#Currently, we track
#MODELS, ASE, ICSE, FSE, ASE, FASE, WCRE, CSMR, ICMT, APSEC, ICSM, CAISE, ER, ECMFA
#The configuration of the json file is explained clearly in the main()

LOG_FILENAME = 'logger_topic_info.log'

INPUT = "../data/topics_identified_man.txt"
OUTPUT = "../data/topics_extracted.txt"
JSON_ENTRY_ATTRIBUTES_FOR_HTML = 15
JSON_ENTRY_ATTRIBUTES_FOR_TEXT = 6
JSON_ENTRY_ATTRIBUTES_FOR_TEXT_IN_HTML = 12
driver = webdriver.Chrome(executable_path='C:\Program Files (x86)\Google\Chrome\chromedriver.exe')

VENUE = ''
YEAR = ''
TYPE = ''


def save_topics(topics):
    f = codecs.open(OUTPUT, "a+", "utf-8")
    output = {"topics": topics, "venue": VENUE, "year": YEAR, "type": TYPE}
    f.write(json.dumps(output) + '\n')
    f.close()


def get_selection_web_elements(start_word, tag_start_word, tag_filter, stop_word, tag_stop_word):
    # if the tag filter is defined, it will select the elements after the start word according to the filter tag
    if tag_filter == 'NULL':
        #collect elements after the stop word, relying or not on the start word tag selected.
        if tag_start_word != 'NULL':
            after_start_word = driver.find_elements_by_xpath(
                "//" + tag_start_word + "/descendant-or-self::*[contains(normalize-space(.),'" + start_word + "')][1]/following::*")
        else:
            after_start_word = driver.find_elements_by_xpath("//*/descendant-or-self::*[contains(normalize-space(.),'" + start_word + "')][1]/following::*")
    else:
        if tag_start_word != 'NULL' and not tag_filter.lower().startswith('all_columns'):
            after_start_word = driver.find_elements_by_xpath(
                "//" + tag_start_word + "/descendant-or-self::*[contains(normalize-space(.),'" + start_word + "')][1]"
                "/following::*[contains(@id,'" + tag_filter + "') or contains(@class,'" + tag_filter + "')]"
                "/descendant-or-self::*")
        elif tag_start_word != 'NULL' and tag_filter.lower().startswith('all_columns'):
            column = tag_filter.split('-')[1]
            after_start_word = driver.find_elements_by_xpath(
                "//" + tag_start_word + "/descendant-or-self::*[contains(normalize-space(.),'" + start_word + "')][1]"
                "/following::tr/td[" + column + "]/descendant-or-self::*")
        else:
            after_start_word = driver.find_elements_by_xpath(
                "//*/descendant-or-self::*[contains(normalize-space(.),'" + start_word + "')][1]"
                "/following::*[contains(@id,'" + tag_filter + "') or contains(@class,'" + tag_filter + "')]"
                "/descendant-or-self::*")

    #collect elements before the stop word, relying or not on the stop word tag selected.
    #if the stop word is not defined ("NULL"),
    #the selection will contain all the web elements from the start_word until the end of the page
    if stop_word != "NULL":
        if tag_stop_word != 'NULL':
            before_stop_word = driver.find_elements_by_xpath("//" + tag_stop_word + ""
                    "/descendant-or-self::*[contains(normalize-space(.),'" + stop_word + "')][1]/preceding::*")
        else:
            before_stop_word = driver.find_elements_by_xpath("//*"
                   "/descendant-or-self::*[contains(normalize-space(.),'" + stop_word + "')][1]/preceding::*")
    else:
        before_stop_word = after_start_word

    #intersection = sorted(set(after_start_word) & set(before_stop_word), key = after_start_word.index)
    intersection = set(after_start_word).intersection(set(before_stop_word))
    return intersection


def define_replacement(member_name_separator):
    replacement = member_name_separator + '.*'
    if member_name_separator == '(':
        replacement = '\(.*'

    return replacement


def add_name_to_list(members, name):
    stripped = re.sub(r'^\W+', '', name.strip())
    if len(stripped) > 3:
        if not stripped in members:
            members.append(stripped)


def is_in_exception(text, exceptions):
    found = False
    for key in exceptions.keys():
        if key in text:
            found = True
            break

    return found


def get_exception(text, exceptions):
    found = ''
    for key in exceptions.keys():
        if key in text:
            found = exceptions.get(key)
            break

    return found


def collect_members_from_web_elements(selected_web_elements, member_tag, member_starts_with, member_ends_with,
                                      single_or_all, exceptions):
    members = []
    for element in selected_web_elements:
        text = element.text.strip()
        #do not analyse empty text
        if text != '':
            if element.tag_name == member_tag:
                if single_or_all == "single":
                    if exceptions:
                        if is_in_exception(text, exceptions):
                            exception = get_exception(text, exceptions)
                            if exception != '':
                                add_name_to_list(members, exception)
                        else:
                            name = digest_text(text, member_starts_with, member_ends_with)
                            if name.strip() != '':
                                add_name_to_list(members, name)
                    else:
                        name = digest_text(text, member_starts_with, member_ends_with)
                        if name.strip() != '':
                            add_name_to_list(members, name)
                else:
                    lines = text.split('\n')
                    for l in lines:
                        name = l.strip()
                        if exceptions:
                            if is_in_exception(text, exceptions):
                                exception = get_exception(text, exceptions)
                                if exception != '':
                                    add_name_to_list(members, exception)
                            else:
                                name = digest_text(name, member_starts_with, member_ends_with)
                                if name.strip() != '':
                                    add_name_to_list(members, name)
                        else:
                            name = digest_text(l.strip(), member_starts_with, member_ends_with)
                            if name.strip() != '':
                                add_name_to_list(members, name)

    return members


def extract_members_from_html(url, start_word, tag_start_word, tag_filter, stop_word, tag_stop_word,
                              member_tag, member_starts_with, member_ends_with, single_or_all,
                              exceptions):
    driver.get(url)
    time.sleep(5)
    selected_web_elements = get_selection_web_elements(start_word, tag_start_word, tag_filter, stop_word, tag_stop_word)
    members = collect_members_from_web_elements(selected_web_elements, member_tag,
                                                member_starts_with, member_ends_with, single_or_all, exceptions)
    return members


def digest_text(content, start_text, stop_text):
    START_TEXT = 'START_TEXT'
    STOP_TEXT = 'STOP_TEXT'
    if start_text in ["null", ""]:
        START_TEXT = ''
    if stop_text in ["null", ""]:
        STOP_TEXT = ''

    #dealing with special characters for regular expressions
    if START_TEXT != '':
        content = content.replace(start_text, START_TEXT, 1)
        content = re.sub('^.*' + START_TEXT, '', content, flags=re.DOTALL)
    if STOP_TEXT != '':
        content = content.replace(stop_text, STOP_TEXT, 1)
        content = re.sub(STOP_TEXT + '.*$', '', content, flags=re.DOTALL)

    return content


def extract_members_from_text_in_html(url, target_tag, start_text, stop_text,
                                      member_separator, member_starts_with, member_ends_with,
                                      exceptions):
    driver.get(url)
    time.sleep(5)
    members = []


    element = driver.find_element_by_xpath("//" + target_tag + "[contains(normalize-space(.),'" + start_text + "')]")
    content = element.text

    content = digest_text(content, start_text, stop_text)
    member_entries = content.split(member_separator)[1:]

    for me in member_entries:
        stripped = me.strip()
        if exceptions:
            if is_in_exception(stripped, exceptions):
                exception = get_exception(stripped, exceptions)
                if exception != '':
                    add_name_to_list(members, exception)
            else:
                name = digest_text(stripped, member_starts_with, member_ends_with)
                if name.strip() != '':
                    add_name_to_list(members, name)
        else:
            name = digest_text(stripped, member_starts_with, member_ends_with)
            if name.strip() != '':
                add_name_to_list(members, name)

    return members


def extract_topic_info_from_html(url,
                                 start_word, tag_start_word, tag_filter, stop_word, tag_stop_word,
                                 member_tag, member_starts_with, member_ends_with, single_or_all,
                                 exceptions):
    members = extract_members_from_html(url, start_word, tag_start_word, tag_filter, stop_word, tag_stop_word,
                                        member_tag, member_starts_with, member_ends_with, single_or_all,
                                        exceptions)
    if len(members) == 0:
        logging.warning("extraction - topics not found! venue/year/type: " + VENUE + "/" + YEAR + "/" + TYPE)
    save_topics(members)


def extract_topic_info_from_text(text, entry_separator):
    members = []
    if entry_separator == '':
        entries = [text]
    else:
        entries = text.split(entry_separator)

    for e in entries:
        add_name_to_list(members, e)
    save_topics(members)


def extract_topic_info_from_text_in_html(url, target_tag, start_text, stop_text,
                                         member_separator, member_starts_with, member_ends_with,
                                         exceptions):
    members = extract_members_from_text_in_html(url, target_tag, start_text, stop_text,
                                                member_separator, member_starts_with, member_ends_with,
                                                exceptions)
    save_topics(members)


def convert_keyword(keyword):
    k = keyword
    if keyword.lower() == "new_line":
        k = '\n'
    elif keyword.lower() == "comma":
        k = ','
    elif keyword.lower() == "empty_string":
        k = ''
    elif keyword.lower() == "left_par":
        k = '('
    elif keyword.lower() == "dash":
        k = '-'
    elif keyword.lower() == "vertical_bar":
        k = '|'
    return k


def check_value(attribute, text, allowed):
    check = text.lower() in allowed and text.lower().strip() != ''

    if check is False:
        logging.warning("extraction - wrong attribute for " + attribute + " .Value: " + text + " is not allowed."
                        + " venue/year/type: " + VENUE + "/" + YEAR + "/" + TYPE)

    return check


def check_type(text, attribute):
    check = True
    if attribute == 'year':
        matchObj = re.match("\d\d\d\d", text)
        if matchObj is None:
            check = False
            logging.warning("extraction - wrong attribute for " + attribute + " . Value: " + text + " is not a four-digit year."
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
                      check_value('containment', json_entry.get("containment"), ['single', 'all']))
        elif parser == "text":
            passed = (len(json_entry) == JSON_ENTRY_ATTRIBUTES_FOR_TEXT and
                      check_type(json_entry.get('year'), 'year'))
        elif parser == "text_in_html":
            passed = (len(json_entry) == JSON_ENTRY_ATTRIBUTES_FOR_TEXT_IN_HTML and
                      check_type(json_entry.get('year'), 'year'))
    else:
        logging.warning("extraction - parser " + parser + " unknown!"
                        +" venue/year/type: " + VENUE + "/" + YEAR + "/" + TYPE)
    return passed


def main():
    logging.basicConfig(filename=LOG_FILENAME, level=logging.WARNING)
    with open(LOG_FILENAME, "w") as log_file:
        log_file.write('\n')
    line_counter = 1
    #Each JSON data per line
    json_file = codecs.open(INPUT, 'r', 'utf-8')
    json_lines = json_file.read()
    for line in json_lines.split('\n'):
        if line.strip() != '':
            if not line.startswith("#"):
                json_entry = json.loads(line)
                try:
                    global VENUE, YEAR, TYPE
                    parser = json_entry.get("parser").lower()
                    VENUE = json_entry.get("venue") #The acronym of the venue to analyse
                    YEAR = json_entry.get("year") #The year of the venue to analyse
                    TYPE = json_entry.get("type") #The type of the topics (applications, industrial, etc.)
                    if check_input(json_entry, parser):
                        #HTML parser. It is used to collect text in one or more HTML tags
                        if parser == 'html':
                            #URL. The url of the program committee or organizers
                            url = json_entry.get("url")
                            #START_TEXT. The starting point to parse the page
                            start_text = json_entry.get("start_text")
                            #TAG_START_TEXT. The tag that contains the START TEXT
                            tag_start_text = json_entry.get("tag_start_text")
                            #FILTER. It used to select only tags with a given id or class attribute
                            #that follow the START_TEXT/TAG_START_TEXT. In addition, you can use the keyword ALL_COLUMNS-COL
                            # and the parser will select all the columns in position COL that are included betweent the START_TEXT/TAG_START_TEXT - STOP_TEXT
                            tag_filter = json_entry.get("filter")
                            #STOP_TEXT. The end point to parse the page
                            stop_text = json_entry.get("stop_text")
                            #TAG_STOP_TEXT. The tag that contains the STOP_TEXT
                            tag_stop_text = json_entry.get("tag_stop_text")
                            #MEMBERS_TAG. The tag that contains the members
                            member_tag = json_entry.get("member_tag")
                            #MEMBER_REMOVE_BEFORE. Digest the content of the member's tag by filtering what is before "member_remove_before"
                            #Possible starts are NULL, COMMA, NEW_LINE, LEFT PAR, DASH, EMPTY_STRING or user defined separators
                            member_starts_with = json_entry.get("member_remove_before").lower()
                            #MEMBERS_REMOVE_AFTER. Digest the content of the member's tag by filtering what is after "member_remove_after"
                            #Possible ends are NULL, COMMA, NEW_LINE, LEFT PAR, DASH, EMPTY_STRING or user defined separators
                            member_ends_with = json_entry.get("member_remove_after").lower()
                            #CONTAINMENT. SINGLE or ALL.
                            single_or_all = json_entry.get("containment").lower()
                            #It tells the program whether the MEMBER_TAG contains one member or all
                            #EXCEPTIONS. Some members may have a content that differs from the rest.
                            #They can be defined as exceptions in the following way {member_to_replace : replacement}
                            exceptions = json_entry.get("exceptions")
                            extract_topic_info_from_html(url,
                                                           start_text, tag_start_text, tag_filter, stop_text, tag_stop_text,
                                                           member_tag, member_starts_with, member_ends_with, single_or_all,
                                                           exceptions)
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
                            #MEMBER_REMOVE_BEFORE. Digest the content of the member's tag by filtering what is before "member_remove_before"
                            #Possible starts are NULL, COMMA, NEW_LINE, LEFT PAR, DASH, EMPTY_STRING or user defined separators
                            member_starts_with = json_entry.get("member_remove_before").lower()
                            #MEMBER_REMOVE_AFTER. Digest the content of the member's tag by filtering what is after "member_remove_after"
                            #Possible ends are NULL, COMMA, NEW_LINE, LEFT PAR, DASH, EMPTY_STRING or user defined separators
                            member_ends_with = json_entry.get("member_remove_after").lower()
                            #MEMBER_SEPARATOR.
                            #It defines how members are separated between each other.
                            #Possible separators are COMMA, NEW_LINE, LEFT PAR, DASH, EMPTY_STRING
                            #or user defined separators
                            member_separator = convert_keyword(json_entry.get("member_separator")).lower()
                            #EXCEPTIONS. Some members may have a content that differs from the rest.
                            #They can be defined as exceptions in the following way:
                            #{member_to_replace-1 : replacement-1, member_to_replace-2 : replacement-2, ...}
                            exceptions = json_entry.get("exceptions")
                            extract_topic_info_from_text_in_html(url, target_tag, start_text, stop_text,
                                                                 member_separator, member_starts_with, member_ends_with,
                                                                 exceptions)
                        #TEXT. It is used when the previous parsers can't do the job.
                        #It expects a text with a list of members
                        #Note that, the the text could contain unrecognized characters
                        #(mostly when copying text from pdf files or old web-sites),
                        #that cause errors in the json decoder
                        elif parser == 'text':
                            #TEXT. It contains a list of members
                            text = json_entry.get("text")
                            #ENTRY_SEPARATOR. It defines how the members (entries) are separated in the text
                            entry_separator = convert_keyword(json_entry.get("entry_separator")).lower()
                            extract_topic_info_from_text(text, entry_separator)
                except Exception as e:
                    logging.warning("extraction - error on json line " + str(line_counter) + "!" + str(e.message))
        line_counter += 1
    json_file.close()
    driver.close()


if __name__ == "__main__":
    main()