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


@WebServlet("/authors")
public class AuthorServlet extends AbstractMetaScienceServlet {

	private static final String SEARCH_PARAM = "search";
	
	private static final long serialVersionUID = 1L;
	
	private final static Logger LOGGER = Logger.getLogger(AuthorServlet.class.getName());
	
	@Override
	protected void doGet(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
		addResponseOptions(resp);
		
		String searchString = req.getParameter(SEARCH_PARAM);
		
		System.out.println("search param : " + searchString);
		
		JsonArray authors = new JsonArray();
		
		if(searchString != null && !searchString.isEmpty()) {
			authors = this.getAllAuthors(searchString);
		}
		
		//Building the response
		JsonObject response = new JsonObject();
		response.add("authors", authors);
		PrintWriter pw = resp.getWriter();
		pw.append(authors.toString());
		
	}
	
	private JsonArray getAllAuthors() throws ServletException {
		Connection con = Pooling.getInstance().getConnection();
		Statement stmt = null;
		ResultSet rs = null;
		JsonArray answer = new JsonArray();
		try {
			stmt = con.createStatement();
			String query = "SELECT author_id, author"
							+ " FROM dblp_main_aliases_new"
							+ " WHERE author IS NOT NULL";
			rs = stmt.executeQuery(query);
			answer = prepareAnswer(rs);
		} catch( SQLException e) {
			throw new ServletException("Error getting author withour search param", e);
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
	
	private JsonArray getAllAuthors(String searchString) throws ServletException {
		Connection con = Pooling.getInstance().getConnection();
		Statement stmt = null;
		ResultSet rs = null;
		JsonArray answer = new JsonArray();
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
	
	private JsonArray prepareAnswer(ResultSet rs) throws ServletException {
		JsonArray answer = new JsonArray();
		
		try {
			while(rs.next()) {
				JsonObject jsonObject = new JsonObject();
				String authorName = rs.getString("author");
				String authorId = rs.getString("author_id");
				jsonObject.addProperty("authorName", authorName);
				jsonObject.addProperty("authorId",authorId);
				answer.add(jsonObject);
			}
		} catch (SQLException e) {
			throw new ServletException("Error retrieving the fields from the ResultSet", e);
		}
		return answer;
	}
	

}
