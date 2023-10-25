package edu.berkeley.cs.jqf.examples.chocopy;

import com.pholser.junit.quickcheck.generator.GenerationStatus;
import com.pholser.junit.quickcheck.generator.Generator;
import com.pholser.junit.quickcheck.random.SourceOfRandomness;
import org.apache.commons.lang3.StringUtils;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.function.Function;

import static org.junit.Assume.assumeTrue;

public class ReversedChocoPySemanticGenerator extends Generator<String> {
    public ReversedChocoPySemanticGenerator() {
        super(String.class); // Register type of generated object

        // Read parameters from system properties
        maxIdentifiers = Integer.getInteger(identifierProp, 3);
        maxItems = Integer.getInteger(itemsProp, 3);
        maxDepth = Integer.getInteger(depthProp, 3);
        maxBound = 4;
        assert(maxIdentifiers > 0);
        assert(maxItems > 0);
        assert(maxDepth > 0);

        // Create set of fixed identifiers
        generateIdentifiers(maxBound);
    }

    private final String identifierProp = "maxIdentifiers";
    private final String itemsProp = "maxItems";
    private final String depthProp = "maxDepth";
    private GenerationStatus status; // saved state object when generating
    private static List<String> identifiers; // Stores generated IDs, to promote re-use
    private static List<String> funcIdentifiers; // Stores generated IDs, to promote re-use
    private static List<String> allTypes; // Keeps track of all types
    private static List<String> classTypes; // Keeps track of all types
    private static int maxIdentifiers;
    private static int maxItems;
    private static int maxDepth;
    private static int maxBound;
    private int statementDepth; // Keeps track of how deep the AST is at any point
    private int declarationDepth; // Keeps track of how deep the AST is at any point
    private int expressionDepth; // Keeps track of how nested an expression is at any point
    private int indentLevel; // Keeps track of indentation level

    private static final String[] BINARY_TOKENS = {
            "+", "-", "*", "//", "%", "and", "or",
            "<", "<=", ">", ">=", "==", "!=", "is"
    };

    private static final String[] BINARY_BOOL_TOKENS = {
            "and", "or"
    };

    private static final String[] BASE_TYPES = {
            "int", "str", "bool", "object"
    };

    private static final String[] INT_LITERALS = {
            "0", "1"
    };

    private static final String[] STRING_LITERALS = {
            "\"a\"", "\"\""
    };

    private static final String[] BOOL_LITERALS = {
            "True", "False"
    };

    private static final String INDENT_TOKEN = "    "; // 4 spaces


    /** Main entry point. Called once per test case. Returns a random ChocoPy program. */
    @Override
    public String generate(SourceOfRandomness random, GenerationStatus status) {
        this.status = status; // we save this so that we can pass it on to other generators
        this.declarationDepth = 0;
        this.statementDepth = 0;
        this.expressionDepth = 0;
        this.indentLevel = 0;
        this.classTypes = new ArrayList<>();
        this.classTypes.add("object");
        this.allTypes = Arrays.asList(BASE_TYPES);
        this.allTypes = new ArrayList<>(this.allTypes);
        for (String identifier : identifiers) {
            this.allTypes.add(identifier);
            this.classTypes.add(identifier);
        }
        return generateProgram(random);
    }

    /** Utility method for generating a random list of items (e.g. statements, arguments, attributes) */
    private static List<String> generateItems(Function<SourceOfRandomness, String> genMethod, SourceOfRandomness random, int minimum) {
        int len = nextIntBound(random, minimum, maxBound, maxItems);
        List<String> items = new ArrayList<>(len);
        for (int i = 0; i < len; i++) {
            items.add(0, genMethod.apply(random));
        }
        return items;
    }

    /** Utility method for generating a random list of items from a list of functions to choose from */
    private static List<String> generateItemsMultipleMethods(List<Function<SourceOfRandomness, String>> genMethods, SourceOfRandomness random, int minimum) {
        int len = nextIntBound(random, minimum, maxBound, maxItems);
        List<String> items = new ArrayList<>(len);
        for (int i = 0; i < len; i++) {
            items.add(0, random.choose(genMethods).apply(random));
        }
        return items;
    }

    private static int nextIntBound(SourceOfRandomness random, int minimum, int maximum, int maxParam) {
        int randInt = random.nextInt(minimum, maximum);
        assumeTrue(randInt <= maxParam);
        return randInt;
    }

    /** Generates a random ChocoPy program of classes, declarations, and statements */
    private String generateProgram(SourceOfRandomness random) {
        String statements = generateBlock(random, 0);
        String declarations = String.join("", generateItemsMultipleMethods(Arrays.asList(
                this::generateClassDef,
                this::generateFuncDef,
                this::generateVarDef
        ), random, 0));
        return declarations + statements;
    }

    /** Generates a random ChocoPy declaration */
    private String generateDeclaration(SourceOfRandomness random) {
        String result = StringUtils.repeat(INDENT_TOKEN, indentLevel);
        int randDepth = nextIntBound(random, 0, maxBound, maxDepth);
        if (declarationDepth >= randDepth) {
            // Choose a random private method from this class, and then call it with `random`
            result += generateVarDef(random);
        } else {
            // If depth is low and we won the flip, then generate compound declarations
            // (that is, declarations that contain other declarations)
            result += random.choose(Arrays.<Function<SourceOfRandomness, String>>asList(
                    this::generateFuncDef
            )).apply(random);
        }
        return result;
    }

    /** Generates a random ChocoPy function declaration */
    private String generateFuncDeclaration(SourceOfRandomness random) {
        String result = StringUtils.repeat(INDENT_TOKEN, indentLevel);
        int randDepth = nextIntBound(random, 0, maxBound, maxDepth);
        if (declarationDepth >= randDepth) {
            // Choose a random private method from this class, and then call it with `random`
            result += random.choose(Arrays.<Function<SourceOfRandomness, String>>asList(
                    this::generateVarDef,
                    this::generateNonlocalDecl,
                    this::generateGlobalDecl
            )).apply(random);
        } else {
            // If depth is low and we won the flip, then generate compound declarations
            // (that is, declarations that contain other declarations)
            result += random.choose(Arrays.<Function<SourceOfRandomness, String>>asList(
                    this::generateFuncDef
            )).apply(random);
        }
        return result + "\n";
    }

    /** Generates a random ChocoPy statement */
    private String generateStatement(SourceOfRandomness random) {
        String result = StringUtils.repeat(INDENT_TOKEN, indentLevel);
        // If depth is too high, then generate only simple statements to prevent infinite recursion
        // If not, generate simple statements after the flip of a coin
        int randDepth = nextIntBound(random, 0, maxBound, maxDepth);
        if (statementDepth >= randDepth) {
            // Choose a random private method from this class, and then call it with `random`
            result += random.choose(Arrays.<Function<SourceOfRandomness, String>>asList(
                    this::generateAssignStmt,
                    this::generatePassStmt,
                    this::generateReturnStmt,
                    this::generateExpressionStmt
            )).apply(random);
        } else {
            // If depth is low and we won the flip, then generate compound statements
            // (that is, statements that contain other statements)
            result += random.choose(Arrays.<Function<SourceOfRandomness, String>>asList(
                    this::generateIfStmt,
                    this::generateForStmt,
                    this::generateWhileStmt
            )).apply(random);
        }
        return result + "\n";
    }

    /** Generates a random ChocoPy expression using recursive calls */
    private String generateExpression(SourceOfRandomness random) {
        String result;
        // Choose terminal if nesting depth is too high or based on a random flip of a coin
        int randDepth = nextIntBound(random, 0, maxBound, maxDepth);
        if (expressionDepth >= randDepth) {
            result = generateCExpression(random);
        } else {
            expressionDepth++;
            // Otherwise, choose a non-terminal generating function
            result = random.choose(Arrays.<Function<SourceOfRandomness, String>>asList(
                    this::generateUnaryBoolExpr,
                    this::generateBinaryBoolExpr,
                    this::generateIfExpr
            )).apply(random);
            expressionDepth--;
        }
        return result;
    }

    private String generateCExpression(SourceOfRandomness random) {
        expressionDepth++;
        String result;
        // Choose terminal if nesting depth is too high or based on a random flip of a coin
        int randDepth = nextIntBound(random, 0, maxBound, maxDepth);
        if (expressionDepth >= randDepth) {
            result = random.choose(Arrays.<Function<SourceOfRandomness, String>>asList(
                    this::generateLiteral,
                    this::generateIdentifier
            )).apply(random);
        } else {
            // Otherwise, choose a non-terminal generating function
            result = random.choose(Arrays.<Function<SourceOfRandomness, String>>asList(
                    this::generateListExpr,
                    this::generateParenExpr,
                    this::generateMemberExpr,
                    this::generateMethodCallExpr,
                    this::generateIndexExpr,
                    this::generateCallExpr,
                    this::generateBinaryExpr,
                    this::generateUnaryExpr
            )).apply(random);
        }
        expressionDepth--;
        return result;
    }

    private String generateAssignStmt(SourceOfRandomness random) {
        String result = "";
        int len = nextIntBound(random, 1, maxBound, maxDepth);
        List<String> items = new ArrayList<>(len);
        for (int i = 0; i < len; i++) {
            String target = random.choose(Arrays.<Function<SourceOfRandomness, String>>asList(
                    this::generateIdentifier,
                    this::generateIndexExpr,
                    this::generateMemberExpr
            )).apply(random);
            items.add(0, target);
//            result = result + "=" + target;
        }

        return String.join("=", items) + "=" + generateExpression(random);
    }

    private String generateBinaryBoolExpr(SourceOfRandomness random) {
        String rhs = generateCExpression(random);
        String token = random.choose(BINARY_BOOL_TOKENS);
        String lhs = generateCExpression(random);

        return lhs + " " + token + " " + rhs;
    }

    /** Generates a random binary expression (e.g. A op B) */
    private String generateBinaryExpr(SourceOfRandomness random) {
        String rhs = generateCExpression(random);
        String token = random.choose(BINARY_TOKENS);
        String lhs = generateCExpression(random);

        return lhs + " " + token + " " + rhs;
    }

    /** Generates a block of statements */
    private String generateBlock(SourceOfRandomness random, int minimum) {
        return String.join("", generateItems(this::generateStatement, random, minimum));
    }

    private String generateCallExpr(SourceOfRandomness random) {
        String args = String.join(",", generateItems(this::generateExpression, random, 0));
        String func = generateFuncIdentifier(random);

        String call = func + "(" + args + ")";
        return call;
    }

    private String generateClassDef(SourceOfRandomness random) {
        indentLevel++;
        String declarationBlock = generateDeclarationBlock(random, 1);
        indentLevel--;
        // Superclass could be one of the identifiers or object. Index should be from 0 to maxIdentifiers inclusive.
        int superClassIndex = nextIntBound(random, 0, classTypes.size(), maxIdentifiers);
        String superClassName = classTypes.get(superClassIndex);
        String className = generateIdentifier(random);
        return "class " + className + "(" + superClassName + "):\n" + declarationBlock + "\n";
    }

    /** Generates a block of VarDefs and FuncDefs*/
    private String generateDeclarationBlock(SourceOfRandomness random, int minimum) {
        return String.join("", generateItems(this::generateDeclaration, random, minimum));
    }

    private String generateExpressionStmt(SourceOfRandomness random) {
        return generateExpression(random);
    }

    private String generateForStmt(SourceOfRandomness random) {
        statementDepth++;
        indentLevel++;
        String block = generateBlock(random, 1);
        indentLevel--;
        String expression = generateExpression(random);
        String identifier = generateIdentifier(random);
        statementDepth--;
        return "for " + identifier + " in " +  expression + ":\n" + block;
    }

    private String generateFuncDef(SourceOfRandomness random) {
        declarationDepth++;
        indentLevel++;
        String block = generateBlock(random, 1);
        String declarations = String.join("", generateItems(this::generateFuncDeclaration, random, 0));
        indentLevel--;

        String returnType = null;
        if (random.nextBoolean()) {
            returnType = "->" + generateType(random);
        } else {
            returnType = "";
        }
        String funcParams = String.join(", ", generateItems(this::generateTypedVar, random, 0));
        String funcIdentifier = generateFuncIdentifier(random);
        declarationDepth--;

        return "def " + funcIdentifier + "(" +  funcParams + ")" + returnType + ":\n" + declarations + block + "\n";
    }

    private String generateGlobalDecl(SourceOfRandomness random) {
        return "global " + generateIdentifier(random) + "\n";
    }

    private String generateIdentifier(SourceOfRandomness random) {
        int index = nextIntBound(random, 0, maxBound, maxIdentifiers - 1);
        return identifiers.get(index);
    }

    private String generateFuncIdentifier(SourceOfRandomness random) {
        int index = nextIntBound(random, 0, funcIdentifiers.size(),
                maxIdentifiers + BASE_TYPES.length);
        return funcIdentifiers.get(index);
    }

    /** Creates initial set of identifiers depending on parameter */
    private void generateIdentifiers(int numIdentifiers) {
        this.identifiers = new ArrayList<>();
        this.funcIdentifiers = new ArrayList<>(Arrays.asList(BASE_TYPES));
        funcIdentifiers.add("len");
        String ident;
        for (int i = 0; i < numIdentifiers; i++) {
            ident = "a" + i;
            identifiers.add(ident);
            funcIdentifiers.add(ident);
        }
    }

    private String generateIfExpr(SourceOfRandomness random) {
        String falseResult = generateExpression(random);
        String condition = generateExpression(random);
        String trueResult = generateExpression(random);
        return  trueResult + " if " + condition + " else " + falseResult;
    }

    private String generateIfStmt(SourceOfRandomness random) {
        statementDepth++;
        String elseBlocks = "";
        if (random.nextBoolean()) {
            elseBlocks += StringUtils.repeat(INDENT_TOKEN, indentLevel);
            elseBlocks += "else:\n";
            indentLevel++;
            elseBlocks += generateBlock(random, 1);
            indentLevel--;
        }
        String elIf = "";
        if (random.nextBoolean()) {
            elIf += StringUtils.repeat(INDENT_TOKEN, indentLevel);
            elIf += "elif " + generateExpression(random) + ":\n";
            indentLevel++;
            elIf += generateBlock(random, 1);
            indentLevel--;
        }
        indentLevel++;
        String blocks = generateBlock(random, 1);
        indentLevel--;
        String condition = generateExpression(random);
//        String result = "if " +  + ":\n";
        statementDepth--;
        return "if " + condition + ":\n" + blocks + elIf + elseBlocks;
    }

    private String generateIndexExpr(SourceOfRandomness random) {
        String index = generateExpression(random);
        String nameExpr = generateCExpression(random);
        return "(" + nameExpr + ")[" + index + "]";
    }

    private String generateListExpr(SourceOfRandomness random) {
        return "[" + String.join(", ", generateItems(this::generateExpression, random, 0)) + "]";
    }

    // Generate fixed primitive literals
    private String generateLiteral(SourceOfRandomness random) {

        return random.choose(Arrays.<Function<SourceOfRandomness, String>>asList(
                this::generateIntLiteral,
                this::generateStringLiteral,
                this::generateBoolLiteral,
                this::generateNoneLiteral)).apply(random);
    }

    private String generateIntLiteral(SourceOfRandomness random) {
        return random.choose(INT_LITERALS);
    }

    private String generateStringLiteral(SourceOfRandomness random) {
        return random.choose(STRING_LITERALS);
    }

    private String generateBoolLiteral(SourceOfRandomness random) {
        return random.choose(BOOL_LITERALS);
    }

    private String generateNoneLiteral(SourceOfRandomness random) {
        return "None";
    }

    private String generateMemberExpr(SourceOfRandomness random) {
        String identifier = generateIdentifier(random);
        String nameExpr = generateCExpression(random);
        return "(" + nameExpr + ")." + identifier;
    }

    private String generateMethodCallExpr(SourceOfRandomness random) {
        String methodCallExpr = generateCallExpr(random);
        String nameExpr = generateCExpression(random);
        return  nameExpr + "." + methodCallExpr;
    }

    private String generateNonlocalDecl(SourceOfRandomness random) {
        return "nonlocal " + generateIdentifier(random) + "\n";
    }

    private String generateParenExpr(SourceOfRandomness random) {
        return "(" + generateExpression(random) + ")";
    }

    private String generatePassStmt(SourceOfRandomness random) {
        return "pass";
    }

    private String generateReturnStmt(SourceOfRandomness random) {
        return random.nextBoolean() ? "return" : "return " + generateExpression(random);
    }

    /** Randomly choose from types and random list depth using maxDepth parameter */
    private String generateType(SourceOfRandomness random) {
        int typeIndex = nextIntBound(random, 0, allTypes.size(), BASE_TYPES.length + maxIdentifiers - 1);
        String type = allTypes.get(typeIndex);
        int listDepth = nextIntBound(random, 0, maxBound, maxDepth);
        for (int i = 0; i < listDepth; i++) {
            type = "[" + type + "]";
        }
        return type;
    }

    private String generateTypedVar(SourceOfRandomness random) {
        String type = generateType(random);
        String iden = generateIdentifier(random);
        return iden + ":" + type;
    }

    private String generateUnaryBoolExpr(SourceOfRandomness random) {
        return "not " + generateExpression(random);
    }

    private String generateUnaryExpr(SourceOfRandomness random) {
        return "-" + generateCExpression(random);
    }

    private String generateVarDef(SourceOfRandomness random) {
        String literal = generateLiteral(random);
        String typedVar = generateTypedVar(random);
        return  typedVar + " = " + literal + "\n";
    }

    private String generateWhileStmt(SourceOfRandomness random) {
        statementDepth++;
        indentLevel++;
        String blocks = generateBlock(random, 1);
        String expr = generateExpression(random);
        String result = "while " + expr + ":\n" + blocks;
        indentLevel--;
        statementDepth--;
        return result;
    }
}
