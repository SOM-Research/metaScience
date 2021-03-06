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

import com.google.gson.JsonArray;
import com.google.gson.JsonObject;

@WebServlet("/conferenceConnection")
public class AuthorConferenceAttendanceServlet extends AbstractMetaScienceServlet {

	private static final long serialVersionUID = 1L;
	
	private int total_attendance;
	private int max_attendance;
	private int total_publications;
	private int max_publications;
	private int average_attendance;
	private int average_publications;
	
	@Override
	protected void doGet(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
		addResponseOptions(resp);
		
		String authorId = req.getParameter(ID_PARAM);
		
		total_attendance = 0;
		total_publications = 0;
		max_attendance = 0;
		max_publications = 0;
		average_attendance = 0;
		average_publications = 0;
		
		if(authorId == null) 
			throw new ServletException("The id cannot be null");
		
		JsonObject response = getAuthorConferenceConnection(authorId);
	
		resp.setContentType("text/x-json;charset=UTF-8");    
		PrintWriter pw = resp.getWriter();
		pw.append(response.toString());
	}
	
	private JsonObject getAuthorConferenceConnection(String authorId) throws ServletException {
		JsonObject result = new JsonObject();
		
		// get author conferences 
		JsonArray conferences = getAuthorConferences(authorId);
		
		// get author information
		
		JsonObject author = getAuthorInformation(authorId);
		
		result.add("author", author);
		result.add("conferences", conferences);
		
		return result;
	}
	
	private JsonObject getAuthorInformation(String authorId) throws ServletException {
		Connection con = Pooling.getInstance().getConnection();
		Statement stmt = null;
		ResultSet rs = null;
		JsonObject answer = new JsonObject();
		try {
			stmt = con.createStatement();
			String query = "SELECT id as author_id, name as author " +
						   "FROM researcher r " +
						   "WHERE id =" + authorId;
			rs = stmt.executeQuery(query);
			answer = prepareAuthorInformationJson(rs);
		} catch( SQLException e) {
			throw new ServletException("Error getting author information", e);
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
	
	private JsonArray getAuthorConferences(String authorId) throws ServletException {
		Connection con = Pooling.getInstance().getConnection();
		Statement stmt = null;
		ResultSet rs = null;
		JsonArray answer = new JsonArray();
		try {
			stmt = con.createStatement();
			String query =  "SELECT acronym as source, COUNT(DISTINCT year) AS attendance, COUNT(*) AS publications, pt.name AS type " +
							"FROM ( " +
							"SELECT c.acronym, ce.year, p.id, p.type " +
							"FROM authorship a JOIN paper p ON a.paper_id = p.id JOIN conference_edition ce ON ce.id = p.published_in JOIN conference c ON c.id = ce.conference_id " +
							"WHERE a.researcher_id = " + authorId + " AND p.type = 1 " +
							"UNION " +
							"SELECT j.acronym, ji.year, p.id, p.type " +
							"FROM authorship a JOIN paper p ON a.paper_id = p.id JOIN journal_issue ji ON ji.id = p.published_in JOIN journal j ON j.id = ji.journal_id " +
							"WHERE a.researcher_id = " + authorId + " AND p.type = 2) AS publications " +
							"JOIN paper_type pt ON pt.id = type " +
							"GROUP BY acronym";	
			rs = stmt.executeQuery(query);
			answer = prepareAuthorConferenceJSon(rs);
		} catch( SQLException e) {
			throw new ServletException("Error getting author information", e);
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
	
	private JsonObject prepareAuthorInformationJson(ResultSet rs) throws ServletException {
		JsonObject author = new JsonObject();
		
		try {
			while(rs.next()) {
				String authorId = rs.getString("author_id");
				String authorName = rs.getString("author");
				
				author.addProperty("id", authorId);
				author.addProperty("name", authorName);
				author.addProperty("total_attendance", total_attendance);
				author.addProperty("max_attendance", max_attendance);
				author.addProperty("total_publications", total_publications);
				author.addProperty("max_publications", max_publications);
			}
		} catch(SQLException e) {
			throw new ServletException("Error retrieving author information fields from ResultSet",e);
		}
		return author;
		
	}
	
	private JsonArray prepareAuthorConferenceJSon(ResultSet rs) throws ServletException {
		JsonArray conferences = new JsonArray();
		
		try {
			while(rs.next()) {
				JsonObject conferenceObject = new JsonObject();
				
				String conferenceSource = rs.getString("source");
				Integer numAttendance = rs.getInt("attendance");
				Integer numPublications = rs.getInt("publications");
				String type = rs.getString("type");
				total_attendance += numAttendance;
				total_publications += numPublications;
				if(numAttendance > max_attendance) {
					max_attendance = numAttendance;
				}
				if(numPublications > max_publications) {
					max_publications = numPublications;
				}
				
				conferenceObject.addProperty("source", conferenceSource);
				conferenceObject.addProperty("attendance", numAttendance);
				conferenceObject.addProperty("publications", numPublications);
				conferenceObject.addProperty("type", type);
				conferences.add(conferenceObject);
				
			}
		} catch(SQLException e) {
			throw new ServletException("Error retrieving author conferences field from the ResultSet", e);
		}
		return conferences;
	}
	

}
