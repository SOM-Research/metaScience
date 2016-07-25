/* number of papers per edition */
CREATE TABLE aux_papers_per_edition
select ce.conference_id, ce.id as conference_edition_id, count(*) as papers, year
from 
	conference_edition ce join paper p on ce.id = p.published_in
group by year, ce.conference_id, ce.id;

/* number of distinct authors per edition */
CREATE TABLE aux_distinct_authors_per_edition
select ce.conference_id, ce.id as conference_edition_id, ce.year, count(distinct a.researcher_id) as unique_authors
from 
	conference_edition ce join paper p on ce.id = p.published_in 
	join authorship a on a.paper_id = p.id 
group by year, ce.conference_id, ce.id;

/* avg number of authors per paper per edition */
CREATE TABLE aux_ratio_authors_per_paper_per_edition
select conference_id, conference_edition_id, year, round(avg(authors),2) as avg_authors_per_paper
from (
	select ce.conference_id, ce.id as conference_edition_id, ce.year, p.id as paper_id, count(a.researcher_id) as authors
	from 
		conference_edition ce join paper p on ce.id = p.published_in 
		join authorship a on a.paper_id = p.id 
	group by ce.year, ce.conference_id, p.id) as authors_per_paper_per_edition
group by year, conference_id, conference_edition_id;

/* avg number of papers per author per edition */
CREATE TABLE aux_ratio_papers_per_author_per_edition
select conference_id, conference_edition_id,year, round(avg(papers),2) as avg_papers_per_author
from (
	select ce.conference_id, ce.id as conference_edition_id, ce.year, a.researcher_id, count(p.id) as papers
	from 
		conference_edition ce join paper p on ce.id = p.published_in 
		join authorship a on a.paper_id = p.id 
	group by ce.year, ce.conference_id, a.researcher_id) as papers_per_author_per_edition
group by year, conference_id, conference_edition_id;

/* size of PC members */
select ce.conference_id, ce.id, ce.year, 
count(distinct pc.researcher_id) as pc_members
from program_committee pc join conference_edition ce 
on pc.conference_edition_id = ce.id
group by ce.conference_id, ce.id
order by year ASC;

