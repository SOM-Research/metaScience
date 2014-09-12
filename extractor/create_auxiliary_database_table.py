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

LOG_FILENAME = 'logger_update_database.log'

def create_auxiliary_tables(cnx):
    cursor = cnx.cursor()
    create_table_aux_program_committee = "CREATE TABLE " + dbconnection.DATABASE_NAME + ".aux_program_committee" \
                                         "(" \
                                         "name varchar(256), " \
                                         "conference varchar(256), " \
                                         "year numeric(5), " \
                                         "role varchar(10), " \
                                         "dblp_author_id numeric(15), " \
                                         "primary key (name, conference, year), " \
                                         "index dblp_author_id (dblp_author_id)" \
                                         ");"
    cursor.execute(create_table_aux_program_committee)

    create_table_aux_scholar_authors = "CREATE TABLE " + dbconnection.DATABASE_NAME + ".aux_scholar_authors" \
                                       "(" \
                                       "name varchar(256), " \
                                       "citations numeric(15), " \
                                       "citations2009 numeric(15), " \
                                       "indexH numeric(15), " \
                                       "indexH2009 numeric(15), " \
                                       "i10 numeric(15), " \
                                       "i102009 numeric(15), " \
                                       "interests text, " \
                                       "dblp_author_id numeric(15), " \
                                       "paper_id numeric(15), " \
                                       "author_url text, " \
                                       "primary key (name, dblp_author_id), " \
                                       "index paper_id (paper_id)" \
                                       ");"
    cursor.execute(create_table_aux_scholar_authors)

    create_table_aux_proceedings = "CREATE TABLE " + dbconnection.DATABASE_NAME + ".aux_dblp_proceedings" \
                                   "(" \
                                   "id int(11) primary key auto_increment, " \
                                   "dblp_id int(8), " \
                                   "dblp_key varchar(150), " \
                                   "url varchar(150), " \
                                   "source varchar(150), " \
                                   "year int(4), " \
                                   "location varchar(256), " \
                                   "type varchar(25), " \
                                   "month varchar(25), " \
                                   "rank varchar(10), " \
                                   "index dblp_key (dblp_key)" \
                                   ");"
    cursor.execute(create_table_aux_proceedings)

    create_table_aux_inproceedings_tracks = "CREATE TABLE " + dbconnection.DATABASE_NAME + ".aux_dblp_inproceedings_tracks" \
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
                                            "index dblp_id (dblp_id), " \
                                            "index url (url), " \
                                            "index dblp_key (dblp_key)" \
                                            ");"
    cursor.execute(create_table_aux_inproceedings_tracks)

    cnx.commit()
    cursor.close()

    create_table_aux_dblp_inproceedings_abstract = "CREATE TABLE " + dbconnection.DATABASE_NAME + ".aux_dblp_inproceedings_abstract" \
                                                   "(" \
                                                   "id int(11) primary key auto_increment, " \
                                                   "dblp_key varchar(150), " \
                                                   "abstract text" \
                                                   ");"
    cursor.execute(create_table_aux_dblp_inproceedings_abstract)

    cnx.commit()
    cursor.close()


def update_conference_database():
    os.system("update_auxiliary_database_tables.py")


def main():
    logging.basicConfig(filename=LOG_FILENAME, level=logging.WARNING)
    with open(LOG_FILENAME, "w") as log_file:
        log_file.write('\n')
    cnx = mysql.connector.connect(**dbconnection.CONFIG)
    #create aux tables
    create_auxiliary_tables(cnx)
    #update database
    update_conference_database()

if __name__ == "__main__":
    main()