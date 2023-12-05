from sudoku import *
import sys

games = SuDokuCollection().query_data(f"select id, puzzle, solution from sudoku", get_all=True)

total_games = len(games)

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
            games_violate_list.append(str(id))
            break
        else:
            board.update(cell, value)

    if board.is_solved():
        games_solved += 1
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