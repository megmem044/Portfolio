# Tic Tac Toe (Java)

A console based Tic Tac Toe game implemented using pure Java.  
The project follows a clean separation of concerns and includes basic tests without external frameworks.

## Features
- Two player console gameplay
- Turn based move handling
- Win detection for rows, columns, and diagonals
- Draw detection
- Board state rendering in console
- Reset and replay support
- Simple test coverage for core game logic

## Project Structure

tictactoe/
├── src/
│ └── com/app/tictactoe/
│ ├── Main.java
│ ├── Game.java
│ ├── Board.java
│ ├── Player.java
│ └── ConsoleUI.java
└── test/
└── com/app/tictactoe/
├── BoardTest.java
└── GameTest.java


## How to Compile

From the project root directory:
javac -d out src/com/app/tictactoe/.java test/com/app/tictactoe/.java


## How to Run Tests
java -cp out com.app.tictactoe.BoardTest
java -cp out com.app.tictactoe.GameTest


## How to Run the Game
java -cp out com.app.tictactoe.Main


## Notes
- No external libraries or frameworks are used
- Tests are written using plain Java assertions
- The project is structured to be easily extensible