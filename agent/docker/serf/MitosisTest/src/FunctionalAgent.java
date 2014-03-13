import java.util.StringTokenizer;


public class FunctionalAgent implements Comparable<FunctionalAgent> {

	private String id;
	private String ip;
	private String role;

	public FunctionalAgent(String id, String port, String role) {
		this.id = id;
		int index = port.indexOf(':');
		this.ip = port.substring(0, index);
		this.role = role;
	}

	public FunctionalAgent(String line) {
		StringTokenizer tokenizer = new StringTokenizer(line);
		id = tokenizer.nextToken();
		ip = tokenizer.nextToken();
		int index = ip.indexOf(':');
		this.ip = ip.substring(0, index);
		tokenizer.nextToken();
		role = tokenizer.nextToken();
		if(!role.endsWith("functional_agent"))
			throw new NotFunctionalAgentException();
	}
	
	
	
	@Override
	public String toString() {
		return "FunctionalAgent [id=" + id + ", ip=" + ip + ", role="
				+ role + "]";
	}

	@Override 
	public boolean equals(Object obj) 
	{
		FunctionalAgent other = (FunctionalAgent)obj;
		return id.equals(other.id) && ip.equals(other.ip) && role.equals(other.role);
	}

	public boolean ip(String ip) {
		return this.ip.equals(ip);
	}

	public int compareTo(FunctionalAgent functionalAgent) {
		return this.ip.compareTo(functionalAgent.ip);
	}
	
}
