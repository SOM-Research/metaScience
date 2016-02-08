package som.metascience;

import java.io.IOException;
import java.io.PrintWriter;
import java.sql.Connection;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import java.util.HashSet;
import java.util.Locale;
import java.util.Set;

import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import com.google.gson.JsonArray;
import com.google.gson.JsonObject;


@WebServlet("/coAuthorConnection")
public class AuthorCoAuthorConnectionServlet extends AbstractMetaScienceServlet {

	private static final long serialVersionUID = 1L;
	
	private int total_collaborations;
	private int total_collaborators;
	private int max_collaborations;
	private double avg_collaborations;
	
	@Override
	protected void doGet(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
		addResponseOptions(resp);
		
		String authorId = req.getParameter(ID_PARAM);
		
		total_collaborations = 0;
		total_collaborators = 0;
		max_collaborations = 0;
		avg_collaborations = 0;
		
		if(authorId == null) {
			throw new ServletException("The id can not be null");
		}
		
		JsonObject response = getCoAuthorConnectionsForAuthorId(authorId);
		//JsonObject response = test();
		
		resp.setContentType("text/x-json;charset=UTF-8");
		PrintWriter pw = resp.getWriter();
		pw.append(response.toString());
		
	}
	
	private JsonObject getCoAuthorConnectionsForAuthorId(String authorId) throws ServletException {
		JsonObject result = new JsonObject();
		
		// Get collaboration first to be able to calculate maximum
		// collaboration number and total number of collaborations
		JsonArray collaborations = getAuthorCollaborations(authorId);
		JsonObject author = getAuthorInformation(authorId);
		
		result.add("author",author);
		result.add("coAuthors", collaborations);
		
		return result;
	}
	
	private JsonObject getAuthorInformation(String authorId) throws ServletException {
		Connection con = Pooling.getInstance().getConnection();
		Statement stmt = null;
		ResultSet rs = null;
		JsonObject answer = new JsonObject();
		try {
			stmt = con.createStatement();
			String query = "SELECT author_id, author"
							+ " FROM dblp_main_aliases_new"
							+ " WHERE author_id = " + authorId;
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
	
	private JsonArray getAuthorCollaborations(String authorId) throws ServletException {
		Connection con = Pooling.getInstance().getConnection();
		Statement stmt = null;
		ResultSet rs = null;
		JsonArray answer = new JsonArray();
		try {
			stmt = con.createStatement();
			String query = "SELECT connected_author_papers.author_id, connected_author_papers.author, COUNT(*) AS relation_strength"
							+ " FROM ("
							+ 	" SELECT id "
							+ 	" FROM dblp_authorid_ref_new airn"
							+ 	" WHERE airn.author_id = " + authorId
							+	") AS target_author_papers"
							+ " JOIN ("
							+ 	" SELECT id, author_id, author"
							+	" FROM dblp_authorid_ref_new airn"
							+	" WHERE airn.author_id <> " + authorId
							+	") AS connected_author_papers"
							+ " ON target_author_papers.id = connected_author_papers.id"
							+ " GROUP BY connected_author_papers.author_id;";

			rs = stmt.executeQuery(query);
			if (rs != null)
				answer = prepareCollaborationJson(rs);
			else
				System.out.println("No CoAuthor connection info! This is strange...");
		} catch( SQLException e) {
			throw new ServletException("Error getting author collaborations", e);
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
				author.addProperty("total_collaborations", total_collaborations);
				author.addProperty("max_collaborations", max_collaborations);
				author.addProperty("total_collaborators", total_collaborators);
				String avg_collaborationsString = String.format(Locale.US, "%.2f", avg_collaborations); // Issue #8
				author.addProperty("average_collaborations", avg_collaborationsString);
			}
		} catch(SQLException e) {
			throw new ServletException("Error retrieving author information fields from ResultSet",e);
		}
		return author;
		
	}
	
	private JsonArray prepareCollaborationJson(ResultSet rs) throws ServletException {
		JsonArray collaborations = new JsonArray();
		
		Set<String> uniqueCoAuthors = new HashSet<String>();
		try {
			while(rs.next()) {
				JsonObject coAuthorObject = new JsonObject();
				
				String coAuthorId = rs.getString("author_id");
				String coAuthorName = rs.getString("author");
				Integer numCollaborations = rs.getInt("relation_strength");
				
				uniqueCoAuthors.add(coAuthorId);
				total_collaborations += numCollaborations;
				if(numCollaborations > max_collaborations) {
					max_collaborations = numCollaborations;
				}
				
				coAuthorObject.addProperty("id", coAuthorId);
				coAuthorObject.addProperty("name", coAuthorName);
				coAuthorObject.addProperty("num_collaborations", numCollaborations);
				collaborations.add(coAuthorObject);
				
			}

			total_collaborators = uniqueCoAuthors.size();
			
			avg_collaborations =  (double)total_collaborations/(double)total_collaborators;
		} catch(SQLException e) {
			throw new ServletException("Error retrieving collaboration field from the ResultSet", e);
		}
		return collaborations;
	}
	
	private JsonObject test() {
		JsonObject result = new JsonObject();
		
		//author
		JsonObject author = new JsonObject();
		author.addProperty("id", 12);
		author.addProperty("name", "Test Author");
		author.addProperty("max_collaborations", 10);
		
		JsonArray coAuthors = new JsonArray();
		JsonObject coAuth1 = new JsonObject();
		coAuth1.addProperty("id", 14);
		coAuth1.addProperty("name", "Co Auth 1");
		coAuth1.addProperty("num_collaborations", 3);
		coAuthors.add(coAuth1);
		
		JsonObject coAuth2 = new JsonObject();
		coAuth2.addProperty("id", 56);
		coAuth2.addProperty("name", "Co Auth2");
		coAuth2.addProperty("num_collaborations", 1);
		coAuthors.add(coAuth2);
		
		JsonObject coAuth3 = new JsonObject();
		coAuth3.addProperty("id", 8338);
		coAuth3.addProperty("name", "Co Auth 3");
		coAuth3.addProperty("num_collaborations", 10);
		coAuthors.add(coAuth3);
		
		result.add("author",author);
		result.add("coAuthors", coAuthors);
		
		return result;
	}

}
