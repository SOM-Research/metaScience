package fr.inria.atlanmod.conferenceanalysis.services.graph;

import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

/**
 * Given a list of nodes and edges, generates a GEXF
 * 
 * @author Javier Canovas (javier.canovas@inria.fr)
 *
 */
public class GexfGenerator {
	List<Node> nodes;
	List<Edge> edges;
	
	public GexfGenerator(List<Node> nodes, List<Edge> edges) {
		if(nodes == null || edges == null) 
			throw new IllegalArgumentException("The list of nodes or edges cannot be null");
		this.nodes = nodes;
		this.edges = edges;
	}
	
	/**
	 * Generates a GEXF from the nodes/edges lists. The position of the nodes is generated randomly
	 * 
	 * @return
	 */
	public String generate() {
		StringBuffer result = new StringBuffer();
		result.append("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n");
        result.append("<gexf xmlns=\"http://www.gephi.org/gexf\" xmlns:viz=\"http://www.gephi.org/gexf/viz\">\n");
        result.append("\t<graph type=\"static\">\n");
        
        result.append("\t\t<attributes class=\"node\" type=\"static\">\n");
        result.append("\t\t\t<attribute id=\"0\" title=\"label\" type=\"string\"/>\n");
        result.append("\t\t</attributes>\n");
        
        result.append("\t\t<nodes>\n");
        for(Node node: nodes) {
            result.append("\t\t\t<node id=\"" + node.getId() + "\" label=\"" + node.getLabel() + "\">\n");
            result.append("\t\t\t\t<viz:color b=\"" + node.getColorBlue() +"\" g=\"" + node.getColorGreen() +"\" r=\"" + node.getColorRed() +"\"/>\n");
            result.append("\t\t\t\t<viz:position x=\"" + (int) (Math.random() * 100) + "\" y=\"" + (int) (Math.random() * 100) + "\" z=\"" + (int) (Math.random() * 100) + "\"/>\n");
            result.append("\t\t\t\t<viz:size value=\"" + node.getSize() + "\"/>\n");
            result.append("\t\t\t\t<attvalues>\n");
            result.append("\t\t\t\t\t<attvalue id=\"0\" value=\"" + node.getLabel() + "\"/>\n");
            result.append("\t\t\t\t</attvalues>\n");
            result.append("\t\t\t</node>\n");
        }
        result.append("\t\t</nodes>\n");

        result.append("\t\t<edges>\n");
        for(Edge edge: edges) {
        	result.append("\t\t\t<edge id=\"" + edge.getId() + "\" source=\"" + edge.getSource() + "\" target=\"" + edge.getTarget() + "\">\n");
        	result.append("\t\t\t\t<viz:color b=\"0\" g=\"0\" r=\"0\"/>\n");
        	result.append("\t\t\t</edge>\n");
        }
        result.append("\t\t</edges>\n");
        result.append("\t</graph>\n");
        result.append("</gexf>\n");

        return result.toString();
	}
	
	public static void main(String[] args) throws IOException {
		Node u1 = new Node("1", "u1", 255, 0, 0, 5);
		Node u2 = new Node("2", "u2", 255, 0, 0, 5);
		Node u3 = new Node("3", "u3", 255, 0, 0, 5);
		Node u4 = new Node("4", "u4", 255, 0, 0, 5);
		List<Node> nodes = new ArrayList<>();
		nodes.add(u1);
		nodes.add(u2);
		nodes.add(u3);
		nodes.add(u4);
		
		Edge e1 = new Edge("1", "1", "2");
		Edge e2 = new Edge("2", "2", "3");
		Edge e3 = new Edge("3", "3", "4");
		List<Edge> edges = new ArrayList<>();
		edges.add(e1);
		edges.add(e2);
		edges.add(e3);
		
		GexfGenerator gen = new GexfGenerator(nodes, edges);
		String gexfString = gen.generate();
		
		FileWriter fw = new FileWriter(new File("../web/data.gexf"));
		fw.write(gexfString);
		fw.close();
		
	}
}
