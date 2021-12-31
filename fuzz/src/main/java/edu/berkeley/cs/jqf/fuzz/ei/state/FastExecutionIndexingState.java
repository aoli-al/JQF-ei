package edu.berkeley.cs.jqf.fuzz.ei.state;

import janala.instrument.FastCoverageListener;

// This logic is similar to FastNonCollidingCoverage.
// We should consider merging them.
public class FastExecutionIndexingState extends AbstractExecutionIndexingState implements FastCoverageListener {
    @Override
    public void logMethodBegin(int iid) {
        setLastEventIid(iid);
        pushCall(iid);
    }

    @Override
    public void logMethodEnd(int iid) {
        setLastEventIid(iid);
        popReturn(iid);
    }

    @Override
    public void logJump(int iid, int branch) {
        setLastEventIid(iid + branch);
    }

    @Override
    public void logLookUpSwitch(int value, int iid, int dflt, int[] cases) {
        // Compute arm index or else default
        int arm = cases.length;
        for (int i = 0; i < cases.length; i++) {
            if (value == cases[i]) {
                arm = i;
                break;
            }
        }
        arm++;
        setLastEventIid(iid + arm);
    }

    @Override
    public void logTableSwitch(int value, int iid, int min, int max, int dflt) {
        int arm = 1 + max - min;
        if (value >= min && value <= max) {
            arm = value - min;
        }
        arm++;
        setLastEventIid(iid + arm);
    }
}
