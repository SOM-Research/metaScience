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
	private static final String ID_PARAM = "id";
	
	@Override
	protected void doGet(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
		addResponseOptions(resp);

		String venueId = req.getParameter(ID_PARAM);
		
		if(venueId == null) 
			throw new ServletException("The id cannot be null");
		
		JsonArray response = getActivityForVenueId(venueId);
		
		resp.setContentType("text/x-json;charset=UTF-8");    
		PrintWriter pw = resp.getWriter();
		pw.append(response.toString());
	}
	
	

	private JsonArray getActivityForVenueId(String venueId) throws ServletException {
		Connection con = Pooling.getInstance().getConnection();
		Statement stmt = null;
		ResultSet rs = null;
		
		// Preparing the result
		JsonArray authors = new JsonArray();
		authors.add(new JsonPrimitive("Authors"));
		JsonArray authorsYear = new JsonArray();
		authorsYear.add(new JsonPrimitive("x1"));
		JsonArray papers = new JsonArray();
		papers.add(new JsonPrimitive("Papers"));
		JsonArray papersYear = new JsonArray();
		papersYear.add(new JsonPrimitive("x2"));
		
		try {
			// Getting authors per year
			String query1 = "SELECT SUM(num_unique_authors) as counter, year " +
					"FROM aux_num_authors_per_conf_per_year " +
					"WHERE source_id = '" + venueId + "' " + 
					"GROUP BY year;";
	
	        stmt = con.createStatement();
	        rs = stmt.executeQuery(query1);
	        
	        while(rs.next()) {
	        	String counter = rs.getString("counter");
	        	String year = rs.getString("year");
	        	authors.add(new JsonPrimitive(counter));
	        	authorsYear.add(new JsonPrimitive(year));
	        }
	        
	        // Getting papers per year
	        String query2 = "SELECT SUM(num_papers) as counter, year " +
					"FROM aux_num_of_papers_per_conference " +
					"WHERE source_id = '" + venueId + "' " + 
					"GROUP BY year;";
	
	        stmt = con.createStatement();
	        rs = stmt.executeQuery(query2);
	        
	        while(rs.next()) {
	        	String counter = rs.getString("counter");
	        	String year = rs.getString("year");
	        	papers.add(new JsonPrimitive(counter));
	        	papersYear.add(new JsonPrimitive(year));
	        }
	        
		} catch (SQLException e) {
			throw new ServletException("Error getting the Id for the venue", e);
		} finally {
			try {
				if(stmt != null) stmt.close();
				if(rs != null) rs.close();
			} catch (SQLException e) {
				throw new ServletException("Impossible to close the connection", e);	
			}
		}

		JsonArray result = new JsonArray();
		result.add(authors);
		result.add(authorsYear);
		result.add(papers);
		result.add(papersYear);
		
		return result;
	}



	private JsonArray testGetActivityForVenueId(String venueId) {
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
