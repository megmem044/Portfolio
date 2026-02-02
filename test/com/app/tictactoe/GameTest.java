package com.app.tictactoe;

public final class GameTest {

    public static void main(String[] args) {
        testTurnSwitchingAfterValidMove();
        testTurnDoesNotSwitchAfterInvalidMove();
        testWinnerIsDetectedAndMappedToPlayer();
        testDrawIsDetected();

        System.out.println("All Game tests passed.");
    }

    private static void testTurnSwitchingAfterValidMove() {
        Player p1 = new Player("P1", 'X');
        Player p2 = new Player("P2", 'O');
        Game game = new Game(p1, p2);

        /* The first turn is expected to start with player one. */
        assertEquals(p1, game.getCurrentPlayer(), "Player one was expected to start.");

        boolean placed = game.makeMove(0, 0);

        /* The move is expected to succeed and the turn is expected to switch. */
        assertTrue(placed, "Move was expected to be accepted.");
        assertEquals(p2, game.getCurrentPlayer(), "Turn was expected to switch to player two.");
    }

    private static void testTurnDoesNotSwitchAfterInvalidMove() {
        Player p1 = new Player("P1", 'X');
        Player p2 = new Player("P2", 'O');
        Game game = new Game(p1, p2);

        boolean firstPlaced = game.makeMove(1, 1);

        /* The first placement is expected to succeed and switch to player two. */
        assertTrue(firstPlaced, "First move was expected to be accepted.");
        assertEquals(p2, game.getCurrentPlayer(), "Turn was expected to switch to player two.");

        boolean secondPlaced = game.makeMove(1, 1);

        /* The second placement is expected to fail and keep player two as current. */
        assertFalse(secondPlaced, "Second move was expected to be rejected.");
        assertEquals(p2, game.getCurrentPlayer(), "Turn was expected to remain with player two.");
    }

    private static void testWinnerIsDetectedAndMappedToPlayer() {
        Player p1 = new Player("P1", 'X');
        Player p2 = new Player("P2", 'O');
        Game game = new Game(p1, p2);

        /*
         A winning row for X is produced with valid alternating moves.
         The O moves are placed in a different row to avoid interference.
        */
        game.makeMove(0, 0); /* X */
        game.makeMove(1, 0); /* O */
        game.makeMove(0, 1); /* X */
        game.makeMove(1, 1); /* O */
        game.makeMove(0, 2); /* X */

        assertTrue(game.hasWinner(), "Winner was expected to be detected.");
        assertEquals(p1, game.getWinner(), "Winner player was expected to be player one.");
        assertTrue(game.isGameOver(), "Game over was expected after a win.");
    }

    private static void testDrawIsDetected() {
        Player p1 = new Player("P1", 'X');
        Player p2 = new Player("P2", 'O');
        Game game = new Game(p1, p2);

        /*
         A draw pattern is created with alternating moves.
         No three in a row is formed for either symbol.
        */
        game.makeMove(0, 0); /* X */
        game.makeMove(0, 1); /* O */
        game.makeMove(0, 2); /* X */

        game.makeMove(1, 1); /* O */
        game.makeMove(1, 0); /* X */
        game.makeMove(1, 2); /* O */

        game.makeMove(2, 1); /* X */
        game.makeMove(2, 0); /* O */
        game.makeMove(2, 2); /* X */

        assertFalse(game.hasWinner(), "Winner was not expected.");
        assertTrue(game.isDraw(), "Draw was expected.");
        assertTrue(game.isGameOver(), "Game over was expected after a draw.");
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

    private static void assertEquals(Object expected, Object actual, String message) {
        if (expected == null && actual == null) {
            return;
        }
        if (expected == null || actual == null) {
            throw new AssertionError(message + " Expected: " + expected + " Actual: " + actual);
        }
        if (!expected.equals(actual)) {
            throw new AssertionError(message + " Expected: " + expected + " Actual: " + actual);
        }
    }
}
