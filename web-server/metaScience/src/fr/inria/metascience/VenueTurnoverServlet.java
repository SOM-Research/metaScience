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
 * Simple servlet to calculate the persihing rate
 */
@WebServlet("/venueTurnover")
public class VenueTurnoverServlet extends AbstractMetaScienceServlet {

    @Override
    protected void doGet(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
        addResponseOptions(resp);

        String venueId = req.getParameter(ID_PARAM);

        if(venueId == null)
            throw new ServletException("The id cannot be null");

        JsonObject response = getTurnoverInfo(venueId);

        resp.setContentType("text/x-json;charset=UTF-8");
        PrintWriter pw = resp.getWriter();
        pw.append(response.toString());
    }

    /**
     * Obtains the turnover information for a venue
     * @param venueId
     * @return
     * @throws ServletException
     */
    private JsonObject getTurnoverInfo(String venueId) throws ServletException {
        Connection con = Pooling.getInstance().getConnection();
        Statement stmt = null;
        ResultSet rs = null;

        // preparing the result
        JsonObject perishingData = new JsonObject();
        JsonObject survivedData = new JsonObject();
        try {
            // We first call the procedure that will fill the table if the data is still not there
            String query1 = "{call dblp.get_perished_survived_authors('" + venueId + "')}";
            CallableStatement cs = con.prepareCall(query1);
            cs.execute();

            // Getting the data yearly
            // We get the number of perished authors per year AND
            // We get the number of survived authors per year
            String query2 = "SELECT p.perished AS perished, s.survived AS survived, p.period AS period " +
                    "FROM " +
                        " (SELECT count(author) AS perished, period FROM _perished_survived_authors_per_conf WHERE conf= '" + venueId + "' AND status = 'perished' GROUP BY period) as p, " +
                        " (SELECT count(author) AS survived, period FROM _perished_survived_authors_per_conf WHERE conf= '" + venueId + "' AND status = 'survived' GROUP BY period) as s " +
                    "WHERE p.period = s.period;";

            stmt = con.createStatement();
            rs = stmt.executeQuery(query2);

            // 1. Creating the info regarding the perished/survived
            JsonArray perishedYearlyValues = new JsonArray();
            JsonArray perishedYearlyRates = new JsonArray();
            perishedYearlyRates.add(new JsonPrimitive("Perished"));
            JsonArray perishedYearlyYears = new JsonArray();
            perishedYearlyYears.add(new JsonPrimitive("x1"));
            JsonArray survivedYearlyValues = new JsonArray();
            JsonArray survivedYearlyRates = new JsonArray();
            survivedYearlyRates.add(new JsonPrimitive("Survived"));
            JsonArray survivedYearlyYears = new JsonArray();
            survivedYearlyYears.add(new JsonPrimitive("x2"));
            // 1.1. Yearly
            while(rs.next()) {
                float perished = rs.getFloat("perished");
                float survived = rs.getFloat("survived");
                String period = rs.getString("period");
                String year = period.substring(period.indexOf("-") + 1, period.length());

                perishedYearlyValues.add(new JsonPrimitive(perished));
                perishedYearlyRates.add(new JsonPrimitive(String.valueOf(perished / (perished + survived))));
                perishedYearlyYears.add(new JsonPrimitive(year));

                survivedYearlyValues.add(new JsonPrimitive(survived));
                survivedYearlyRates.add(new JsonPrimitive(String.valueOf(survived / (perished + survived))));
                survivedYearlyYears.add(new JsonPrimitive(year));
            }
            // 1.2 Average
            Iterator<JsonElement> perishedIterator = perishedYearlyValues.iterator();
            float totalPerished = 0;
            while(perishedIterator.hasNext()) {
                float value = perishedIterator.next().getAsFloat();
                totalPerished += value;
            }

            Iterator<JsonElement> survivedIterator = survivedYearlyValues.iterator();
            float totalSurvived = 0;
            while(survivedIterator.hasNext()) {
                float value = survivedIterator.next().getAsFloat();
                totalSurvived += value;
            }

            // 2. preparing the final JSON objects
            JsonArray perishedYearly = new JsonArray();
            perishingData.addProperty("avg", String.valueOf(totalPerished / (totalPerished + totalSurvived)).substring(0, 4));
            perishedYearly.add(perishedYearlyValues);
            perishedYearly.add(perishedYearlyRates);
            perishedYearly.add(perishedYearlyYears);
            perishingData.add("yearly", perishedYearly);

            JsonArray survivedYearly = new JsonArray();
            survivedData.addProperty("avg", String.format("%%.2f",totalSurvived / (totalPerished + totalSurvived)).substring(0, 4));
            survivedYearly.add(survivedYearlyValues);
            survivedYearly.add(survivedYearlyRates);
            survivedYearly.add(survivedYearlyYears);
            survivedData.add("yearly", survivedYearly);
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

        // Building the result
        JsonObject result = new JsonObject();
        result.add("perished", perishingData);
        result.add("survived", survivedData);
        return result;

    }
}
