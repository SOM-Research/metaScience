__author__ = 'valerio cosentino'

from selenium import webdriver
from random import randint
import time
import json
import re

driver = webdriver.Chrome(executable_path='C:\Program Files (x86)\Google\Chrome\chromedriver.exe')
URL = 'http://dblp.uni-trier.de/db/'

MANUAL_SELECTION = True
MANUAL_SELECTION_URL = 'http://dblp.uni-trier.de/pers/hd/c/Cabot:Jordi'

#type must be defined both for manual and random selection
type = 'person' #article, inproceedings

OUTPUT = './dblp-data.txt'


def get_random_index(start, end):
    return randint(start, end)


def get_index(browsable_element, type):
    found = None
    for e in browsable_element.find_elements_by_tag_name('li'):
        try:
            if e.find_element_by_class_name(type):
                elements = e.find_element_by_tag_name('ul').find_elements_by_tag_name('li')
                random_index = get_random_index(0, len(elements)-1)
                found = elements[random_index]
                break
        except:
            found = None

    return found


def rest_a_bit():
    time.sleep(5)


def calculate_activity_along_the_years():
    publ_section = driver.find_element_by_id('publ-section')
    entries = publ_section.find_elements_by_tag_name('li')

    entries_per_year = {}

    current_year = None
    for e in entries:
        try:
            class_name = e.get_attribute('class')

            if class_name == 'year':
                current_year = e.text
                if not entries_per_year.get(current_year):
                    entries_per_year.update({current_year: {}})
            elif class_name == 'entry inproceedings':
                pubs = entries_per_year.get(current_year)
                if pubs.get('conference'):
                    pubs.update({'conference': pubs.get('conference')+1})
                else:
                    pubs.update({'conference': 1})

            elif class_name == 'entry article':
                pubs = entries_per_year.get(current_year)
                if pubs.get('journal'):
                    pubs.update({'journal': pubs.get('journal')+1})
                else:
                    pubs.update({'journal': 1})

            elif class_name == 'entry book':
                pubs = entries_per_year.get(current_year)
                if pubs.get('book'):
                    pubs.update({'book': pubs.get('book')+1})
                else:
                    pubs.update({'book': 1})

            elif class_name == 'entry editor':
                pubs = entries_per_year.get(current_year)
                if pubs.get('editor'):
                    pubs.update({'editor': pubs.get('editor')+1})
                else:
                    pubs.update({'editor': 1})

            elif class_name.startswith('entry'):
                pubs = entries_per_year.get(current_year)
                if pubs.get('other'):
                    pubs.update({'other': pubs.get('other')+1})
                else:
                    pubs.update({'other': 1})

        except:
            continue

    return entries_per_year


def calculate_average_publications_per_year(entries_per_year):
    sum_pubs_per_year = 0
    for year in entries_per_year.keys():
        pubs_per_year = entries_per_year.get(year)
        sum_pubs_per_year += sum(pubs_per_year.values())

    return round(float(sum_pubs_per_year)/len(entries_per_year.keys()), 2)


def calculate_total_publications(entries_per_year):
    sum_pubs_per_year = 0
    for year in entries_per_year.keys():
        pubs_per_year = entries_per_year.get(year)
        sum_pubs_per_year += sum(pubs_per_year.values())

    return sum_pubs_per_year


def calculate_total_number_of_coauthors(coauthor_connection):
    return len(coauthor_connection.keys())


def calculate_average_number_of_coauthors():
    author_name = driver.find_element_by_id('headline').find_element_by_tag_name('h1').text

    publ_section = driver.find_element_by_id('publ-section')
    entries = publ_section.find_elements_by_tag_name('li')

    coauthors = []
    for e in entries:
        try:
            class_name = e.get_attribute('class')
            if class_name.startswith('entry'):
                number_of_coauthors = 0
                spans = e.find_elements_by_tag_name('span')
                for span in spans:
                    item_prop = span.get_attribute('itemprop')
                    if item_prop == 'author':
                        coauthor_name = span.text
                        if coauthor_name != author_name:
                            number_of_coauthors += 1
                coauthors.append(number_of_coauthors)
        except:
            continue

    return round(sum(coauthors)/float(len(coauthors)),2)


def calculate_number_of_type(entries_per_year, type):
    sum_type = 0
    for year in entries_per_year.keys():
        pubs_per_year = entries_per_year.get(year)
        if pubs_per_year.get(type):
            sum_type += pubs_per_year.get(type)

    return sum_type


def calculate_coauthor_connection():
    author_name = driver.find_element_by_id('headline').find_element_by_tag_name('h1').text

    publ_section = driver.find_element_by_id('publ-section')
    entries = publ_section.find_elements_by_tag_name('li')
    connections = {}
    for e in entries:
        try:
            class_name = e.get_attribute('class')

            if class_name.startswith('entry'):
                spans = e.find_elements_by_tag_name('span')
                for span in spans:
                    item_prop = span.get_attribute('itemprop')
                    if item_prop == 'author':
                        coauthor_name = span.text
                        if coauthor_name != author_name:
                            if connections.get(coauthor_name):
                                connections.update({coauthor_name: connections.get(coauthor_name)+1})
                            else:
                                connections.update({coauthor_name: 1})
        except:
            continue

    return connections


def update_connection_map(connections, connections_per_year):
    for c in connections_per_year.keys():
        if c in connections.keys():
            value = connections.get(c)
            attendance = value.get('attendance')
            publication = value.get('publication')
            value.update({'attendance': attendance+1, 'publication': publication+connections_per_year.get(c)})
        else:
            connections.update({c : {'attendance': 1, 'publication': connections_per_year.get(c)}})


def digest_venue_name(name):
    return re.sub('\(.*\)', '', name).strip()


def calculate_venue_connection():
    publ_section = driver.find_element_by_id('publ-section')
    entries = publ_section.find_elements_by_tag_name('li')
    connections = {}
    current_year = None
    for e in entries:
        try:
            class_name = e.get_attribute('class')

            if class_name == 'year':
                if current_year is not None:
                    update_connection_map(connections, connections_per_year)

                current_year = e.text
                connections_per_year = {}
            elif class_name in ('entry inproceedings', 'entry article'):
                spans = e.find_elements_by_tag_name('span')
                for span in spans:
                    item_prop = span.get_attribute('itemprop')
                    if item_prop == 'isPartOf':
                        item_type = span.get_attribute('itemtype')
                        if 'Series' in item_type or 'Periodical' in item_type:
                            venue_name = digest_venue_name(span.text)


                            if connections_per_year.get(venue_name):
                                connections_per_year.update({venue_name: connections_per_year.get(venue_name)+1})
                            else:
                                connections_per_year.update({venue_name: 1})
        except:
            continue

    update_connection_map(connections, connections_per_year)

    return connections


def calculate_number_of_pages(interval):
    try:
        if '-' in interval:
            splitted = interval.split('-')
            pages = int(splitted[1]) - int(splitted[0])
        else:
            pages = 1
    except:
        pages = 0

    return pages


def update_page_evolution_map(page_evolution_per_year, page_evolution, current_year):
    contributed_pages = []
    total_coll = 0
    for value in page_evolution.values():
        pages = value.get('pages')
        coll = value.get('coll')
        if pages > 0:
            contributed_pages.append(float(pages)/(coll+1))
        total_coll += coll

    page_evolution_per_year.update({current_year: {'avg.pages': round(sum(contributed_pages)/len(contributed_pages), 2), 'n.coll': total_coll}})


def calculate_page_evolution():
    author_name = driver.find_element_by_id('headline').find_element_by_tag_name('h1').text

    publ_section = driver.find_element_by_id('publ-section')
    entries = publ_section.find_elements_by_tag_name('li')
    page_evolution_per_year = {}
    current_year = None
    paper_counter = 0
    for e in entries:
        try:
            class_name = e.get_attribute('class')

            if class_name == 'year':
                if current_year is not None:
                    update_page_evolution_map(page_evolution_per_year, page_evolution, current_year)

                current_year = e.text
                page_evolution = {}
            elif class_name.startswith('entry'):
                paper_counter += 1
                spans = e.find_elements_by_tag_name('span')
                collaborations = 0
                pages = 0
                for span in spans:
                    item_prop = span.get_attribute('itemprop')
                    if item_prop == 'pagination':
                        page_interval = span.text
                        pages = calculate_number_of_pages(page_interval)

                    elif item_prop == 'author':
                        coauthor_name = span.text
                        if coauthor_name != author_name:
                            collaborations += 1

                page_evolution.update({paper_counter: {'pages': pages, 'coll': collaborations}})

        except:
            continue

    update_page_evolution_map(page_evolution_per_year, page_evolution, current_year)

    return page_evolution_per_year


def init_output():
    open(OUTPUT, 'w').close()


def write_to_output(text):
    f = open(OUTPUT, 'a+')
    f.write(text)
    f.close()


def calculate_statistics_for_person():
    init_output()

    entries_per_year = calculate_activity_along_the_years()
    total_publications = calculate_total_publications(entries_per_year)
    total_journals = calculate_number_of_type(entries_per_year, 'journal')
    total_conferences = calculate_number_of_type(entries_per_year, 'conference')
    total_books = calculate_number_of_type(entries_per_year, 'book')
    total_editors = calculate_number_of_type(entries_per_year, 'editor')
    total_others = calculate_number_of_type(entries_per_year, 'other')
    average_publications_year = calculate_average_publications_per_year(entries_per_year)

    write_to_output('total number of publications: ' + str(total_publications))
    write_to_output('\n')
    write_to_output('total number of journals: ' + str(total_journals))
    write_to_output('\n')
    write_to_output('total number of conferences: ' + str(total_conferences))
    write_to_output('\n')
    write_to_output('total number of books: ' + str(total_books))
    write_to_output('\n')
    write_to_output('total number of editors: ' + str(total_editors))
    write_to_output('\n')
    write_to_output('total number of other pubs: ' + str(total_others))
    write_to_output('\n')
    write_to_output('average number of publications per year: ' + str(average_publications_year))
    write_to_output('\n')

    coauthor_connection = calculate_coauthor_connection()
    number_of_coauthors = calculate_total_number_of_coauthors(coauthor_connection)
    average_number_of_coauthors = calculate_average_number_of_coauthors()

    write_to_output('total number of co-authors: ' + str(number_of_coauthors))
    write_to_output('\n')
    write_to_output('average number of co-authors: ' + str(average_number_of_coauthors))
    write_to_output('\n')

    venue_connection = calculate_venue_connection()

    write_to_output('\n')
    write_to_output('Activity along the years:')
    write_to_output('\n')
    write_to_output(json.dumps(entries_per_year, indent=4, sort_keys=True))
    write_to_output('\n')
    write_to_output('\n')
    pages_evolution = calculate_page_evolution()
    write_to_output('Written pages evolution')
    write_to_output('\n')
    write_to_output(json.dumps(pages_evolution, indent=4, sort_keys=True))
    write_to_output('\n')
    write_to_output('\n')
    write_to_output('Co-author connection:')
    write_to_output('\n')
    write_to_output(json.dumps(coauthor_connection, indent=4, sort_keys=True, ensure_ascii=False).encode('utf-8'))
    write_to_output('\n')
    write_to_output('\n')
    write_to_output('Venue connection:')
    write_to_output('\n')
    write_to_output(json.dumps(venue_connection, indent=4, sort_keys=True))
    write_to_output('\n')

def calculate_statistics_for_journal():
    None


def calculate_statistics_for_conference():
    None


def calculate_statistics(type):
    if type == 'person':
        calculate_statistics_for_person()
    elif type == 'article':
        calculate_statistics_for_journal()
    elif type == 'inproceedings':
        calculate_statistics_for_conference()
    else:
        print 'type ' + type + ' not treated'


def browse(type):
    browsable = driver.find_element_by_id('browsable')
    index = get_index(browsable, type)
    index.click()
    rest_a_bit()
    typed_elements = driver.find_elements_by_tag_name('li')
    random_typed_element = typed_elements[get_random_index(0, len(typed_elements)-1)]
    rest_a_bit()
    random_typed_element.find_element_by_tag_name('a').click()
    rest_a_bit()

    calculate_statistics(type)


def main():
    if MANUAL_SELECTION:
       driver.get(MANUAL_SELECTION_URL)
       calculate_statistics(type)
    else:
        driver.get(URL)
        browse(type)

if __name__ == "__main__":
    main()

