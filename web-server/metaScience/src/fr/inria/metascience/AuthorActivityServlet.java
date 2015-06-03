package fr.inria.metascience;

import java.io.IOException;
import java.io.PrintWriter;
import java.sql.Connection;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import java.util.Map;
import java.util.TreeMap;

import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.google.gson.JsonPrimitive;

import fr.inria.metascience.elements.Publications;

@WebServlet("/authorActivity")
public class AuthorActivityServlet extends AbstractMetaScienceServlet {

	private static final long serialVersionUID = 1L;
	
	private int totalArticles = 0;
	private int totalBooks = 0;
	private int totalIncollections = 0;
	private int totalInproceedings = 0;
	private int totalMasterThesis = 0;
	private int totalPHDThesis = 0;
	private int totalProceedings = 0;
	private int totalWebsites = 0;
	
	private int numberOfYear = 0;

	@Override
	protected void doGet(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
		addResponseOptions(resp);
		
		totalArticles = 0;
		totalBooks = 0;
		totalIncollections = 0;
		totalInproceedings = 0;
		totalMasterThesis = 0;
		totalPHDThesis = 0;
		totalProceedings = 0;
		totalWebsites = 0;
		
		numberOfYear = 0;

		String authorId = req.getParameter(ID_PARAM);

		if(authorId == null) 
			throw new ServletException("The id cannot be null");

		//JsonObject response = testGetActivityForVenueId();
		JsonObject response = getActivityForAuthorId(authorId);

		resp.setContentType("text/x-json;charset=UTF-8");    
		PrintWriter pw = resp.getWriter();
		pw.append(response.toString());
	}
	
	private JsonObject getActivityForAuthorId(String authorId) throws ServletException {
		JsonObject result = new JsonObject();
		
		JsonObject publicationsInformation = getPublicationInformation(authorId);
		JsonObject publicationsTotals = getPublicationsTotals();
		//JsonObject collaborationInformation = getCollaborationInformation(authorId);
		
		result.add("pub", publicationsTotals);
		//result.add("collaborations",collaborationInformation);
		result.add("publications", publicationsInformation);
		
		return result;
		
	}
	
//	private JsonObject getCollaborationInformation(String authorId) throws ServletException {
//		JsonObject answer = new JsonObject();
//		
//		Connection con = Pooling.getInstance().getConnection();
//		Statement stmt = null;
//		ResultSet rs = null;
//		
//		try {
//			String query = "SELECT COUNT(*) AS collaborations, AVG(collaborators) AS average"
//					+ " FROM ("
//					+ " 	SELECT target_author_papers.id, COUNT(*) AS collaborators"
//					+ " 	FROM ("
//					+ "			SELECT id"
//					+ "			FROM dblp_authorid_ref_new airn"
//					+ "			WHERE airn.author_id = " + authorId
//					+ " 	) AS target_author_papers"
//					+ " 	JOIN ("
//					+ " 		SELECT id, author_id, author"
//					+ "			FROM dblp_authorid_ref_new airn"
//					+ "			WHERE airn.author_id <> " + authorId
//					+ " 	) AS connected_author_papers"
//					+ " 	ON target_author_papers.id = connected_author_papers.id"
//					+ " 	GROUP BY connected_author_papers.id"
//					+ " ) AS collaborations;";
//	
//	        stmt = con.createStatement();
//	        rs = stmt.executeQuery(query);
//	        
//	        int totalCollaborations = 0;
//        	double avgCollaborations = 0;
//	        if(rs.next()) {
//	        	totalCollaborations = rs.getInt("collaborations");
//	        	avgCollaborations = rs.getDouble("average");
//	        }
//	        
//	        answer.addProperty("total", totalCollaborations);
//	        answer.add("avg", new JsonPrimitive(avgCollaborations));
//		} catch (SQLException e) {
//			throw new ServletException("Error accesing the database", e);
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
//	}
	
	private JsonObject getPublicationsTotals() {
		JsonObject publicationsTotals = new JsonObject();
		
		int total = totalArticles + totalBooks + totalIncollections + totalInproceedings + totalMasterThesis + totalPHDThesis + totalProceedings + totalWebsites;
		double avgPublication = total / numberOfYear;
		
		publicationsTotals.addProperty("total", total);
		publicationsTotals.addProperty("totalArticles", totalArticles);
		publicationsTotals.addProperty("totalBooks", totalBooks);
		publicationsTotals.addProperty("totalIncollections", totalIncollections);
		publicationsTotals.addProperty("totalInproceedings", totalInproceedings);
		publicationsTotals.addProperty("totalMasterThesis", totalMasterThesis);
		publicationsTotals.addProperty("totalPHDThesis", totalPHDThesis);
		publicationsTotals.addProperty("totalProceedings", totalProceedings);
		publicationsTotals.addProperty("totalWebsites", totalWebsites);
		publicationsTotals.addProperty("avgPublications", avgPublication);
		
		return publicationsTotals;
	}
	
	private JsonObject getPublicationInformation(String authorId) throws ServletException {
		
		JsonObject answer = new JsonObject();
		
		Connection con = Pooling.getInstance().getConnection();
		Statement stmt = null;
		ResultSet rs = null;
		
		try {
			String query = "SELECT airn.author_id, airn.author, pub.year, pub.type, COUNT(pub.year) AS number"
							+ " FROM dblp_pub_new pub"
							+ " JOIN dblp_authorid_ref_new airn"
							+ " ON pub.id=airn.id"
							+ " WHERE airn.author_id = " + authorId
							+ " GROUP BY pub.year, pub.type;";
	
	        stmt = con.createStatement();
	        rs = stmt.executeQuery(query);
	        
	        answer = preparePublicationInformationJson(rs);
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
		return answer;
		
	}
	
	private JsonObject preparePublicationInformationJson(ResultSet rs) throws ServletException {
		JsonObject publicationsJson = new JsonObject();
		
		Map<Integer,Publications> yearPublicationsMap = new TreeMap<Integer,Publications>();
		
		try {
			while(rs.next()) {
				String publicationType = rs.getString("type");
				int publicationYear = rs.getInt("year");
				int publicationNumber = rs.getInt("number");
				
				Publications yearPublications = yearPublicationsMap.get(publicationYear);
				if(yearPublications == null) {
					numberOfYear++;
					yearPublications = new Publications(publicationYear);
					
					yearPublicationsMap.put(publicationYear, yearPublications);
				}
				setPublicationsType(yearPublications, publicationType, publicationNumber);
				
			}
			
			// Build year publications JsonArray
			publicationsJson = preparePublicationsForC3(yearPublicationsMap);
			
		} catch(SQLException e) {
			throw new ServletException("Error retrieving publication information field from ResultSet",e);
		}
		
		return publicationsJson;
	}
	
	private JsonObject preparePublicationsForC3(Map<Integer,Publications> publications) {
		JsonObject publicationsJson = new JsonObject();
		
		JsonArray publicationYears = new JsonArray();
		JsonArray publicationArticle = new JsonArray();
		publicationArticle.add(new JsonPrimitive("Articles"));
		JsonArray publicationBook = new JsonArray();
		publicationBook.add(new JsonPrimitive("Books"));
		JsonArray publicationIncollection = new JsonArray();
		publicationIncollection.add(new JsonPrimitive("Incollections"));
		JsonArray publicationInproceedings = new JsonArray();
		publicationInproceedings.add(new JsonPrimitive("Inproceedings"));
		JsonArray publicationMasterThesis = new JsonArray();
		publicationMasterThesis.add(new JsonPrimitive("Master Thesis"));
		JsonArray publicationPHDThesis = new JsonArray();
		publicationPHDThesis.add(new JsonPrimitive("Phd Thesis"));
		JsonArray publicationProceedings = new JsonArray();
		publicationProceedings.add(new JsonPrimitive("Proceedings"));
		JsonArray publicationWebsites = new JsonArray();
		publicationWebsites.add(new JsonPrimitive("Websites"));
		
		for(Integer year : publications.keySet()) {
			Publications pub = publications.get(year);
			publicationYears.add(new JsonPrimitive(year));
			
			publicationArticle.add(new JsonPrimitive(pub.getArticles()));
			publicationBook.add(new JsonPrimitive(pub.getBooks()));
			publicationIncollection.add(new JsonPrimitive(pub.getIncollections()));
			publicationInproceedings.add(new JsonPrimitive(pub.getInproceedings()));
			publicationMasterThesis.add(new JsonPrimitive(pub.getMasterthesis()));
			publicationPHDThesis.add(new JsonPrimitive(pub.getPhdthesis()));
			publicationProceedings.add(new JsonPrimitive(pub.getProceedings()));
			publicationWebsites.add(new JsonPrimitive(pub.getWebsites()));
			
		}
		
		publicationsJson.add("years", publicationYears);
		publicationsJson.add("articles",publicationArticle);
		publicationsJson.add("books",publicationBook);
		publicationsJson.add("incollections",publicationIncollection);
		publicationsJson.add("inproceedings",publicationInproceedings);
		publicationsJson.add("masterThesis",publicationMasterThesis);
		publicationsJson.add("phdThesis",publicationPHDThesis);
		publicationsJson.add("proceedings",publicationProceedings);
		publicationsJson.add("websites",publicationWebsites);
		
		return publicationsJson;
	}
	
	private void setPublicationsType(Publications yearPublications, String publicationType, int publicationCount) {
		if(publicationType.equals("article")) {
			yearPublications.setArticles(publicationCount);
			totalArticles += publicationCount;
		} else if(publicationType.equals("book")) {
			yearPublications.setBooks(publicationCount);
			totalBooks += publicationCount;
		} else if(publicationType.equals("incollection")) {
			yearPublications.setIncollections(publicationCount);
			totalIncollections += publicationCount;
		} else if(publicationType.equals("inproceedings")) {
			yearPublications.setInproceedings(publicationCount);
			totalInproceedings += publicationCount;
		} else if(publicationType.equals("masterthesis")) {
			yearPublications.setMasterthesis(publicationCount);
			totalMasterThesis += publicationCount;
		} else if(publicationType.equals("phdthesis")) {
			yearPublications.setPhdthesis(publicationCount);
			totalPHDThesis += publicationCount;
		} else if(publicationType.equals("proceedings")) {
			yearPublications.setProceedings(publicationCount);
			totalProceedings += publicationCount;
		} else if(publicationType.equals("www")) {
			yearPublications.setWebsites(publicationCount);
			totalWebsites += publicationCount;
		} else {
			//No corresponding type
		}
	}
	
}
