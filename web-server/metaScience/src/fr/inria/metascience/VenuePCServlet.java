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
 * Computes basic data related to program committee
 */
@WebServlet("/venuePC")
public class VenuePCServlet extends AbstractMetaScienceServlet {
    private static final long serialVersionUID = 48L;

    @Override
    protected void doGet(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
        addResponseOptions(resp);

        String venueId = req.getParameter(ID_PARAM);

        if(venueId == null)
            throw new ServletException("The id cannot be null");

        JsonObject response = getPCForVenueId(venueId);

        resp.setContentType("text/x-json;charset=UTF-8");
        PrintWriter pw = resp.getWriter();
        pw.append(response.toString());
    }

    private JsonObject getPCForVenueId(String venueId) throws ServletException {
        Connection con = Pooling.getInstance().getConnection();
        Statement stmt = null;
        ResultSet rs = null;

        // preparing the result
        JsonObject withPCData = new JsonObject();
        JsonObject withoutPCData = new JsonObject();
        try {
            // 1. Getting the data yearly
            String query1 = "SELECT perc_of_coauthored_papers_pc_members AS withPC, perc_of_no_coauthored_papers_pc_members AS withoutPC, pub_year AS year " +
                    "FROM " +
                    " _pc_coauthored_papers_rate " +
                    "WHERE conf= '" + venueId + "';";

            stmt = con.createStatement();
            rs = stmt.executeQuery(query1);

            JsonArray withPCYearlyRates = new JsonArray();
            withPCYearlyRates.add(new JsonPrimitive("PCcoauthoredPapers"));
            JsonArray withPCYearlyYears = new JsonArray();
            withPCYearlyYears.add(new JsonPrimitive("x1"));

            JsonArray withoutPCYearlyRates = new JsonArray();
            withoutPCYearlyRates.add(new JsonPrimitive("NoPCcoauthoredPapers"));
            JsonArray withoutPCYearlyYears = new JsonArray();
            withoutPCYearlyYears.add(new JsonPrimitive("x2"));

            while(rs.next()) {
                float withPC = rs.getFloat("withPC")/100;
                float withoutPC = rs.getFloat("withoutPC")/100;
                String year = rs.getString("year");

                withPCYearlyRates.add(new JsonPrimitive(withPC));
                withPCYearlyYears.add(new JsonPrimitive(year));

                withoutPCYearlyRates.add(new JsonPrimitive(withoutPC));
                withoutPCYearlyYears.add(new JsonPrimitive(year));
            }

            // 2. Getting the avg data
            String query2 = "SELECT ROUND(AVG(perc_of_coauthored_papers_pc_members), 2) AS avg_withPC, ROUND(AVG(perc_of_no_coauthored_papers_pc_members), 2) AS avg_withoutPC " +
                    "FROM " +
                    " _pc_coauthored_papers_rate " +
                    "WHERE conf= '" + venueId + "';";

            stmt = con.createStatement();
            rs = stmt.executeQuery(query2);

            float avgWithPC = 0;
            float avgWithoutPC = 0;
            while(rs.next()) {
                avgWithPC = rs.getFloat("avg_withPC");
                avgWithoutPC = rs.getFloat("avg_withoutPC");
            }

            // 2. preparing the final JSON objects
            withPCData.addProperty("avg", avgWithPC);
            JsonArray withPCYearly = new JsonArray();
            withPCYearly.add(withPCYearlyRates);
            withPCYearly.add(withPCYearlyYears);
            withPCData.add("yearly", withPCYearly);

            withoutPCData.addProperty("avg", avgWithoutPC);
            JsonArray withoutPCYearly = new JsonArray();
            withoutPCYearly.add(withoutPCYearlyRates);
            withoutPCYearly.add(withoutPCYearlyYears);
            withoutPCData.add("yearly", withoutPCYearly);
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
        result.add("withPC", withPCData);
        result.add("withoutPC", withoutPCData);
        return result;
    }
}
