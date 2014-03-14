import static org.junit.Assert.*;

import java.io.*;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.Comparator;
import java.util.HashSet;
import java.util.Iterator;
import java.util.List;
import java.util.Set;
import java.util.StringTokenizer;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;

public class SpeakToCommandLine {

	private ArrayList<FunctionalAgent> agents;
	private String FILE_NAME = "/home/preznik/dev/mitosis/agent/docker/serf/test/test.txt";
	
	
	@After
	public void removeFile() {
		File file = new File(FILE_NAME);
		assertTrue(file.delete());
	}
	
	@Before
	public void collectMembers() throws Exception {
		ProcessBuilder builder = new ProcessBuilder(
				"serf", "members");
		
		builder.redirectErrorStream(true);
		Process p = builder.start();
		BufferedReader r = new BufferedReader(new InputStreamReader(p.getInputStream()));
		String line;
		agents = new ArrayList<FunctionalAgent>();
		while (true) {
			line = r.readLine();
			if (line == null) {
				break;
			}
			try {
				agents.add(new FunctionalAgent(line));
			}
			catch (NotFunctionalAgentException e){
				//Ignore
				
			}
		}
	}
	
	
	
	@Before
	public void sendMessage() throws Exception {
		ProcessBuilder builder = new ProcessBuilder(
				"serf", "event", "TEST_BREAK_FILE");
		
		builder.redirectErrorStream(true);
		Process p = builder.start();
	}
	
	@Test
	public void members() throws IOException, InterruptedException {
		Thread.sleep(7000);
		ArrayList<IPAndMessage> messages = new ArrayList<IPAndMessage>();

		BufferedReader reader = new BufferedReader(new FileReader(new File(FILE_NAME)));
		String temp = reader.readLine();
		while (temp != null) {
			StringTokenizer tokenizer = new StringTokenizer(temp);
			String ip = tokenizer.nextToken();
			String message = tokenizer.nextToken();
			IPAndMessage ipAndMessage = new IPAndMessage();
			ipAndMessage.ip = ip;
			ipAndMessage.message = message;
			messages.add(ipAndMessage);
			temp = reader.readLine();
		}
		
		Collections.sort(agents);
		Collections.sort(messages);
		
		Iterator<FunctionalAgent> iteratorAgents = agents.iterator();
		Iterator<IPAndMessage> iteratorMessages = messages.iterator();
		while (iteratorAgents.hasNext()) {
			FunctionalAgent temp1 = iteratorAgents.next();
			IPAndMessage temp2 = iteratorMessages.next();
			assertTrue(temp1.ip(temp2.ip));
		}
		reader.close();
	}
	
	class IPAndMessage implements Comparable<IPAndMessage>
	{
		public String ip;
		public String message;
		
		
		@Override
		public int hashCode() {
			final int prime = 31;
			int result = 1;
			result = prime * result + getOuterType().hashCode();
			result = prime * result + ((ip == null) ? 0 : ip.hashCode());
			result = prime * result
					+ ((message == null) ? 0 : message.hashCode());
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
			IPAndMessage other = (IPAndMessage) obj;
			if (!getOuterType().equals(other.getOuterType()))
				return false;
			if (ip == null) {
				if (other.ip != null)
					return false;
			} else if (!ip.equals(other.ip))
				return false;
			if (message == null) {
				if (other.message != null)
					return false;
			} else if (!message.equals(other.message))
				return false;
			return true;
		}
		@Override
		public String toString() {
			return "IPAndMessage [ip=" + ip + ", message=" + message + "]";
		}
		private SpeakToCommandLine getOuterType() {
			return SpeakToCommandLine.this;
		}
		@Override
		public int compareTo(IPAndMessage o) {
			return ip.compareTo(o.ip);
		}
		
		
	}
}
