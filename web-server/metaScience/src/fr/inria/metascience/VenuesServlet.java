package fr.inria.metascience;

import java.io.IOException;
import java.io.PrintWriter;
import java.util.logging.Logger;

import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import com.google.gson.JsonArray;
import com.google.gson.JsonObject;


/**
 * GET method returns the list of venues
 *
 */
@WebServlet("/venues")
public class VenuesServlet extends AbstractMetaScienceServlet{
	private static final String SEARCH_PARAM = "search";
	
	private static final long serialVersionUID = 1L;

	private final static Logger LOGGER = Logger.getLogger(VenuesServlet.class.getName()); 

	@Override
	protected void doGet(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
		addResponseOptions(resp);
		
		// Obtains the search param
		String searchString = req.getParameter(SEARCH_PARAM);

		// This list contains the list of JSON object representing venues
		JsonArray venues = new JsonArray();
		
		if(searchString != null) {
			// TODO Ask the database to retrieve ALL the venues (no search param)
			LOGGER.info("Asked for venues with search string: " + searchString);
			test(venues);
		} else {
			// TODO Ask the database to retrieve those venues LIKE searchString
			LOGGER.info("Asked for venues without search string");
			test(venues);
		}
		
		// Building the response
		JsonObject response = new JsonObject();
		response.add("venues", venues);
		PrintWriter pw = resp.getWriter();
		pw.append(venues.toString());
	}
	
	/**
	 * Just for testing purposes
	 * 
	 * @param venues
	 */
	private void test(JsonArray venues) {
		// Build a JSON object for the venue
		// One object per venue
		JsonObject venue = new JsonObject();
		venue.addProperty("name", "models");
		venue.addProperty("id", "1");
		venues.add(venue);

		JsonObject venue2 = new JsonObject();
		venue2.addProperty("name", "icmt");
		venue2.addProperty("id", "2");
		venues.add(venue2);
	}
}
