/* number of publications per year per type for a given author */
select airn.author_id, airn.author, pub.year, pub.type, count(pub.year) as number 
	from dblp_pub_new pub 
	join dblp_authorid_ref_new airn 
	on pub.id=airn.id 
	where airn.author_id = 636270
	group by pub.year, pub.type;

/* number of pages per year for a given author */
select airn.author_id, airn.author, pub.year, sum(calculate_num_of_pages(pub.pages)) as num_pages
from dblp_pub_new pub join dblp_authorid_ref_new airn 
on pub.id = airn.id
where airn.author_id = 636270
group by pub.year;

/* total number of pages and average number of pages written per paper by a given author */
select author_id, author, sum(pages) as total_pages, avg(pages/authors) as avg_owned_pages
from (
select pub.id, title, airn.author_id, airn.author, calculate_num_of_pages(pages) as pages, max(author_num) + 1 as authors
from dblp_pub_new pub join dblp_authorid_ref_new airn on pub.id = airn.id
join dblp_author_ref_new arn on pub.id = arn.id
where airn.author_id = 636270 and pages is not null
group by pub.id) as pub_info;

/* conference attendance for a given author */
select airn.author_id, airn.author, source, count(distinct year) as presence
from dblp_pub_new pub join dblp_authorid_ref_new airn 
on pub.id = airn.id
where source IS NOT NULL and airn.author_id = 636270 and type = 'inproceedings' and title NOT LIKE '%workshop%'
group by airn.author_id, source;

/* publications in conference for a given author */
select airn.author_id, airn.author, source, count(*) as presence
from dblp_pub_new pub join dblp_authorid_ref_new airn 
on pub.id = airn.id
where source IS NOT NULL and airn.author_id = 636270 and type = 'inproceedings' and title NOT LIKE '%workshop%'
group by airn.author_id, source;

/* collaboration graph for a given author */
select connected_author_papers.author_id, connected_author_papers.author, count(*) as relation_strength
from (
select id
from dblp_authorid_ref_new airn
where airn.author_id = 636270) as target_author_papers
join
(select id, author_id, author
from dblp_authorid_ref_new airn
where airn.author_id <> 636270) as connected_author_papers
on target_author_papers.id = connected_author_papers.id
group by connected_author_papers.author_id;

/* number of pages per author per year for a given conference */
select airn.author_id, airn.author, sum(calculate_num_of_pages(pub.pages)) as total_pages
from dblp_pub_new pub join dblp_authorid_ref_new airn 
on pub.id = airn.id
where source = 'icse' and type = 'inproceedings' and title NOT LIKE '%workshop%' and pages is not null
group by airn.author_id;

/* top regular author attendance for a given conference */
select airn.author_id, airn.author, count(distinct year) as presence
from dblp_pub_new pub join dblp_authorid_ref_new airn 
on pub.id = airn.id
where source = 'icse'
group by airn.author_id
order by presence desc
limit 10;

/* top author conference publications for a given conference */
select airn.author_id, airn.author, count(pub.id) as publications
from dblp_pub_new pub join dblp_authorid_ref_new airn 
on pub.id = airn.id
where source = 'icse'
group by airn.author_id
order by publications desc
limit 10;