package fr.inria.atlanmod.conferenceanalysis.services.graph;

import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;

/**
 * This class generates a GEXF file from a database.
 * 
 * @author Javier Canovas (javier.canovas@inria.fr)
 *
 */
public class GraphGenerator {
	public static void main(String[] args) throws IOException {
		Connection conn = null;
		Statement stmt = null;
		ResultSet rSet = null;

		HashMap<String, Node> labels = new HashMap<>();
		HashMap<String, Node> users = new HashMap<>();
		HashMap<String, Edge> edges = new HashMap<>();
		HashMap<String, Edge> cachedEdges = new HashMap<>();

		try {
			Class.forName("com.mysql.jdbc.Driver");
			conn = DriverManager.getConnection("jdbc:mysql://atlanmodexp.info.emn.fr:13506/vissoft14?user=root&password=coitointerrotto");
			stmt = conn.createStatement();
			//rSet = stmt.executeQuery("select label_id, user_id from vissoft14.label_issue_comments where label_id is not null");
			rSet = stmt.executeQuery("select rl.name as label_name, u.login as user_login from vissoft14.label_issue_comments lic, vissoft14.repo_labels rl, vissoft14.users u where label_id is not null and lic.label_id = rl.id and lic.user_id = u.id");

			int nodeCounter = 0;
			int edgeCounter = 0;

			while(rSet.next()) {
				String labelId = rSet.getString("label_name");
				Node labelNode = labels.get(labelId);
				String internalLabelId = null;
				if(labelNode == null) {
					internalLabelId = String.valueOf(nodeCounter++);
					labelNode = new Node(internalLabelId, labelId, 255, 0, 0, 300);
					labels.put(labelId, labelNode);
				} else {
					internalLabelId = labelNode.getId();
					//labelNode.setSize(labelNode.getSize() + 1);
				}

				String userId = rSet.getString("user_login");
				Node userNode = users.get(userId);
				String internalUserId = null;
				if(userNode == null) {
					internalUserId = String.valueOf(nodeCounter++);
					userNode = new Node(String.valueOf(internalUserId), userId, 0, 255, 0, 30);
					users.put(userId, userNode);
				} else {
					internalUserId = userNode.getId();
					userNode.setSize(userNode.getSize() + 1);
				}

				String cachedEdgeId = internalLabelId + "-" + internalUserId;
				if(cachedEdges.get(cachedEdgeId) == null) {
					String internalEdgeId = String.valueOf(edgeCounter++);
					Edge edge = new Edge(internalEdgeId, internalLabelId, internalUserId);
					edges.put(internalEdgeId, edge);
					cachedEdges.put(cachedEdgeId, edge);
				}

			}
			conn.close();
			stmt.close();
			rSet.close();
		} catch (ClassNotFoundException e1) {
			System.err.println("The mysql driver could not be instantiated");
			e1.printStackTrace();
		} catch (SQLException e) {
			System.err.println("There was and error in mysql");
			e.printStackTrace();
		}

		List<Node> nodesGen = new ArrayList<>();
		nodesGen.addAll(labels.values());
		nodesGen.addAll(users.values());

		List<Edge> edgesGen = new ArrayList<>();
		edgesGen.addAll(edges.values());
		GexfGenerator generator = new GexfGenerator(nodesGen, edgesGen);
		String gexfString = generator.generate();

		FileWriter fw = new FileWriter(new File("../web/data.gexf"));
		fw.write(gexfString);
		fw.close();
	}
}
