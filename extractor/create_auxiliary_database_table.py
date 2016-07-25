__author__ = 'atlanmod'

import logging
import mysql.connector
from mysql.connector import errorcode
import os
import database_connection_config as dbconnection

#This script creates the auxiliary tables that rely on the dblp database.
#Such tables are:
# aux_dblp_inproceedings_tracks
# aux_dblp_proceedings
# aux_program_committee
# aux_scholar_authors
# aux_dblp_inproceedings_abstract

LOG_FILENAME = 'logger_update_database.log'


def create_auxiliary_tables(cnx):
    cursor = cnx.cursor()
    create_table_aux_program_committee = "CREATE TABLE aux_program_committee" \
                                         "(" \
                                         "name varchar(256), " \
                                         "conference varchar(256), " \
                                         "year numeric(5), " \
                                         "role varchar(10), " \
                                         "dblp_author_id numeric(15), " \
                                         "primary key (name, conference, year), " \
                                         "index dblp_author_id (dblp_author_id)" \
                                         ") ENGINE=InnoDB DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC;"
    cursor.execute(create_table_aux_program_committee)

    create_table_aux_topics = "CREATE TABLE aux_topics" \
                                         "(" \
                                         "name varchar(256), " \
                                         "venue varchar(256), " \
                                         "type varchar(256), " \
                                         "year numeric(5), " \
                                         "primary key (name, venue, year) " \
                                         ") ENGINE=InnoDB DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC;"
    cursor.execute(create_table_aux_topics)

    create_table_aux_scholar_authors = "CREATE TABLE aux_scholar_authors" \
                                       "(" \
                                       "name varchar(256), " \
                                       "citations numeric(15), " \
                                       "citations_5Y numeric(15), " \
                                       "indexH numeric(15), " \
                                       "indexH_5Y numeric(15), " \
                                       "i10 numeric(15), " \
                                       "i10_5Y numeric(15), " \
                                       "interests text, " \
                                       "dblp_author_id numeric(15), " \
                                       "dblp_paper_id numeric(15), " \
                                       "author_url text, " \
                                       "tracked_at date, " \
                                       "primary key (name, dblp_author_id, tracked_at), " \
                                       "index dblp_paper_id (dblp_paper_id)" \
                                       ") ENGINE=InnoDB DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC;"
    cursor.execute(create_table_aux_scholar_authors)

    create_table_aux_proceedings = "CREATE TABLE aux_dblp_proceedings" \
                                   "(" \
                                   "id int(11) primary key auto_increment, " \
                                   "dblp_id int(8), " \
                                   "dblp_key varchar(150), " \
                                   "url varchar(150), " \
                                   "source varchar(150), " \
                                   "year int(4), " \
                                   "title varchar(255), " \
                                   "location varchar(256), " \
                                   "type varchar(25), " \
                                   "month varchar(25), " \
                                   "rank varchar(10), " \
                                   "index dblp_id (dblp_id), " \
                                   "index dblp_key (dblp_key)" \
                                   ") ENGINE=InnoDB DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC;"
    cursor.execute(create_table_aux_proceedings)

    create_table_aux_inproceedings_tracks = "CREATE TABLE aux_dblp_inproceedings_tracks" \
                                            "(" \
                                            "id int(11) primary key auto_increment, " \
                                            "dblp_id int(8), " \
                                            "dblp_key varchar(150), " \
                                            "crossref varchar(50), " \
                                            "url varchar(150), " \
                                            "title text, " \
                                            "track varchar(256), " \
                                            "subtrack1 varchar(256), " \
                                            "subtrack2 varchar(256), " \
                                            "citations numeric(10), " \
                                            "tracked_at date, " \
                                            "index dblp_id (dblp_id), " \
                                            "index url (url), " \
                                            "index dblp_key (dblp_key)" \
                                            ") ENGINE=InnoDB DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC;"
    cursor.execute(create_table_aux_inproceedings_tracks)

    create_table_aux_dblp_inproceedings_abstract = "CREATE TABLE aux_dblp_inproceedings_abstract" \
                                                   "(" \
                                                   "id int(11) primary key auto_increment, " \
                                                   "dblp_id int(8), " \
                                                   "dblp_key varchar(150), " \
                                                   "abstract text, " \
                                                   "index dblp_id (dblp_id)" \
                                                   ") ENGINE=InnoDB DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC;"
    cursor.execute(create_table_aux_dblp_inproceedings_abstract)

    cnx.commit()
    cursor.close()


def update_conference_database():
    os.system("update_auxiliary_database_tables.py")


def prepare_db(cnx):
    cursor = cnx.cursor()
    cursor.execute("set global innodb_file_format = BARRACUDA")
    cursor.execute("set global innodb_file_format_max = BARRACUDA")
    cursor.execute("set global innodb_large_prefix = ON")
    cursor.execute("set global character_set_server = utf8")
    cnx.commit()
    cursor.close()


def main():
    logging.basicConfig(filename=LOG_FILENAME, level=logging.WARNING)
    with open(LOG_FILENAME, "w") as log_file:
        log_file.write('\n')
    cnx = mysql.connector.connect(**dbconnection.CONFIG)
    #prepare db
    prepare_db(cnx)
    #create aux tables
    create_auxiliary_tables(cnx)
    #update database
    #update_conference_database()

if __name__ == "__main__":
    main()