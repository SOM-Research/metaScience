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
    /** Parameter indicating the span **/
    static final String SPAN_PARAM = "span";

    @Override
    protected void doGet(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
        addResponseOptions(resp);

        String venueId = req.getParameter(ID_PARAM);
        String span = req.getParameter(SPAN_PARAM);
        if(span == null) span = "1";

        if(venueId == null)
            throw new ServletException("The id cannot be null");

        JsonObject response = getTurnoverInfo(venueId, span);

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
    private JsonObject getTurnoverInfo(String venueId, String span) throws ServletException {
        Connection con = Pooling.getInstance().getConnection();
        Statement stmt = null;
        ResultSet rs = null;

        // preparing the result
        JsonObject perishingData = new JsonObject();
        JsonObject survivedData = new JsonObject();
        try {
            // We first call the procedure that will fill the table if the data is still not there
            String query1 = "{call " + dblpSchema + ".get_perished_survived_authors('" + venueId + "', " + span + ")}";
            CallableStatement cs = con.prepareCall(query1);
            cs.execute();

            // Getting the data yearly
            // We get the number of perished authors per year AND
            // We get the number of survived authors per year
            String query2 = "SELECT p.perished AS perished, s.survived AS survived, p.period AS period " +
                    "FROM " +
                        " (SELECT count(author) AS perished, period FROM _perished_survived_authors_per_conf WHERE span= '" + span + "' AND conf= '" + venueId + "' AND status = 'perished' GROUP BY period) as p, " +
                        " (SELECT count(author) AS survived, period FROM _perished_survived_authors_per_conf WHERE span= '" + span + "' AND conf= '" + venueId + "' AND status = 'survived' GROUP BY period) as s " +
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
                //String year = period.substring(period.indexOf("-") + 1, period.length());

                perishedYearlyValues.add(new JsonPrimitive(perished));
                perishedYearlyRates.add(new JsonPrimitive(String.valueOf(perished / (perished + survived))));
                perishedYearlyYears.add(new JsonPrimitive(period));

                survivedYearlyValues.add(new JsonPrimitive(survived));
                survivedYearlyRates.add(new JsonPrimitive(String.valueOf(survived / (perished + survived))));
                survivedYearlyYears.add(new JsonPrimitive(period));
            }
            // 1.2 Average perished/survived
            String query3 = "SELECT ROUND(AVG((perished/(perished+survived))*100), 2) as avg" +
                    " FROM" +
                    "   (SELECT count(author) AS perished, period FROM _perished_survived_authors_per_conf WHERE span='" + span + "' AND conf= '" + venueId + "' AND status = 'perished' GROUP BY period) as p," +
                    "   (SELECT count(author) AS survived, period FROM _perished_survived_authors_per_conf WHERE span= '" + span + "'  AND conf='" + venueId + "'  AND status = 'survived' GROUP BY period) as s" +
                    " WHERE p.period = s.period;";

            stmt = con.createStatement();
            rs = stmt.executeQuery(query3);
            while(rs.next()) {
                String avg = rs.getString("avg");
                perishingData.addProperty("avg", avg);
            }

            // 1.3 Average perished/survived
            String query4 = "SELECT ROUND(AVG((survived/(perished+survived))*100), 2) as avg" +
                    " FROM" +
                    "   (SELECT count(author) AS perished, period FROM _perished_survived_authors_per_conf WHERE span='" + span + "' AND conf= '" + venueId + "' AND status = 'perished' GROUP BY period) as p," +
                    "   (SELECT count(author) AS survived, period FROM _perished_survived_authors_per_conf WHERE span= '" + span + "'  AND conf='" + venueId + "'  AND status = 'survived' GROUP BY period) as s" +
                    " WHERE p.period = s.period;";

            stmt = con.createStatement();
            rs = stmt.executeQuery(query4);
            while(rs.next()) {
                String avg = rs.getString("avg");
                survivedData.addProperty("avg", avg);
            }

            // 2. preparing the final JSON objects
            JsonArray perishedYearly = new JsonArray();
            perishedYearly.add(perishedYearlyValues);
            perishedYearly.add(perishedYearlyRates);
            perishedYearly.add(perishedYearlyYears);
            perishingData.add("yearly", perishedYearly);

            JsonArray survivedYearly = new JsonArray();
            survivedYearly.add(survivedYearlyValues);
            survivedYearly.add(survivedYearlyRates);
            survivedYearly.add(survivedYearlyYears);
            survivedData.add("yearly", survivedYearly);
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
        JsonObject result = new JsonObject();
        result.add("perished", perishingData);
        result.add("survived", survivedData);
        return result;

    }
}
