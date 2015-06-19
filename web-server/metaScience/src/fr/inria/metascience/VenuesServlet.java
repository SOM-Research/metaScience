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
	
	private static final long serialVersionUID = 1L;

	private final static Logger LOGGER = Logger.getLogger(VenuesServlet.class.getName()); 

	@Override
	protected void doGet(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
		addResponseOptions(resp);
		
		// Obtains the search param
		String searchString = req.getParameter(SEARCH_PARAM);

		// This list contains the list of JSON object representing venues
		JsonArray venues = new JsonArray();
		
		if(searchString != null && !searchString.isEmpty()) {
			// TODO Ask the database to retrieve those venues LIKE searchString
			venues = this.getAllVenues(searchString);
		} /*else {
			// TODO Ask the database to retrieve ALL the venues (no search param)
			venues = this.getAllVenues();
		}*/
		
		// Building the response
		JsonObject response = new JsonObject();
		response.add("venues", venues);
		PrintWriter pw = resp.getWriter();
		pw.append(venues.toString());
	}
	
	/**
	 * Returns the list of venues
	 * 
	 * @return ResultSet
	 * @throws ServletException 
	 */
	private JsonArray getAllVenues() throws ServletException {
		Connection con = Pooling.getInstance().getConnection();
		Statement stmt = null;
		ResultSet rs = null;
		JsonArray answer = new JsonArray();
		try {
			stmt = con.createStatement();
			String query = "SELECT DISTINCT source, title"
							+ " FROM dblp_pub_new" // added in v0.2.0, before it was aux_dblp_proceedings
							+ " WHERE source IS NOT NULL AND "
							+ " type = 'proceedings'"; // changed in v0.2.0, before it was conference
			rs = stmt.executeQuery(query);
			answer = prepareAnswer(rs);
		} catch (SQLException e) {
			throw new ServletException("Error getting venues without search param", e);
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
	 * Returns the list of venues LIKE a specific search string
	 * 
	 * @param searchString
	 * @return
	 * @throws ServletException 
	 */
	private JsonArray getAllVenues(String searchString) throws ServletException {
		Connection con = Pooling.getInstance().getConnection();
		Statement stmt = null;
		ResultSet rs = null;
		JsonArray answer = new JsonArray();
		try {
			stmt = con.createStatement();
			String query = "SELECT DISTINCT source, title"
							+ " FROM dblp_pub_new" // changed in v0.2.0, before it was aux_dblp_proceedings
							+ " WHERE source IS NOT NULL AND "
							+ " type = 'proceedings' AND " // changed in v0.2.0, before it was conference
							+ " (source LIKE '%" + searchString + "%' OR title LIKE '%" + searchString + "%' ) ";
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
	 * Digest the ResultSet to create a JsonArray to be used as response
	 * 
	 * @param rs
	 * @return
	 * @throws ServletException 
	 */
	private JsonArray prepareAnswer(ResultSet rs) throws ServletException {
		JsonArray answer = new JsonArray();
		
		try {
			while(rs.next()) {
				JsonObject jsonObject = new JsonObject();
				String venue = rs.getString("source");
				String title = rs.getString("title");
				jsonObject.addProperty("name", venue.toUpperCase() + " - " + title);
				jsonObject.addProperty("id", venue);
				answer.add(jsonObject);
			}
		} catch (SQLException e) {
			throw new ServletException("Error retrieving the fields from the ResultSet", e);	
		}
		
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
