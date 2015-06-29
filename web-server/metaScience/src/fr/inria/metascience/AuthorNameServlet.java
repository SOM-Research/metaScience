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

@WebServlet("/authorName")
public class AuthorNameServlet extends AbstractMetaScienceServlet {

	private static final long serialVersionUID = 1L;

	@Override
	protected void doGet(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
		addResponseOptions(resp);
		
		String authorId = req.getParameter(ID_PARAM);
		
		if(authorId == null) 
			throw new ServletException("The id cannot be null");
		
		String authorName = getNameForAuthorId(authorId);

		if(authorName != null && !authorName.equals("")) {
			JsonObject response = new JsonObject();
			response.addProperty("name", authorName);

			resp.setContentType("text/x-json;charset=UTF-8");
			PrintWriter pw = resp.getWriter();
			pw.append(response.toString());
		} else {
			resp.sendError(HttpServletResponse.SC_NOT_FOUND);
		}
	}
	

	private String getNameForAuthorId(String authorId) throws ServletException {
		Connection con = Pooling.getInstance().getConnection();
		String authorName = "";
		Statement stmt = null;
		ResultSet rs = null;
		
		try {
			String query = "SELECT author"
							+ " FROM dblp_main_aliases_new"
							+ " WHERE author_id='" + authorId + "'";
	
	        stmt = con.createStatement();
	        rs = stmt.executeQuery(query);
	        
	        if (rs.next())
	        	authorName = rs.getString("author");
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
		return authorName;
	}
}
