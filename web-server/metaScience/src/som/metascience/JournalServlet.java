package som.metascience;

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
	private static final String REQUEST_TYPE = "type";
	
	private static final long serialVersionUID = 1L;

	private final static Logger LOGGER = Logger.getLogger(JournalServlet.class.getName()); 

	@Override
	protected void doGet(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
		addResponseOptions(resp);
		
		String searchString = new String(req.getParameter(SEARCH_PARAM).getBytes("iso-8859-1"),"utf-8");
		String requestType = req.getParameter(REQUEST_TYPE);

		JsonObject response = new JsonObject();		
		
		if(searchString != null && !searchString.isEmpty() && requestType != null) {
			if(requestType.equals("1")) {
				response = this.getAllJournals(searchString);
			} else if(requestType.equals("2")) {
				response = this.getJournalByName(searchString);
			} else {
				throw new ServletException("Request Parameter Error");
			}
		}
		
		//Building the response
		resp.setContentType("application/json");
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
	private JsonObject getAllJournals(String searchString) throws ServletException {
		Connection con = Pooling.getInstance().getConnection();
		Statement stmt = null;
		ResultSet rs = null;
		JsonObject answer = new JsonObject();
		try {
			stmt = con.createStatement();
			String query = "SELECT source, source_id"
							+ " FROM dblp_pub_new"
							+ " WHERE source IS NOT NULL AND"
							+ " type = 'article' AND "
							+ " (source LIKE '%" + searchString + "%' OR source_id LIKE '%" + searchString + "%' ) "
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
	
	private JsonObject getJournalByName(String searchString) throws ServletException {
		Connection con = Pooling.getInstance().getConnection();
		Statement stmt = null;
		ResultSet rs = null;
		JsonObject answer = new JsonObject();
		try {
			stmt = con.createStatement();
			String query = "SELECT source, source_id"
					+ " FROM dblp_pub_new"
					+ " WHERE source IS NOT NULL AND"
					+ " type = 'article' AND "
					+ " (source LIKE '" + searchString + "' OR source_id LIKE '" + searchString + "' )"
					+ " GROUP BY source;";
			rs = stmt.executeQuery(query);
			answer = prepareAnswer(rs);
		} catch( SQLException e) {
			throw new ServletException("Error getting journal with search param : " + searchString, e);
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
	private JsonObject prepareAnswer(ResultSet rs) throws ServletException {
		JsonObject answer = new JsonObject();
		
		JsonArray journals = new JsonArray();
		int resultCount = 0;
		
		try {
			while(rs.next()) {
				resultCount++;
				JsonObject jsonObject = new JsonObject();
				String journal = rs.getString("source");
				String journalId = rs.getString("source_id");
				if(journalId == null) journalId = "";
				jsonObject.addProperty("journalName", journalId.toUpperCase() + " - " + journal);
				jsonObject.addProperty("journalId", journal);
				journals.add(jsonObject);
			}
		} catch (SQLException e) {
			throw new ServletException("Error retrieving the fields from the ResultSet", e);	
		}
		
		answer.addProperty("count", resultCount);
		answer.add("journals", journals);
		
		return answer;
	}
}
