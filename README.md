# Project description
Video walkthrough is here: https://www.youtube.com/watch?v=R9cXEKlBsh4

My project is to write an AI program to automatically solve Sudoku game.

Disclaimer: this AI program has nothing to do with Deep Learning Neural Networks framework. Instead, it is implemented based on the principles of Knowledge Representation and Reasoning (check it out here: https://en.wikipedia.org/wiki/Knowledge_representation_and_reasoning)

More information in this repo:
- requirements.txt: contains the modules required to run the program. User can first implement these packages in the terminal using the command `pip install -r requirements.txt`
- sudoku.py: contains all the objects of the SudokuAI
- runner.py: this program is written to run the game in terminal. User can see this by typing the command `python runner.py`
- test.py: this program is written as a visualization on how fast and robust this program is when solving 9 million Sudoku games. User can try this by typing the command `python test.py`
- game.py: this program is the GUI. User can start the program and play with it by typing the command `python game.py`
- Within these programs, the puzzle game is queried from the database `sudoku.db`. This database is heavy and located outside of this repo (link provided above). Thus, to make these programs work, user must download the database, and then change in `sudoku.py` at class `SuDokuCollection()` as `SuDokuCollection(source_data_path=<path>)` where `<path>` is the local path of this database.
