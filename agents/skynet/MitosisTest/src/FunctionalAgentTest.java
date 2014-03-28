import static org.junit.Assert.*;

import org.junit.Before;
import org.junit.Test;


public class FunctionalAgentTest {

	private FunctionalAgent actual;

	@Before
	public void construct() {

		actual = new FunctionalAgent("cde409076bcb     172.17.0.3:7946    alive    role=functional_agent");
		FunctionalAgent expected = new FunctionalAgent("cde409076bcb", "172.17.0.3:888", "role=functional_agent");
		assertEquals(expected, actual);
	}
	
	@Test
	public void ip() {
		assertTrue(actual.ip("172.17.0.3"));
	}
}
