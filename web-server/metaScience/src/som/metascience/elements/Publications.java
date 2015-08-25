package som.metascience.elements;

import com.google.gson.JsonObject;

public class Publications {
	
	private int year;
	private int articles = 0;
	private int articlePages = 0;
	private int books = 0;
	private int bookPages = 0;
	private int incollections = 0;
	private int incollectionPages = 0;
	private int inproceedings = 0;
	private int inproceedingPages = 0;
	private int masterthesis = 0;
	private int masterthesisPages = 0;
	private int phdthesis = 0;
	private int phdthesisPages = 0;
	private int proceedings = 0;
	private int proceedingPages = 0;
	private int websites = 0;
	// not sure about that !
	private int websitesPages = 0;
	
	public Publications(int year) {
		this.year = year;
	}

	public int getArticles() {
		return articles;
	}

	public void setArticles(int articles, Integer pages) {
		this.articles = articles;
		if(pages != null)
			this.articlePages = pages;
	}

	public int getBooks() {
		return books;
	}

	public void setBooks(int books,Integer pages) {
		this.books = books;
		this.bookPages = pages;
	}

	public int getIncollections() {
		return incollections;
	}

	public void setIncollections(int incollections, Integer pages) {
		this.incollections = incollections;
		this.incollectionPages = pages;
	}

	public int getInproceedings() {
		return inproceedings;
	}

	public void setInproceedings(int inprocedings, Integer pages) {
		this.inproceedings = inprocedings;
		this.inproceedingPages = pages;
	}

	public int getMasterthesis() {
		return masterthesis;
	}

	public void setMasterthesis(int masterthesis, Integer pages) {
		this.masterthesis = masterthesis;
		this.masterthesisPages = pages;
	}

	public int getPhdthesis() {
		return phdthesis;
	}

	public void setPhdthesis(int phdthesis, Integer pages) {
		this.phdthesis = phdthesis;
		this.phdthesisPages = pages;
	}

	public int getProceedings() {
		return proceedings;
	}

	public void setProceedings(int proceedings, Integer pages) {
		this.proceedings = proceedings;
		this.proceedingPages = pages;
	}

	public int getWebsites() {
		return websites;
	}

	public void setWebsites(int websites, Integer pages) {
		this.websites = websites;
		this.websitesPages = pages;
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

	public int getYear() {
		return year;
	}

	public int getArticlePages() {
		return articlePages;
	}

	public int getBookPages() {
		return bookPages;
	}

	public int getIncollectionPages() {
		return incollectionPages;
	}

	public int getInproceedingPages() {
		return inproceedingPages;
	}

	public int getMasterthesisPages() {
		return masterthesisPages;
	}

	public int getPhdthesisPages() {
		return phdthesisPages;
	}

	public int getProceedingPages() {
		return proceedingPages;
	}

	public int getWebsitesPages() {
		return websitesPages;
	}
	
	

}
