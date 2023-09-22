package edu.berkeley.cs.jqf.examples.jython;


import com.pholser.junit.quickcheck.From;
import edu.berkeley.cs.jqf.examples.chocopy.ChocoPySemanticGenerator;
import edu.berkeley.cs.jqf.examples.python.PythonGenerator;
import edu.berkeley.cs.jqf.fuzz.Fuzz;
import edu.berkeley.cs.jqf.fuzz.JQF;
import edu.berkeley.cs.jqf.fuzz.guidance.TimeoutException;
import org.junit.runner.RunWith;
import org.python.core.PyException;
import org.python.core.PySyntaxError;
import org.python.util.PythonInterpreter;

@RunWith(JQF.class)
public class JythonInterpreterTest {
    @Fuzz
    public void testWithGenerator(@From(PythonGenerator.class) String code) throws Throwable {
        try (PythonInterpreter interp = new PythonInterpreter()) {
            interp.exec(code);
        } catch (PyException e) {
            if (e.getCause() instanceof TimeoutException) {
                throw e.getCause();
            }
        }
    }
}
