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


@WebServlet("/authors")
public class AuthorServlet extends AbstractMetaScienceServlet {

	private static final String SEARCH_PARAM = "search";
	private static final String REQUEST_TYPE = "type";
	
	private static final long serialVersionUID = 1L;
	
	private final static Logger LOGGER = Logger.getLogger(AuthorServlet.class.getName());
	
	@Override
	protected void doGet(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
		addResponseOptions(resp);
		
		String searchString = new String(req.getParameter(SEARCH_PARAM).getBytes("iso-8859-1"),"utf-8");
		String requestType = req.getParameter(REQUEST_TYPE);
		
		JsonObject response = new JsonObject();
		
		if(searchString != null && !searchString.isEmpty()) {
			if(requestType.equals("1")) {
				response = this.getAllAuthors(searchString);
			} else if(requestType.equals("2")) {
				response = this.getAuthorByName(searchString);
			} else {
				throw new ServletException("Request Parameter Error");
			}
		}
		
		//Building the response
		resp.setContentType("application/json");
		PrintWriter pw = resp.getWriter();
		pw.append(response.toString());
		
	}
	
//	private JsonArray getAllAuthors() throws ServletException {
//		Connection con = Pooling.getInstance().getConnection();
//		Statement stmt = null;
//		ResultSet rs = null;
//		JsonArray answer = new JsonArray();
//		try {
//			stmt = con.createStatement();
//			String query = "SELECT author_id, author"
//							+ " FROM dblp_main_aliases_new"
//							+ " WHERE author IS NOT NULL";
//			rs = stmt.executeQuery(query);
//			answer = prepareAnswer(rs);
//		} catch( SQLException e) {
//			throw new ServletException("Error getting author withour search param", e);
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
//		
//	}
	
	private JsonObject getAllAuthors(String searchString) throws ServletException {
		Connection con = Pooling.getInstance().getConnection();
		Statement stmt = null;
		ResultSet rs = null;
		JsonObject answer = new JsonObject();
		try {
			stmt = con.createStatement();
			String query = "SELECT author_id, author"
							+ " FROM dblp_main_aliases_new"
							+ " WHERE author IS NOT NULL AND"
							+ " (author LIKE '%" + searchString + "%')";
			rs = stmt.executeQuery(query);
			answer = prepareAnswer(rs);
		} catch( SQLException e) {
			throw new ServletException("Error getting author with search param : " + searchString, e);
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
	
	private JsonObject getAuthorByName(String searchString) throws ServletException {
		Connection con = Pooling.getInstance().getConnection();
		Statement stmt = null;
		ResultSet rs = null;
		JsonObject answer = new JsonObject();
		try {
			stmt = con.createStatement();
			String query = "SELECT author_id, author"
							+ " FROM dblp_main_aliases_new"
							+ " WHERE author IS NOT NULL AND"
							+ " (author LIKE '" + searchString + "')";
			rs = stmt.executeQuery(query);
			answer = prepareAnswer(rs);
		} catch( SQLException e) {
			throw new ServletException("Error getting author with search param : " + searchString, e);
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
	
	private JsonObject prepareAnswer(ResultSet rs) throws ServletException {
		JsonObject answer = new JsonObject();
		
		JsonArray authors = new JsonArray();
		int resultCount = 0;
		try {
			while(rs.next()) {
				resultCount++;
				JsonObject jsonObject = new JsonObject();
				String authorName = rs.getString("author");
				String authorId = rs.getString("author_id");
				jsonObject.addProperty("authorName", authorName);
				jsonObject.addProperty("authorId",authorId);
				authors.add(jsonObject);
			}
		} catch (SQLException e) {
			throw new ServletException("Error retrieving the fields from the ResultSet", e);
		}
		
		answer.addProperty("count", resultCount);
		answer.add("authors", authors);
		
		return answer;
	}
	

}
