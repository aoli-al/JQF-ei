# DATASET = ["ant", "maven", "bcel", "rhino", "closure"]
DATASET = ["closure"]
ALGORITHM = ["zest-fast", "ei-fast"]
ALGORITHM = ["ei-fast"]

TEST_CLASS_PREFIX = "edu.berkeley.cs.jqf.examples."
DATASET_TEST_CLASS_MAPPING = {
    "ant": TEST_CLASS_PREFIX + "ant.ProjectBuilderTest",
    "maven": TEST_CLASS_PREFIX + "maven.ModelReaderTest",
    "bcel": TEST_CLASS_PREFIX + "bcel.ParserTest",
    "closure": TEST_CLASS_PREFIX + "closure.CompilerTest",
    "rhino": TEST_CLASS_PREFIX + "rhino.CompilerTest"
}
# ALGORITHM = ["zest-fast", "ei-fast", "zest-no-count", "ei-no-count"]
