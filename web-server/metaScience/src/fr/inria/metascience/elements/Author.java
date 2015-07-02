package fr.inria.metascience.elements;

public class Author {
	
	
	private String name;
	private int numberPublications;
	
	public Author(String name, int numberPublications) {
		this.name = name;
		this.numberPublications = numberPublications;
	}
	
	public int getNumberPublications() {
		return this.numberPublications;
	}
	
	public String getName() {
		return this.name;
	}

}
