/* 1. top regular author attendance for a given conference */
select airn.author_id, airn.author, count(distinct year) as presence
from dblp_pub_new pub join dblp_authorid_ref_new airn 
on pub.id = airn.id
where source = 'icse' and pub.type = 'inproceedings'
group by airn.author_id
order by presence desc
limit 10;

/* 2. top author conference publications for a given conference */
select airn.author_id, airn.author, count(pub.id) as publications
from dblp_pub_new pub join dblp_authorid_ref_new airn 
on pub.id = airn.id
where source = 'icse' and pub.type = 'inproceedings'
group by airn.author_id
order by publications desc
limit 10;

/* 3. collaboration graph between authors of a given conference */
select connections.*, source_authors.publications, target_authors.publications
from (
select source_author_name, source_author_id, target_author_name, target_author_id, relation_strength
from
(
select source_authors.author as source_author_name, source_authors.author_id as source_author_id, 
target_authors.author as target_author_name, target_authors.author_id as target_author_id, 
count(*) as relation_strength, source_authors.author_id * target_authors.author_id as connection_id
from (
select pub.id as pub, author, author_id
from dblp_pub_new pub 
	join dblp_authorid_ref_new airn 
	on pub.id = airn.id 
where source = 'icse' and pub.type = 'inproceedings') as source_authors
join
(select pub.id as pub, author, author_id
from dblp_pub_new pub 
	join dblp_authorid_ref_new airn 
	on pub.id = airn.id 
where source = 'icse' and pub.type = 'inproceedings') as target_authors
on source_authors.pub = target_authors.pub and source_authors.author_id <> target_authors.author_id
group by source_authors.author_id, target_authors.author_id) as x
where relation_strength > 1
group by connection_id) as connections
join
(select airn.author_id, airn.author, count(pub.id) as publications
from dblp_pub_new pub join dblp_authorid_ref_new airn 
on pub.id = airn.id
where source = 'icse' and pub.type = 'inproceedings'
group by airn.author_id) as source_authors
on connections.source_author_id = source_authors.author_id
join
(select airn.author_id, airn.author, count(pub.id) as publications
from dblp_pub_new pub join dblp_authorid_ref_new airn 
on pub.id = airn.id
where source = 'icse' and pub.type = 'inproceedings'
group by airn.author_id) as target_authors
on connections.target_author_id = target_authors.author_id;

/* 4. number of papers per author per conf per year */
create table _number_papers_per_author_per_conf_per_year as
select auth.author_id as author_id, auth.author as author_name, 
count(distinct pub.id) as num_paper_per_author, source, source_id, year
from dblp_pub_new pub
join
dblp_authorid_ref_new auth
on pub.id = auth.id
where type = 'inproceedings'
group by author_id, source, source_id, year;

/* 5. number of authors (unique and not) per satellite and main conferences per year*/
create table _num_authors_per_conf_per_year as
select count(auth.author_id) as num_authors, count(distinct auth.author_id) as num_unique_authors, source, source_id, year
from dblp_pub_new pub
join
dblp_authorid_ref_new auth
on pub.id = auth.id
where type = 'inproceedings'
group by source, source_id, year;

/* 6. avg number of authors per paper per conf per year */
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

/* 7. avg number of papers per author per conf per year */
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