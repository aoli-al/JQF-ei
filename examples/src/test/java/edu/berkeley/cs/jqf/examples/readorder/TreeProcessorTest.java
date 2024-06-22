package edu.berkeley.cs.jqf.examples.readorder;

import com.pholser.junit.quickcheck.From;
import edu.berkeley.cs.jqf.fuzz.Fuzz;
import edu.berkeley.cs.jqf.fuzz.JQF;
import org.junit.runner.RunWith;
import readorder.TreeProcessor;

@RunWith(JQF.class)
public class TreeProcessorTest {
    @Fuzz
    public void testWithGeneratorLTR(@From(NodeGenerator.class)TreeProcessor.Node node) {
        TreeProcessor.processLTR(node);
    }

    @Fuzz
    public void testWithGeneratorRTL(@From(NodeGenerator.class)TreeProcessor.Node node) {
        TreeProcessor.processRTL(node);
    }
}
