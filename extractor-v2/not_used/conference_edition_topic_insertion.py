__author__ = 'valerio cosentino'

import json
import codecs
import mysql.connector
from mysql.connector import errorcode
import db_config
import re

INPUT = "../data/er_topics.txt"


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


def insert_topics(cnx, topics):
    cursor = cnx.cursor()

    for topic in topics:
        query = "INSERT IGNORE INTO `" + db_config.DB_NAME + "`.topic VALUES(NULL, %s)"
        arguments = [digest_topic(topic)]
        cursor.execute(query, arguments)
        cnx.commit()

    cursor.close()


def get_topic_id(cnx, topic):
    topic_id = None
    cursor = cnx.cursor()

    query = "SELECT id FROM `" + db_config.DB_NAME + "`.topic WHERE name = %s"
    arguments = [topic]
    cursor.execute(query, arguments)

    row = cursor.fetchone()

    if row:
        topic_id = row[0]

    cursor.close()

    return topic_id


def insert_topic_conference_edition(cnx, conference_edition_id, topic_id):
    cursor = cnx.cursor()
    query = "INSERT IGNORE INTO `" + db_config.DB_NAME + "`.topic_conference_edition VALUES(%s, %s)"
    arguments = [topic_id, conference_edition_id]
    cursor.execute(query, arguments)
    cnx.commit()
    cursor.close()


def digest_topic(topic):
    no_parenthesis = re.sub("\(.*\)", "", topic)
    no_alpha = re.sub(r"^\W+|\W+$", "", no_parenthesis)
    return no_alpha.lower()


def insert_in_db(cnx, topics, venue, year):
    conference_edition_id = get_conference_id(cnx, venue, year)

    insert_topics(cnx, topics)

    for topic in topics:
        topic_id = get_topic_id(cnx, digest_topic(topic))

        if conference_edition_id:
            insert_topic_conference_edition(cnx, conference_edition_id, topic_id)
        else:
            print "conference edition not found for: " + venue + "/" + str(year)
            break


def establish_connection():
    return mysql.connector.connect(**db_config.CONFIG)


def main():
    cnx = establish_connection()
    json_file = codecs.open(INPUT, 'r', 'utf-8')
    json_lines = json_file.read()
    for line in json_lines.split('\n'):
        if not line.startswith("#") and len(line.strip()) > 0:
            json_entry = json.loads(line)
            topics = json_entry.get('topics')
            venue = json_entry.get('venue')
            year = json_entry.get('year')
            insert_in_db(cnx, topics, venue, year)
    cnx.close()

if __name__ == "__main__":
    main()
