package som.metascience;

import java.io.IOException;
import java.io.PrintWriter;
import java.sql.Connection;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import java.util.Locale;
import java.util.Map;
import java.util.TreeMap;

import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.google.gson.JsonPrimitive;

import som.metascience.elements.Publications;

/**
 * This servlet returns the activity for an author
 *
 * The current mapping between DBLP paper types and metaScience is:
 *   article -> journal paper
 *   proceedings -> editor
 *   book -> book
 *   incollection -> part of book or collection
 *   inproceeding -> conference paper
 *   phd thesis, master thesis and website -> others
 *
 */
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

		JsonObject response = getActivityForAuthorId(authorId);

		resp.setContentType("text/x-json;charset=UTF-8");    
		PrintWriter pw = resp.getWriter();
		pw.append(response.toString());
	}
	
	private JsonObject getActivityForAuthorId(String authorId) throws ServletException {
		JsonObject result = new JsonObject();
		
		JsonObject publicationsInformation = getPublicationInformation(authorId);
		JsonObject publicationsTotals = getPublicationsTotals();
		
		result.add("pub", publicationsTotals);
		result.add("publications", publicationsInformation);
		
		return result;
		
	}
	
	private JsonObject getPublicationsTotals() {
		JsonObject publicationsTotals = new JsonObject();
		
		int total = totalArticles + totalBooks + totalIncollections + totalInproceedings + totalMasterThesis + totalPHDThesis + totalProceedings + totalWebsites;
		double avgPublication = (double) total / (double) numberOfYear;
		String avgPublicationString = String.format(Locale.US, "%.2f", avgPublication); // Issue #8
		
		publicationsTotals.addProperty("total", total);
		publicationsTotals.addProperty("totalArticles", totalArticles);
		publicationsTotals.addProperty("totalBooks", totalBooks);
		publicationsTotals.addProperty("totalIncollections", totalIncollections);
		publicationsTotals.addProperty("totalInproceedings", totalInproceedings);
		publicationsTotals.addProperty("totalMasterThesis", totalMasterThesis);
		publicationsTotals.addProperty("totalOthers", totalPHDThesis+totalMasterThesis+totalWebsites); // Issue #15
		publicationsTotals.addProperty("totalPHDThesis", totalPHDThesis);
		publicationsTotals.addProperty("totalProceedings", totalProceedings);
		publicationsTotals.addProperty("totalWebsites", totalWebsites);
		publicationsTotals.addProperty("avgPublications", avgPublicationString);
		
		return publicationsTotals;
	}
	
	private JsonObject getPublicationInformation(String authorId) throws ServletException {
		
		JsonObject answer = new JsonObject();
		
		Connection con = Pooling.getInstance().getConnection();
		Statement stmt = null;
		ResultSet rs = null;
		
		try {
			String query = "SELECT airn.author_id, airn.author, pub.year, pub.type, COUNT(pub.year) AS number, SUM(calculate_num_of_pages(pages)) AS pages"
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
				int publicationPages = rs.getInt("pages");
				
				Publications yearPublications = yearPublicationsMap.get(publicationYear);
				if(yearPublications == null) {
					numberOfYear++;
					yearPublications = new Publications(publicationYear);
					
					yearPublicationsMap.put(publicationYear, yearPublications);
				}
				setPublicationsType(yearPublications, publicationType, publicationNumber,publicationPages);
				
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
				
		// Publication number
		JsonArray publicationArticle = new JsonArray();
		publicationArticle.add(new JsonPrimitive("Journal papers"));
		JsonArray publicationBook = new JsonArray();
		publicationBook.add(new JsonPrimitive("Books"));
		JsonArray publicationIncollection = new JsonArray();
		publicationIncollection.add(new JsonPrimitive("Part of book or collection"));
		JsonArray publicationInproceedings = new JsonArray();
		publicationInproceedings.add(new JsonPrimitive("Conference papers"));
		JsonArray publicationProceedings = new JsonArray();
		publicationProceedings.add(new JsonPrimitive("Editor"));

		JsonArray publicationOthers = new JsonArray(); // Issue #15
		publicationOthers.add(new JsonPrimitive("Others"));
		
		// publication pages
		JsonArray publicationArticlePages = new JsonArray();
		publicationArticlePages.add(new JsonPrimitive("Journal papers"));
		JsonArray publicationBookPages = new JsonArray();
		publicationBookPages.add(new JsonPrimitive("BooksPages"));
		JsonArray publicationIncollectionPages = new JsonArray();
		publicationIncollectionPages.add(new JsonPrimitive("Part of book or collection"));
		JsonArray publicationInproceedingsPages = new JsonArray();
		publicationInproceedingsPages.add(new JsonPrimitive("Conference papers"));
		JsonArray publicationProceedingsPages = new JsonArray();
		publicationProceedingsPages.add(new JsonPrimitive("Editor"));

		JsonArray publicationOthersPages = new JsonArray(); // Issue #15
		publicationOthersPages.add(new JsonPrimitive("OthersPages"));
		
		/*JsonArray publicationMasterThesis = new JsonArray();
		publicationMasterThesis.add(new JsonPrimitive("Master Thesis"));
		JsonArray publicationPHDThesis = new JsonArray();
		publicationPHDThesis.add(new JsonPrimitive("Phd Thesis"));
		JsonArray publicationWebsites = new JsonArray();
		publicationWebsites.add(new JsonPrimitive("Websites"));*/
		
		for(Integer year : publications.keySet()) {
			Publications pub = publications.get(year);
			publicationYears.add(new JsonPrimitive(year));
			
			publicationArticle.add(new JsonPrimitive(pub.getArticles()));
			publicationArticlePages.add(new JsonPrimitive(pub.getArticlePages()));
			publicationBook.add(new JsonPrimitive(pub.getBooks()));
			publicationBookPages.add(new JsonPrimitive(pub.getBookPages()));
			publicationIncollection.add(new JsonPrimitive(pub.getIncollections()));
			publicationIncollectionPages.add(new JsonPrimitive(pub.getIncollectionPages()));
			publicationInproceedings.add(new JsonPrimitive(pub.getInproceedings()));
			publicationInproceedingsPages.add(new JsonPrimitive(pub.getInproceedingPages()));
			publicationProceedings.add(new JsonPrimitive(pub.getProceedings()));
			publicationProceedingsPages.add(new JsonPrimitive(pub.getProceedingPages()));

			publicationOthers.add(new JsonPrimitive(pub.getMasterthesis()+pub.getPhdthesis()+pub.getWebsites())); // Issue #15
			publicationOthersPages.add(new JsonPrimitive(pub.getMasterthesisPages()+pub.getPhdthesisPages()+pub.getWebsitesPages()));
			/*publicationMasterThesis.add(new JsonPrimitive(pub.getMasterthesis()));
			publicationPHDThesis.add(new JsonPrimitive(pub.getPhdthesis()));
			publicationWebsites.add(new JsonPrimitive(pub.getWebsites()));*/
			
		}
		
		JsonObject articleObject = new JsonObject();
		articleObject.add("publications", publicationArticle);
		articleObject.add("pages",publicationArticlePages);
		
		JsonObject bookObject = new JsonObject();
		bookObject.add("publications", publicationBook);
		bookObject.add("pages",publicationBookPages);
		
		JsonObject incollectionObject = new JsonObject();
		incollectionObject.add("publications", publicationIncollection);
		incollectionObject.add("pages",publicationIncollectionPages);
		
		JsonObject inproceedingsObject = new JsonObject();
		inproceedingsObject.add("publications", publicationInproceedings);
		inproceedingsObject.add("pages",publicationInproceedingsPages);
		
		JsonObject proceedingsObject = new JsonObject();
		proceedingsObject.add("publications", publicationProceedings);
		proceedingsObject.add("pages",publicationProceedingsPages);
		
		JsonObject othersObject = new JsonObject();
		othersObject.add("publications", publicationOthers);
		othersObject.add("pages",publicationOthersPages);
		
		publicationsJson.add("years", publicationYears);
		publicationsJson.add("articles",articleObject);
		publicationsJson.add("books",bookObject);
		publicationsJson.add("incollections",incollectionObject);
		publicationsJson.add("inproceedings",inproceedingsObject);
		publicationsJson.add("proceedings",proceedingsObject);
		publicationsJson.add("others",othersObject);// Issue #15
		/*publicationsJson.add("masterThesis",publicationMasterThesis);
		publicationsJson.add("phdThesis",publicationPHDThesis);
		publicationsJson.add("websites",publicationWebsites);*/
		
		return publicationsJson;
	}
	
	private void setPublicationsType(Publications yearPublications, String publicationType, int publicationCount, int publicationPages) {
		if(publicationType.equals("article")) {
			yearPublications.setArticles(publicationCount,publicationPages);
			totalArticles += publicationCount;
		} else if(publicationType.equals("book")) {
			yearPublications.setBooks(publicationCount,publicationPages);
			totalBooks += publicationCount;
		} else if(publicationType.equals("incollection")) {
			yearPublications.setIncollections(publicationCount,publicationPages);
			totalIncollections += publicationCount;
		} else if(publicationType.equals("inproceedings")) {
			yearPublications.setInproceedings(publicationCount,publicationPages);
			totalInproceedings += publicationCount;
		} else if(publicationType.equals("masterthesis")) {
			yearPublications.setMasterthesis(publicationCount,publicationPages);
			totalMasterThesis += publicationCount;
		} else if(publicationType.equals("phdthesis")) {
			yearPublications.setPhdthesis(publicationCount,publicationPages);
			totalPHDThesis += publicationCount;
		} else if(publicationType.equals("proceedings")) {
			yearPublications.setProceedings(publicationCount,publicationPages);
			totalProceedings += publicationCount;
		} else if(publicationType.equals("www")) {
			yearPublications.setWebsites(publicationCount,publicationPages);
			totalWebsites += publicationCount;
		} else {
			//No corresponding type
		}
	}
	
	private JsonObject test() {
		JsonObject publicationsJson = new JsonObject();
		
		
		
		return publicationsJson;
	}
	
	
	
}
