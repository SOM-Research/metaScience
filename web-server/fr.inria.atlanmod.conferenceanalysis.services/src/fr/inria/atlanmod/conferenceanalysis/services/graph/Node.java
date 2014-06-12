package fr.inria.atlanmod.conferenceanalysis.services.graph;

/**
 * Auxiliar class to represent nodes in GEXF
 * 
 * @author Javier Canovas (javier.canovas@inria.fr)
 *
 */
public class Node {
	String id;
	String label;
	int colorRed;
	int colorGreen;
	int colorBlue;
	int size;
	
	public Node(String id, String label, int red, int green, int blue, int size) {
		this.setId(id);
		this.setLabel(label);
		this.setColor(red, green, blue);
		this.setSize(size);
	}
	public String getId() {
		return id;
	}
	public void setId(String id) {
		if(id == null || id.equals("")) 
			throw new IllegalArgumentException("The id cannot be null");
		this.id = id;
	}
	public int getSize() {
		return size;
	}
	public void setSize(int size) {
		if(size < 0) 
			throw new IllegalArgumentException("The size cannot be negative");
		this.size = size;
	}
	public String getLabel() {
		return label;
	}
	public void setLabel(String label) {
		if(label == null || label.equals("")) 
			throw new IllegalArgumentException("The label cannot be null");
		this.label = label;
	}
	public int getColorRed() {
		return colorRed;
	}
	public int getColorGreen() {
		return colorGreen;
	}
	public int getColorBlue() {
		return colorBlue;
	}
	public void setColor(int red, int green, int blue) {
		if(red < 0 || red > 255 || green < 0 || green > 255 || blue < 0 || blue > 255) 
			throw new IllegalArgumentException("The color values should be between 0 and 255");
		this.colorRed = red;
		this.colorGreen = green;
		this.colorBlue = blue;
	}
	
}
