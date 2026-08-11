package com.app.tictactoe;

public final class Main {

    public static void main(String[] args) {
        ConsoleUI ui = new ConsoleUI();

        Player playerOne = new Player("Player 1", 'X');
        Player playerTwo = new Player("Player 2", 'O');

        Game game = new Game(playerOne, playerTwo);

        ui.showWelcome();

        boolean keepPlaying = true;

        while (keepPlaying) {
            runSingleGame(ui, game);

            keepPlaying = ui.promptPlayAgain();

            if (keepPlaying) {
                /* A fresh game state is restored before the next round begins. */
                game.reset();
                System.out.println();
            }
        }

        ui.close();
    }

    private static void runSingleGame(ConsoleUI ui, Game game) {
        /* The main turn loop is executed until a win or draw state is reached. */
        while (!game.isGameOver()) {
            ui.displayBoard(game.getBoard());
            ui.showTurn(game.getCurrentPlayer());

            int[] move = ui.promptMove();
            int row = move[0];
            int col = move[1];

            boolean accepted;

            try {
                /* The move is attempted through the game API. */
                accepted = game.makeMove(row, col);
            } catch (IllegalArgumentException e) {
                /* Out of range input is treated as an invalid move. */
                accepted = false;
            }

            if (!accepted) {
                ui.showInvalidMove();
                System.out.println();
            } else {
                System.out.println();
            }
        }

        /* The final board is displayed once the game ends. */
        ui.displayBoard(game.getBoard());

        if (game.hasWinner()) {
            ui.showWinner(game.getWinner());
        } else {
            ui.showDraw();
        }
    }
}
