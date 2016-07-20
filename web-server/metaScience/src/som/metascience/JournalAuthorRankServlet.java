package som.metascience;

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

@WebServlet("/journalAuthorRank")
public class JournalAuthorRankServlet extends AbstractMetaScienceServlet {

	private static final long serialVersionUID = 1L;
	
	@Override
	protected void doGet(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
		addResponseOptions(resp);
		
		String journalId = req.getParameter(ID_PARAM);
		
		if(journalId == null) 
			throw new ServletException("The id cannot be null");
		
		JsonObject topAuthors = getTopAuthorForJournalId(journalId);
		JsonObject regularAuthors = getRegularAuthorForJournalId(journalId);
		
		JsonObject response = new JsonObject();
		response.add("top",topAuthors);
		response.add("regular",regularAuthors);

		resp.setContentType("text/x-json;charset=UTF-8");    
		PrintWriter pw = resp.getWriter();
		pw.append(response.toString());
	}
	
	private JsonObject getTopAuthorForJournalId(String journalId) throws ServletException {
		JsonObject topAuthors = new JsonObject();
		
		Connection con = Pooling.getInstance().getConnection();
		Statement stmt = null;
		ResultSet rs = null;
		
		try {
			String query = "SELECT r.id as author_id, r.name as author, COUNT(p.id) AS publications " +
						   "FROM journal j JOIN journal_issue ji " +
						   "ON j.id = ji.journal_id " +
						   "JOIN paper p on p.published_in = ji.id " +
						   "JOIN authorship a ON a.paper_id = p.id " +
						   "JOIN researcher r ON r.id = a.researcher_id " +
						   "WHERE acronym = '" + journalId + "' AND p.type = 2 " +
						   "GROUP BY r.id " +
						   "ORDER BY publications DESC " +
						   "LIMIT 5";
	
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
	
	private JsonObject getRegularAuthorForJournalId(String journalId) throws ServletException {
		JsonObject regularAuthors = new JsonObject();
		
		Connection con = Pooling.getInstance().getConnection();
		Statement stmt = null;
		ResultSet rs = null;
		
		try {
			String query = "SELECT r.id as author_id, r.name as author, COUNT(DISTINCT ji.year) AS presence " +
						   "FROM journal j JOIN journal_issue ji " +
						   "ON j.id = ji.journal_id " +
						   "JOIN paper p on p.published_in = ji.id " +
						   "JOIN authorship a ON a.paper_id = p.id " +
						   "JOIN researcher r ON r.id = a.researcher_id " +
						   "WHERE acronym = '" + journalId + "' AND p.type = 2 " +
						   "GROUP BY r.id " +
						   "ORDER BY presence DESC " +
						   "LIMIT 5";
	
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