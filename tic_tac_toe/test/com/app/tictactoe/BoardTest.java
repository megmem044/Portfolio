package com.app.tictactoe;

public final class BoardTest {

    public static void main(String[] args) {
        testBoardStartsEmpty();
        testPlaceSymbolSucceedsOnEmptyCell();
        testPlaceSymbolFailsOnOccupiedCell();
        testWinnerInRow();
        testWinnerInColumn();
        testWinnerInDiagonal();
        testDrawCondition();

        System.out.println("All Board tests passed.");
    }

    private static void testBoardStartsEmpty() {
        Board board = new Board();

        /* Every cell is expected to be empty after construction. */
        for (int r = 0; r < Board.SIZE; r++) {
            for (int c = 0; c < Board.SIZE; c++) {
                assertEquals(' ', board.getCell(r, c), "Board cell was expected to be empty.");
            }
        }
    }

    private static void testPlaceSymbolSucceedsOnEmptyCell() {
        Board board = new Board();

        boolean placed = board.placeSymbol(0, 0, 'X');

        /* A valid placement is expected to return true and update the cell. */
        assertTrue(placed, "Placement was expected to succeed on an empty cell.");
        assertEquals('X', board.getCell(0, 0), "Cell was expected to contain X after placement.");
    }

    private static void testPlaceSymbolFailsOnOccupiedCell() {
        Board board = new Board();

        boolean firstPlaced = board.placeSymbol(1, 1, 'O');
        boolean secondPlaced = board.placeSymbol(1, 1, 'X');

        /* The second placement is expected to fail because the cell is occupied. */
        assertTrue(firstPlaced, "First placement was expected to succeed.");
        assertFalse(secondPlaced, "Second placement was expected to fail on an occupied cell.");
        assertEquals('O', board.getCell(1, 1), "Cell was expected to remain O after failed placement.");
    }

    private static void testWinnerInRow() {
        Board board = new Board();

        board.placeSymbol(0, 0, 'X');
        board.placeSymbol(0, 1, 'X');
        board.placeSymbol(0, 2, 'X');

        /* A row winner is expected to be detected. */
        assertEquals('X', board.getWinnerSymbol(), "Row winner X was expected.");
        assertTrue(board.hasWinner(), "Winner was expected to exist.");
    }

    private static void testWinnerInColumn() {
        Board board = new Board();

        board.placeSymbol(0, 2, 'O');
        board.placeSymbol(1, 2, 'O');
        board.placeSymbol(2, 2, 'O');

        /* A column winner is expected to be detected. */
        assertEquals('O', board.getWinnerSymbol(), "Column winner O was expected.");
        assertTrue(board.hasWinner(), "Winner was expected to exist.");
    }

    private static void testWinnerInDiagonal() {
        Board board = new Board();

        board.placeSymbol(0, 0, 'X');
        board.placeSymbol(1, 1, 'X');
        board.placeSymbol(2, 2, 'X');

        /* A diagonal winner is expected to be detected. */
        assertEquals('X', board.getWinnerSymbol(), "Diagonal winner X was expected.");
        assertTrue(board.hasWinner(), "Winner was expected to exist.");
    }

    private static void testDrawCondition() {
        Board board = new Board();

        /* The board is filled in a pattern that produces no winner. */
        board.placeSymbol(0, 0, 'X');
        board.placeSymbol(0, 1, 'O');
        board.placeSymbol(0, 2, 'X');

        board.placeSymbol(1, 0, 'X');
        board.placeSymbol(1, 1, 'O');
        board.placeSymbol(1, 2, 'O');

        board.placeSymbol(2, 0, 'O');
        board.placeSymbol(2, 1, 'X');
        board.placeSymbol(2, 2, 'X');

        assertFalse(board.hasWinner(), "Winner was not expected for this board state.");
        assertTrue(board.isFull(), "Board was expected to be full.");
        assertTrue(board.isDraw(), "Draw was expected when full board has no winner.");
    }

    private static void assertTrue(boolean condition, String message) {
        if (!condition) {
            throw new AssertionError(message);
        }
    }

    private static void assertFalse(boolean condition, String message) {
        if (condition) {
            throw new AssertionError(message);
        }
    }

    private static void assertEquals(char expected, char actual, String message) {
        if (expected != actual) {
            throw new AssertionError(message + " Expected: " + expected + " Actual: " + actual);
        }
    }
}
