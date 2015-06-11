package fr.inria.metascience;

import java.io.IOException;
import java.io.PrintWriter;

import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

/**
 * Simple servlet to check the status in the servlet container
 */
@WebServlet("/status")
public class StatusServlet extends AbstractMetaScienceServlet {
	private static final long serialVersionUID = 69L;

	@Override
	protected void doGet(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
		addResponseOptions(resp);
		PrintWriter pw = resp.getWriter();
		
		pw.println("allowsOrigin: " + allowOrigin);
	}

}
