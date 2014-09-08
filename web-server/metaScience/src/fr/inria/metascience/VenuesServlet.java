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
 *
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
		
		if(searchString != null) {
			// TODO Ask the database to retrieve those venues LIKE searchString
			venues = this.prepareAnswer(this.getAllVenues(searchString));
			LOGGER.info("Asked for venues with search string: " + searchString);
			test(venues);
		} else {
			// TODO Ask the database to retrieve ALL the venues (no search param)
			venues = this.prepareAnswer(this.getAllVenues());
			LOGGER.info("Asked for venues without search string");
			test(venues);
		}
		
		// Building the response
		JsonObject response = new JsonObject();
		response.add("venues", venues);
		PrintWriter pw = resp.getWriter();
		pw.append(venues.toString());
	}
	
	private ResultSet getAllVenues() {
		Connection con = Pooling.getInstance().getConnection();
		Statement stmt = null;
		ResultSet rs = null;
		try {
			stmt = con.createStatement();
			String query = "select title, source"
							+ " from dblp_pub_new"
							+ " where source is not null";
			rs = stmt.executeQuery(query);
		} 
		catch (SQLException e) {
			e.printStackTrace();		
		} finally {
			try {
				stmt.close();
				rs.close();
			}
			catch (SQLException e) {
				e.printStackTrace();
			}
		}
		
		return rs;
	}
	
	private ResultSet getAllVenues(String searchString) {
		Connection con = Pooling.getInstance().getConnection();
		Statement stmt = null;
		ResultSet rs = null;
		try {
			stmt = con.createStatement();
			String query = "SELECT title, source"
							+ " FROM dblp_pub_new"
							+ " WHERE source IS NOT NULL AND type = 'proceedings' AND"
							+ " title LIKE '%" + searchString + "%' OR source LIKE '%" + searchString + "%'";
			rs = stmt.executeQuery(query);
		} 
		catch (SQLException e) {
			e.printStackTrace();		
		} finally {
			try {
				stmt.close();
				rs.close();
			}
			catch (SQLException e) {
				e.printStackTrace();
			}
		}
		
		return rs;
	}
	
	private JsonArray prepareAnswer(ResultSet rs) {
		JsonArray answer = null;
		
		try {
			while(rs.next()) {
				String venue = rs.getString("source") + " - " + rs.getString("title");
				
			}
		} catch (SQLException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
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
