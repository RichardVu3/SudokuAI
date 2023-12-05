# Project description
Video walkthrough is here: https://www.youtube.com/watch?v=R9cXEKlBsh4

My final project is to write an AI program to automatically solve Sudoku game.

Disclaimer: this AI program has nothing to do with Deep Learning Neural Networks framework. Instead, it is implemented based on the principles of Knowledge Representation and Reasoning (check it out here: https://en.wikipedia.org/wiki/Knowledge_representation_and_reasoning)

This program can:
1. Store 9 million Sudoku games from an Excel file downloaded from an online source and store it into a database (source file and database are stored in this shared Google drive: https://drive.google.com/drive/folders/12mPZS2QOLToOLaZTJ4YwBDQHnPw7pl8v?usp=sharing)
2. Take an input as a Sudoku game
3. Based on the game rule, this will fill up the number until the game is solved
4. This program should not take more time than me solving the game (to say that this algorithm should be efficient and do not contain some loops that spends more than 2 minutes to fill a new number)
5. Each turn when a number is filled, the program will print out the number and its location
6. A GUI is implemented to show the progress. It also can be seen from the terminal

My execution plan:
- By the end of week 4, I will have explored the framework and starts designing the program flow and objects
- By the end of week 5, I will have implemented the basic functions (taking input, checking validity, checking result,...) for the program 
- From week 6 to 7, I will have implemented the core function of the AI program and make sure it works.
- Week 8 is to buffer one more week for the core function to work efficiently. If it does, I will start building the GUI with Tkinter
- By the end of week 9, I will have finished the GUI
- By the due date of the project, I will have finished testing and making the video walkthrough and submitting the project to the repo

More information in this repo:
- requirements.txt: contains the modules required to run the program. User can first implement these packages in the terminal using the command `pip install -r requirements.txt`
- sudoku.py: contains all the objects of the SudokuAI
- runner.py: this program is written to run the game in terminal. User can see this by typing the command `python runner.py`
- test.py: this program is written as a visualization on how fast and robust this program is when solving 9 million Sudoku games. User can try this by typing the command `python test.py`
- game.py: this program is the GUI. User can start the program and play with it by typing the command `python game.py`
- Within these programs, the puzzle game is queried from the database `sudoku.db`. This database is heavy and located outside of this repo (link provided above). Thus, to make these programs work, user must download the database, and then change in `sudoku.py` at class `SuDokuCollection()` as `SuDokuCollection(source_data_path=<path>)` where `<path>` is the local path of this database.
