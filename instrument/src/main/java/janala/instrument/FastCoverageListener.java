package janala.instrument;

public abstract class FastCoverageListener {
    static class Default extends FastCoverageListener {}

    public void logMethodBegin(int iid) {}

    public void logReturn(int iid) {}

    public void logJump(int iid, int branch) {}

    public void logLookUpSwitch(int value, int iid, int dflt, int[] cases) {}

    public void logTableSwitch(int value, int iid, int min, int max, int dflt) {}

    public static FastCoverageListener DEFAULT = new Default();
}
