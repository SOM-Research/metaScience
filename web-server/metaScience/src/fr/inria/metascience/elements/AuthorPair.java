package fr.inria.metascience.elements;

public class AuthorPair {

	private String sourceAuthorId;
	private String targetAuthorId;
	
	public AuthorPair(String source, String target) {
		this.sourceAuthorId = source;
		this.targetAuthorId = target;
	}
	
	
	public String getSource() {
		return this.sourceAuthorId;
	}
	
	public String getTarget() {
		return this.targetAuthorId;
	}


	@Override
	public int hashCode() {
		final int prime = 31;
		int result = 1;
		result = prime * result
				+ ((sourceAuthorId == null) ? 0 : sourceAuthorId.hashCode());
		result = prime * result
				+ ((targetAuthorId == null) ? 0 : targetAuthorId.hashCode());
		return result;
	}


	@Override
	public boolean equals(Object obj) {
		if (this == obj)
			return true;
		if (obj == null)
			return false;
		if (getClass() != obj.getClass())
			return false;
		AuthorPair other = (AuthorPair) obj;
		if (sourceAuthorId == null) {
			if (other.sourceAuthorId != null)
				return false;
		} else if (!sourceAuthorId.equals(other.sourceAuthorId))
			return false;
		if (targetAuthorId == null) {
			if (other.targetAuthorId != null)
				return false;
		} else if (!targetAuthorId.equals(other.targetAuthorId))
			return false;
		
		
		
		return true;
	}
	
	
}
