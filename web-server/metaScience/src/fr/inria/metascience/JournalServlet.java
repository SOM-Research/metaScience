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

@WebServlet("/journals")
public class JournalServlet extends AbstractMetaScienceServlet{
	private static final String SEARCH_PARAM = "search";
	
	private static final long serialVersionUID = 1L;

	private final static Logger LOGGER = Logger.getLogger(VenuesServlet.class.getName()); 

	@Override
	protected void doGet(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
		addResponseOptions(resp);
		
		// Obtains the search param
		String searchString = req.getParameter(SEARCH_PARAM);

		// This list contains the list of JSON object representing venues
		JsonArray journals = new JsonArray();
		
		if(searchString != null && !searchString.isEmpty()) {
			// TODO Ask the database to retrieve those venues LIKE searchString
			journals = this.getAllJournals(searchString);
		} /*else {
			// TODO Ask the database to retrieve ALL the venues (no search param)
			venues = this.getAllVenues();
		}*/
		
		// Building the response
		JsonObject response = new JsonObject();
		response.add("journals", journals);
		PrintWriter pw = resp.getWriter();
		pw.append(response.toString());
	}
	
	/**
	 * Returns the list of venues LIKE a specific search string
	 * 
	 * @param searchString
	 * @return
	 * @throws ServletException 
	 */
	private JsonArray getAllJournals(String searchString) throws ServletException {
		Connection con = Pooling.getInstance().getConnection();
		Statement stmt = null;
		ResultSet rs = null;
		JsonArray answer = new JsonArray();
		try {
			stmt = con.createStatement();
			String query = "SELECT source"
							+ " FROM dblp_pub_new"
							+ " WHERE source IS NOT NULL AND"
							+ " type = 'article' AND "
							+ " source LIKE '%" + searchString + "%'"
							+ " GROUP BY source;";
			rs = stmt.executeQuery(query);
			answer = prepareAnswer(rs);
		} catch (SQLException e) {
			throw new ServletException("Error getting journals with search param", e);	
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
				String journal = rs.getString("source");
				jsonObject.addProperty("journalName", journal.toUpperCase());
				jsonObject.addProperty("journalId", journal);
				answer.add(jsonObject);
			}
		} catch (SQLException e) {
			throw new ServletException("Error retrieving the fields from the ResultSet", e);	
		}
		
		return answer;
	}
}
