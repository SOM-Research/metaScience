package fr.inria.metascience;

import java.io.IOException;
import java.io.PrintWriter;
import java.sql.Connection;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;

import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import com.google.gson.JsonObject;

@WebServlet("/venueAuthorRank")
public class VenueAuthorRankServlet extends AbstractMetaScienceServlet {

	private static final long serialVersionUID = 1L;
	
	@Override
	protected void doGet(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
		addResponseOptions(resp);
		
		String venueId = req.getParameter(ID_PARAM);
		String subVenueId = req.getParameter(SUBID_PARAM);
		
		if(venueId == null) 
			throw new ServletException("The id cannot be null");
		
		JsonObject topAuthors = getTopAuthorForVenueId(venueId,subVenueId);
		JsonObject regularAuthors = getRegularAuthorForVenueId(venueId,subVenueId);
		
		JsonObject response = new JsonObject();
		response.add("top",topAuthors);
		response.add("regular",regularAuthors);

		resp.setContentType("text/x-json;charset=UTF-8");    
		PrintWriter pw = resp.getWriter();
		pw.append(response.toString());
	}
	
	private JsonObject getTopAuthorForVenueId(String venueId, String subVenueId) throws ServletException {
		JsonObject topAuthors = new JsonObject();
		
		// Checking if we know the conference has different source / source_id
        String sourceId = preCachedVenues.get(venueId);
        if(sourceId == null) sourceId = venueId;

        String source = subVenueId; // THIS FIXES EVERYTHING
        if(subVenueId == null) source = sourceId;
		
		Connection con = Pooling.getInstance().getConnection();
		Statement stmt = null;
		ResultSet rs = null;
		
		try {
			String query = "SELECT airn.author_id, airn.author, COUNT(pub.id) AS publications"
					+ " FROM dblp_pub_new pub"
					+ " JOIN dblp_authorid_ref_new airn"
					+ " ON pub.id = airn.id"
					+ " WHERE source = '" + source + "'"
					+ " AND pub.type = 'inproceedings'"
					+ " GROUP BY airn.author_id"
					+ " ORDER BY publications desc"
					+ " LIMIT 5;";
	
	        stmt = con.createStatement();
	        rs = stmt.executeQuery(query);
	        
	        topAuthors = prepareTopAuthorResults(rs);
	        
		} catch (SQLException e) {
			throw new ServletException("Error accesing the database", e);
		} finally {
			try {
				if(stmt != null) stmt.close();
				if(rs != null) rs.close();
				if(con != null) con.close();
			} catch (SQLException e) {
				throw new ServletException("Impossible to close the connection", e);	
			}
		}
		
		return topAuthors;
	}
	
	private JsonObject getRegularAuthorForVenueId(String venueId, String subVenueId) throws ServletException {
		JsonObject regularAuthors = new JsonObject();
		
		// Checking if we know the conference has different source / source_id
        String sourceId = preCachedVenues.get(venueId);
        if(sourceId == null) sourceId = venueId;

        String source = subVenueId; // THIS FIXES EVERYTHING
        if(subVenueId == null) source = sourceId;
		
		Connection con = Pooling.getInstance().getConnection();
		Statement stmt = null;
		ResultSet rs = null;
		
		try {
			String query = "SELECT airn.author_id, airn.author, COUNT(DISTINCT year) AS presence"
					+ " FROM dblp_pub_new pub"
					+ " JOIN dblp_authorid_ref_new airn"
					+ " ON pub.id = airn.id"
					+ " WHERE source = '" + source + "'"
					+ " AND pub.type = 'inproceedings'"
					+ " GROUP BY airn.author_id"
					+ " ORDER BY presence DESC"
					+ " LIMIT 5;";
	
	        stmt = con.createStatement();
	        rs = stmt.executeQuery(query);
	        
	        regularAuthors = prepareRegularAuthorsResults(rs);
	        
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
		
		return regularAuthors;
	}
	
	private JsonObject prepareTopAuthorResults(ResultSet rs) throws ServletException {
		
		JsonObject topAuthorsJson = new JsonObject();
		try {
			while(rs.next()) {
				String authorName = rs.getString("author");
				int authorPublicationsCount = rs.getInt("publications");
				int authorRank = rs.getRow();
				
				JsonObject authorJson = new JsonObject();
				authorJson.addProperty("name", authorName);
				authorJson.addProperty("publications", authorPublicationsCount);
				
				topAuthorsJson.add(Integer.toString(authorRank), authorJson);
			}
		} catch(SQLException e) {
			throw new ServletException("Error retrieving publication information field from ResultSet",e);
		}
		
		return topAuthorsJson;
	}
	
	private JsonObject prepareRegularAuthorsResults(ResultSet rs) throws ServletException {
		JsonObject regularAuthorsJson = new JsonObject();
		try {
			while(rs.next()) {
				String authorName = rs.getString("author");
				int authorPresenceCount = rs.getInt("presence");
				int authorRank = rs.getRow();
				
				JsonObject authorJson = new JsonObject();
				authorJson.addProperty("name", authorName);
				authorJson.addProperty("presence", authorPresenceCount);
				
				regularAuthorsJson.add(Integer.toString(authorRank), authorJson);
			}
		} catch(SQLException e) {
			throw new ServletException("Error retrieving regular authors information field from ResultSet",e);
		}
		return regularAuthorsJson;
	}

}
