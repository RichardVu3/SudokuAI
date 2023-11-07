from sudoku import *
import sys

# Successful solving puzzles: 8995909, 7941996, 7941421, 8687596, 7639009, 3907620, 4721579, 4721523, 3546782, 2901458, 1959271, 798098, 72578

# games = SuDokuCollection().query_data("select id, puzzle, solution from sudoku where level_of_difficulty='Hard'")

for text in sys.stdin:
    ids = text

# ids = '8995909, 7941996, 7941421, 8687596, 7639009, 3907620, 4721579, 4721523, 3546782, 2901458, 1959271, 798098, 72578'

games = SuDokuCollection(source_data_path='/home/richardvu/intermediate-python-programming/SudokuAI/', db_name='unsolved_sudoku.db').query_data(f"select id, puzzle, solution from sudoku where id in ({ids})", get_all=True)

# games = SuDokuCollection(source_data_path='/home/richardvu/intermediate-python-programming/SudokuAI/', db_name='unsolved_sudoku.db').query_data(f"select id, puzzle, solution from sudoku", get_all=True)

total_games = len(games)

print(total_games)

#sys.exit(0)

games_solved = 0

games_violate_list = []

games_not_solved_list = []

for game in games:
    id, puzzle, solution = game

    board = Board(puzzle, solution)

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
            games_violate_list.append(str(id))
            break
        else:
            board.update(cell, value)

    if board.is_solved():
        games_solved += 1
        # game_solved_list.append(id)
        print(f"Game {id} solved.")
    else:
        print(f"Game {id} cannot be solved.")
        games_not_solved_list.append(str(id))

print()

print(f"Succefully solved {games_solved} out of {total_games} games.")

print()

print("Violation: ", ','.join(games_violate_list))

print()

print("Not solved: ", ','.join(games_not_solved_list))
