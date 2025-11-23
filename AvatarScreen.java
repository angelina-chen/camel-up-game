import java.util.ArrayList;
import java.util.List;
import java.util.Scanner;

public class AvatarScreen {

    private static final String[] AVATAR_FACES = {
        "(•‿•)",
        "(≧◡≦)",
        "(°ᴗ°)",
        "(^‿^)",
        "(•̀ᴗ•́)و",
        "(^人^)"
    };

    public static void main(String[] args) {
        List<String> playerNames = new ArrayList<>();

        if (args.length > 0) {
            // Use names passed from Python
            for (String arg : args) {
                playerNames.add(arg);
            }
        } else {
            // Fallback: standalone mode, ask in Java
            Scanner scanner = new Scanner(System.in);
            System.out.println("=== Camel Up: Player Avatar Setup ===");
            System.out.print("How many players? ");
            int numPlayers = readPositiveInt(scanner);

            for (int i = 1; i <= numPlayers; i++) {
                System.out.print("Enter name for Player " + i + " (leave blank for default): ");
                String name = scanner.nextLine().trim();
                if (name.isEmpty()) {
                    name = "Player " + i;
                }
                playerNames.add(name);
            }
            scanner.close();
        }

        System.out.println();
        System.out.println("=== Player Avatars ===");
        printAvatarRow(playerNames);
    }

    private static int readPositiveInt(Scanner scanner) {
        while (true) {
            String line = scanner.nextLine().trim();
            try {
                int value = Integer.parseInt(line);
                if (value > 0) {
                    return value;
                } else {
                    System.out.print("Please enter a positive integer: ");
                }
            } catch (NumberFormatException e) {
                System.out.print("Invalid number. Please enter a positive integer: ");
            }
        }
    }

    private static void printAvatarRow(List<String> playerNames) {
        int n = playerNames.size();

        // Top border
        for (int i = 0; i < n; i++) {
            System.out.print("+----------------------+  ");
        }
        System.out.println();

        // Name line
        for (int i = 0; i < n; i++) {
            String name = playerNames.get(i);
            String label = " " + name + " ";
            System.out.print("|" + center(label, 22) + "|  ");
        }
        System.out.println();

        // Player index line
        for (int i = 0; i < n; i++) {
            String label = "Player " + (i + 1);
            System.out.print("|" + center(label, 22) + "|  ");
        }
        System.out.println();

        // Avatar face line
        for (int i = 0; i < n; i++) {
            String face = AVATAR_FACES[i % AVATAR_FACES.length];
            System.out.print("|" + center(face, 22) + "|  ");
        }
        System.out.println();

        // Bottom border
        for (int i = 0; i < n; i++) {
            System.out.print("+----------------------+  ");
        }
        System.out.println();
    }

    private static String center(String text, int width) {
        if (text.length() >= width) {
            return text.substring(0, width);
        }
        int totalPadding = width - text.length();
        int left = totalPadding / 2;
        int right = totalPadding - left;
        return " ".repeat(left) + text + " ".repeat(right);
    }
}
