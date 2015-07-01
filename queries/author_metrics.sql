/* 1. number of publications per year per type for a given author */
select airn.author_id, airn.author, pub.year, pub.type, count(pub.year) as number 
	from dblp_pub_new pub 
	join dblp_authorid_ref_new airn 
	on pub.id=airn.id 
	where airn.author_id = 636270
	group by pub.year, pub.type;

/* 2. number of pages per year for a given author (in conference or journal) */
select airn.author_id, airn.author, pub.year, sum(calculate_num_of_pages(pub.pages)) as num_pages
from dblp_pub_new pub join dblp_authorid_ref_new airn 
on pub.id = airn.id
where airn.author_id = 636270
group by pub.year;

/* 3. total number of pages and average number of pages written per paper (in conference or journal) by a given author */
select author_id, author, sum(pages) as total_pages, round(avg(pages/authors),2) as avg_owned_pages
from (
select pub.id, title, airn.author_id, airn.author, calculate_num_of_pages(pages) as pages, max(author_num) + 1 as authors
from dblp_pub_new pub join dblp_authorid_ref_new airn on pub.id = airn.id
join dblp_author_ref_new arn on pub.id = arn.id
where airn.author_id = 636270 and pages is not null
group by pub.id) as pub_info;

/* 4. conference attendance for a given author */
select airn.author_id, airn.author, source, count(distinct year) as presence
from dblp_pub_new pub join dblp_authorid_ref_new airn 
on pub.id = airn.id
where source IS NOT NULL and airn.author_id = 636270 and type = 'inproceedings'
group by airn.author_id, source;

/* 5. journal attendance for a given author */
select airn.author_id, airn.author, source, count(distinct year) as presence
from dblp_pub_new pub join dblp_authorid_ref_new airn 
on pub.id = airn.id
where source IS NOT NULL and airn.author_id = 636270 and type = 'article' 
group by airn.author_id, source;

/* 6. publications in conference for a given author */
select airn.author_id, airn.author, source, count(*) as presence
from dblp_pub_new pub join dblp_authorid_ref_new airn 
on pub.id = airn.id
where source IS NOT NULL and airn.author_id = 636270 and type = 'inproceedings'
group by airn.author_id, source;

/* 7. publications in journal for a given author */
select airn.author_id, airn.author, source, count(*) as presence
from dblp_pub_new pub join dblp_authorid_ref_new airn 
on pub.id = airn.id
where source IS NOT NULL and airn.author_id = 636270 and type = 'article'
group by airn.author_id, source;

/* 8. collaboration graph for a given author (it includes collaborations in conferences, journals, informal reports, etc.)  */
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

/* 9. number of pages and average of number of pages written by the author per year */
select author_id, author, sum(pages) as total_pages, year, round(avg(pages/authors),2) as avg_owned_pages
from (
select pub.id, pub.year, title, airn.author_id, airn.author, calculate_num_of_pages(pages) as pages, max(author_num) + 1 as authors
from dblp_pub_new pub join dblp_authorid_ref_new airn on pub.id = airn.id
join dblp_author_ref_new arn on pub.id = arn.id
where airn.author_id = 636270 and pages is not null
group by pub.id) as pub_info
group by pub_info.year;

/* 10. number of co-authors per year */
select author_id, author, sum(coauthors)
from (
select pub.id, pub.year, title, airn.author_id, airn.author, if(max(author_num) + 1 = 1, 0, max(author_num)) as coauthors
from dblp_pub_new pub join dblp_authorid_ref_new airn on pub.id = airn.id
join dblp_author_ref_new arn on pub.id = arn.id
where airn.author_id = 636270
group by pub.id) as pub_info
group by pub_info.year;

/* 11. distinct number of co-authors for a given author */
select count(*) as total
from (
select author_id
from
(select pub.id, airn.author_id, airn.author
from dblp_pub_new pub join dblp_authorid_ref_new airn on pub.id = airn.id
where airn.author_id <> 636270) as co_authors
join
(select pub.id
from dblp_pub_new pub join dblp_authorid_ref_new airn on pub.id = airn.id
where airn.author_id = 636270) as author
on co_authors.id = author.id
group by author_id) as total_coauthors;

/* 12. total number of conferences and average number of conference per year for a given author */
select sum(number_of_conferences) as total_conferences, round(avg(number_of_conferences),2) as average_conferences
from (
select airn.author_id, airn.author, year, count(year) as number_of_conferences
from dblp_pub_new pub join dblp_authorid_ref_new airn 
on pub.id = airn.id
where source IS NOT NULL and airn.author_id = 636270 and type = 'inproceedings'
group by year) as conferences;

/* 13. publications in venue for a given author */
select airn.author_id, airn.author, source, count(*) as presence, type
from dblp_pub_new pub join dblp_authorid_ref_new airn 
on pub.id = airn.id
where source IS NOT NULL and airn.author_id = 636270 and type IN ('inproceedings', 'article')
group by airn.author_id, source;

/* 14. number of publications per year per type & total number of pages */
SELECT airn.author_id, airn.author, pub.year, pub.type, COUNT(pub.year) AS number, SUM(calculate_num_of_pages(pages)) as pages
 FROM dblp_pub_new pub
JOIN dblp_authorid_ref_new airn
ON pub.id=airn.id
WHERE airn.author_id = 684483
GROUP BY pub.year, pub.type;

/* 15. Average number of co-authors, sum of coauthors (with duplicates), participation in papers per year*/
select author_id, author, year, round(avg(co_authors),2) as avg_coauthors, sum(co_authors) as sum_coauthors, round(sum(participation),2) as participation
from (
select pub.id, pub.year, title, airn.author_id, airn.author, max(author_num) as co_authors, 1/(max(author_num) + 1) as participation
from dblp_pub_new pub join dblp_authorid_ref_new airn on pub.id = airn.id
join dblp_author_ref_new arn on pub.id = arn.id
where airn.author_id = 636270 and pages is not null
group by pub.id) as pub_info
group by pub_info.year;

/* 16. Average number of co-authors per author*/
select round(avg(co_authors),2) as total_avg_coauthors
from (
select pub.id, pub.year, title, airn.author_id, airn.author, max(author_num) as co_authors
from dblp_pub_new pub join dblp_authorid_ref_new airn on pub.id = airn.id
join dblp_author_ref_new arn on pub.id = arn.id
where airn.author_id = 573097 and pages is not null
group by pub.id) as pub_info;
