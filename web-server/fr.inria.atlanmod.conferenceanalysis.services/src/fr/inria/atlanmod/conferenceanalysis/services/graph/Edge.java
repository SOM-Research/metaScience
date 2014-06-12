package fr.inria.atlanmod.conferenceanalysis.services.graph;

/**
 * Auxiliar class to represent edges in GEXF
 * 
 * @author Javier Canovas (javier.canovas@inria.fr)
 *
 */
public class Edge {
	String id;
	String source;
	String target;
	public Edge(String id, String source, String target) {
		this.setId(id);
		this.setSource(source);
		this.setTarget(target);
	}
	public String getId() {
		return id;
	}
	public void setId(String id) {
		if(id == null || id.equals("")) 
			throw new IllegalArgumentException("The id cannot be null");
		this.id = id;
	}
	public String getSource() {
		return source;
	}
	public void setSource(String source) {
		if(source == null || source.equals("")) 
			throw new IllegalArgumentException("The source cannot be null");
		this.source = source;
	}
	public String getTarget() {
		return target;
	}
	public void setTarget(String target) {
		if(target == null || target.equals("")) 
			throw new IllegalArgumentException("The target cannot be null");
		this.target = target;
	}
}
