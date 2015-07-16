package som.metascience;

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

/**
 * Created by useradm on 25/09/14.
 */
@WebServlet("/subvenues")
public class SubvenuesServlet extends AbstractMetaScienceServlet{
    private static final String SEARCH_PARAM = "search";

    private static final long serialVersionUID = 132L;

    @Override
    protected void doGet(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
        addResponseOptions(resp);

        // Obtains the source id
        String sourceId = req.getParameter(ID_PARAM);

        // Obtains the search param
        String searchString = req.getParameter(SEARCH_PARAM);

        JsonArray sources = null;
        if(searchString == null) {
            sources = getAllSubvenues(sourceId);
        } else {
            sources = getAllSubvenues(searchString, sourceId);
        }

        // Building the response
        PrintWriter pw = resp.getWriter();
        pw.append(sources.toString());
    }

    private JsonArray getAllSubvenues(String searchString, String sourceId) throws ServletException {
        Connection con = Pooling.getInstance().getConnection();
        Statement stmt = null;
        ResultSet rs = null;
        JsonArray answer = new JsonArray();

        try {
            String query = "SELECT source, source_id " +
                    "FROM _num_authors_per_conf_per_year " +
                    "WHERE source_id = '" + sourceId + "' AND source LIKE '%" + searchString + "%' " +
                    "GROUP BY source;";

            stmt = con.createStatement();
            rs = stmt.executeQuery(query);

            while(rs.next()) {
                JsonObject subvenue = new JsonObject();
                String foundSource = rs.getString("source");
                String foundSourceId = rs.getString("source_id");
                // TODO get the real name?
                if(!foundSource.toLowerCase().equals(sourceId.toLowerCase())) {
                    subvenue.addProperty("name", foundSource);
                    subvenue.addProperty("id", foundSource);
                    answer.add(subvenue);
                }
            }
        } catch (SQLException e) {
            throw new ServletException("Error getting venues with search param", e);
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

    private JsonArray getAllSubvenues(String sourceId) throws ServletException {
        Connection con = Pooling.getInstance().getConnection();
        Statement stmt = null;
        ResultSet rs = null;
        JsonArray answer = new JsonArray();

        // We add the main source
        JsonObject mainVenue = new JsonObject();
        mainVenue.addProperty("name", "Main conference track");
        mainVenue.addProperty("id", sourceId);
        answer.add(mainVenue);
        try {
            String query = "SELECT source, source_id " +
                    "FROM _num_authors_per_conf_per_year " +
                    "WHERE source_id = '" + sourceId + "' " +
                    "GROUP BY source;";

            stmt = con.createStatement();
            rs = stmt.executeQuery(query);

            while(rs.next()) {
                JsonObject subvenue = new JsonObject();
                String foundSource = rs.getString("source");
                String foundSourceId = rs.getString("source_id");
                // TODO get the real name?
                if(!foundSource.toLowerCase().equals(sourceId.toLowerCase())) {
                    subvenue.addProperty("name", foundSource);
                    subvenue.addProperty("id", foundSource);
                    answer.add(subvenue);
                }
            }
        } catch (SQLException e) {
            throw new ServletException("Error getting venues with search param", e);
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
}
