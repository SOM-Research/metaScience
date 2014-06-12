package fr.inria.atlanmod.conferenceanalysis.services;

import java.io.IOException;
import java.io.PrintWriter;

import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

@WebServlet("/locationsPerConference")
public class LocationsPerConference extends HttpServlet {

	protected void doPost(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException  {
		response.setHeader("Access-Control-Allow-Origin", "*");
		response.setHeader("Access-Control-Allow-Methods", "GET,POST,PUT,DELETE,OPTIONS");
		
		String conferenceId = request.getParameter("conference");
		System.out.println("Conference received: " + conferenceId);
		
		String result = "{    \"GBR\": { \"ocurrences\": 0},    \"DEU\": { \"ocurrences\": 200},    \"USA\": { \"ocurrences\": 300},    \"BRA\": { \"ocurrences\": 400},    \"CAN\": { \"ocurrences\": 500},    \"FRA\": { \"ocurrences\": 600},    \"RUS\": { \"ocurrences\": 700}}";
		
		PrintWriter out = response.getWriter();
        out.print(result); 
	}

	@Override
	protected void doOptions(HttpServletRequest request, HttpServletResponse response)throws ServletException, IOException
	{
		response.setHeader("Access-Control-Allow-Origin", "*");
		response.setHeader("Access-Control-Allow-Methods", "GET,POST,PUT,DELETE,OPTIONS");
		response.setHeader("Access-Control-Allow-Headers", "Origin, X-Requested-With, Content-Type, Accept");
		super.doOptions(request, response);

	}
}
