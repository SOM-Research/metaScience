/* These queries allow us to get the same information we were obtaining before
 * by analyzing the HTML from DBLP */

/* Calculating the nodes of the graph
 * Each author will be a node. An author has a name and the list of editions
 * of the conference in which he/she got a paper accepted 
 * This query has been defined for ICMT as example */
SELECT 
	man.author as author, 
	count(distinct(pn.year)) as number_of_editions_participating,
	count(pn.year) as number_of_papers_accepted,
	GROUP_CONCAT(pn.year ORDER BY pn.year DESC SEPARATOR ', ') as participated_in_editions
FROM 
	dblp.dblp_authorid_ref_new airn, /* to get the author id */
	dblp.dblp_main_aliases_new man,  /* to get the main alias of the author */
	dblp.dblp_pub_new pn
WHERE
	pn.type='inproceedings' AND pn.source='ICMT' AND airn.id = pn.id AND airn.author_id = man.author_id
GROUP BY
	man.author;

/* Calculating the edges of the graph
 * The following table gets the authors per paper, the position of each author
 * and the publication year
 * There will be an edge between two nodes (i.e., authors) when thy share a paper .
 * NOTE: The first tables in the join are used to avoid clash conflicts with the names. */
SELECT 
	man.author AS author, 
	airn.author_id AS author_id, 
	arn.author_num AS position, 
	pn.title AS paper, 
	pn.year AS year
FROM 
	dblp.dblp_author_ref_new arn,    /* to get the author position */
	dblp.dblp_authorid_ref_new airn, /* to get the author id */
	dblp.dblp_main_aliases_new man,  /* to get the main alias of the author */
	dblp.dblp_pub_new pn
WHERE 
	pn.type='inproceedings' AND pn.source='ICMT' AND airn.id = pn.id AND arn.id = pn.id AND airn.author_id = man.author_id;
