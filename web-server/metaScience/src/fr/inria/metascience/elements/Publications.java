package fr.inria.metascience.elements;

import com.google.gson.JsonObject;

public class Publications {
	
	private int year;
	private int articles = 0;
	private int books = 0;
	private int incollections = 0;
	private int inproceedings = 0;
	private int masterthesis = 0;
	private int phdthesis = 0;
	private int proceedings = 0;
	private int websites = 0;
	
	public Publications(int year) {
		this.year = year;
	}

	public int getArticles() {
		return articles;
	}

	public void setArticles(int articles) {
		this.articles = articles;
	}

	public int getBooks() {
		return books;
	}

	public void setBooks(int books) {
		this.books = books;
	}

	public int getIncollections() {
		return incollections;
	}

	public void setIncollections(int incollections) {
		this.incollections = incollections;
	}

	public int getInproceedings() {
		return inproceedings;
	}

	public void setInproceedings(int inprocedings) {
		this.inproceedings = inprocedings;
	}

	public int getMasterthesis() {
		return masterthesis;
	}

	public void setMasterthesis(int masterthesis) {
		this.masterthesis = masterthesis;
	}

	public int getPhdthesis() {
		return phdthesis;
	}

	public void setPhdthesis(int phdthesis) {
		this.phdthesis = phdthesis;
	}

	public int getProceedings() {
		return proceedings;
	}

	public void setProceedings(int proceedings) {
		this.proceedings = proceedings;
	}

	public int getWebsites() {
		return websites;
	}

	public void setWebsites(int websites) {
		this.websites = websites;
	}
	
	public JsonObject toJson() {
		JsonObject result = new JsonObject();
		
		result.addProperty("year",this.year);
		result.addProperty("articles", this.articles);
		result.addProperty("books", this.books);
		result.addProperty("incollections", this.incollections);
		result.addProperty("inproceedings", this.inproceedings);
		result.addProperty("masterthesis", this.masterthesis);
		result.addProperty("phdthesis", this.phdthesis);
		result.addProperty("proceedings", this.proceedings);
		result.addProperty("websites", this.websites);
		
		return result;
	}

}
