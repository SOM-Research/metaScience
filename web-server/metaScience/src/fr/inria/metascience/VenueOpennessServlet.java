package fr.inria.metascience;

import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonPrimitive;

import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.io.PrintWriter;
import java.sql.*;
import java.util.Iterator;

/**
 * Simple servlet to calculate the openness rate
 */
@WebServlet("/venueOpenness")
public class VenueOpennessServlet extends AbstractMetaScienceServlet {
    
	private static final long serialVersionUID = 1L;

	@Override
    protected void doGet(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
        addResponseOptions(resp);

        String venueId = req.getParameter(ID_PARAM);

        if(venueId == null)
            throw new ServletException("The id cannot be null");

        JsonObject response = getOpennessInfo(venueId);

        resp.setContentType("text/x-json;charset=UTF-8");
        PrintWriter pw = resp.getWriter();
        pw.append(response.toString());
    }

    /**
     * Obtains the openness information for a venue
     * @param venueId
     * @return
     * @throws ServletException
     */
    private JsonObject getOpennessInfo(String venueId) throws ServletException {
        Connection con = Pooling.getInstance().getConnection();
        Statement stmt = null;
        ResultSet rs = null;

        // preparing the result
        JsonObject openness = new JsonObject();
        try {
            // We first call the procedure that will fill the table if the data is still not there
            String query1 = "{call dblp20150613.get_openness_conf('" + venueId + "')}";
            CallableStatement cs = con.prepareCall(query1);
            cs.execute();

            // RESULTS for PAPERS
            JsonObject opennessPapers = new JsonObject();

            // Getting the average
            String query2 = "SELECT ROUND(AVG(o.from_outsiders/o.number_of_papers)*100,2) as avg " +
                    "FROM _openness_conf o WHERE conf='" + venueId + "';";
            stmt = con.createStatement();
            rs = stmt.executeQuery(query2);

            // Building the response for the average
            while(rs.next()) {
                String avg = rs.getString("avg");
                opennessPapers.addProperty("avg", avg);
            }

            // Getting the data yearly
            String query3 = "SELECT ROUND((o.from_outsiders/o.number_of_papers), 2) as ratio, o.year as year " +
                    "FROM _openness_conf o WHERE conf='" + venueId + "';";
            stmt = con.createStatement();
            rs = stmt.executeQuery(query3);

            // Building the response per year
            JsonArray opennessPapersYearlyValues = new JsonArray();
            opennessPapersYearlyValues.add(new JsonPrimitive("PapersFromNewcomers"));
            JsonArray opennessPapersYearlyYears = new JsonArray();
            opennessPapersYearlyYears.add(new JsonPrimitive("x1"));
            while(rs.next()) {
                String ratio = rs.getString("ratio");
                String year = rs.getString("year");
                opennessPapersYearlyValues.add(new JsonPrimitive(ratio));
                opennessPapersYearlyYears.add(new JsonPrimitive(year));
            }
            JsonArray opennessPapersYearly = new JsonArray();
            opennessPapersYearly.add(opennessPapersYearlyValues);
            opennessPapersYearly.add(opennessPapersYearlyYears);
            opennessPapers.add("yearly", opennessPapersYearly);
            openness.add("papers", opennessPapers);

            // RESULTS for AUTHORS
            JsonObject opennessAuthors = new JsonObject();

            // Getting the average select
            String query4 = "SELECT ROUND(AVG(o.perc_new_authors),2) as avg " +
                    "FROM _openness_conf o WHERE conf='" + venueId + "';";
            stmt = con.createStatement();
            rs = stmt.executeQuery(query4);

            // Building the response for the average
            while(rs.next()) {
                String avg = rs.getString("avg");
                opennessAuthors.addProperty("avg", avg);
            }

            // Getting the data yearly
            String query5 = "SELECT ROUND(o.perc_new_authors/100, 2) as ratio, o.year as year " +
                    "FROM _openness_conf o WHERE conf='" + venueId + "';";
            stmt = con.createStatement();
            rs = stmt.executeQuery(query5);

            // Building the response per year
            JsonArray opennessAuthorsYearlyValues = new JsonArray();
            opennessAuthorsYearlyValues.add(new JsonPrimitive("Authors"));
            JsonArray opennessAuthorsYearlyYears = new JsonArray();
            opennessAuthorsYearlyYears.add(new JsonPrimitive("x4"));
            while(rs.next()) {
                String ratio = rs.getString("ratio");
                String year = rs.getString("year");
                opennessAuthorsYearlyValues.add(new JsonPrimitive(ratio));
                opennessAuthorsYearlyYears.add(new JsonPrimitive(year));
            }
            JsonArray opennessAuthorsYearly = new JsonArray();
            opennessAuthorsYearly.add(opennessAuthorsYearlyValues);
            opennessAuthorsYearly.add(opennessAuthorsYearlyYears);
            opennessAuthors.add("yearly", opennessAuthorsYearly);
            openness.add("authors", opennessAuthors);

            // EXTRA: RESULTS for PAPERS FROM COMMUNITY
            JsonObject opennessPapersCommunity = new JsonObject();

            // Getting the average
            String query6 = "SELECT ROUND(AVG(o.from_community/o.number_of_papers)*100,2) as avg " +
                    "FROM _openness_conf o WHERE conf='" + venueId + "';";
            stmt = con.createStatement();
            rs = stmt.executeQuery(query6);

            // Building the response for the average
            while(rs.next()) {
                String avg = rs.getString("avg");
                opennessPapersCommunity.addProperty("avg", avg);
            }

            // Getting the data yearly
            String query7 = "SELECT ROUND((o.from_community/o.number_of_papers), 2) as ratio, o.year as year " +
                    "FROM _openness_conf o WHERE conf='" + venueId + "';";
            stmt = con.createStatement();
            rs = stmt.executeQuery(query7);

            // Building the response per year
            JsonArray opennessPapersCommunityYearlyValues = new JsonArray();
            opennessPapersCommunityYearlyValues.add(new JsonPrimitive("PapersFromCommunity"));
            JsonArray opennessPapersCommunityYearlyYears = new JsonArray();
            opennessPapersCommunityYearlyYears.add(new JsonPrimitive("x2"));
            while(rs.next()) {
                String ratio = rs.getString("ratio");
                String year = rs.getString("year");
                opennessPapersCommunityYearlyValues.add(new JsonPrimitive(ratio));
                opennessPapersCommunityYearlyYears.add(new JsonPrimitive(year));
            }
            JsonArray opennessPapersCommunityYearly = new JsonArray();
            opennessPapersCommunityYearly.add(opennessPapersCommunityYearlyValues);
            opennessPapersCommunityYearly.add(opennessPapersCommunityYearlyYears);
            opennessPapersCommunity.add("yearly", opennessPapersCommunityYearly);
            openness.add("papersCommunity", opennessPapersCommunity);

            // EXTRA: RESULTS for PAPERS FROM COMMUNITY AND NEWCOMERS
            JsonObject opennessPapersBoth = new JsonObject();

            // Getting the average
            String query8 = "SELECT ROUND(AVG(1-((o.from_outsiders + o.from_community)/o.number_of_papers))*100,2) as avg " +
                    "FROM _openness_conf o WHERE conf='" + venueId + "';";
            stmt = con.createStatement();
            rs = stmt.executeQuery(query8);

            // Building the response for the average
            while(rs.next()) {
                String avg = rs.getString("avg");
                opennessPapersBoth.addProperty("avg", avg);
            }

            // Getting the data yearly
            String query9 = "SELECT ROUND(1-((o.from_outsiders + o.from_community)/o.number_of_papers), 2) as ratio, o.year as year " +
                    "FROM _openness_conf o WHERE conf='" + venueId + "';";
            stmt = con.createStatement();
            rs = stmt.executeQuery(query9);

            // Building the response per year
            JsonArray opennessPapersBothYearlyValues = new JsonArray();
            opennessPapersBothYearlyValues.add(new JsonPrimitive("PapersFromBoth"));
            JsonArray opennessPapersBothYearlyYears = new JsonArray();
            opennessPapersBothYearlyYears.add(new JsonPrimitive("x3"));
            while(rs.next()) {
                String ratio = rs.getString("ratio");
                String year = rs.getString("year");
                opennessPapersBothYearlyValues.add(new JsonPrimitive(ratio));
                opennessPapersBothYearlyYears.add(new JsonPrimitive(year));
            }
            JsonArray opennessPapersBothYearly = new JsonArray();
            opennessPapersBothYearly.add(opennessPapersBothYearlyValues);
            opennessPapersBothYearly.add(opennessPapersBothYearlyYears);
            opennessPapersBoth.add("yearly", opennessPapersBothYearly);
            openness.add("papersBoth", opennessPapersBoth);
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

        // Building the result
        JsonObject result = openness;
        return result;
    }
}
