package fr.inria.metascience;

import com.google.gson.JsonObject;

import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.io.PrintWriter;

@WebServlet("/version")
public class VersionServlet extends AbstractMetaScienceServlet{
    protected void doGet(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
        addResponseOptions(resp);
        JsonObject response = new JsonObject();

        // Building the response
        response.addProperty("version", metascienceVersion);
        resp.setContentType("text/x-json;charset=UTF-8");
        PrintWriter pw = resp.getWriter();
        pw.append(response.toString());
    }
}
