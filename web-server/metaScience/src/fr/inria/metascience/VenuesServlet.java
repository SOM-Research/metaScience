package fr.inria.metascience;

import java.io.IOException;
import java.io.PrintWriter;
import java.sql.Connection;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import java.util.logging.Logger;

import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import com.google.gson.JsonArray;
import com.google.gson.JsonObject;


/**
 * GET method returns the list of venues
 */
@WebServlet("/venues")
public class VenuesServlet extends AbstractMetaScienceServlet{
	private static final String SEARCH_PARAM = "search";
	private static final String REQUEST_TYPE = "type";
	
	private static final long serialVersionUID = 1L;

	private final static Logger LOGGER = Logger.getLogger(VenuesServlet.class.getName()); 

	@Override
	protected void doGet(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
		addResponseOptions(resp);
		
		JsonObject response = new JsonObject();
		
		// Obtains the search param
		String searchString = req.getParameter(SEARCH_PARAM);
		String requestType = req.getParameter(REQUEST_TYPE);
		
		if(searchString != null && !searchString.isEmpty()) {
			if(requestType.equals("1")) {
				// Search being triggered by combo box
				response = this.getAllVenues(searchString);
			} else if(requestType.equals("2")){
				// search being triggered by button
				response = this.getVenueByName(searchString);
			} else {
				throw new ServletException("Request Parameter Error");
			}
			// TODO Ask the database to retrieve those venues LIKE searchString
			
		} /*else {
			// TODO Ask the database to retrieve ALL the venues (no search param)
			venues = this.getAllVenues();
		}*/
		
		// Building the response
		PrintWriter pw = resp.getWriter();
		pw.append(response.toString());
	}
	
	/**
	 * Returns the list of venues
	 * 
	 * @return ResultSet
	 * @throws ServletException 
	 */
//	private JsonArray getAllVenues() throws ServletException {
//		Connection con = Pooling.getInstance().getConnection();
//		Statement stmt = null;
//		ResultSet rs = null;
//		JsonArray answer = new JsonArray();
//		try {
//			stmt = con.createStatement();
//			String query = "SELECT DISTINCT source, title"
//							+ " FROM aux_dblp_proceedings"
//							+ " WHERE source IS NOT NULL AND "
//							+ " type = 'conference'";
//			rs = stmt.executeQuery(query);
//			answer = prepareAnswer(rs);
//		} catch (SQLException e) {
//			throw new ServletException("Error getting venues without search param", e);
//		} finally {
//			try {
//				if(stmt != null) stmt.close();
//				if(rs != null) rs.close();
//				if(con != null) con.close();
//			} catch (SQLException e) {
//				throw new ServletException("Impossible to close the connection", e);
//			}
//		}
//		return answer;
//	}
	
	/**
	 * Returns the list of venues LIKE a specific search string
	 * 
	 * @param searchString
	 * @return
	 * @throws ServletException 
	 */
	private JsonObject getAllVenues(String searchString) throws ServletException {
		Connection con = Pooling.getInstance().getConnection();
		Statement stmt = null;
		ResultSet rs = null;
		JsonObject answer = new JsonObject();
		try {
			stmt = con.createStatement();
			String query = "SELECT DISTINCT source, title"
							+ " FROM aux_dblp_proceedings"
							+ " WHERE source IS NOT NULL AND "
							+ " type = 'conference' AND " // changed in v0.2.0, before it was conference
							+ " (source LIKE '%" + searchString + "%' OR title LIKE '%" + searchString + "%' ) "
							+ " GROUP BY title";
			rs = stmt.executeQuery(query);
			answer = prepareAnswer(rs);
		} catch (SQLException e) {
			throw new ServletException("Error getting venues with search param", e);	
		} finally {
			try {
				if(stmt != null) stmt.close();
				if(rs != null) rs.close();
				if(con != null) con.close();
			} catch (SQLException e) {
				throw new ServletException("Impossible to close the connection", e);	
			}
		}
		return answer;
	}
	
	private JsonObject getVenueByName(String searchString) throws ServletException {
		Connection con = Pooling.getInstance().getConnection();
		Statement stmt = null;
		ResultSet rs = null;
		JsonObject answer = new JsonObject();
		try {
			stmt = con.createStatement();
			String query = "SELECT DISTINCT source, title"
							+ " FROM aux_dblp_proceedings"
							+ " WHERE source IS NOT NULL AND "
							+ " type = 'conference' AND " // changed in v0.2.0, before it was conference
							+ " (source LIKE '" + searchString + "' OR title LIKE '" + searchString + "' ) "
							+ " GROUP BY title";
			rs = stmt.executeQuery(query);
			answer = prepareAnswer(rs);
		} catch (SQLException e) {
			throw new ServletException("Error getting venues with search param", e);	
		} finally {
			try {
				if(stmt != null) stmt.close();
				if(rs != null) rs.close();
				if(con != null) con.close();
			} catch (SQLException e) {
				throw new ServletException("Impossible to close the connection", e);	
			}
		}
		return answer;
	}
	
	/**
	 * Digest the ResultSet to create a JsonObject to be used as response
	 * 
	 * @param rs
	 * @return
	 * @throws ServletException 
	 */
	private JsonObject prepareAnswer(ResultSet rs) throws ServletException {
		JsonObject answer = new JsonObject();
		
		JsonArray venues = new JsonArray();
		int resultCount = 0;

		try {
			while(rs.next()) {
				resultCount++;
				JsonObject jsonObject = new JsonObject();
				String venue = rs.getString("source");
				String title = rs.getString("title");
				jsonObject.addProperty("name", venue.toUpperCase() + " - " + title);
				jsonObject.addProperty("id", venue);
				venues.add(jsonObject);
			}
		} catch (SQLException e) {
			throw new ServletException("Error retrieving the fields from the ResultSet", e);	
		}
		
		answer.addProperty("count", resultCount);
		answer.add("venues", venues);
		
		return answer;
	}
	
	/**
	 * Just for testing purposes
	 * 
	 * @param venues
	 */
	private void test(JsonArray venues) {
		// Build a JSON object for the venue
		// One object per venue
		JsonObject venue = new JsonObject();
		venue.addProperty("name", "models");
		venue.addProperty("id", "1");
		venues.add(venue);

		JsonObject venue2 = new JsonObject();
		venue2.addProperty("name", "icmt");
		venue2.addProperty("id", "2");
		venues.add(venue2);
	}
}
