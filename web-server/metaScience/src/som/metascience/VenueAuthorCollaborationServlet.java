package som.metascience;

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

import som.metascience.elements.Author;
import som.metascience.elements.AuthorPair;

@WebServlet("/venueAuthorCollaboration")
public class VenueAuthorCollaborationServlet extends AbstractMetaScienceServlet {
	
	private static final long serialVersionUID = 1L;
	
	private int maxCollaborations;
	private int maxPublications;
	
	@Override
	protected void doGet(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
		addResponseOptions(resp);
		
		String venueId = req.getParameter(ID_PARAM);
        String subVenueId = req.getParameter(SUBID_PARAM);

		if(venueId == null) 
			throw new ServletException("The id cannot be null");
		
		maxCollaborations = 0;
		maxPublications = 0;
		
		JsonObject response = getVenueAuthorCollaboration(venueId,subVenueId);
		
		JsonObject propJson = new JsonObject();
		propJson.addProperty("maxCollaborations", maxCollaborations);
		propJson.addProperty("maxPublications", maxPublications);
		response.add("prop", propJson);
		
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
        //System.out.println("source : " + source);
		
		Connection con = Pooling.getInstance().getConnection();
		Statement stmt = null;
		ResultSet rs = null;
		
		try {
			String query = 
					"SELECT connections.*, source.publications AS source_author_publications, target.publications AS target_author_publications " +
					"FROM ( " +
						"SELECT source_author_name, source_author_id, target_author_name, target_author_id, relation_strength " +
						"FROM ( " +
							"SELECT " +
								"source_author_name, source_author_id, " +
								"target_author_name, target_author_id, " +
								"CONCAT(GREATEST(source_author_id, target_author_id), '-', LEAST(source_author_id, target_author_id)) AS connection_id, " +
								"COUNT(*) AS relation_strength " +
							"FROM ( " +
								"SELECT r1.name as source_author_name, source.researcher_id as source_author_id, target.researcher_id as target_author_id, r2.name as target_author_name " + 
								"FROM authorship source JOIN paper p ON p.id = source.paper_id JOIN conference_edition ce ON ce.id = p.published_in " +
								"JOIN authorship target ON source.paper_id = target.paper_id AND source.researcher_id <> target.researcher_id " +
								"JOIN researcher r1 ON source.researcher_id = r1.id JOIN researcher r2 ON target.researcher_id = r2.id " +
								"JOIN conference c ON c.id = ce.conference_id " +
								"WHERE acronym = '" + source + "' AND p.type = 1) AS connections " +
							"GROUP BY source_author_id, target_author_id) AS result " +
						"GROUP BY connection_id " +
						"ORDER BY relation_strength DESC) AS connections " +
					"JOIN ( " +
						"SELECT a.researcher_id, COUNT(*) AS publications " +
						"FROM conference c JOIN conference_edition ce ON c.id = ce.conference_id " + 
						"JOIN paper p ON ce.id = p.published_in " +
						"JOIN authorship a ON a.paper_id = p.id " +
						"WHERE acronym = '" + source + "' AND p.type = 1 " +
						"GROUP BY a.researcher_id) AS source " +
					"ON source.researcher_id =  connections.source_author_id " +
					"JOIN ( " +
						"SELECT a.researcher_id, COUNT(*) AS publications " +
						"FROM conference c JOIN conference_edition ce ON c.id = ce.conference_id " +
						"JOIN paper p ON ce.id = p.published_in " +
						"JOIN authorship a ON a.paper_id = p.id " +
						"WHERE acronym = '" + source + "' AND p.type = 1 " +
						"GROUP BY a.researcher_id) AS target " +
					"ON target.researcher_id =  connections.target_author_id";
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
			
			Map<String,Author> authorNodeMap = new HashMap<String,Author>();
			Map<AuthorPair,Integer> authorLinksMap = new HashMap<AuthorPair,Integer>();
			while(rs.next()) {
				String sourceAuthorName = rs.getString("source_author_name");
				String sourceAuthorId = rs.getString("source_author_id");
				String targetAuthorName = rs.getString("target_author_name");
				String targetAuthorId = rs.getString("target_author_id");
				int relationStrength = rs.getInt("relation_strength");
				int sourceAuthorPublications = rs.getInt("source_author_publications");
				int targetAuthorPublications = rs.getInt("target_author_publications");
				
				authorNodeMap.put(sourceAuthorId, new Author(sourceAuthorName,sourceAuthorPublications));
				authorNodeMap.put(targetAuthorId, new Author(targetAuthorName,targetAuthorPublications));
				
				AuthorPair authorPair = new AuthorPair(sourceAuthorId, targetAuthorId);
				if(!authorLinksMap.containsKey(new AuthorPair(targetAuthorId,sourceAuthorId))) {
					authorLinksMap.put(authorPair, relationStrength);
				} else {
					System.out.println("already existing inverse pair");
				}
				
				if( relationStrength > maxCollaborations) {
					maxCollaborations = relationStrength;
				}
				
				if(sourceAuthorPublications > maxPublications) {
					maxPublications = sourceAuthorPublications;
				}
				
				if(targetAuthorPublications > maxPublications) {
					maxPublications = targetAuthorPublications;
				}
			}
			
			JsonArray authorNodes = new JsonArray();
			for(String authorId : authorNodeMap.keySet()) {
				Author author = authorNodeMap.get(authorId);
				
				JsonObject authorNode = new JsonObject();
				authorNode.addProperty("id", authorId);
				authorNode.addProperty("name", author.getName());
				authorNode.addProperty("publications", author.getNumberPublications());
				
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
