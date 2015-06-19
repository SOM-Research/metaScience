package fr.inria.metascience;

import java.io.IOException;
import java.io.PrintWriter;
import java.sql.Connection;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import java.util.Arrays;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;

import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.google.gson.JsonPrimitive;

@WebServlet("/venueTitleCloud")
public class VenueTitleCloudServlet extends AbstractMetaScienceServlet {
	
	private static String[] blackList = {"i","me","my","myself","we","us","our","ours","ourselves","you","your","yours","yourself","yourselves","he","him","his","himself","she","her","hers","herself","it","its","itself","they","them","their","theirs","themselves","what","which","who","whom","whose","this","that","these","those","am","is","are","was","were","be","been","being","have","has","had","having","do","does","did","doing","will","would","should","can","could","ought","i'm","you're","he's","she's","it's","we're","they're","i've","you've","we've","they've","i'd","you'd","he'd","she'd","we'd","they'd","i'll","you'll","he'll","she'll","we'll","they'll","isn't","aren't","wasn't","weren't","hasn't","haven't","hadn't","doesn't","don't","didn't","won't","wouldn't","shan't","shouldn't","can't","cannot","couldn't","mustn't","let's","that's","who's","what's","here's","there's","when's","where's","why's","how's","a","an","the","and","but","if","or","because","as","until","while","of","at","by","for","with","about","against","between","into","through","during","before","after","above","below","to","from","up","upon","down","in","out","on","off","over","under","again","further","then","once","here","there","when","where","why","how","all","any","both","each","few","more","most","other","some","such","no","nor","not","only","own","same","so","than","too","very","say","says","said","shall"};
	private static Set<String> blackListSet = new HashSet<String>(Arrays.asList(blackList));

	private static final long serialVersionUID = 1L;
	
	protected void doGet(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
		addResponseOptions(resp);

		String venueId = req.getParameter(ID_PARAM);
        String subVenueId = req.getParameter(SUBID_PARAM);

		if(venueId == null) 
			throw new ServletException("The id cannot be null");

		//JsonObject response = testGetActivityForVenueId();
		JsonObject response = getTitleCloudInformation(venueId, subVenueId);

		resp.setContentType("text/x-json;charset=UTF-8");
		PrintWriter pw = resp.getWriter();
		pw.append(response.toString());
	}
	
	private JsonObject getTitleCloudInformation(String venueId, String subVenueId) throws ServletException {
		JsonObject answer = new JsonObject();
		
		// Checking if we know the conference has different source / source_id
        String sourceId = preCachedVenues.get(venueId);
        if(sourceId == null) sourceId = venueId;

        String source = subVenueId; // THIS FIXES EVERYTHING
        if(subVenueId == null) source = sourceId;
		
		Connection con = Pooling.getInstance().getConnection();
		Statement stmt = null;
		ResultSet rs = null;
		
		try {
			String query = "SELECT title, year" +
					" FROM dblp.dblp_pub_new" +
					" WHERE type = 'inproceedings'" +
					" AND source = '" + source + "'" +
					" ORDER BY year;";
	
	        stmt = con.createStatement();
	        rs = stmt.executeQuery(query);
	        
	        answer = prepareTitleCloudInformation(rs);
	        
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
		
		return answer;
	}
	
	private JsonObject prepareTitleCloudInformation(ResultSet rs) throws ServletException {
		
		
		JsonObject titleCloudJson = new JsonObject();
		
		//JsonArray yearsJson = new JsonArray();
		
		
		Map<String,Integer> globalTitleCloudMap = new HashMap<String,Integer>();
		Map<Integer,Map<String,Integer>> yearTitleCloudMapContainer = new HashMap<Integer, Map<String,Integer>>();
		try {
			while(rs.next()) {
				String title = rs.getString("title");
				int year =  rs.getInt("year");
				
				Map<String,Integer> yearTitleCloudMap = yearTitleCloudMapContainer.get(year);
				if(yearTitleCloudMap == null) {
					yearTitleCloudMap = new HashMap<String, Integer>();
					yearTitleCloudMapContainer.put(year, yearTitleCloudMap);
					//yearsJson.add(new JsonPrimitive(year));
				}
				
				//split title
				String lowerTitle = title.toLowerCase();
				
				String[] lowerTitleSpaceSplit = lowerTitle.split(" ");
				for(String lowerTitleWord : lowerTitleSpaceSplit) {
					lowerTitleWord = lowerTitleWord.trim();
					lowerTitleWord = lowerTitleWord.replaceAll("[^A-Za-z0-9*-]", "");
					if(!lowerTitleWord.isEmpty() && !blackListSet.contains(lowerTitleWord)){
						Integer globalWordOccurence = globalTitleCloudMap.get(lowerTitleWord);
						Integer yearWordOccurence = yearTitleCloudMap.get(lowerTitleWord);
						if(yearWordOccurence == null) {
							yearWordOccurence = 1;
						} else {
							yearWordOccurence += 1;
						}
						
						if(globalWordOccurence == null) {
							globalWordOccurence = 1;
						} else {
							globalWordOccurence += 1;
						}
						
						yearTitleCloudMap.put(lowerTitleWord, yearWordOccurence);
						globalTitleCloudMap.put(lowerTitleWord,globalWordOccurence);
					}
				}
			}
			
			JsonArray globalTitleCloudJsonArray = prepareGlobalTitleCloud(globalTitleCloudMap);
			JsonObject yearsTitleCloudJson = prepareYearsTitleCloud(yearTitleCloudMapContainer);
			
			titleCloudJson.add("global", globalTitleCloudJsonArray);
			titleCloudJson.add("yearly", yearsTitleCloudJson);
			
			
		} catch(SQLException e) {
			throw new ServletException("Error retrieving publication information field from ResultSet",e);
		}
		
		return titleCloudJson;
	}
	
	private JsonObject prepareYearsTitleCloud(Map<Integer,Map<String,Integer>> yearTitleMapContainer) {
		JsonObject yearsTitleCloudJson = new JsonObject();
		
		JsonArray yearsJson = new JsonArray();
		for(Integer year : yearTitleMapContainer.keySet()) {
			Map<String,Integer> yearTitleWordMap = yearTitleMapContainer.get(year);
			
			JsonArray yearWordsJson = new JsonArray();
			for(String word : yearTitleWordMap.keySet()) {
				Integer occurence = yearTitleWordMap.get(word);
				JsonObject wordJson = new JsonObject();
				wordJson.addProperty("text", word);
				wordJson.addProperty("size", occurence);
				yearWordsJson.add(wordJson);
			}
			
			yearsTitleCloudJson.add(year.toString(), yearWordsJson);
			yearsJson.add(new JsonPrimitive(year));
		}
		yearsTitleCloudJson.add("years",yearsJson);
		
		return yearsTitleCloudJson;
	}
	
	private JsonArray prepareGlobalTitleCloud(Map<String,Integer> globalTitleWordCloudMap) {
		System.out.println(globalTitleWordCloudMap.size());
		JsonArray globalWordJsonArray = new JsonArray();
		
		for(String word : globalTitleWordCloudMap.keySet()) {
			Integer occurence = globalTitleWordCloudMap.get(word);
			
			JsonObject wordJson = new JsonObject();
			wordJson.addProperty("text", word);
			wordJson.addProperty("size", occurence);
			globalWordJsonArray.add(wordJson);
		}
		
		return globalWordJsonArray;
	}
	
	

}
