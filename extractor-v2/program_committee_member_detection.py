__author__ = 'valerio cosentino'

from selenium import webdriver
import json
import re
import time
import codecs
from collections import Counter
import string
import unicodedata

INPUT = "../data/program_committee_member_target.txt"
OUTPUT = "../data/program_committee_member_identified_aut.txt"

#minimum number of members (listed elements)
MINIMUM_NUMBER_OF_ELEMENTS = 10

MINIMUM_WORDS_IN_ELEMENT = 3
MAXIMUM_WORDS_IN_ELEMENT = 10

MAXIMUM_WORDS_IN_TITLE = 4

#number of word to add as start_text and end_text
NUMBER_OF_WORDS = 4
NEW_LINE = "NEW_LINE"

#target word
TARGET_WORD = 'program committee'
AUXILIARY_TARGET_WORDS = ['programme committee', 'program commiittee', 'PC members', 'scientific committee']

#forbidden words
FORBIDDEN_WORDS_IN_START = ['chair']
FORBIDDEN_WORDS_IN_ELEMENTS = ['review', 'tutorial committee', 'conference committee', 'organizing committee', 'organising committee',
                   'steering']

driver = webdriver.Chrome(executable_path='C:\Program Files (x86)\Google\Chrome\chromedriver.exe')


def add_instructions_text_in_html_parser(url, type, venue, year, start_text, end_text, member_separator, member_remove_before, member_remove_after, role, mixed_roles):
    instruction = '{"parser": "text_in_html","url": \"' + url + '\","target_tag":"body","start_text": \"'+ start_text + \
                  '\","stop_text": \"' + end_text + '\",\"member_separator": \"' + member_separator + '\","member_remove_before": "' + member_remove_before + '"' + \
                  ',"member_remove_after": "' + member_remove_after + '","exceptions": {}, "mixed_roles": "' + mixed_roles + '", "inverted_member_name": "NO"' + \
                  ',"type": \"' + type + '\","venue": \"' + venue + '\","year": \"' + year + '\", \"role": \"' + role + '\"}'

    write_to_file(instruction)


def add_instructions_html_parser(url, type, venue, year, role, prev, next, member_remove_before, member_remove_after, member_tag, mixed_roles, containment):
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
                  '\","tag_stop_text": \"' + end_tag + '\","member_tag": \"' + member_tag + '\","member_remove_before": "' + member_remove_before + '"' + \
                  ',"member_remove_after": "' + member_remove_after + '","exceptions": {},"containment":"' + containment + '", "mixed_roles": "' + mixed_roles + '", "inverted_member_name": "NO"' + \
                  ',"type": \"' + type + '\","venue": \"' + venue + '\","year": \"' + year + '\","role": \"' + role + '\"}'

    write_to_file(instruction)


def write_to_file(instruction):
    a = 5
    # f = codecs.open(OUTPUT, "a+", "utf-8")
    # f.write(instruction + '\n')
    # f.close()


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


def infer_type_from_text(start_text, body_content, default_type):
    type = default_type
    before_text = body_content.split(start_text)[0]
    lines = [splitted for splitted in before_text.split('\n') if splitted.strip() != '']
    lines.reverse()
    for line in lines:
        if len(line) <= MAXIMUM_WORDS_IN_TITLE or line.isupper():
            type = line
            break

    return type


def infer_type_from_tag(element, default_type):
    type = default_type
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
    for c in [c for c in candidates if not in_text(FORBIDDEN_WORDS_IN_START, c.text.lower())]:
        if len(c.text.split(' ')) <= MAXIMUM_WORDS_IN_TITLE and c.tag_name in ['h1', 'h2', 'h3']:
            selected_candidate = c
            break

    if not selected_candidate:
        selected_candidate = candidates[-1]

    return selected_candidate


def find_no_empty_next_element(start_element):
    found = None
    if start_element:
        next_elements = start_element.find_elements_by_xpath('./following::*')
        next_elements_no_empty = [n for n in next_elements if n.text != '' and not in_text(FORBIDDEN_WORDS_IN_ELEMENTS, n.text.lower())]

        if next_elements_no_empty:
            found = next_elements_no_empty[0]

    return found


def find_mixed_roles_from_text(text):
    lines = text.split('\n')
    hits = [sel for sel in lines if in_text(FORBIDDEN_WORDS_IN_START, sel.lower())]
    if len(hits) > 0:
        found = "YES"
    else:
        found = "NO"

    return found


def find_mixed_roles(start_element, end_element):
    if start_element:
        next_elements = start_element.find_elements_by_xpath('./following::*')

    if end_element:
        prev_elements = end_element.find_elements_by_xpath('./preceding::*')

    if start_element and end_element:
        selected_elements = list(set(next_elements).intersection(set(prev_elements)))
    else:
        selected_elements = next_elements

    hits = [sel for sel in selected_elements if in_text(FORBIDDEN_WORDS_IN_START, sel.text)]

    if len(hits) > 0:
        found = "YES"
    else:
        found = "NO"

    return found



def find_list_tag(start_element, end_element):
    found = None
    if start_element:
        next_elements = start_element.find_elements_by_xpath('./following::*')

    if end_element:
        prev_elements = end_element.find_elements_by_xpath('./preceding::*')

    if start_element and end_element:
        occ_tags = Counter([n.tag_name for n in list(set(next_elements).intersection(set(prev_elements))) if n.text != '' and n.tag_name not in ['a', 'span', 'font']]).most_common()
    elif start_element:
        occ_tags = Counter([n.tag_name for n in next_elements if n.text != '' and n.tag_name not in ['a', 'span', 'font']]).most_common()

    if occ_tags:
        most_common = occ_tags[0]
        if most_common[1] > MINIMUM_NUMBER_OF_ELEMENTS:
            found = most_common[0]
    else:
        print "start_element not found!"

    return found


def find_end_element(start_element):
    next_elements = [n for n in start_element.find_elements_by_xpath('./following::*') if n.text != '' and n.tag_name not in ['a', 'span', 'font']]
    selected_candidate = None

    for n in next_elements[MINIMUM_NUMBER_OF_ELEMENTS:]:
        processed_line = strip_2character_word(n.text.lower())
        if n.text.strip() != '':
            if len(processed_line) < MINIMUM_WORDS_IN_ELEMENT or len(processed_line) > MAXIMUM_WORDS_IN_ELEMENT or in_text(FORBIDDEN_WORDS_IN_ELEMENTS, n.text.lower()):
                selected_candidate = n
                break

    return selected_candidate


def collect_list(url, venue, year, role, type):
    found = collect_html_list(url, venue, year, role, type)

    if not found:
        found = collect_text_list(url, venue, year, role, type)

    return found


def check_following_lines(pos, lines):
    check = True
    next_lines = lines[pos:pos+MINIMUM_NUMBER_OF_ELEMENTS+1]
    for nl in next_lines:
        if in_text(FORBIDDEN_WORDS_IN_ELEMENTS, nl.lower()):
            check = False
            break

    return check


def find_start_text(content):
    lines = content.split('\n')
    selected_candidate = None
    candidates = []
    for i in range(len(lines)):
        line_lowercase = lines[i].lower()
        if TARGET_WORD in line_lowercase and len(lines[i].split(' ')) <= MAXIMUM_WORDS_IN_TITLE:
            candidates.append(i)

    if not selected_candidate:
        for i in range(len(lines)):
            line_lowercase = lines[i].lower()
            for aux in AUXILIARY_TARGET_WORDS:
                if aux in line_lowercase and len(lines[i].split(' ')) <= MAXIMUM_WORDS_IN_TITLE:
                    candidates.append(i)

    if candidates:
        selected_candidate = lines[candidates[-1]].strip()

    return selected_candidate


def strip_2character_word(line):
    words = line.split(' ')
    return [w for w in words if len(w) > 2]


def find_end_text(start_text, content):
    selected_candidate = None
    after_text = content.split(start_text)[1]

    lines = after_text.split('\n')[MINIMUM_NUMBER_OF_ELEMENTS:]
    for line in lines:
        digested_line = re.sub("\(.*\)", "", line)
        if line.strip() != '':
            if in_text(FORBIDDEN_WORDS_IN_ELEMENTS, line.lower()) or len(strip_2character_word(digested_line)) < MINIMUM_WORDS_IN_ELEMENT or len(strip_2character_word(digested_line)) > MAXIMUM_WORDS_IN_ELEMENT:
               selected_candidate = line.strip()
               break

    return selected_candidate


def find_member_separator_from_html(start_element, end_element, tag):
    if start_element:
        next_elements = start_element.find_elements_by_xpath('./following::*')

    if end_element:
        prev_elements = end_element.find_elements_by_xpath('./preceding::*')

    if start_element and end_element:
        selected_elements = list(set(next_elements).intersection(set(prev_elements)))
    else:
        selected_elements = next_elements

    members = [sel.text for sel in selected_elements if sel.tag_name == tag]
    member_remove_before = identify_common_start(members)
    member_remove_after = identify_common_end(members)

    return [member_remove_before, member_remove_after]


def identify_common_end(list):
    ends = []
    for e in list:
        e = remove_accents(e)
        if len(e) > 1:
            for c in e[3:]:
                if not c.isalpha() and not c.isspace() and c != '.':
                    ends.append(c)
                    break
    try:
        most_common_end = Counter(ends).most_common()[0]
        if most_common_end[1] >= MINIMUM_NUMBER_OF_ELEMENTS:
            end = most_common_end[0]
        else:
            end = "NULL"
    except:
        end = "NULL"

    return end


def remove_accents(data):
    return ''.join(x for x in unicodedata.normalize('NFKD', data))


def identify_common_start(list):
    digested = []
    for e in list:
        if len(e) > 1:
            e = remove_accents(e)
            if re.match("^\w+", e, re.M):
                digested.append("alphanumeric")
            elif re.match("^\W+", e, re.M):
                matchObj = re.match("^\W+", e, re.M)
                try:
                    digested.append(matchObj.group(1))
                except:
                    continue
    most_common_start = Counter(digested).most_common()[0]

    if most_common_start[0] == "alphanumeric":
        identified = "NULL"
    else:
        identified = most_common_start[0]
    return identified


def find_member_separator_from_text(selected_text):

    lines = [splitted for splitted in selected_text.split('\n') if splitted != '']
    member_remove_before = identify_common_start(lines)
    member_remove_after = identify_common_end(lines)

    return [member_remove_before, member_remove_after]


def collect_text_list(url, venue, year, role, type):
    body_content = driver.find_element_by_tag_name("body").text
    found = True
    start_text = find_start_text(body_content)
    end_text = find_end_text(start_text, body_content)

    after_text = body_content.split(start_text)[1]

    if end_text:
        selected_text = after_text.split(end_text)[0]
    else:
        selected_text = after_text

    member_separator = find_member_separator_from_text(selected_text)
    mixed_roles = find_mixed_roles_from_text(selected_text)
    inferred_type = infer_type_from_text(start_text, body_content, type)

    if start_text == '' or not start_text:
        start_text = take_words(body_content, NUMBER_OF_WORDS, "first")
        found = False
    else:
        start_text = take_words(start_text, NUMBER_OF_WORDS, "last")

    if end_text == '' or not end_text:
        end_text = "NULL"
    else:
        end_text = take_words(end_text, NUMBER_OF_WORDS, "first")

    add_instructions_text_in_html_parser(url, inferred_type, venue, year, start_text, end_text, NEW_LINE,
                                         member_separator[0], member_separator[1], role, mixed_roles)

    return found


def find_end_element_for_text_in_html_element(element):
    found = None
    if element:
        next_elements = element.find_elements_by_xpath('./following::*')
        next_elements_no_empty = [n for n in next_elements if n.text != '' and in_text(FORBIDDEN_WORDS_IN_ELEMENTS, n.text.lower())]

        if next_elements_no_empty:
            found = next_elements_no_empty[0]

    return found


def get_candidates():
    candidates = driver.find_elements_by_xpath("//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '" + TARGET_WORD + "')]")

    if not candidates:
        for aux in  AUXILIARY_TARGET_WORDS:
            candidates = driver.find_elements_by_xpath("//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '" + aux + "')]")
            if candidates:
                break

    return candidates


def collect_html_list(url, venue, year, role, type):
    candidates = get_candidates()
    found = True

    if candidates:

        start_element = find_start_element(candidates)

        if start_element:
            end_element = find_end_element(start_element)
            list_tag = find_list_tag(start_element, end_element)
            mixed_roles = find_mixed_roles(start_element, end_element)
            if list_tag:
                member_separator = find_member_separator_from_html(start_element, end_element, list_tag)
                type_inferred = infer_type_from_tag(start_element, type)
                add_instructions_html_parser(url, type_inferred, venue, year, role,
                                             start_element,
                                             end_element,
                                             member_separator[0],
                                             member_separator[1],
                                             list_tag,
                                             mixed_roles,
                                             "SINGLE")
            else:
                next_element = find_no_empty_next_element(start_element)
                if next_element:
                    end_element = find_end_element_for_text_in_html_element(next_element)
                    member_separator = find_member_separator_from_text(next_element.text)
                    mixed_roles = find_mixed_roles_from_text(next_element.text)
                    add_instructions_html_parser(url, type, venue, year, role,
                                             start_element,
                                             end_element,
                                             member_separator[0],
                                             member_separator[1],
                                             next_element.tag_name,
                                             mixed_roles,
                                             "ALL")
                else:
                    found = False

        else:
            found = False
    else:
        found = False

    return found


def detect(url, conf, year, role, type):
    driver.get(url)
    time.sleep(5)

    found = collect_list(url, conf, year, role, type)
    if not found:
        print "problems with: " + url


def main():
    json_file = codecs.open(INPUT, 'r', 'utf-8')
    json_lines = json_file.read()
    for line in json_lines.split('\r'):
        if not line.startswith("#") and len(line.strip()) > 0:
            json_entry = json.loads(line)
            url = json_entry.get('url')
            venue = json_entry.get('venue')
            role = json_entry.get('role')
            type = json_entry.get('type')
            year = json_entry.get('year')
            detect(url, venue, year, role, type)
    driver.close()

if __name__ == "__main__":
    main()
