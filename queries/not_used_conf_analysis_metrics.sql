/*
* CREATE AND POPULATE TRENDING TOPIC IN PAPERS TABLE
* Current topics: UML, MDA, CLOUD, GRID, ASPECT, MINING, 
* SECURITY, AGILE, ONTOLOGY, QoS, DoS, VERIFICATION, ANDROID, OPTIMIZATION, XML, CSP
* DDoS, HTML, API, SCALABILITY, GREEDY, LAMBDA, CROWDSOURCING, VISUALIZATION, XQUERY
*/

create table _trending_topics_in_paper (num_of_papers numeric(11), year numeric(4), topic varchar(256));

/* UML */
insert into _trending_topics_in_paper
select count(*) as papers, year, 'UML' as word
from dblp_pub_new
where type = 'inproceedings' and (title REGEXP BINARY '([[:punct:]]|[[:space:]])UML([[:punct:]]|[[:space:]])' or title REGEXP '([[:punct:]]|[[:space:]])unified modeling language(s)*([[:punct:]]|[[:space:]])') and crossref IN 	(	
												select dblp_key
												from dblp_pub_new
												where type = 'proceedings'
												and (title LIKE '%software%' or title LIKE '%engineering%')
												)
group by year;

/* MDA */
insert into _trending_topics_in_paper
select count(*) as papers, year, 'MDA' as word
from dblp_pub_new
where type = 'inproceedings' and title REGEXP BINARY '([[:punct:]]|[[:space:]])MDA([[:punct:]]|[[:space:]])' AND crossref IN 	(	
												select dblp_key
												from dblp_pub_new
												where type = 'proceedings'
												and (title LIKE '%software%' or title LIKE '%engineering%')
												)
group by year;

/* CLOUD */
insert into _trending_topics_in_paper
select count(*) as papers, year, 'cloud' as word
from dblp_pub_new
where type = 'inproceedings' and title REGEXP '([[:punct:]]|[[:space:]])cloud([[:punct:]]|[[:space:]])' and crossref IN (	
												select dblp_key
												from dblp_pub_new
												where type = 'proceedings'
												and (title LIKE '%software%' or title LIKE '%engineering%')
												)
group by year;

/* GRID */
insert into _trending_topics_in_paper
select count(*) as papers, year, 'grid' as word
from dblp_pub_new
where type = 'inproceedings' and title REGEXP '([[:punct:]]|[[:space:]])grid([[:punct:]]|[[:space:]])' and crossref IN 	(	
												select dblp_key
												from dblp_pub_new
												where type = 'proceedings'
												and (title LIKE '%software%' or title LIKE '%engineering%')
												)
group by year;

/* ASPECT */
insert into _trending_topics_in_paper
select count(*) as papers, year, 'aspect' as word
from dblp_pub_new
where type = 'inproceedings' and title REGEXP '([[:punct:]]|[[:space:]])aspect([[:punct:]]|[[:space:]])' and crossref IN 	(	
												select dblp_key
												from dblp_pub_new
												where type = 'proceedings'
												and (title LIKE '%software%' or title LIKE '%engineering%')
												)
group by year;


/* Mining */
insert into _trending_topics_in_paper
select count(*) as papers, year, 'mining' as word
from dblp_pub_new
where type = 'inproceedings' and title REGEXP '([[:punct:]]|[[:space:]])mining([[:punct:]]|[[:space:]])' and crossref IN 	(	
												select dblp_key
												from dblp_pub_new
												where type = 'proceedings'
												and (title LIKE '%software%' or title LIKE '%engineering%')
												)
group by year;


/* Security */
insert into _trending_topics_in_paper
select count(*) as papers, year, 'security' as word
from dblp_pub_new
where type = 'inproceedings' and title REGEXP '([[:punct:]]|[[:space:]])security([[:punct:]]|[[:space:]])' and crossref IN 	(	
												select dblp_key
												from dblp_pub_new
												where type = 'proceedings'
												and (title LIKE '%software%' or title LIKE '%engineering%')
												)
group by year;


/* Agile */
insert into _trending_topics_in_paper
select count(*) as papers, year, 'agile' as word
from dblp_pub_new
where type = 'inproceedings' and title REGEXP '([[:punct:]]|[[:space:]])agile([[:punct:]]|[[:space:]])' and crossref IN 	(	
												select dblp_key
												from dblp_pub_new
												where type = 'proceedings'
												and (title LIKE '%software%' or title LIKE '%engineering%')
												)
group by year;


/* Ontology */
insert into _trending_topics_in_paper
select count(*) as papers, year, 'ontology' as word
from dblp_pub_new
where type = 'inproceedings' and title REGEXP '([[:punct:]]|[[:space:]])ontolog(y|ies)([[:punct:]]|[[:space:]])' and crossref IN 	(	
												select dblp_key
												from dblp_pub_new
												where type = 'proceedings'
												and (title LIKE '%software%' or title LIKE '%engineering%')
												)
group by year;

/* QoS */
insert into _trending_topics_in_paper
select count(*) as papers, year, 'QoS' as word
from dblp_pub_new
where type = 'inproceedings' and title REGEXP BINARY '([[:punct:]]|[[:space:]])QoS([[:punct:]]|[[:space:]])' and crossref IN 	(	
												select dblp_key
												from dblp_pub_new
												where type = 'proceedings'
												and (title LIKE '%software%' or title LIKE '%engineering%')
												)
group by year;

/* DoS */
insert into _trending_topics_in_paper
select count(*) as papers, year, 'DoS' as word
from dblp_pub_new
where type = 'inproceedings' and title REGEXP BINARY '([[:punct:]]|[[:space:]])DoS([[:punct:]]|[[:space:]])' and crossref IN 	(	
												select dblp_key
												from dblp_pub_new
												where type = 'proceedings'
												and (title LIKE '%software%' or title LIKE '%engineering%')
												)
group by year;


/* Verification */
insert into _trending_topics_in_paper
select count(*) as papers, year, 'verification' as word
from dblp_pub_new
where type = 'inproceedings' and title REGEXP '([[:punct:]]|[[:space:]])verification([[:punct:]]|[[:space:]])' and crossref IN 	(	
												select dblp_key
												from dblp_pub_new
												where type = 'proceedings'
												and (title LIKE '%software%' or title LIKE '%engineering%')
												)
group by year;


/* Android */
insert into _trending_topics_in_paper
select count(*) as papers, year, 'android' as word
from dblp_pub_new
where type = 'inproceedings' and title REGEXP '([[:punct:]]|[[:space:]])android([[:punct:]]|[[:space:]])' and crossref IN 	(	
												select dblp_key
												from dblp_pub_new
												where type = 'proceedings'
												and (title LIKE '%software%' or title LIKE '%engineering%')
												)
group by year;

/* Optimization */
insert into _trending_topics_in_paper
select count(*) as papers, year, 'optimization' as word
from dblp_pub_new
where type = 'inproceedings' and title REGEXP '([[:punct:]]|[[:space:]])optimization([[:punct:]]|[[:space:]])' and crossref IN 	(	
												select dblp_key
												from dblp_pub_new
												where type = 'proceedings'
												and (title LIKE '%software%' or title LIKE '%engineering%')
												)
group by year;


/* XML */
insert into _trending_topics_in_paper
select count(*) as papers, year, 'Fuzzy' as word
from dblp_pub_new
where type = 'inproceedings' and title REGEXP '([[:punct:]]|[[:space:]])fuzzy([[:punct:]]|[[:space:]])' and crossref IN 	(	
												select dblp_key
												from dblp_pub_new
												where type = 'proceedings'
												and (title LIKE '%software%' or title LIKE '%engineering%')
												)
group by year;

/* CSP */
insert into _trending_topics_in_paper
select count(*) as papers, year, 'CSP' as word
from dblp_pub_new
where type = 'inproceedings' and title REGEXP BINARY '([[:punct:]]|[[:space:]])CSP(s)*([[:punct:]]|[[:space:]])' and crossref IN 	(	
												select dblp_key
												from dblp_pub_new
												where type = 'proceedings'
												and (title LIKE '%software%' or title LIKE '%engineering%')
												)
group by year;

/* DDoS */
insert into _trending_topics_in_paper
select count(*) as papers, year, 'DDoS' as word
from dblp_pub_new
where type = 'inproceedings' and title REGEXP '([[:punct:]]|[[:space:]])DDoS([[:punct:]]|[[:space:]])' and crossref IN 	(	
												select dblp_key
												from dblp_pub_new
												where type = 'proceedings'
												and (title LIKE '%software%' or title LIKE '%engineering%')
												)
group by year;

/* HTML */
insert into _trending_topics_in_paper
select count(*) as papers, year, 'HTML' as word
from dblp_pub_new
where type = 'inproceedings' and title REGEXP '([[:punct:]]|[[:space:]])HTML([[:punct:]]|[[:space:]])' and crossref IN 	(	
												select dblp_key
												from dblp_pub_new
												where type = 'proceedings'
												and (title LIKE '%software%' or title LIKE '%engineering%')
												)
group by year;

/* API */
insert into _trending_topics_in_paper
select count(*) as papers, year, 'API' as word
from dblp_pub_new
where type = 'inproceedings' and title REGEXP '([[:punct:]]|[[:space:]])API([[:punct:]]|[[:space:]])' and crossref IN 	(	
												select dblp_key
												from dblp_pub_new
												where type = 'proceedings'
												and (title LIKE '%software%' or title LIKE '%engineering%')
												)
group by year;


/* scalability */
insert into _trending_topics_in_paper
select count(*) as papers, year, 'scalability' as word
from dblp_pub_new
where type = 'inproceedings' and title REGEXP '([[:punct:]]|[[:space:]])scalability([[:punct:]]|[[:space:]])' and crossref IN 	(	
												select dblp_key
												from dblp_pub_new
												where type = 'proceedings'
												and (title LIKE '%software%' or title LIKE '%engineering%')
												)
group by year;


/* greedy */
insert into _trending_topics_in_paper
select count(*) as papers, year, 'greedy' as word
from dblp_pub_new
where type = 'inproceedings' and title REGEXP '([[:punct:]]|[[:space:]])greedy([[:punct:]]|[[:space:]])' and crossref IN 	(	
												select dblp_key
												from dblp_pub_new
												where type = 'proceedings'
												and (title LIKE '%software%' or title LIKE '%engineering%')
												)
group by year;

/* lambda */
insert into _trending_topics_in_paper
select count(*) as papers, year, 'lambda' as word
from dblp_pub_new
where type = 'inproceedings' and title REGEXP '([[:punct:]]|[[:space:]])lambda([[:punct:]]|[[:space:]])' and crossref IN 	(	
												select dblp_key
												from dblp_pub_new
												where type = 'proceedings'
												and (title LIKE '%software%' or title LIKE '%engineering%')
												)
group by year;

/* crowdsourcing */
insert into _trending_topics_in_paper
select count(*) as papers, year, 'crowdsourcing' as word
from dblp_pub_new
where type = 'inproceedings' and title REGEXP '([[:punct:]]|[[:space:]])crowdsourcing([[:punct:]]|[[:space:]])' and crossref IN 	(	
												select dblp_key
												from dblp_pub_new
												where type = 'proceedings'
												and (title LIKE '%software%' or title LIKE '%engineering%')
												)
group by year;

/* visualization */
insert into _trending_topics_in_paper
select count(*) as papers, year, 'visualization' as word
from dblp_pub_new
where type = 'inproceedings' and title REGEXP '([[:punct:]]|[[:space:]])visualization([[:punct:]]|[[:space:]])' and crossref IN 	(	
												select dblp_key
												from dblp_pub_new
												where type = 'proceedings'
												and (title LIKE '%software%' or title LIKE '%engineering%')
												)
group by year;

/* xquery */
insert into _trending_topics_in_paper
select count(*) as papers, year, 'xquery' as word
from dblp_pub_new
where type = 'inproceedings' and title REGEXP '([[:punct:]]|[[:space:]])xquery([[:punct:]]|[[:space:]])' and crossref IN 	(	
												select dblp_key
												from dblp_pub_new
												where type = 'proceedings'
												and (title LIKE '%software%' or title LIKE '%engineering%')
												)
group by year;

/* number of papers per satellite and main conferences per year */
create table _num_of_papers_per_conference_per_year as
select count(id) as num_papers, source, source_id, year
from dblp_pub_new where type = 'inproceedings' and source_id is not null and source is not null
group by source, source_id, year;

/* number of authors (unique and not) per satellite and main conferences per year*/
create table _num_authors_per_conf_per_year as
select count(auth.author_id) as num_authors, count(distinct auth.author_id) as num_unique_authors, source, source_id, year
from dblp_pub_new pub
join
dblp_authorid_ref_new auth
on pub.id = auth.id
where type = 'inproceedings'
group by source, source_id, year;

/* avg number of authors per paper per conf per year */
create table _avg_number_authors_per_paper_per_conf_per_year as
select avg(author_per_paper) as avg_author_per_paper, source, source_id, year
from (
	select count(auth.author_id) as author_per_paper, pub.id as paper_id, source, source_id, year
	from dblp_pub_new pub
	join
	dblp_authorid_ref_new auth
	on pub.id = auth.id
	where type = 'inproceedings'
	group by paper_id, source, source_id, year) as count
group by source, source_id, year;

/* number of papers per author per conf per year */
create table _number_papers_per_author_per_conf_per_year as
select auth.author_id as author_id, auth.author as author_name, 
count(distinct pub.id) as num_paper_per_author, source, source_id, year
from dblp_pub_new pub
join
dblp_authorid_ref_new auth
on pub.id = auth.id
where type = 'inproceedings'
group by author_id, source, source_id, year;

/* avg number of papers per author per conf per year */
create table _avg_number_papers_per_author_per_conf_per_year as
select avg(num_paper_per_author) as avg_num_paper_per_author, source, source_id, year
from (select auth.author_id as author_id, auth.author as author_name, 
count(distinct pub.id) as num_paper_per_author, source, source_id, year
from dblp_pub_new pub
join
dblp_authorid_ref_new auth
on pub.id = auth.id
where type = 'inproceedings'
group by author_id, source, source_id, year) as count
group by source, source_id, year;

/* number of pages per conference per year and avg number of pages per conference per year*/
/* note that some page intervals are wrong, currently we do not remove them */
create table _num_and_avg_pages_per_conf_per_year as
select source, source_id, year, sum(calculate_num_of_pages(pages)) as sum_of_pages, avg(calculate_num_of_pages(pages)) as avg_num_of_pages
from dblp_pub_new 
where type = 'inproceedings' and pages is not null
group by source, source_id, year;