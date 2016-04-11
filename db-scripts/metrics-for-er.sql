select pc.pc_size, edition.papers, pc.year
from (
/* size of PC members */
select ce.conference_id, ce.id, ce.year, 
count(distinct pc.researcher_id) as pc_size
from program_committee pc join conference_edition ce 
on pc.conference_edition_id = ce.id
where year > 2005
group by ce.conference_id, ce.id
order by year ASC) as pc
join
(/* papers per edition */
select year, count(*) as papers
from paper p join conference_edition ce on p.published_in = ce.id
where year > 2005
group by year) as edition
on pc.year = edition.year;

/* age of PC members */
select researcher_id, r.name, count(*) as presence
from program_committee pc join conference_edition ce 
on pc.conference_edition_id = ce.id
join researcher r
on r.id = pc.researcher_id
where year > 2005
group by researcher_id;


/* avg age PC members*/
select avg(presence) as presence
from (
select researcher_id, r.name, count(*) as presence
from program_committee pc join conference_edition ce 
on pc.conference_edition_id = ce.id
join researcher r
on r.id = pc.researcher_id
where year > 2005
group by researcher_id) as pc_age;


/* PC members in 2015 not publishing in the last 3 editions */
select pc_2015.researcher_id, pc_2015.researcher_name
from 
(select researcher_id, r.name as researcher_name
from program_committee pc left join researcher r on pc.researcher_id = r.id
join conference_edition ce on pc.conference_edition_id = ce.id
where ce.year = 2015) as pc_2015
left join
(select researcher_id
from authorship a join paper p on a.paper_id = p.id
join conference_edition ce on ce.id = p.published_in
where year >= 2012 and year <= 2014
group by researcher_id) as authors_3_last_editions
on pc_2015.researcher_id = authors_3_last_editions.researcher_id
where authors_3_last_editions.researcher_id is null;

/* Researchers not PC members in 2015 publishing in the last 3 editions */
select presence_authors_3_last_editions.researcher_id, presence_authors_3_last_editions.researcher_name
from 
(select researcher_id, researcher_name, count(*) as presence
from (
	select researcher_id, r.name as researcher_name, year
	from authorship a join paper p on a.paper_id = p.id
	join conference_edition ce on ce.id = p.published_in
	join researcher r on r.id = a.researcher_id
	where year >= 2012 and year <= 2014
	group by researcher_id, year) as researcher_per_year
group by researcher_id) as presence_authors_3_last_editions
left join
(select researcher_id
from program_committee pc join conference_edition ce on pc.conference_edition_id = ce.id
where ce.year = 2015) as pc_2015
on presence_authors_3_last_editions.researcher_id = pc_2015.researcher_id
where presence = 3 and pc_2015.researcher_id is null;

/* Topics ER */
select topic_id, t.name as topic_name, count(*) as occurrence
from topic_conference_edition tce join conference_edition ce 
on tce.conference_edition_id = ce.id
join topic t on t.id = tce.topic_id
group by topic_id;

