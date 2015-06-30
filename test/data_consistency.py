__author__ = 'valerio cosentino'

from selenium import webdriver
from random import randint
import time
import json
import re
from itertools import chain
from collections import Counter
import operator

driver = webdriver.Chrome(executable_path='C:\Program Files (x86)\Google\Chrome\chromedriver.exe')
driver_edition = webdriver.Chrome(executable_path='C:\Program Files (x86)\Google\Chrome\chromedriver.exe')
driver_author = webdriver.Chrome(executable_path='C:\Program Files (x86)\Google\Chrome\chromedriver.exe')
URL = 'http://dblp.uni-trier.de/db/'

MANUAL_SELECTION = True
MANUAL_SELECTION_URL = 'http://dblp1.uni-trier.de/db/conf/msr/index.html' #
# http://dblp.uni-trier.de/db/conf/icmt/' #'http://dblp.uni-trier.de/db/conf/ecmdafa/index.html' #'http://dblp.uni-trier.de/pers/hd/c/Cabot:Jordi'
ACTIVATE_CONFERENCE_FILTER = False
CONFERENCE_FILTER = 'ECMFA'
MINIMUM_COAUTHOR_CONNECTION_STRENGTH = 5

#type must be defined both for manual and random selection
type = 'inproceedings' #person, article, inproceedings

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


def calculate_researcher_activity_along_the_years():
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

            elif class_name == 'entry incollection':
                pubs = entries_per_year.get(current_year)
                if pubs.get('incollection'):
                    pubs.update({'incollection': pubs.get('incollection')+1})
                else:
                    pubs.update({'incollection': 1})

            elif class_name.startswith('entry'):
                pubs = entries_per_year.get(current_year)
                if pubs.get('other'):
                    pubs.update({'other': pubs.get('other')+1})
                else:
                    pubs.update({'other': 1})

        except:
            continue

    return entries_per_year


def calculate_average_researcher_publications_per_year(entries_per_year):
    sum_pubs_per_year = 0
    for year in entries_per_year.keys():
        pubs_per_year = entries_per_year.get(year)
        sum_pubs_per_year += sum(pubs_per_year.values())

    return round(float(sum_pubs_per_year)/len(entries_per_year.keys()), 2)


def calculate_researcher_total_publications(entries_per_year):
    sum_pubs_per_year = 0
    for year in entries_per_year.keys():
        pubs_per_year = entries_per_year.get(year)
        sum_pubs_per_year += sum(pubs_per_year.values())

    return sum_pubs_per_year


def calculate_researcher_total_number_of_coauthors(coauthor_connection):
    return len(coauthor_connection.keys())


def calculate_researcher_average_number_of_coauthors():
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


def calculate_number_of_publication_type_for_researcher(entries_per_year, type):
    sum_type = 0
    for year in entries_per_year.keys():
        pubs_per_year = entries_per_year.get(year)
        if pubs_per_year.get(type):
            sum_type += pubs_per_year.get(type)

    return sum_type


def calculate_researcher_coauthor_connection():
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


def calculate_researcher_venue_connection():
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
    entries_per_year = calculate_researcher_activity_along_the_years()
    total_publications = calculate_researcher_total_publications(entries_per_year)
    total_journals = calculate_number_of_publication_type_for_researcher(entries_per_year, 'journal')
    total_conferences = calculate_number_of_publication_type_for_researcher(entries_per_year, 'conference')
    total_books = calculate_number_of_publication_type_for_researcher(entries_per_year, 'book')
    total_editors = calculate_number_of_publication_type_for_researcher(entries_per_year, 'editor')
    total_others = calculate_number_of_publication_type_for_researcher(entries_per_year, 'other')
    average_publications_year = calculate_average_researcher_publications_per_year(entries_per_year)

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

    coauthor_connection = calculate_researcher_coauthor_connection()
    number_of_coauthors = calculate_researcher_total_number_of_coauthors(coauthor_connection)
    average_number_of_coauthors = calculate_researcher_average_number_of_coauthors()

    write_to_output('total number of co-authors: ' + str(number_of_coauthors))
    write_to_output('\n')
    write_to_output('average number of co-authors: ' + str(average_number_of_coauthors))
    write_to_output('\n')

    venue_connection = calculate_researcher_venue_connection()

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


def get_attribute(edition, attribute_name, attribute_value):
    attribute = None
    spans = edition.find_elements_by_tag_name('span')
    for span in spans:
        item_prop = span.get_attribute(attribute_name)
        if item_prop == attribute_value:
            attribute = span.text
            break

    return attribute


def get_papers_in_edition(driver):
    lis = driver.find_elements_by_tag_name('li')

    papers = []
    for li in lis:
        if li.get_attribute('class') == "entry inproceedings":
            papers.append(li)

    return papers


def get_author_name(link):
    driver_author.get(link)
    author_name = driver_author.find_element_by_id("headline").find_element_by_tag_name("h1").text
    return author_name


def analyse_edition(year, href_edition):
    driver_edition.get(href_edition)

    authors_in_papers = []
    authors_in_edition = {}
    papers = get_papers_in_edition(driver_edition)
    for paper in papers:
        spans = paper.find_elements_by_tag_name('span')
        authors = []
        for span in spans:
            if span.get_attribute('itemprop') == 'author':
                author_name = get_author_name(span.find_element_by_tag_name('a').get_attribute('href'))
                authors.append(author_name)
        authors_in_papers.append(authors)

    authors_in_edition.update({year: authors_in_papers})

    return authors_in_edition


def get_info_editions():
    editions = driver.find_elements_by_class_name('publ-list')
    editions_info = {}
    for edition in editions:
        year = get_attribute(edition, 'itemprop', 'datePublished')

        if ACTIVATE_CONFERENCE_FILTER:
            name = get_attribute(edition, 'class', 'title')
            if CONFERENCE_FILTER in name.split(' '):
                contents = edition.find_element_by_link_text('[contents]')
                href_edition = contents.get_attribute('href')
                editions_info.update(analyse_edition(year, href_edition))
        else:
            contents = edition.find_element_by_link_text('[contents]')
            href_edition = contents.get_attribute('href')
            editions_info.update(analyse_edition(year, href_edition))

    return editions_info


def calculate_conference_number_of_papers(editions):
    papers = {}
    for e in editions.keys():
        papers.update({e: len(editions.get(e))})

    return papers


def calculate_conference_average_number_of_papers(editions):
    papers = calculate_conference_number_of_papers(editions).values()
    return round((float(sum(papers))/len(editions.keys())), 2)


def calculate_conference_number_of_distinct_authors(editions):
    authors_in_editions = {}
    for e in editions.keys():
        distinct_authors = list(set(list(chain.from_iterable(editions.get(e)))))
        authors_in_editions.update({e: len(distinct_authors)})

    return authors_in_editions


def calculate_conference_average_number_of_distinct_authors(editions):
    authors_in_editions = calculate_conference_number_of_distinct_authors(editions).values()
    return round(float(sum(authors_in_editions))/len(authors_in_editions), 2)


def calculate_conference_number_of_authors_per_paper(editions):
    authors_per_papers = {}
    for e in editions.keys():
        papers = editions.get(e)
        authors_in_papers = []
        for p in papers:
            authors_in_papers.append(len(p))
        authors_per_papers.update({e: round(sum(authors_in_papers)/float(len(authors_in_papers)),2)})

    return authors_per_papers


def calculate_conference_average_number_of_authors_per_paper(editions):
    authors_in_papers = calculate_conference_number_of_authors_per_paper(editions).values()
    return round(float(sum(authors_in_papers))/len(authors_in_papers), 2)


def calculate_conference_number_of_papers_per_author(editions):
    papers_per_authors = {}
    for e in editions.keys():
        authors = [val for sublist in editions.get(e) for val in sublist]
        author_frequency = Counter(authors).values()
        papers_per_authors.update({e: round(float(sum(author_frequency))/len(author_frequency), 2)})

    return papers_per_authors


def calculate_conference_average_number_of_papers_per_author(editions):
    papers_per_authors = calculate_conference_number_of_papers_per_author(editions).values()
    return round(float(sum(papers_per_authors))/len(papers_per_authors), 2)


def calculate_conference_perishing_rate(editions):
    perishing_rates = {}

    sorted_keys = sorted(editions.keys())

    distinct_authors_in_previous_edition = set(list(chain.from_iterable(editions.get(sorted_keys[0]))))
    for e in sorted_keys[1:]:
        distinct_authors = set(list(chain.from_iterable(editions.get(e))))
        survived = len(list(distinct_authors_in_previous_edition.intersection(distinct_authors)))
        perished = len(list(distinct_authors_in_previous_edition)) - survived
        perishing_rate = round((float(perished) / (perished + survived)) * 100, 2)
        perishing_rates.update({e: perishing_rate})
        distinct_authors_in_previous_edition = distinct_authors

    return perishing_rates


def calculate_conference_average_perishing_rate(editions):
    perishing_rates = calculate_conference_perishing_rate(editions).values()
    return round(sum(perishing_rates)/float(len(perishing_rates)), 2)


def calculate_conference_openness_rate(editions):
    openness_rates = {}

    sorted_keys = sorted(editions.keys())

    community_authors = set(list(chain.from_iterable(editions.get(sorted_keys[0]))))
    openness_rates.update({sorted_keys[0]: (0.0, 100.0)})
    for e in sorted_keys[1:]:
        papers = editions.get(e)
        papers_from_new_comers = 0
        papers_from_community = 0
        for paper_authors in papers:
            intersection = list(set(paper_authors).intersection(community_authors))
            if len(intersection) == len(paper_authors):
                papers_from_community += 1
            elif len(intersection) == 0:
                papers_from_new_comers += 1
        openness_rates.update({e: (round((papers_from_community/float(len(papers)))*100, 2), round((papers_from_new_comers/float(len(papers)))*100, 2))})
        distinct_authors = set(list(chain.from_iterable(editions.get(e))))
        new_authors = distinct_authors - community_authors
        community_authors = set(list(community_authors) + list(new_authors))

    return openness_rates


def calculate_average_openness_rate(editions):
    openness_rates = calculate_conference_openness_rate(editions).values()

    return ({'from_new_comers': round(sum([x[1] for x in openness_rates])/float(len(openness_rates)), 2),
            'from_community': round(sum([x[0] for x in openness_rates])/float(len(openness_rates)), 2)})


def calculate_top_authors(editions):
    top_authors = {}
    for e in editions.keys():
        authors = [val for sublist in editions.get(e) for val in sublist]
        author_frequency = Counter(authors)
        top_authors = dict(Counter(top_authors)+author_frequency)

    sorted_by_value = sorted(top_authors.items(), key=operator.itemgetter(1), reverse=True)[:10]

    return sorted_by_value


def calculate_top_regular_authors(editions):
    regular_authors = {}
    for e in editions.keys():
        distinct_authors = set(list(chain.from_iterable(editions.get(e))))
        author_frequency = Counter(distinct_authors)
        regular_authors = dict(Counter(regular_authors)+author_frequency)

    sorted_by_value = sorted(regular_authors.items(), key=operator.itemgetter(1), reverse=True)[:10]

    return sorted_by_value


def calculate_strength_between_authors(author_a, author_b, editions):
    strength = 0
    for e in editions.keys():
        papers = editions.get(e)
        for paper in papers:
            if author_a in paper and author_b in paper:
                strength += 1

    return strength


def flatten(*args):
    for x in args:
        if hasattr(x, '__iter__'):
            for y in flatten(*x):
                yield y
        else:
            yield x


def calculate_co_author_connections(editions, minimum_strength):
    author_connections = {}
    distinct_authors_in_conference = list(set(flatten([editions.values()])))
    for i in range(0, len(distinct_authors_in_conference)-2):
        author_i = distinct_authors_in_conference[i]
        for j in range(i+1, len(distinct_authors_in_conference)-1):
            author_j = distinct_authors_in_conference[j]
            strength = calculate_strength_between_authors(author_i, author_j, editions)

            if strength >= minimum_strength:
                author_connections.update({author_i + '-' + author_j: str(strength)})

    return author_connections


def calculate_statistics_for_conference():
    editions = get_info_editions()

    average_number_of_papers = calculate_conference_average_number_of_papers(editions)
    average_number_of_authors = calculate_conference_average_number_of_distinct_authors(editions)
    average_number_of_authors_per_paper = calculate_conference_average_number_of_authors_per_paper(editions)
    average_number_of_papers_per_author = calculate_conference_average_number_of_papers_per_author(editions)
    average_perishing_rate = calculate_conference_average_perishing_rate(editions)
    average_openness_rate = calculate_average_openness_rate(editions)
    top_authors = calculate_top_authors(editions)
    top_regular_authors = calculate_top_regular_authors(editions)
    co_author_connections = calculate_co_author_connections(editions, MINIMUM_COAUTHOR_CONNECTION_STRENGTH)

    write_to_output('average number of papers: ' + str(average_number_of_papers))
    write_to_output('\n')
    write_to_output('\n')
    write_to_output('average number of authors: ' + str(average_number_of_authors))
    write_to_output('\n')
    write_to_output('\n')
    write_to_output('average number of authors per paper: ' + str(average_number_of_authors_per_paper))
    write_to_output('\n')
    write_to_output('\n')
    write_to_output('average number of papers per author: ' + str(average_number_of_papers_per_author))
    write_to_output('\n')
    write_to_output('\n')
    write_to_output('average perishing rate: ' + str(average_perishing_rate))
    write_to_output('\n')
    write_to_output('\n')
    write_to_output('average openness rate: ' + str(average_openness_rate))
    write_to_output('\n')
    write_to_output('\n')
    write_to_output('top authors: ' + json.dumps(top_authors, indent=4, sort_keys=True, ensure_ascii=False).encode('utf-8'))
    write_to_output('\n')
    write_to_output('\n')
    write_to_output('top regular authors: ' + json.dumps(top_regular_authors, indent=4, sort_keys=True, ensure_ascii=False).encode('utf-8'))
    write_to_output('\n')
    write_to_output('\n')
    write_to_output('activity along the years: ' + json.dumps(({'papers': calculate_conference_number_of_papers(editions),
                                                                'authors': calculate_conference_number_of_distinct_authors(editions)}), indent=4, sort_keys=True))
    write_to_output('\n')
    write_to_output('\n')
    write_to_output('ratios along the years: ' + json.dumps(({'authors_per_paper': calculate_conference_number_of_authors_per_paper(editions),
                                                                'papers_per_author': calculate_conference_number_of_papers_per_author(editions)}), indent=4, sort_keys=True))
    write_to_output('\n')
    write_to_output('\n')
    write_to_output('turnover information: ' + json.dumps({'perishing_rate': calculate_conference_perishing_rate(editions)}, indent=4, sort_keys=True))
    write_to_output('\n')
    write_to_output('\n')
    write_to_output('openness information: ' + json.dumps({'from_community/from_new_comers': calculate_conference_openness_rate(editions)}, indent=4, sort_keys=True))
    write_to_output('\n')
    write_to_output('\n')
    write_to_output('co-author connections: ' + json.dumps(co_author_connections, indent=4, sort_keys=True, ensure_ascii=False).encode('utf-8'))


def calculate_statistics(type):
    init_output()
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

    driver.close()
    driver_edition.close()
    driver_author.close()

if __name__ == "__main__":
    main()

