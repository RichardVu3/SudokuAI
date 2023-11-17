from sudoku import *
import sys

id, puzzle, solution = SuDokuCollection(source_data_path='/home/richardvu/intermediate-python-programming/SudokuAI/', db_name='unsolved_sudoku.db')\
    .query_data(f"select id,  puzzle, solution from sudoku where id = 1594", get_all=False)

# Current unsolved: 464

board = Board(puzzle, solution)

print("Puzzle")

board.print_board()

print("")

# print("Solution")

# board.print_board(puzzle=False)

# print("")

print("AI Play")

ai = SuDokuAI(board.puzzle)

ai.infer_knowledge()

while not board.is_solved():
    cell, value = ai.fill()
    if cell == "No more cell to be inferred.":
        break
    elif not isinstance(cell, tuple):
        break
    try:
        board.is_violating(cell, value)
    except GameViolation:
        print(f"Game {id}: Cell {cell} with value {value} violates the Game.")
        # sys.exit(0)
    else:
        board.update(cell, value)
            
board.print_board()

print()

if board.is_solved():
    print("Congratulations. Your AI solved the Sudoku game. Yayyyyyyy.")

print()

print("Known", len(ai.known))

print(ai.known)

print("")

print("Knowledge", len(ai.knowledges))

print(ai.knowledges)

print("")