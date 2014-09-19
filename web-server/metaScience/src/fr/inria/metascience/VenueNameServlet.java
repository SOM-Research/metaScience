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
		
		JsonObject response = new JsonObject();
		response.addProperty("name", venueName);

		resp.setContentType("text/x-json;charset=UTF-8");    
		PrintWriter pw = resp.getWriter();
		pw.append(response.toString());
	}
	

	private String getNameForVenueId(String venueId) throws ServletException {
		Connection con = Pooling.getInstance().getConnection();
		String venueName = "";
		Statement stmt = null;
		ResultSet rs = null;
		
		try {
			String query = "SELECT DISTINCT title"
							+ " FROM aux_dblp_proceedings"
							+ " WHERE source IS NOT NULL AND source = '" + venueId + "'";
	
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
