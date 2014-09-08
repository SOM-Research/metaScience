package fr.inria.metascience;

import java.io.IOException;
import java.io.PrintWriter;

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
		String name = "MODELS";  // TESTING
		
		JsonObject response = new JsonObject();
		response.addProperty("name", name);

		resp.setContentType("text/x-json;charset=UTF-8");    
		PrintWriter pw = resp.getWriter();
		pw.append(response.toString());
	}
}
