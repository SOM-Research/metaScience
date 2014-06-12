package fr.inria.atlanmod.conferenceanalysis.services;

import java.io.IOException;
import java.io.PrintWriter;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;

import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import fr.inria.atlanmod.conferenceanalysis.services.graph.Edge;
import fr.inria.atlanmod.conferenceanalysis.services.graph.GexfGenerator;
import fr.inria.atlanmod.conferenceanalysis.services.graph.Node;

@WebServlet("/authorsPapersPerConference")
public class AuthorsPapersPerConference extends HttpServlet {

	protected void doPost(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException  {
		response.setHeader("Access-Control-Allow-Origin", "*");
		response.setHeader("Access-Control-Allow-Methods", "GET,POST,PUT,DELETE,OPTIONS");
		
		String conferenceId = request.getParameter("conference");
		System.out.println("Conference received: " + conferenceId);
		
		String query = "SELECT " +
					"man.author AS author, " + 
					"airn.author_id AS author_id, " +  
					"pn.title AS paper, " +  
					"pn.year AS year " + 
				"FROM " +  
					"dblp.dblp_authorid_ref_new airn, " + 
					"dblp.dblp_main_aliases_new man, " + 
					"dblp.dblp_pub_new pn " + 
				"WHERE " +  
					"pn.type='inproceedings' AND pn.source='" + conferenceId + "' AND pn.year = 2013 AND airn.id = pn.id AND airn.author_id = man.author_id;";
		

		HashMap<String, Node> authors = new HashMap<>();
		HashMap<String, Node> papers = new HashMap<>();
		HashMap<String, Edge> edges = new HashMap<>();
		HashMap<String, Edge> cachedEdges = new HashMap<>();

		int nodeCounter = 0;
		int edgeCounter = 0;
		String conferenceInternalId = String.valueOf(nodeCounter++);
		Node conferenceNode = new Node(conferenceInternalId, conferenceId, 0, 0, 0, 10);
		
		Connection conn = null;
		Statement stmt = null;
		ResultSet rSet = null;
        try {
			Class.forName("com.mysql.jdbc.Driver");
			conn = DriverManager.getConnection("jdbc:mysql://atlanmodexp.info.emn.fr:13506/dblp?useUnicode=true&characterEncoding=UTF-8&user=root&password=coitointerrotto");
			stmt = conn.createStatement();
			rSet = stmt.executeQuery(query);
			
			while(rSet.next()) {
				String authorName = rSet.getString("author");
				String authorId = rSet.getString("author_id");
				String paperName = rSet.getString("paper");
				String year = rSet.getString("year");
				
				Node authorNode = authors.get(authorName);
				String authorInternalId = null;
				if(authorNode == null) {
					authorInternalId = String.valueOf(nodeCounter++);
					authorNode = new Node(authorInternalId, authorName, 255, 0, 0, 5);
					authors.put(authorName, authorNode);
				} else {
					authorInternalId = authorNode.getId();
				}

				Node paperNode = papers.get(paperName);
				String paperInternalId = null;
				if(paperNode == null) {
					paperInternalId = String.valueOf(nodeCounter++);
					paperNode = new Node(paperInternalId, paperName, 0, 255, 0, 5);
					papers.put(paperName, paperNode);
					
					String edgeInternalId = String.valueOf(edgeCounter++);
					Edge edge = new Edge(edgeInternalId, conferenceInternalId, paperInternalId);
					edges.put(edgeInternalId, edge);
				} else {
					paperInternalId = paperNode.getId();
				}

				String cachedEdgeId = authorInternalId + "-" + paperInternalId;
				if(cachedEdges.get(cachedEdgeId) == null) {
					String edgeInternalId = String.valueOf(edgeCounter++);
					Edge edge = new Edge(edgeInternalId, authorInternalId, paperInternalId);
					edges.put(edgeInternalId, edge);
					cachedEdges.put(cachedEdgeId, edge);
				}

			}
			conn.close();
			stmt.close();
			rSet.close();
        } catch (ClassNotFoundException e1) {
			throw new ServletException("The mysql driver could not be instantiated");
		} catch (SQLException e) {
			throw new ServletException("There was and error in mysql");
		}
        
        List<Node> nodesGen = new ArrayList<>();
        nodesGen.add(conferenceNode);
		nodesGen.addAll(authors.values());
		nodesGen.addAll(papers.values());

		List<Edge> edgesGen = new ArrayList<>();
		edgesGen.addAll(edges.values());
		GexfGenerator generator = new GexfGenerator(nodesGen, edgesGen);
		String gexfString = generator.generate();

		PrintWriter out = response.getWriter();
        out.print(gexfString); 
	}

	@Override
	protected void doOptions(HttpServletRequest request, HttpServletResponse response)throws ServletException, IOException
	{
		response.setHeader("Access-Control-Allow-Origin", "*");
		response.setHeader("Access-Control-Allow-Methods", "GET,POST,PUT,DELETE,OPTIONS");
		response.setHeader("Access-Control-Allow-Headers", "Origin, X-Requested-With, Content-Type, Accept");
		super.doOptions(request, response);

	}
}
