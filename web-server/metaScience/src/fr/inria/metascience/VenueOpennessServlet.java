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
            String query1 = "{call dblp.get_openness_conf('" + venueId + "')}";
            CallableStatement cs = con.prepareCall(query1);
            cs.execute();

            // Getting the average
            String query2 = "SELECT ROUND(AVG(o.from_outsiders/o.number_of_papers)*100,2) as avg " +
                    "FROM dblp._openness_conf o WHERE conf='" + venueId + "';";
            stmt = con.createStatement();
            rs = stmt.executeQuery(query2);

            // Building the response for the average
            while(rs.next()) {
                String avg = rs.getString("avg");
                openness.addProperty("avg", avg);
            }

            // Getting the data yearly
            String query3 = "SELECT ROUND((o.from_outsiders/o.number_of_papers), 2) as ratio, o.year as year " +
                    "FROM dblp._openness_conf o WHERE conf='" + venueId + "';";
            stmt = con.createStatement();
            rs = stmt.executeQuery(query3);

            // Building the response per year
            JsonArray opennessYearlyValues = new JsonArray();
            opennessYearlyValues.add(new JsonPrimitive("Openness"));
            JsonArray opennessYearlyYears = new JsonArray();
            opennessYearlyYears.add(new JsonPrimitive("x1"));
            while(rs.next()) {
                String ratio = rs.getString("ratio");
                String year = rs.getString("year");
                opennessYearlyValues.add(new JsonPrimitive(ratio));
                opennessYearlyYears.add(new JsonPrimitive(year));
            }
            JsonArray opennessYearly = new JsonArray();
            opennessYearly.add(opennessYearlyValues);
            opennessYearly.add(opennessYearlyYears);
            openness.add("yearly", opennessYearly);
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
        result.add("openness", openness);
        return result;
    }
}
