package edu.berkeley.cs.jqf.fuzz.ei;

import edu.berkeley.cs.jqf.fuzz.ei.input.Input;
import edu.berkeley.cs.jqf.fuzz.guidance.Guidance;
import edu.berkeley.cs.jqf.fuzz.guidance.GuidanceException;
import edu.berkeley.cs.jqf.fuzz.guidance.Result;
import edu.berkeley.cs.jqf.instrument.tracing.events.TraceEvent;

import java.io.IOException;
import java.io.InputStream;
import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Date;
import java.util.Deque;
import java.util.function.Consumer;

public class GuidanceBase implements Guidance {
    /** Current input that's running -- valid after getInput() and before handleResult(). */
    protected Input<?> currentInput;

    /** Queue of seeds to fuzz. */
    protected Deque<Input> seedInputs = new ArrayDeque<>();

    /** Set of saved inputs to fuzz. */
    protected ArrayList<Input> savedInputs = new ArrayList<>();

    /** Whether the application has more than one thread running coverage-instrumented code */
    protected boolean multiThreaded = false;

    /** Blind fuzzing -- if true then the queue is always empty. */
    protected boolean blind;

    /** The number of trials completed. */
    protected long numTrials = 0;

    /** Index of currentInput in the savedInputs -- valid after seeds are processed (OK if this is inaccurate). */
    protected int currentParentInputIdx = 0;

    /** Baseline number of mutated children to produce from a given parent input. */
    protected final int NUM_CHILDREN_BASELINE = 50;

    /**
     * Conditionally run a method using synchronization.
     *
     * This is used to handle multi-threaded fuzzing.
     */
    protected void conditionallySynchronize(boolean cond, Runnable task) {
        if (cond) {
            synchronized (this) {
                task.run();
            }
        } else {
            task.run();
        }
    }

    @Override
    public InputStream getInput() throws IllegalStateException, GuidanceException {
        conditionallySynchronize(multiThreaded, () -> {
            // Clear coverage stats for this run
            runCoverage.clear();

            // Choose an input to execute based on state of queues
            if (!seedInputs.isEmpty()) {
                // First, if we have some specific seeds, use those
                currentInput = seedInputs.removeFirst();

                // Hopefully, the seeds will lead to new coverage and be added to saved inputs

            } else if (savedInputs.isEmpty()) {
                // If no seeds given try to start with something random
                if (!blind && numTrials > 100_000) {
                    throw new GuidanceException("Too many trials without coverage; " +
                            "likely all assumption violations");
                }

                // Make fresh input using either list or maps
                // infoLog("Spawning new input from thin air");
                currentInput = createFreshInput();
            } else {
                // The number of children to produce is determined by how much of the coverage
                // pool this parent input hits
                Input currentParentInput = savedInputs.get(currentParentInputIdx);
                int targetNumChildren = getTargetChildrenForParent(currentParentInput);
                if (numChildrenGeneratedForCurrentParentInput >= targetNumChildren) {
                    // Select the next saved input to fuzz
                    currentParentInputIdx = (currentParentInputIdx + 1) % savedInputs.size();

                    // Count cycles
                    if (currentParentInputIdx == 0) {
                        completeCycle();
                    }

                    numChildrenGeneratedForCurrentParentInput = 0;
                }
                Input parent = savedInputs.get(currentParentInputIdx);

                // Fuzz it to get a new input
                // infoLog("Mutating input: %s", parent.desc);
                currentInput = parent.fuzz(random);
                numChildrenGeneratedForCurrentParentInput++;

                // Write it to disk for debugging
                try {
                    writeCurrentInputToFile(currentInputFile);
                } catch (IOException ignore) {
                }

                // Start time-counting for timeout handling
                this.runStart = new Date();
                this.branchCount = 0;
            }
        });

        return createParameterStream();
    }

    protected int getTargetChildrenForParent(Input parentInput) {
        // Baseline is a constant
        int target = NUM_CHILDREN_BASELINE;

        // We like inputs that cover many things, so scale with fraction of max
        if (maxCoverage > 0) {
            target = (NUM_CHILDREN_BASELINE * parentInput.nonZeroCoverage) / maxCoverage;
        }

        // We absolutely love favored inputs, so fuzz them more
        if (parentInput.isFavored()) {
            target = target * NUM_CHILDREN_MULTIPLIER_FAVORED;
        }

        return target;
    }


    protected Input<?> createFreshInput() {
        return null;
    }

    @Override
    public boolean hasInput() {
        return false;
    }

    @Override
    public void handleResult(Result result, Throwable error) throws GuidanceException {

    }

    @Override
    public Consumer<TraceEvent> generateCallBack(Thread thread) {
        return null;
    }
}
