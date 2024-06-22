package edu.berkeley.cs.jqf.examples.readorder;

import com.pholser.junit.quickcheck.generator.GenerationStatus;
import com.pholser.junit.quickcheck.generator.Generator;
import com.pholser.junit.quickcheck.random.SourceOfRandomness;
import readorder.TreeProcessor;

public class NodeGenerator extends Generator<TreeProcessor.Node> {

    public NodeGenerator() {
        super(TreeProcessor.Node.class);
    }

    @Override
    public TreeProcessor.Node generate(SourceOfRandomness sourceOfRandomness, GenerationStatus generationStatus) {
        TreeProcessor.Node left = null;
        TreeProcessor.Node right = null;
        if (sourceOfRandomness.nextInt() % 2 == 0) {
            left = generate(sourceOfRandomness, generationStatus);
        }
        if (sourceOfRandomness.nextInt() % 2 == 0) {
            right = generate(sourceOfRandomness, generationStatus);
        }
        return new TreeProcessor.Node(left, right, sourceOfRandomness.nextByte((byte) 0, (byte) 100));
    }
}
