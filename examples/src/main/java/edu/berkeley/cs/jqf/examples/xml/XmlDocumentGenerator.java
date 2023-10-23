package edu.berkeley.cs.jqf.examples.xml;

import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;
import javax.xml.parsers.ParserConfigurationException;
import javax.xml.transform.Transformer;
import javax.xml.transform.TransformerException;
import javax.xml.transform.TransformerFactory;
import javax.xml.transform.dom.DOMSource;
import javax.xml.transform.stream.StreamResult;
import java.io.IOException;
import java.io.StringWriter;

import com.pholser.junit.quickcheck.generator.GenerationStatus;
import com.pholser.junit.quickcheck.generator.Generator;
import com.pholser.junit.quickcheck.generator.Size;
import com.pholser.junit.quickcheck.internal.GeometricDistribution;
import com.pholser.junit.quickcheck.random.SourceOfRandomness;
import edu.berkeley.cs.jqf.examples.common.AlphaStringGenerator;
import edu.berkeley.cs.jqf.examples.common.Dictionary;
import edu.berkeley.cs.jqf.examples.common.DictionaryBackedStringGenerator;
import org.junit.Assume;
import org.w3c.dom.DOMException;
import org.w3c.dom.Document;
import org.w3c.dom.Element;
import org.w3c.dom.Text;

/**
 * A generator for XML documents.
 *
 * @author Rohan Padhye
 */
public class XmlDocumentGenerator extends Generator<String> {

    private static DocumentBuilderFactory documentBuilderFactory =
            DocumentBuilderFactory.newInstance();

    private static GeometricDistribution geometricDistribution =
            new GeometricDistribution();

    /** Mean number of child nodes for each XML element. */
    private static final double MEAN_NUM_CHILDREN = 4;

    /** Mean number of attributes for each XML element. */
    private static final double MEAN_NUM_ATTRIBUTES = 2;

    /**
     * Minimum size of XML tree.
     * @see {@link #configure(Size)}
     */
    private int minDepth = 0;

    /**
     * Maximum size of XML tree.
     * @see {@link #configure(Size)}
     */
    private int maxDepth = 4;

    private Generator<String> stringGenerator = new AlphaStringGenerator();

    public XmlDocumentGenerator() {
        super(String.class);
    }

    /**
     * Configures the minimum/maximum size of the XML document.
     *
     * This method is not usually invoked directly. Instead, use
     * the `@Size` annotation on fuzzed parameters to configure
     * automatically.
     *
     * @param size the min/max size of the XML document
     */
    public void configure(Size size) {
        minDepth = size.min();
        maxDepth = size.max();
    }


    /**
     * Configures the string generator used by this generator to use
     * a dictionary. This is useful for overriding the default
     * arbitrary string generator with something that pulls tag names
     * from a predefined list.
     *
     * @param dict the dictionary file
     * @throws IOException if the dictionary file cannot be read
     */
    public void configure(Dictionary dict) throws IOException {
        stringGenerator = new DictionaryBackedStringGenerator(dict.value(), stringGenerator);
    }

    /**
     * Generators a random XML document.
     * @param random a source of pseudo-random values
     * @param status generation state
     * @return a randomly-generated XML document
     */
    @Override
    public String generate(SourceOfRandomness random, GenerationStatus status) {
        DocumentBuilder builder;
        try {
            builder = documentBuilderFactory.newDocumentBuilder();
        } catch (ParserConfigurationException e) {
            throw new RuntimeException(e);
        }

        if (stringGenerator == null) {
            stringGenerator = gen().type(String.class);
        }

        Document document = builder.newDocument();
        try {
            populateDocument(document, random, status);
        } catch (DOMException e) {
            Assume.assumeNoException(e);
        }

        try {
            TransformerFactory transformerFactory = TransformerFactory.newInstance();
            Transformer transformer = transformerFactory.newTransformer();
            StringWriter stream = new StringWriter();
            transformer.transform(new DOMSource(document), new StreamResult(stream));
            return stream.toString();
        } catch (TransformerException e) {
            throw new RuntimeException(e);
        }
    }

    private String makeString(SourceOfRandomness random, GenerationStatus status) {
        return stringGenerator.generate(random, status);
    }

    private Document populateDocument(Document document, SourceOfRandomness random, GenerationStatus status) {
        Element root = document.createElement(makeString(random, status));
        populateElement(document, root, random, status, 0);
        document.appendChild(root);
        return document;
    }

    private void populateElement(Document document, Element elem, SourceOfRandomness random, GenerationStatus status, int depth) {
        // Add attributes
        int numAttributes = Math.max(0, geometricDistribution.sampleWithMean(MEAN_NUM_ATTRIBUTES, random)-1);
        for (int i = 0; i < numAttributes; i++) {
            elem.setAttribute(makeString(random, status), makeString(random, status));
        }
        // Make children
        if (depth < minDepth || (depth < maxDepth && random.nextBoolean())) {
            int numChildren = Math.max(0, geometricDistribution.sampleWithMean(MEAN_NUM_CHILDREN, random)-1);
            for (int i = 0; i < numChildren; i++) {
                Element child = document.createElement(makeString(random, status));
                populateElement(document, child, random, status, depth+1);
                elem.appendChild(child);
            }
        } else if (random.nextBoolean()) {
            // Add text
            Text text = document.createTextNode(makeString(random, status));
            elem.appendChild(text);
        } else if (random.nextBoolean()) {
            // Add text as CDATA
            Text text = document.createCDATASection(makeString(random, status));
            elem.appendChild(text);
        }
    }
}
