package readorder;

public class TreeProcessor {
    public static class Node {
       Node left;
       Node right;
       byte data;
       public Node(Node left, Node right, byte data) {
           this.left = left;
           this.right = right;
           this.data = data;
       }
    }

    public static void processLTR(Node n) {
        if (n.left == null) {
            if (n.right == null) {
                System.exit(1);
            }
        }
    }

    public static void processRTL(Node n) {
        if (n.right == null) {
            if (n.left == null) {
                System.exit(1);
            }
        }
    }
}
