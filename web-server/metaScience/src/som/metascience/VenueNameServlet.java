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

import com.google.gson.JsonObject;


/**
 * Simple servlet to get the name from an id
 */
@WebServlet("/venueName")
public class VenueNameServlet extends AbstractMetaScienceServlet {
	private static final long serialVersionUID = 3L;

	@Override
	protected void doGet(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
		addResponseOptions(resp);
		
		String venueId = req.getParameter(ID_PARAM);
		
		if(venueId == null) 
			throw new ServletException("The id cannot be null");
		
		String venueName = getNameForVenueId(venueId);

		if(venueName != null && !venueName.equals("")) {
			JsonObject response = new JsonObject();
			response.addProperty("name", venueName);

			resp.setContentType("text/x-json;charset=UTF-8");
			PrintWriter pw = resp.getWriter();
			pw.append(response.toString());
		} else {
			resp.sendError(HttpServletResponse.SC_NOT_FOUND);
		}

	}
	

	private String getNameForVenueId(String venueId) throws ServletException {
		Connection con = Pooling.getInstance().getConnection();
		String venueName = "";
		Statement stmt = null;
		ResultSet rs = null;
		
		try {
			String query = "SELECT name as title"
							+ " FROM conference"
							+ " WHERE acronym = '" + venueId + "'";
	
	        stmt = con.createStatement();
	        rs = stmt.executeQuery(query);
	        
	        if (rs.next())
	        	venueName = rs.getString("title");
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
		return venueName;
	}
}
