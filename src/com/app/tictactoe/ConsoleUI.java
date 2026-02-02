package com.app.tictactoe;

import java.util.Scanner;

public final class ConsoleUI {

    /* A single scanner instance is used for all console input. */
    private final Scanner scanner;

    public ConsoleUI() {
        /* The scanner is initialized to read from standard input. */
        scanner = new Scanner(System.in);
    }

    public void showWelcome() {
        /* A welcome message is displayed at program start. */
        System.out.println("Welcome to Tic Tac Toe");
        System.out.println();
    }

    public void displayBoard(Board board) {
        /* The board display is delegated to the board formatting method. */
        System.out.println(board.toDisplayString());
    }

    public void showTurn(Player player) {
        /* The active player information is displayed before each move. */
        System.out.println(player.getName() + "'s turn (" + player.getSymbol() + ")");
    }

    public int[] promptMove() {
        /* Input is requested until valid numeric values are provided. */
        while (true) {
            try {
                System.out.print("Enter row (0 to 2): ");
                int row = Integer.parseInt(scanner.nextLine());

                System.out.print("Enter column (0 to 2): ");
                int col = Integer.parseInt(scanner.nextLine());

                return new int[] { row, col };
            } catch (NumberFormatException e) {
                /* Invalid numeric input is handled without crashing the program. */
                System.out.println("Invalid input. Please enter numbers only.");
            }
        }
    }

    public void showInvalidMove() {
        /* Feedback is given when a move cannot be applied. */
        System.out.println("That move is not allowed. Try again.");
    }

    public void showWinner(Player winner) {
        /* The winning player is announced when the game ends. */
        System.out.println();
        System.out.println("Winner: " + winner.getName() + " (" + winner.getSymbol() + ")");
    }

    public void showDraw() {
        /* A draw message is displayed when no winner exists. */
        System.out.println();
        System.out.println("The game ended in a draw.");
    }

    public boolean promptPlayAgain() {
        /* User input is requested to determine if another game should start. */
        System.out.print("Play again? (y/n): ");
        String input = scanner.nextLine().trim().toLowerCase();

        return input.equals("y");
    }

    public void close() {
        /* The scanner resource is closed when the application ends. */
        scanner.close();
    }
}
