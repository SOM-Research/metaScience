package som.metascience;

import java.io.IOException;
import java.io.PrintWriter;
import java.sql.Connection;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;

import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import com.google.gson.JsonObject;

/**
 * Servlet implementation class JournalNameServlet
 */
@WebServlet("/journalName")
public class JournalNameServlet extends AbstractMetaScienceServlet {
	private static final long serialVersionUID = 1L;
       
	@Override
	protected void doGet(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
		addResponseOptions(resp);
		
		String journalId = req.getParameter(ID_PARAM);
		
		if(journalId == null) 
			throw new ServletException("The id cannot be null");
		
		String journalName = getNameForJournalId(journalId);

		if(journalName != null && !journalName.equals("")) {
			JsonObject response = new JsonObject();
			response.addProperty("name", journalName);

			resp.setContentType("text/x-json;charset=UTF-8");
			PrintWriter pw = resp.getWriter();
			pw.append(response.toString());
		} else {
			resp.sendError(HttpServletResponse.SC_NOT_FOUND);
		}

	}

	private String getNameForJournalId(String journalId) throws ServletException {
		Connection con = Pooling.getInstance().getConnection();
		String venueName = "";
		Statement stmt = null;
		ResultSet rs = null;
		
		try {
			String query = "SELECT name"
							+ " FROM journal"
							+ " WHERE acronym = '" + journalId + "'";
	
	        stmt = con.createStatement();
	        rs = stmt.executeQuery(query);
	        
	        if (rs.next())
	        	venueName = rs.getString("name");
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
