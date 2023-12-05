from sudoku import *

while True:
    try:
        game_id = int(input("Input game ID from 0 to 8999999: "))
    except:
        print("Invalid number.")
        continue
    else:
        if game_id > 8999999 or game_id < 0:
            print("Game ID out of range.")
            continue
        else:
            print()
            break

id, puzzle, solution = SuDokuCollection().query_data(f"select id,  puzzle, solution from sudoku where id = {game_id}", get_all=False)

board = Board(puzzle, solution)

print("******** Puzzle ********")

print()

board.print_board()

print()

print("******** AI Play ********")

print()

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
    else:
        board.update(cell, value)
            
board.print_board()

print()

if board.is_solved():
    print("Congratulations. Your AI solved the Sudoku game. Yayyyyyyy.")
    print()