package com.app.tictactoe;

public final class Game {

    /* The board is responsible for storing and evaluating game state. */
    private final Board board;

    /* Two players are stored to alternate turns. */
    private final Player playerOne;
    private final Player playerTwo;

    /* The current player reference is updated after each valid move. */
    private Player currentPlayer;

    public Game(Player playerOne, Player playerTwo) {
        /* Player references are validated to prevent null game state. */
        if (playerOne == null || playerTwo == null) {
            throw new IllegalArgumentException("Players must not be null.");
        }

        if (playerOne.getSymbol() == playerTwo.getSymbol()) {
            throw new IllegalArgumentException("Players must use different symbols.");
        }

        this.board = new Board();
        this.playerOne = playerOne;
        this.playerTwo = playerTwo;

        /* The first player is selected as the starting player by default. */
        this.currentPlayer = playerOne;
    }

    public Board getBoard() {
        /* The board reference is exposed for reading game state. */
        return board;
    }

    public Player getCurrentPlayer() {
        /* The current player is returned to determine whose turn it is. */
        return currentPlayer;
    }

    public boolean makeMove(int row, int col) {
        /* A move attempt is delegated to the board for validation. */
        boolean placed = board.placeSymbol(row, col, currentPlayer.getSymbol());

        if (!placed) {
            /* The turn is not advanced when the move is invalid. */
            return false;
        }

        /* The active player is switched only after a successful move. */
        switchTurn();
        return true;
    }

    public boolean hasWinner() {
        /* The board is queried to determine if a winning state exists. */
        return board.hasWinner();
    }

    public Player getWinner() {
        /* The winning symbol is retrieved from the board. */
        char winnerSymbol = board.getWinnerSymbol();

        if (winnerSymbol == ' ') {
            return null;
        }

        /* The player associated with the winning symbol is returned. */
        if (playerOne.getSymbol() == winnerSymbol) {
            return playerOne;
        }

        return playerTwo;
    }

    public boolean isDraw() {
        /* A draw state is delegated to board evaluation logic. */
        return board.isDraw();
    }

    public boolean isGameOver() {
        /* The game is over when either a winner or a draw exists. */
        return hasWinner() || isDraw();
    }

    public void reset() {
        /* The board state is cleared and the starting player is restored. */
        board.clear();
        currentPlayer = playerOne;
    }

    private void switchTurn() {
        /* The active player reference is toggled after each valid move. */
        if (currentPlayer == playerOne) {
            currentPlayer = playerTwo;
        } else {
            currentPlayer = playerOne;
        }
    }
}
