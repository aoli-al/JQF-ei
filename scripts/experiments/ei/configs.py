# DATASET = ["ant", "bcel", "rhino", "closure"]
# DATASET = ["rhino", "closure"]
DATASET = [
    #  "ant", "maven", "bcel",
    "rhino", "closure", 
    #  "chocopy", "gson", "jackson"
]
# DATASET = ["bcel"]
# DATASET = ["rhino"]
# DATASET = ["bcel", "rhino", "closure"]
# DATASET = ["rhino", "closure"]
#  DATASET = ["chacopy"]
ALGORITHM = ["zest", "ei", "ei-no-havoc", "mix"]
#  ALGORITHM = ["ei-fast"]

GENERATOR = [
    'testWithGenerator',
    #  "testWithSmallReversedGenerator",
    #  "testWithLargeReversedGenerator",
]

TEST_CLASS_PREFIX = "edu.berkeley.cs.jqf.examples."
DATASET_TEST_CLASS_MAPPING = {
    "ant": TEST_CLASS_PREFIX + "ant.ProjectBuilderTest",
    "maven": TEST_CLASS_PREFIX + "maven.ModelReaderTest",
    "bcel": TEST_CLASS_PREFIX + "bcel.ParserTest",
    "closure": TEST_CLASS_PREFIX + "closure.CompilerTest",
    "rhino": TEST_CLASS_PREFIX + "rhino.CompilerTest",
    "chocopy": TEST_CLASS_PREFIX + "chocopy.SemanticAnalysisTest",
    "gson": TEST_CLASS_PREFIX + "gson.JsonTest",
    "jackson": TEST_CLASS_PREFIX + "jackson.JsonTest",

}
