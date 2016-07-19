__author__ = 'valerio cosentino'

from selenium import webdriver
import json
import re
import time
import codecs
from collections import Counter

INPUT = "../data/topics_target.txt"
OUTPUT = "../data/topics_identified_aut.txt"

#minimum number of topics (listed elements)
MINIMUM_NUMBER_OF_ELEMENTS = 7

MAXIMUM_WORDS_IN_ELEMENT = 10

MAXIMUM_WORDS_IN_TITLE = 3

MEMBER_SEPARATORS = ["NEW_LINE", "COMMA", "LEFT_PAR", "DASH"]

#number of word to add as start_text and end_text
NUMBER_OF_WORDS = 4

#target word
TARGET_WORD = 'topic'
AUXILIARY_TARGET_WORDS = ['contribution']

#forbidden words
FORBIDDEN_WORDS = ['committee', 'important date', 'conference', 'chair', 'proceedings', 'significant',
                   'doctoral', 'symposium', 'paper', 'submission', 'how to ', 'accepted', 'unpublished']

driver = webdriver.Chrome(executable_path='C:\Program Files (x86)\Google\Chrome\chromedriver.exe')


def add_instructions_text_in_html_parser(url, type, venue, year, start_text, end_text, member_separator):
    instruction = '{"parser": "text_in_html","url": \"' + url + '\","target_tag":"body","start_text": \"'+ start_text + \
                  '\","stop_text": \"' + end_text + '\",\"member_separator": \"' + member_separator + '\","member_remove_before": "NULL"' + \
                  ',"member_remove_after": "NULL","exceptions": {}' + \
                  ',"type": \"' + type + '\","venue": \"' + venue + '\","year": \"' + year + '\"}'

    write_to_file(instruction)


def add_instructions_html_parser(url, type, venue, year, prev, next, member_tag):
    if prev:
        start_tag = prev.tag_name
        start_text = take_words(prev.text, NUMBER_OF_WORDS, "last")
    else:
        start_tag = "NULL"
        start_text = "NULL"

    if next:
        end_tag = next.tag_name
        end_text = take_words(next.text, NUMBER_OF_WORDS, "first")
    else:
        end_tag = "NULL"
        end_text = "NULL"
    instruction = '{"parser": "html","url": \"' + url + '\","start_text": \"'+ start_text + \
                  '\","tag_start_text": \"' + start_tag + '\","filter": "NULL","stop_text": \"' + end_text + \
                  '\","tag_stop_text": \"' + end_tag + '\","member_tag": \"' + member_tag + '\","member_remove_before": "NULL"' + \
                  ',"member_remove_after": "NULL","exceptions": {},"containment":"SINGLE"' + \
                  ',"type": \"' + type + '\","venue": \"' + venue + '\","year": \"' + year + '\"}'

    write_to_file(instruction)


def write_to_file(instruction):
    f = codecs.open(OUTPUT, "a+", "utf-8")
    f.write(instruction + '\n')
    f.close()


def take_words(text, n, pos):
    words = "NULL"
    if text != '':
        eol = text.split('\n')
        if len(eol) > 1:
            if pos == "last":
                words = ' '.join(eol[-1].split(' ')[-n:])
            else:
                words = ' '.join(eol[0].split(' ')[:n])
        else:
            if pos == "last":
                words = ' '.join(text.split(' ')[-n:])
            else:
                words = ' '.join(text.split(' ')[:n])

    if words == '':
        words = "NULL"

    return words


def in_text(words, text):
    found = False
    for w in words:
        if w in text:
            found = True
            break

    return found


def infer_type_from_text(start_text, body_content):
    type = "main"
    before_text = body_content.split(start_text)[0]
    lines = [splitted for splitted in before_text.split('\n') if splitted.strip() != '']
    lines.reverse()
    for line in lines:
        if len(line) <= MAXIMUM_WORDS_IN_TITLE or line.isupper():
            type = line
            break

    return type


def infer_type_from_tag(element):
    type = "main"
    precedent_elements = element.find_elements_by_xpath("./preceding::*")
    precedent_elements.reverse()
    precedent_elements.insert(0, element)

    for prec in precedent_elements:
        if prec.text.strip() != '':
            if prec.tag_name in ['h1', 'h2'] and len(prec.text.split('\n')) == 1:
                type = prec.text
                break

    return type


def find_start_element(candidates):
    selected_candidate = None
    for c in candidates:
        sentences = c.text.split('.')
        last_sentence = sentences[-1].lower().strip()

        if TARGET_WORD in last_sentence and last_sentence.endswith(":"):
            selected_candidate = c
            break

    if not selected_candidate:
        for c in candidates:
            sentences = c.text.split('.')
            last_sentence = sentences[-1].lower().strip()
            matched = [a for a in AUXILIARY_TARGET_WORDS if a in last_sentence]
            if len(matched) > 0 and last_sentence.endswith(":"):
                selected_candidate = c
                break

    if not selected_candidate:
        for c in candidates:
            eol = c.text.split('\n')
            if len(eol) == 1:
                content = eol[0].lower().strip()
                if TARGET_WORD in content and len(content.split(' ')) <= MAXIMUM_WORDS_IN_TITLE and c.tag_name not in ['a', 'li']:
                    selected_candidate = c
                    break

    return selected_candidate


def find_list_tag(start_element, end_element):
    found = None
    if start_element:
        next_elements = start_element.find_elements_by_xpath('./following::*')

    if end_element:
        prev_elements = end_element.find_elements_by_xpath('./preceding::*')

    if start_element and end_element:
        occ_tags = Counter([n.tag_name for n in list(set(next_elements).intersection(set(prev_elements))) if n.text != '']).most_common()
    elif start_element:
        occ_tags = Counter([n.tag_name for n in next_elements if n.text != '']).most_common()

    if occ_tags:
        most_common = occ_tags[0]
        if most_common[1] > MINIMUM_NUMBER_OF_ELEMENTS:
            found = most_common[0]
    else:
        print "start_element not found!"

    return found


def find_end_element(start_element):
    next_elements = [n for n in start_element.find_elements_by_xpath('./following::*') if n.text != '']
    selected_candidate = None

    for n in next_elements[MINIMUM_NUMBER_OF_ELEMENTS:]:
        if in_text(FORBIDDEN_WORDS, n.text.lower()):
           selected_candidate = n
           break

    return selected_candidate


def collect_list(url, venue, year):
    found = collect_html_list(url, venue, year)

    if not found:
        found = collect_text_list(url, venue, year)

    return found


def check_following_lines(pos, lines):
    check = True
    next_lines = lines[pos:pos+MINIMUM_NUMBER_OF_ELEMENTS+1]
    for nl in next_lines:
        if in_text(FORBIDDEN_WORDS, nl.lower()):
            check = False
            break

    return check


def find_start_text(content):
    sentences = content.split('.')
    selected_candidate = None
    for sent in sentences:
        sent_lowercase = sent.lower()
        if TARGET_WORD in sent_lowercase and ":" in sent:
            match = re.search(TARGET_WORD + '[^:]*:', sent_lowercase, re.DOTALL)
            if not match:
                continue
            else:
                selected_candidate = sent[match.regs[0][0]:match.regs[0][1]]
                if '\n' in selected_candidate:
                    selected_candidate = selected_candidate.split('\n')[-1]
                break

    if not selected_candidate:
        for sent in sentences:
            sent_lowercase = sent.lower()
            matched = [a for a in AUXILIARY_TARGET_WORDS if a in sent_lowercase]
            if len(matched) > 0 and ":" in sent:
                match = re.search(matched[0] + '(?!:).*:', sent_lowercase, re.DOTALL)
                if not match:
                    continue
                else:
                    selected_candidate = sent[match.regs[0][0]:match.regs[0][1]]
                    if '\n' in selected_candidate:
                        selected_candidate = selected_candidate.split('\n')[-1]
                    break

    if not selected_candidate:
        lines = [splitted for splitted in content.split('\n') if splitted.strip() != '']
        for i in range(len(lines)):
            line_lowercase = lines[i].lower()
            if TARGET_WORD in line_lowercase and len(line_lowercase.split(' ')) <= MAXIMUM_WORDS_IN_TITLE and check_following_lines(i, lines):
                selected_candidate = lines[i]
                break

    return selected_candidate


def find_end_text(start_text, content):
    selected_candidate = None
    after_text = content.split(start_text)[1]

    lines = after_text.split('\n')
    for line in lines:
        digested_line = re.sub("\(.*\)", "", line)
        if in_text(FORBIDDEN_WORDS, line.lower()) or len(digested_line.split(' ')) > MAXIMUM_WORDS_IN_ELEMENT or ':' in digested_line:
           selected_candidate = line.split('.')[0]
           break

    return selected_candidate


#TODO
def identify_common_start(list):
    identified = MEMBER_SEPARATORS[2]
    digested = []
    for e in list:
        if re.match("^\w+", e, re.M):
            digested.append("alphanumeric")
    most_common_start = Counter(list).most_common()

    if most_common_start == "alphanumeric":
        identified = MEMBER_SEPARATORS[0]
    return identified


def find_member_separator(start_text, end_text, content):
    after_text = content.split(start_text)[1]
    selected_text = after_text.split(end_text)[0]

    lines = [splitted for splitted in selected_text.split('\n') if splitted != '']
    most_frequent_separator = identify_common_start([line[0] for line in lines])

    return most_frequent_separator


def collect_text_list(url, venue, year):
    body_content = driver.find_element_by_tag_name("body").text
    found = True
    start_text = find_start_text(body_content)
    end_text = find_end_text(start_text, body_content)
    member_separator = MEMBER_SEPARATORS[0] #find_member_separator(start_text, end_text, body_content)

    type = infer_type_from_text(start_text, body_content)

    if start_text == '' or not start_text:
        start_text = take_words(body_content, NUMBER_OF_WORDS, "first")
        found = False
    else:
        start_text = take_words(start_text, NUMBER_OF_WORDS, "last")

    if end_text == '' or not end_text:
        end_text = take_words(body_content, NUMBER_OF_WORDS, "last")
        found = False
    else:
        end_text = take_words(end_text, NUMBER_OF_WORDS, "first")

    add_instructions_text_in_html_parser(url, type, venue, year, start_text, end_text, member_separator)

    return found


def collect_html_list(url, venue, year):
    candidates = driver.find_elements_by_xpath("//*[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '" + TARGET_WORD + "')]")
    found = True
    start_element = find_start_element(candidates)

    if start_element:
        end_element = find_end_element(start_element)
        list_tag = find_list_tag(start_element, end_element)

        type = infer_type_from_tag(start_element)

        if list_tag:
            add_instructions_html_parser(url, type, venue, year,
                                         start_element,
                                         end_element,
                                         list_tag)
        else:
            found = False

    else:
        found = False

    return found


def detect(url, conf, year):
    driver.get(url)
    time.sleep(5)

    found = collect_list(url, conf, year)
    if not found:
        print "problems with: " + url


def main():
    json_file = codecs.open(INPUT, 'r', 'utf-8')
    json_lines = json_file.read()
    for line in json_lines.split('\r\n'):
        if not line.startswith("#") and len(line.strip()) > 0:
            json_entry = json.loads(line)
            url = json_entry.get('url')
            venue = json_entry.get('venue')
            year = json_entry.get('year')
            detect(url, venue, year)
    driver.close()

if __name__ == "__main__":
    main()
