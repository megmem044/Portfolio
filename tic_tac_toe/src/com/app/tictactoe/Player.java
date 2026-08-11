package com.app.tictactoe;

public final class Player {

    /* The name is stored for display and identification purposes. */
    private final String name;

    /* The symbol represents the mark placed on the board by this player. */
    private final char symbol;

    public Player(String name, char symbol) {
        /* Input validation is performed to prevent invalid player creation. */
        if (name == null || name.isBlank()) {
            throw new IllegalArgumentException("Player name must not be empty.");
        }

        if (symbol != 'X' && symbol != 'O') {
            throw new IllegalArgumentException("Player symbol must be X or O.");
        }

        this.name = name;
        this.symbol = symbol;
    }

    public String getName() {
        /* The player name is returned without modification. */
        return name;
    }

    public char getSymbol() {
        /* The player symbol is returned for board placement. */
        return symbol;
    }
}
