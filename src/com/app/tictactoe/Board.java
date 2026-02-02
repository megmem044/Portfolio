package com.app.tictactoe;

import java.util.Arrays;

public final class Board {

    /* The board size is fixed to three for a standard Tic Tac Toe grid. */
    public static final int SIZE = 3;

    /* The grid is used to store the current state of the board. */
    private final char[][] grid;

    public Board() {
        /* The grid is initialized when the board is created. */
        grid = new char[SIZE][SIZE];
        clear();
    }

    public void clear() {
        /* Each cell is reset to a space character to represent emptiness. */
        for (int r = 0; r < SIZE; r++) {
            Arrays.fill(grid[r], ' ');
        }
    }

    public char getCell(int row, int col) {
        /* Bounds are validated to prevent invalid array access. */
        validateBounds(row, col);
        return grid[row][col];
    }

    public boolean placeSymbol(int row, int col, char symbol) {
        /* Input values are validated before attempting placement. */
        validateBounds(row, col);
        validateSymbol(symbol);

        /* Placement is rejected if the cell is already occupied. */
        if (grid[row][col] != ' ') {
            return false;
        }

        /* The symbol is written to the board if the move is valid. */
        grid[row][col] = symbol;
        return true;
    }

    public boolean isFull() {
        /* The board is scanned to check if any empty cell remains. */
        for (int r = 0; r < SIZE; r++) {
            for (int c = 0; c < SIZE; c++) {
                if (grid[r][c] == ' ') {
                    return false;
                }
            }
        }
        return true;
    }

    public char getWinnerSymbol() {
        /* Winning conditions are checked row by row first. */
        char rowWinner = winnerFromRows();
        if (rowWinner != ' ') {
            return rowWinner;
        }

        /* Column checks are performed next if no row winner exists. */
        char colWinner = winnerFromCols();
        if (colWinner != ' ') {
            return colWinner;
        }

        /* Diagonal checks are performed last. */
        return winnerFromDiagonals();
    }

    public boolean hasWinner() {
        /* A winner exists if a non empty symbol is returned. */
        return getWinnerSymbol() != ' ';
    }

    public boolean isDraw() {
        /* A draw is identified when the board is full and no winner exists. */
        return isFull() && !hasWinner();
    }

    public String toDisplayString() {
        /* A formatted string is constructed for console display. */
        StringBuilder sb = new StringBuilder();

        for (int r = 0; r < SIZE; r++) {
            sb.append(" ");
            for (int c = 0; c < SIZE; c++) {
                sb.append(grid[r][c]);
                if (c < SIZE - 1) {
                    sb.append(" | ");
                }
            }
            sb.append("\n");

            /* Separator lines are added between rows. */
            if (r < SIZE - 1) {
                sb.append("---+---+---\n");
            }
        }

        return sb.toString();
    }

    private char winnerFromRows() {
        /* Each row is checked for three matching non empty symbols. */
        for (int r = 0; r < SIZE; r++) {
            char a = grid[r][0];
            char b = grid[r][1];
            char c = grid[r][2];

            if (a != ' ' && a == b && b == c) {
                return a;
            }
        }
        return ' ';
    }

    private char winnerFromCols() {
        /* Each column is checked for three matching non empty symbols. */
        for (int c = 0; c < SIZE; c++) {
            char a = grid[0][c];
            char b = grid[1][c];
            char d = grid[2][c];

            if (a != ' ' && a == b && b == d) {
                return a;
            }
        }
        return ' ';
    }

    private char winnerFromDiagonals() {
        /* The center cell is used to simplify diagonal winner checks. */
        char center = grid[1][1];

        if (center != ' ' && grid[0][0] == center && grid[2][2] == center) {
            return center;
        }

        if (center != ' ' && grid[0][2] == center && grid[2][0] == center) {
            return center;
        }

        return ' ';
    }

    private void validateBounds(int row, int col) {
        /* Input is rejected if it falls outside the board boundaries. */
        if (row < 0 || row >= SIZE || col < 0 || col >= SIZE) {
            throw new IllegalArgumentException("Row and column must be between 0 and 2.");
        }
    }

    private void validateSymbol(char symbol) {
        /* Only X and O are allowed as valid player symbols. */
        if (symbol != 'X' && symbol != 'O') {
            throw new IllegalArgumentException("Symbol must be X or O.");
        }
    }
}
