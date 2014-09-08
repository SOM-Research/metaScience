package fr.inria.metascience;

import java.io.IOException;
import java.util.Properties;

import javax.servlet.ServletException;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

/**
 * This class includes some common functionalities for metaScience servlets
 *
 */
public class AbstractMetaScienceServlet extends HttpServlet {
	private static final long serialVersionUID = 315L;
	
	/**
	 * String to be used for CORS
	 */
	String allowOrigin;
	
	@Override
	public void init() throws ServletException {
		try {
			Properties properties = new Properties();
			properties.load(getServletContext().getResourceAsStream("/WEB-INF/config.properties"));
			allowOrigin = properties.getProperty("allowOrigin");
			if(allowOrigin == null)
				throw new ServletException("No value for allowOrigin in config file");
		} catch (IOException e) {
			throw new ServletException("No configuration found");
		}
	}

	@Override
	public void doOptions(HttpServletRequest arg0, HttpServletResponse response) throws ServletException, IOException {
		addResponseOptions(response);
	}

	protected void addResponseOptions(HttpServletResponse response) {
		response.setHeader("Access-Control-Allow-Origin", allowOrigin);
		response.setHeader("Access-Control-Allow-Methods", "GET,POST,PUT,DELETE,OPTIONS");
		response.setHeader("Access-Control-Allow-Headers", "Origin,	X-Requested-With, Content-Type, Accept");
		response.addHeader("Access-Control-Allow-Credentials", "true");
	}

}
