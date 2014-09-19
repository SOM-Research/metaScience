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

@WebServlet("/venueActivity")
public class VenueActivityServlet extends AbstractMetaScienceServlet {
	private static final long serialVersionUID = 4L;

	@Override
	protected void doGet(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
		addResponseOptions(resp);

		String venueId = req.getParameter(ID_PARAM);

		if(venueId == null) 
			throw new ServletException("The id cannot be null");

		//JsonObject response = testGetActivityForVenueId();
		JsonObject response = getActivityForVenueId(venueId);

		resp.setContentType("text/x-json;charset=UTF-8");    
		PrintWriter pw = resp.getWriter();
		pw.append(response.toString());
	}



	private JsonObject getActivityForVenueId(String venueId) throws ServletException {
		Connection con = Pooling.getInstance().getConnection();
		Statement stmt = null;
		ResultSet rs = null;

		// Preparing the result
		JsonObject authors = new JsonObject();
		JsonObject papers = new JsonObject();
		JsonObject authorsPerPaper = new JsonObject();
		JsonObject papersPerAuthor = new JsonObject();
		try {
			// AUTHORS
			// Getting avergae authors 
			String query1 = "SELECT ROUND(AVG(num_unique_authors), 2) as avg " +
					"FROM _num_authors_per_conf_per_year " +
					"WHERE source_id = '" + venueId + "' AND source = '" + venueId + "';";

			stmt = con.createStatement();
			rs = stmt.executeQuery(query1);

			while(rs.next()) {
				String avg = rs.getString("avg");
				authors.addProperty("avg", avg);
			}

			// Getting authors per year
			String query2 = "SELECT ROUND(AVG(num_unique_authors), 2) as counter, year " +
					"FROM _num_authors_per_conf_per_year " +
					"WHERE source_id = '" + venueId + "' AND source = '" + venueId + "' GROUP BY year;";

			stmt = con.createStatement();
			rs = stmt.executeQuery(query2);

			JsonArray authorsYearlyValues = new JsonArray();
			authorsYearlyValues.add(new JsonPrimitive("Authors"));
			JsonArray authorsYearlyYears = new JsonArray();
			authorsYearlyYears.add(new JsonPrimitive("x1"));
			while(rs.next()) {
				String counter = rs.getString("counter");
				String year = rs.getString("year");
				authorsYearlyValues.add(new JsonPrimitive(counter));
				authorsYearlyYears.add(new JsonPrimitive(year));
			}
			JsonArray authorsYearly = new JsonArray();
			authorsYearly.add(authorsYearlyValues);
			authorsYearly.add(authorsYearlyYears);
			authors.add("yearly", authorsYearly);			

			// PAPERS
			// Getting average papers
			String query3 = "SELECT ROUND(AVG(num_papers), 2) as avg " +
					"FROM _num_of_papers_per_conference_per_year " +
					"WHERE source_id = '" + venueId + "' AND source = '" + venueId + "';";

			stmt = con.createStatement();
			rs = stmt.executeQuery(query3);

			while(rs.next()) {
				String avg = rs.getString("avg");
				papers.addProperty("avg", avg);
			}

			// Getting papers per year
			String query4 = "SELECT ROUND(AVG(num_papers), 2) as counter, year " +
					"FROM _num_of_papers_per_conference_per_year " +
					"WHERE source_id = '" + venueId + "' AND source = '" + venueId + "' GROUP BY year;";

			stmt = con.createStatement();
			rs = stmt.executeQuery(query4);

			JsonArray papersYearlyValues = new JsonArray();
			papersYearlyValues.add(new JsonPrimitive("Papers"));
			JsonArray papersYearlyYears = new JsonArray();
			papersYearlyYears.add(new JsonPrimitive("x2"));
			while(rs.next()) {
				String counter = rs.getString("counter");
				String year = rs.getString("year");
				papersYearlyValues.add(new JsonPrimitive(counter));
				papersYearlyYears.add(new JsonPrimitive(year));
			}
			JsonArray papersYearly = new JsonArray();
			papersYearly.add(papersYearlyValues);
			papersYearly.add(papersYearlyYears);
			papers.add("yearly", papersYearly);	

			// AUTHORS PER PAPER
			// Getting average value
			String query5 = "SELECT ROUND(AVG(avg_author_per_paper), 2) as avg " +
					"FROM _avg_number_authors_per_paper_per_conf_per_year " +
					"WHERE source_id = '" + venueId + "' AND source = '" + venueId + "';";

			stmt = con.createStatement();
			rs = stmt.executeQuery(query5);

			while(rs.next()) {
				String avg = rs.getString("avg");
				authorsPerPaper.addProperty("avg", avg);
			}

			// Getting papers per year
			String query6 = "SELECT ROUND(AVG(avg_author_per_paper), 2) as counter, year " +
					"FROM _avg_number_authors_per_paper_per_conf_per_year " +
					"WHERE source_id = '" + venueId + "' AND source = '" + venueId + "' GROUP BY year;";

			stmt = con.createStatement();
			rs = stmt.executeQuery(query6);

			JsonArray authorsPerPaperYearlyValues = new JsonArray();
			authorsPerPaperYearlyValues.add(new JsonPrimitive("AuthorsPerPaper"));
			JsonArray authorsPerPaperYearlyYears = new JsonArray();
			authorsPerPaperYearlyYears.add(new JsonPrimitive("x1"));
			while(rs.next()) {
				String counter = rs.getString("counter");
				String year = rs.getString("year");
				authorsPerPaperYearlyValues.add(new JsonPrimitive(counter));
				authorsPerPaperYearlyYears.add(new JsonPrimitive(year));
			}
			JsonArray authorsPerPaperYearly = new JsonArray();
			authorsPerPaperYearly.add(authorsPerPaperYearlyValues);
			authorsPerPaperYearly.add(authorsPerPaperYearlyYears);
			authorsPerPaper.add("yearly", authorsPerPaperYearly);	

			// PAPERS PER AUTHOR
			// Getting average value
			String query7 = "SELECT ROUND(AVG(avg_num_paper_per_author), 2) as avg " +
					"FROM _avg_number_papers_per_author_per_conf_per_year " +
					"WHERE source_id = '" + venueId + "' AND source = '" + venueId + "';";

			stmt = con.createStatement();
			rs = stmt.executeQuery(query7);

			while(rs.next()) {
				String avg = rs.getString("avg");
				papersPerAuthor.addProperty("avg", avg);
			}

			// Getting papers per year
			String query8 = "SELECT ROUND(AVG(avg_num_paper_per_author), 2) as counter, year " +
					"FROM _avg_number_papers_per_author_per_conf_per_year " +
					"WHERE source_id = '" + venueId + "' AND source = '" + venueId + "' GROUP BY year;";

			stmt = con.createStatement();
			rs = stmt.executeQuery(query8);

			JsonArray papersPerAuthorYearlyValues = new JsonArray();
			papersPerAuthorYearlyValues.add(new JsonPrimitive("PapersPerAuthor"));
			JsonArray papersPerAuthorYearlyYears = new JsonArray();
			papersPerAuthorYearlyYears.add(new JsonPrimitive("x2"));
			while(rs.next()) {
				String counter = rs.getString("counter");
				String year = rs.getString("year");
				papersPerAuthorYearlyValues.add(new JsonPrimitive(counter));
				papersPerAuthorYearlyYears.add(new JsonPrimitive(year));
			}
			JsonArray papersPerAuthorYearly = new JsonArray();
			papersPerAuthorYearly.add(papersPerAuthorYearlyValues);
			papersPerAuthorYearly.add(papersPerAuthorYearlyYears);
			papersPerAuthor.add("yearly", papersPerAuthorYearly);	

		} catch (SQLException e) {
			throw new ServletException("Error getting the Id for the venue", e);
		} finally {
			try {
				if(stmt != null) stmt.close();
				if(rs != null) rs.close();
				if(con != null) con.close();
			} catch (SQLException e) {
				throw new ServletException("Impossible to close the connection", e);	
			}
		}

		JsonObject result = new JsonObject();
		result.add("authors", authors);
		result.add("papers", papers);
		result.add("authorsPerPaper", authorsPerPaper);
		result.add("papersPerAuthor", papersPerAuthor);
		return result;
	}



	private JsonArray testGetActivityForVenueId() {
		JsonArray authors = new JsonArray();
		authors.add(new JsonPrimitive("Authors"));
		authors.add(new JsonPrimitive(3));
		authors.add(new JsonPrimitive(56));
		authors.add(new JsonPrimitive(23));
		authors.add(new JsonPrimitive(72));
		authors.add(new JsonPrimitive(23));

		JsonArray authorsYear = new JsonArray();
		authorsYear.add(new JsonPrimitive("x1"));
		authorsYear.add(new JsonPrimitive(2014));
		authorsYear.add(new JsonPrimitive(2013));
		authorsYear.add(new JsonPrimitive(2012));
		authorsYear.add(new JsonPrimitive(2011));
		authorsYear.add(new JsonPrimitive(2010));

		JsonArray papers = new JsonArray();
		papers.add(new JsonPrimitive("Papers"));
		papers.add(new JsonPrimitive(12));
		papers.add(new JsonPrimitive(32));
		papers.add(new JsonPrimitive(23));
		papers.add(new JsonPrimitive(22));
		papers.add(new JsonPrimitive(16));

		JsonArray papersYear = new JsonArray();
		papersYear.add(new JsonPrimitive("x2"));
		papersYear.add(new JsonPrimitive(2014));
		papersYear.add(new JsonPrimitive(2013));
		papersYear.add(new JsonPrimitive(2012));
		papersYear.add(new JsonPrimitive(2011));
		papersYear.add(new JsonPrimitive(2010));


		JsonArray result = new JsonArray();
		result.add(authors);
		result.add(authorsYear);
		result.add(papers);
		result.add(papersYear);

		return result;
	}

}
