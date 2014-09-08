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
 *
 */
@WebServlet("/venueName")
public class VenueNameServlet extends AbstractMetaScienceServlet {
	private static final long serialVersionUID = 3L;
	private static final String ID_PARAM = "id";
	
	@Override
	protected void doGet(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
		addResponseOptions(resp);
		
		String venueId = req.getParameter(ID_PARAM);
		
		if(venueId == null) 
			throw new ServletException("The id cannot be null");
		
		// TODO Ask the database the name for venueId venue
		String venueName = getNameForVenueId(venueId);
		
		JsonObject response = new JsonObject();
		response.addProperty("name", venueName);

		resp.setContentType("text/x-json;charset=UTF-8");    
		PrintWriter pw = resp.getWriter();
		pw.append(response.toString());
	}
	

	private String getNameForVenueId(String venueId) {
		Connection con = Pooling.getInstance().getConnection();
		String venueName = "";
		Statement stmt = null;
		ResultSet rs = null;
		try {
			String query = "SELECT title, source"
							+ " FROM dblp_pub_new"
							+ " WHERE source IS NOT NULL AND id = " + venueId;
	
	        stmt = con.createStatement();
	        rs = stmt.executeQuery(query);
	        if (rs.next())
	        	venueName = rs.getString("source") + " - " + rs.getString("title");
	        	
	        
		} catch (SQLException e) {
			e.printStackTrace();		
		} finally {
			try {
				stmt.close();
				rs.close();
			}
			catch (SQLException e) {
				e.printStackTrace();
			}
		}
		return venueName;
	}
}
