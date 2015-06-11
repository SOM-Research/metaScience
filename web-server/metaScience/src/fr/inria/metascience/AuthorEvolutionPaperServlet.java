package fr.inria.metascience;

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
import com.google.gson.JsonPrimitive;

@WebServlet("/paperEvolution")
public class AuthorEvolutionPaperServlet extends AbstractMetaScienceServlet {
	
	private static final long serialVersionUID = 1L;

	@Override
	protected void doGet(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
		addResponseOptions(resp);

		String authorId = req.getParameter(ID_PARAM);

		if(authorId == null) 
			throw new ServletException("The id cannot be null");

		JsonObject response = getPaperEvolutionInformation(authorId);

		resp.setContentType("text/x-json;charset=UTF-8");    
		PrintWriter pw = resp.getWriter();
		pw.append(response.toString());
	}
	
	private JsonObject getPaperEvolutionInformation(String authorId) throws ServletException {
		JsonObject paperInformationJson = new JsonObject();
		
		JsonObject pagesInformationJson = getPagesInformation(authorId);
		JsonObject coAuthorInformationJson = getCoAuthorInformation(authorId);
		
		paperInformationJson.add("coAuthors", coAuthorInformationJson);
		paperInformationJson.add("pages",pagesInformationJson);
		
		return paperInformationJson;
	}
	
	private JsonObject getPagesInformation(String authorId) throws ServletException {
		JsonObject pagesInformationJson = new JsonObject();
		
		Connection con = Pooling.getInstance().getConnection();
		Statement stmt = null;
		ResultSet rs = null;
		try {
			stmt = con.createStatement();
			String query = "SELECT author_id, author, SUM(pages) AS total_pages, year, ROUND(AVG(pages/authors),2) AS avg_owned_pages"
						+ "	FROM ("
						+ "		SELECT pub.id, pub.year, title, airn.author_id, airn.author, calculate_num_of_pages(pages) AS pages, MAX(author_num) + 1 AS authors"
						+ "		FROM dblp_pub_new pub"
						+ "		JOIN dblp_authorid_ref_new airn"
						+ "		ON pub.id = airn.id"
						+ "		JOIN dblp_author_ref_new arn"
						+ "		ON pub.id = arn.id"
						+ "		WHERE airn.author_id = " + authorId
						+ "		AND pages IS NOT NULL"
						+ "		GROUP BY pub.id"
						+ "	) AS pub_info"
						+ "	GROUP BY pub_info.year;";
			rs = stmt.executeQuery(query);
			pagesInformationJson = preparePagesInformation(rs);
		} catch( SQLException e) {
			throw new ServletException("Error getting pages information", e);
		} finally {
			try {
				if(stmt != null) stmt.close();
				if(rs != null) rs.close();
				if(con != null) con.close();
			} catch (SQLException e) {
				throw new ServletException("Impossible to close the connection", e);
			}
		}
		return pagesInformationJson;
		
	}
	
	private JsonObject getCoAuthorInformation(String authorId) throws ServletException {
		JsonObject coAuthorInformationJson = new JsonObject();
		
		Connection con = Pooling.getInstance().getConnection();
		Statement stmt = null;
		ResultSet rs = null;
		try {
			stmt = con.createStatement();
			String query = "SELECT author_id, author, SUM(coauthors) AS number_coAuthors, year"
						+ "	FROM ("
						+ "		SELECT pub.id, pub.year, title, airn.author_id, airn.author, IF(MAX(author_num) + 1 = 1, 0, MAX(author_num)) AS coauthors"
						+ "		FROM dblp_pub_new pub"
						+ "		JOIN dblp_authorid_ref_new airn"
						+ "		ON pub.id = airn.id"
						+ "		JOIN dblp_author_ref_new arn"
						+ "		ON pub.id = arn.id"
						+ "		WHERE airn.author_id = " + authorId
						+ "		AND pages IS NOT NULL"
						+ "		GROUP BY pub.id"
						+ "	) AS pub_info"
						+ "	GROUP BY pub_info.year;";
			rs = stmt.executeQuery(query);
			coAuthorInformationJson = prepareCoAuthorInformation(rs);
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
		return coAuthorInformationJson;
	}
	
	private JsonObject preparePagesInformation(ResultSet rs) throws ServletException {
		JsonObject pages = new JsonObject();
		
		try {
			JsonArray years = new JsonArray();
			JsonArray average = new JsonArray();
			average.add(new JsonPrimitive("average"));
			
			while(rs.next()) {
				String authorId = rs.getString("author_id");
				String authorName = rs.getString("author");
				int authorTotalPages = rs.getInt("total_pages");
				int year = rs.getInt("year");
				double averageOwnedPages = rs.getDouble("avg_owned_pages");
				
				years.add(new JsonPrimitive(year));
				average.add(new JsonPrimitive(averageOwnedPages));
			}
			
			pages.add("years",years);
			pages.add("averagePages",average);
		} catch(SQLException e) {
			throw new ServletException("Error retrieving author information fields from ResultSet",e);
		}
		return pages;
	}
	
	private JsonObject prepareCoAuthorInformation(ResultSet rs) throws ServletException {
		JsonObject coAuthors = new JsonObject();
		
		try {
			JsonArray years = new JsonArray();
			JsonArray coAuthorsNumbers = new JsonArray();
			coAuthorsNumbers.add(new JsonPrimitive("num_coAuthors"));
			
			while(rs.next()) {
				String authorId = rs.getString("author_id");
				String authorName = rs.getString("author");
				int authorCoAuthorNumber = rs.getInt("number_coAuthors");
				int year = rs.getInt("year");
				
				years.add(new JsonPrimitive(year));
				
				coAuthorsNumbers.add(new JsonPrimitive(authorCoAuthorNumber));
			}
			
			coAuthors.add("years", years);
			coAuthors.add("num_coAuthors", coAuthorsNumbers);
		} catch(SQLException e) {
			throw new ServletException("Error retrieving co author evolution information fields from ResultSet",e);
		}
		return coAuthors;
	}

}