package edu.berkeley.cs.jqf.fuzz.ei.input;

import edu.berkeley.cs.jqf.fuzz.util.Coverage;
import edu.berkeley.cs.jqf.fuzz.util.Metric;
import org.eclipse.collections.impl.set.mutable.primitive.IntHashSet;

import java.io.File;
import java.util.Random;

import static java.lang.Math.ceil;
import static java.lang.Math.log;

/**
 * A candidate or saved test input that maps objects of type K to bytes.
 */
public abstract class Input<K> implements Iterable<Integer> {

    /**
     * The file where this input is saved.
     *
     * <p>This field is null for inputs that are not saved.</p>
     */
    public File saveFile = null;

    /**
     * An ID for a saved input.
     *
     * <p>This field is -1 for inputs that are not saved.</p>
     */
    public int id;

    /**
     * The description for this input.
     *
     * <p>This field is modified by the construction and mutation
     * operations.</p>
     */
    public String desc;

    /**
     * The run coverage for this input, if the input is saved.
     *
     * <p>This field is null for inputs that are not saved.</p>
     */
    public Metric coverage = null;

    /**
     * The number of non-zero elements in `coverage`.
     *
     * <p>This field is -1 for inputs that are not saved.</p>
     *
     * <p></p>When this field is non-negative, the information is
     * redundant (can be computed using {@link Coverage#getNonZeroCount()}),
     * but we store it here for performance reasons.</p>
     */
    public int nonZeroCoverage = -1;

    /**
     * The number of mutant children spawned from this input that
     * were saved.
     *
     * <p>This field is -1 for inputs that are not saved.</p>
     */
    public int offspring = -1;

    /**
     * The set of coverage keys for which this input is
     * responsible.
     *
     * <p>This field is null for inputs that are not saved.</p>
     *
     * <p>Each coverage key appears in the responsibility set
     * of exactly one saved input, and all covered keys appear
     * in at least some responsibility set. Hence, this list
     * needs to be kept in-sync with {@link #responsibleInputs}.</p>
     */
    public IntHashSet responsibilities = null;

    /**
     * Create an empty input.
     */
    public Input() {
        desc = "random";
    }

    /**
     * Create a copy of an existing input.
     *
     * @param toClone the input map to clone
     */
    public Input(Input toClone) {
        desc = String.format("src:%06d", toClone.id);
    }

    public abstract int getOrGenerateFresh(K key, Random random);
    public abstract int size();
    public abstract Input fuzz(Random random);
    public abstract void gc();

    /**
     * Returns whether this input should be favored for fuzzing.
     *
     * <p>An input is favored if it is responsible for covering
     * at least one branch.</p>
     *
     * @return whether or not this input is favored
     */
    public boolean isFavored() {
        return responsibilities.size() > 0;
    }

    /**
     * Sample from a geometric distribution with given mean.
     *
     * Utility method used in implementing mutation operations.
     *
     * @param random a pseudo-random number generator
     * @param mean the mean of the distribution
     * @return a randomly sampled value
     */
    public static int sampleGeometric(Random random, double mean) {
        double p = 1 / mean;
        double uniform = random.nextDouble();
        return (int) ceil(log(1 - uniform) / log(1 - p));
    }
}

