package fr.inria.metascience;

import java.io.IOException;
import java.io.PrintWriter;
import java.sql.Connection;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import java.util.HashMap;
import java.util.Map;

import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import com.google.gson.JsonArray;
import com.google.gson.JsonObject;

import fr.inria.metascience.elements.AuthorPair;

@WebServlet("/venueAuthorCollaboration")
public class VenueAuthorCollaborationServlet extends AbstractMetaScienceServlet {
	
	private static final long serialVersionUID = 1L;
	
	@Override
	protected void doGet(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
		addResponseOptions(resp);
		
		String venueId = req.getParameter(ID_PARAM);
        String subVenueId = req.getParameter(SUBID_PARAM);

		if(venueId == null) 
			throw new ServletException("The id cannot be null");
		
		JsonObject response = getVenueAuthorCollaboration(venueId,subVenueId);
		//JsonObject response = test();
		
		resp.setContentType("text/x-json;charset=UTF-8");
		PrintWriter pw = resp.getWriter();
		pw.append(response.toString());
		
	}
	
	private JsonObject getVenueAuthorCollaboration(String venueId, String subVenueId) throws ServletException {
		
		JsonObject venueAuthorCollaboration = new JsonObject();
		
		// Checking if we know the conference has different source / source_id
        String sourceId = preCachedVenues.get(venueId);
        if(sourceId == null) sourceId = venueId;

        String source = subVenueId; // THIS FIXES EVERYTHING
        if(subVenueId == null) source = sourceId;
        System.out.println("source : " + source);
		
		Connection con = Pooling.getInstance().getConnection();
		Statement stmt = null;
		ResultSet rs = null;
		
		try {
			String query = "SELECT source_author_name, source_author_id, target_author_name, target_author_id, relation_strength"
					+ " FROM ("
					+ " 	SELECT source_authors.author AS source_author_name, source_authors.author_id AS source_author_id,"
					+ "				target_authors.author as target_author_name, target_authors.author_id as target_author_id,"
					+ "				COUNT(*) AS relation_strength, source_authors.author_id * target_authors.author_id AS connection_id"
					+ "		FROM ("
					+ "			SELECT pub.id as pub, author, author_id"
					+ "			FROM dblp_pub_new pub"
					+ "			JOIN dblp_authorid_ref_new airn"
					+ "			ON pub.id = airn.id"
					+ "			WHERE source = '" + source + "'" 
					+ "		) AS source_authors"
					+ "		JOIN ("
					+ "			SELECT pub.id as pub, author, author_id"
					+ "			FROM dblp_pub_new pub"
					+ "			JOIN dblp_authorid_ref_new airn"
					+ "			ON pub.id = airn.id"
					+ "			WHERE source = '" + source + "'"
					+ "		) AS target_authors"
					+ "		ON source_authors.pub = target_authors.pub"
					+ "		AND source_authors.author_id <> target_authors.author_id"
					+ "		GROUP BY source_authors.author_id, target_authors.author_id"
					+ " ) AS x"
					+ "	WHERE relation_strength > 1"
					+ " GROUP BY connection_id;";
	
	        stmt = con.createStatement();
	        rs = stmt.executeQuery(query);
	        
	        venueAuthorCollaboration = prepareVenueAuthorCollaboration(rs);
	        
		} catch (SQLException e) {
			throw new ServletException("Error accessing the database", e);
		} finally {
			try {
				if(stmt != null) stmt.close();
				if(rs != null) rs.close();
				if(con != null) con.close();
			} catch (SQLException e) {
				throw new ServletException("Impossible to close the connection", e);	
			}
		}
		
		return venueAuthorCollaboration;
	}
	
	private JsonObject prepareVenueAuthorCollaboration(ResultSet rs) throws ServletException {
		JsonObject venueAuthorCollaboration = new JsonObject();
		
		try {
			
			Map<String,String> authorNodeMap = new HashMap<String,String>();
			Map<AuthorPair,Integer> authorLinksMap = new HashMap<AuthorPair,Integer>();
			while(rs.next()) {
				String sourceAuthorName = rs.getString("source_author_name");
				String sourceAuthorId = rs.getString("source_author_id");
				String targetAuthorName = rs.getString("target_author_name");
				String targetAuthorId = rs.getString("target_author_id");
				int relationStrength = rs.getInt("relation_strength");
				
				authorNodeMap.put(sourceAuthorId, sourceAuthorName);
				authorNodeMap.put(targetAuthorId, targetAuthorName);
				
				AuthorPair authorPair = new AuthorPair(sourceAuthorId, targetAuthorId);
				if(!authorLinksMap.containsKey(new AuthorPair(targetAuthorId,sourceAuthorId))) {
					authorLinksMap.put(authorPair, relationStrength);
				} else {
					System.out.println("lol");
				}
			}
			
			JsonArray authorNodes = new JsonArray();
			for(String authorId : authorNodeMap.keySet()) {
				JsonObject authorNode = new JsonObject();
				authorNode.addProperty("id", authorId);
				authorNode.addProperty("name", authorNodeMap.get(authorId));
				
				authorNodes.add(authorNode);
			}
			
			JsonArray authorLinks = new JsonArray();
			for(AuthorPair authorPair : authorLinksMap.keySet()) {
				JsonObject authorLink = new JsonObject();
				authorLink.addProperty("source", authorPair.getSource());
				authorLink.addProperty("target",authorPair.getTarget());
				authorLink.addProperty("value", authorLinksMap.get(authorPair));
				
				authorLinks.add(authorLink);
			}
			
			venueAuthorCollaboration.add("nodes", authorNodes);
			venueAuthorCollaboration.add("links", authorLinks);
		} catch (SQLException e) {
			throw new ServletException("Error retreving venue author collaboration fields from Result Set", e);
		}
		
		return venueAuthorCollaboration;
	}

}
