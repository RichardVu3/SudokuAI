import random, sqlite3, os
import pandas as pd
from colorama import Fore, Style
from collections import Counter
from itertools import combinations


class GameViolation(Exception):
    '''
    GameViolation is raised when The Game rule is violated (this is to ensure that the AI always give the correct answer)
    '''
    pass


class SuDokuCollection:
    '''
    This class is to store the Sudoku puzzles and solutions to the Database
    '''
    def __init__(self, source_data_path="~/personal/final-project-RichardVu3/sudoku.csv", re_read_data=False):
        # We create a database in the folder where the source data file exists
        current_dir = os.getcwd() # get the current working directory
        database_path = source_data_path[:(source_data_path.rfind("/"))]
        if '~' in source_data_path:
            database_path = database_path.replace('~', os.path.expanduser('~'))
        os.chdir(database_path) # change the working directory to the one where the source data exists
        self.connect = sqlite3.connect("sudoku.db")
        self.cursor = self.connect.cursor()
        if re_read_data:
            self.source_data_path = source_data_path
            self.store_data_to_database()
        os.chdir(current_dir) # return back to the working directory where the program exists
    
    def read_data(self):
        '''
        This function reads data from a csv file and store as a attribute of the object
        CSV file has 2 columns: puzzle (the sudoku puzzle) and solution (the solution of the sudoku puzzle)
        It also adds a column to define the level of difficulty

        Modify: create a new object attribute name self.source_data. This is a DataFrame with 3 columns: puzzle, solution and level_of_difficulty
        '''
        self.source_data = pd.read_csv(self.source_data_path)
        def define_difficulty(row):
            if row.count('0') >= 47:
                return 'Hard'
            elif row.count('0') >= 39:
                return 'Medium'
            else:
                return 'Easy'
        self.source_data['level_of_difficulty'] = self.source_data['puzzle'].apply(define_difficulty)

    def initialize_table(self):
        '''
        This function is to create the data schema of database
        '''
        create_table = """
            CREATE TABLE IF NOT EXISTS sudoku (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                puzzle TEXT NOT NULL,
                solution TEXT NOT NULL,
                level_of_difficulty TEXT NOT NULL
            )
        """
        self.cursor.execute(create_table)
        self.connect.commit()

    def delete_all(self):
        '''
        Delete all data in table
        '''
        self.cursor.execute("DELETE FROM sudoku")
        self.connect.commit()

    def store_data_to_database(self):
        '''
        This function is to store the data from csv file to the database
        '''
        self.initialize_table()
        self.read_data()
        self.source_data.to_sql(name='sudoku', con=self.connect, if_exists='replace', index=True, index_label='id')
        self.connect.commit()

    def query_data(self, query, get_all=True):
        '''
        This function lets the user to use SQL to query the data from the table
        The structure of a row in the table: id, puzzle, solution, level_of_difficulty

        Input:  a query (written in SQL), type str
        Ouput:  all the query result if get_all is True (list of tuples),
                a random row in the query result if get_all is False (a tuple)
        '''
        if get_all:
            return self.cursor.execute(query).fetchall()
        return random.choice(self.cursor.execute(query).fetchall())


class Board:
    '''
    This is the representation of the Sudoku game
    '''
    def __init__(self, puzzle, solution):
        '''
        Inititalize the board

        Input: receive puzzle and solution. Each of them is a string containing 81 numbers, representing a sudoku game from left to right,
        from top to bottom. Puzzle contains '0' as the blank space. Solution contains no '0'

        Modify: create 2 attributes, self.puzzle and self.solution, each of which is a list of 9 lists whereas each Sudoku row is an inner list
        '''
        def deserialize(string):
            '''
            Input: an 81-chars string containing number
            Output: a list of 9 lists whereas each inner list contains 9 elements, representing a sudoku row
            '''
            return [[int(s) for s in string[i:i+9]] for i in range(0, len(string), 9)]

        self.puzzle = deserialize(puzzle)
        self.solution = deserialize(solution)
        self.given_cells = [(row, column) for row in range(9) for column in range(9) if self.puzzle[row][column] != 0] # the cells are given at the beginning of the game
    
    def is_solved(self):
        '''
        Check whether the solved puzzle is accurate
        
        Output: return True if the solved puzzle is the same as the solution, False otherwise
        '''
        return self.puzzle == self.solution
    
    def is_violating(self, cell, value):
        '''
        Check whether an input into a cell is a violation to the rule

        Input: a cell in format (row_num, column_num), type tuple
               value: is a number to input in the cell
        
        Output: raise GameViolation Exception
        '''
        row_num, column_num = cell
        if value in self.puzzle[row_num] or\
            value in [r[column_num] for r in self.puzzle] or\
            value in [self.puzzle[r][c] for r in range((row_num//3)*3, (row_num//3)*3+3) for c in range((column_num//3)*3, (column_num//3)*3+3)]:
            raise GameViolation
    
    def print_board(self, with_color=True, puzzle=True):
        '''
        This function prints out the current status of the game.
        The given numbers are colored differently compared to the filled number

        Input: puzzle: print the puzzle if True, else solution
        
        Output: print the board with the color rule as described
        '''
        if puzzle:
            to_print = self.puzzle
        else:
            to_print = self.solution
        if with_color:
            for row in range(9):
                if row % 3 == 0 and row > 0:
                    print('- - - - - - - - - - -')
                for column in range(9):
                    if column % 3 == 0 and column > 0:
                        print('|', end=' ')
                    item = to_print[row][column]
                    if item == 0:
                        item = ' '
                    if (row, column) in self.given_cells:
                        print(Fore.MAGENTA + str(item) + Style.RESET_ALL, end=' ')
                    else:
                        print(Fore.GREEN + str(item) + Style.RESET_ALL, end=' ')
                print('\n', end='')
        else:
            i = 0
            for row in to_print:
                if i % 3 == 0 and i > 0:
                    print('- - - - - - - - - - -')
                row = [str(ele) for ele in row]
                to_be_printed = ' | '.join([' '.join(row[i:i+3]) for i in range(0, len(row), 3)]) .replace('0', ' ')
                print(to_be_printed)
                i += 1
    
    def update(self, cell, value):
        '''
        This function updates the board with the value at the cell if no GameViolation is raised

        Input: cell: a tuple of (row, column)
               value: the number to fill in the cell
        
        Modify: self.puzzle if GameViolation is not raised, else do nothing
        '''
        row, column = cell
        self.puzzle[row][column] = value

    def get_puzzle(self):
        '''
        Safely access the class attribute `puzzle`
        '''
        return self.puzzle
    
    def get_solution(self):
        '''
        Safely access the class attribute `solution`
        '''
        return self.solution
    
    def get_cell_value(self, position):
        '''
        Safely get the value at `position`

        Input: position: a tuple of (row, column)

        Return: the value at position
        '''
        row, column = position
        value = int(self.puzzle[row][column])
        return value if value > 0 else None
    
    def get_given_cells(self):
        '''
        Safely access the class attribute `given_cells`
        '''
        return self.given_cells
    
    
class SuDokuAI:
    '''
    This is the representation of the AI to solve the Sudoku game
    '''
    def __init__(self, board):
        '''
        Initiate all necessary attributes

        Highlights: The SuDoKuAI only reads the board the first time to initialize the puzzle. Afterwards, it interacts with the Board

        Input: board: a list of 9 lists with given numbers and 0s representing blank cells
        '''
        # Contains all the possible values of each unknown cells
        self.knowledges = dict()
        # Contains all the known cells
        self.known = dict()
        # This is the cell the AI sends to the Board. When the class is instantiated, this set contains all given cells
        self.send = set()
        # Group all the cells in the same block together
        blocks = {(row, column): [] for row in range(0,9,3) for column in range(0,9,3)}
        for row in range(9):
            for column in range(9):
                value = board[row][column]
                if value == 0:
                    self.knowledges[(row, column)] = set(range(1, 10))
                    for block in blocks:
                        if self.is_same_block(((row, column), block)):
                            blocks[block].append((row, column))
                else:
                    self.known[(row, column)] = value
                    self.send.add((row, column))
        
        self.blocks = [set(block) for block in blocks.values()] # a list of sets, each set represents a block

    def fill(self):
        '''
        This function returns a random known cell to the board
        
        Output: a known cell in self.known but not in self.send

        Modify: nothing
        '''
        try:
            cell = random.choice(list(set(self.known.keys()).difference(self.send)))
        except IndexError:
            return "No more cell to be inferred.", ""
        except Exception as e:
            return e, ""
        value = self.known[cell]
        self.send.add(cell)
        return cell, value
    
    def known_cell(self, possible_values):
        '''
        This function updates the knowledge if a cell can be filled with a number

        Input: a set of possible values of a cell

        Ouput: True if there is only one option for the cell. False otherwise
        '''
        if len(possible_values) == 1:
            return True
        return False
        
    def remove_numbers(self, cell, numbers, reverse=False):
        '''
        This function removes the numbers from the possible set
        
        Input: a cell: tuple
                a set of number: a set
                reversse: True if we want to remove numbers from cell else we remove other elements except number
        
        Modify: itself with fewer values in the possible set of a particular cell
        '''
        if reverse:
            self.knowledges[cell] = numbers
        else:
            self.knowledges[cell] = self.knowledges[cell].difference(numbers)
    
    def infer_knowledge(self):
        '''
        This is the core coordination of the AI. The function is to use strategies to solve the Sudoku game.

        First, the knowledge is initiated by calling conclude_cells()
        Then, if the game can be solely solved with hidden_single(), end the function
        Else, call multiple high-level strategies to infer new knowledge to solve the game.

        There is one loop with a tracker varibale `times`. This loop is to ensure that all the high-level strategies can
        interact with each other to solve the game at least once.
        '''
        self.conclude_cells()
        times = 0
        while times <= 1:
            self.hidden_single()
            if len(self.knowledges) == 0:
                break
            self.naked_pair()
            self.pointing_pair()
            self.empty_rectangle()
            self.y_wings()
            self.x_wings()
            times += 1

    def conclude_cells(self):
        '''
        Remove all invalid numbers from the knowledge base based on inference process.
        If a value is ensured to be in a position, remove that from the knowledge base and add it to self.known
        '''
        bfr_infer, aftr_infer = 0, 1
        while aftr_infer != 0:
            if bfr_infer == aftr_infer:
                break
            bfr_infer = len(self.knowledges)
            # First, remove invalid numbers from the knowledge base
            for knowledge in self.knowledges:
                known_values = set(
                        [self.known[cell] for cell in self.known if \
                        self.is_same_row((cell, knowledge)) or\
                        self.is_same_column((cell, knowledge)) or\
                        self.is_same_block((cell, knowledge))]
                    )
                self.remove_numbers(knowledge, known_values)
            # Then, check whether we can conclude any cells
            cells = list(self.knowledges.keys())
            for cell in cells:
                if self.known_cell(self.knowledges[cell]):
                    value = self.knowledges.pop(cell).pop()
                    self.known[cell] = value
            aftr_infer = len(self.knowledges)

    def hidden_single(self):
        '''
        If one of the candidates within a cell is the only candidate in a row, column or block, that candidate is the solution of the cell.
        '''
        if len(self.knowledges) == 0:
            return
        # Row and Column
        for row_or_column in [0, 1]:
            lines = set([cell[row_or_column] for cell in self.knowledges.keys()])
            for line in lines:
                cells_in_check = {key: value for key, value in self.knowledges.items() if key[row_or_column] == line}
                possibles = [possible for cell in cells_in_check for possible in cells_in_check[cell]]
                unique_values = [pair[0] for pair in Counter(possibles).most_common() if pair[1] == 1]
                for unique_value in unique_values:
                    cell = [cell for cell in cells_in_check if unique_value in cells_in_check[cell]][0]
                    self.remove_numbers(cell, set([unique_value]), reverse=True)
            self.conclude_cells()

        # Block
        blocks = dict()
        for row in range(0, 9, 3):
            for column in range(0, 9, 3):
                for cell in self.knowledges:
                    if self.is_same_block((cell, (row, column))):
                        if (row, column) not in blocks:
                            blocks[(row, column)] = []
                        blocks[(row, column)].append(cell)
        for block in blocks:
            cells_in_check = {key: value for key, value in self.knowledges.items() if key in blocks[block]}
            possibles = [possible for cell in cells_in_check for possible in cells_in_check[cell]]
            unique_values = [pair[0] for pair in Counter(possibles).most_common() if pair[1] == 1]
            for unique_value in unique_values:
                cell = [cell for cell in cells_in_check if unique_value in cells_in_check[cell]][0]
                self.remove_numbers(cell, set([unique_value]), reverse=True)
        self.conclude_cells()

    def naked_pair(self):
        '''
        If a pair of candidates exist in two cells within the same row, column or block, the pair of candidates are the solutions to those
        two cells and all other cells can eliminate this pair of candidates
        '''
        if len(self.knowledges) == 0:
            return
        def run_naked_pair(pair, possible_set):
            '''
            Execute the elimination of the naked pair
            Input: pair: the naked pair
                    possible_set: the values to be removed from the pair
            '''
            cell_1, cell_2 = pair
            # Row
            if self.is_same_row((cell_1, cell_2)):
                for cell in set(self.knowledges.keys()).difference(set(pair)):
                    if self.is_same_row((cell, cell_1)):
                        self.remove_numbers(cell, set(possible_set))
            # Column
            elif self.is_same_column((cell_1, cell_2)):
                for cell in set(self.knowledges.keys()).difference(set(pair)):
                    if self.is_same_column((cell, cell_1)):
                        self.remove_numbers(cell, set(possible_set))
            # Block
            if self.is_same_block((cell_1, cell_2)):
                for cell in set(self.knowledges.keys()).difference(set(pair)):
                    if self.is_same_block((cell, cell_1)):
                        self.remove_numbers(cell, set(possible_set))
        
        # Get all the cells with 2 possible values
        two_values_cells = {key: value for key, value in self.knowledges.items() if len(value) == 2}
        possible_sets = set([tuple(sorted(list(value))) for value in two_values_cells.values()])
        for possible_set in possible_sets:
            cells = [key for key in two_values_cells.keys() if two_values_cells[key] == set(possible_set)]
            if len(cells) > 2:
                for pair in list(combinations(cells, 2)):
                    run_naked_pair(pair, possible_set)
            elif len(cells) == 2:
                run_naked_pair(cells, possible_set)
        self.hidden_single()

    def pointing_pair(self):
        '''
        A candidate appears only in two (or three) cells in a block and those cells are in the same row or column, then all appearances of that
        candidate outside the block in the same row or column can be eliminated.
        '''
        if len(self.knowledges) == 0:
            return
        for block in self.blocks:
            cells_in_block = {cell: value for cell, value in self.knowledges.items() if cell in block}
            if len(cells_in_block) <= 1:
                continue
            candidates = dict()
            for cell, values in cells_in_block.items():
                for value in values:
                    if value not in candidates:
                        candidates[value] = set()
                    candidates[value].add(cell)
            for candidate in candidates:
                if self.is_same_row(candidates[candidate]):
                    row = list(candidates[candidate])[0][0]
                    for knowledge in set(self.knowledges.keys()).difference(set(cells_in_block)):
                        if knowledge[0] == row and candidate in self.knowledges[knowledge]:
                            self.remove_numbers(knowledge, set([candidate]))
                elif self.is_same_column(candidates[candidate]):
                    column = list(candidates[candidate])[0][1]
                    for knowledge in set(self.knowledges.keys()).difference(set(cells_in_block)):
                        if knowledge[1] == column and candidate in self.knowledges[knowledge]:
                            self.remove_numbers(knowledge, set([candidate]))
            self.hidden_single()

    def empty_rectangle(self):
        '''
        An Empty Rectangle as a rectangle that is inside a Square and the corners of which do not contain a particular Candidate.
        If we can find a Strong Link that has one of its ends on the same Row as one of the Rows of the Square that contains the
        Empty Rectangle and if that Row does not contain any corner of the Empty Rectangle, then the Candidate can not be the
        solution in the Cell that is located on the same Row as the other end of the Strong Link and on the Column of the Square
        that does not contain any corner of the Empty Rectangle.
        '''
        if len(self.knowledges) == 0:
            return
        
        def lookup_empty_rectangle(row_or_column, candidate, cell_1, cell_2):
            to_return = []
            for cell_to_follow in (cell_1, cell_2):
                cell_not_to_follow = cell_2 if cell_to_follow == cell_1 else cell_1
                if row_or_column == 0:
                    to_lookup, inverse_lookup = 1, 0
                else:
                    to_lookup, inverse_lookup = 0, 1
                cells_to_check = {cell for cell in self.knowledges if (not self.is_same_block((cell, cell_to_follow))) and cell[to_lookup] == cell_to_follow[to_lookup] and candidate in self.knowledges[cell]}
                blocks = {tuple(block.intersection(set(self.knowledges.keys()))) for cell in cells_to_check for block in self.blocks if cell in block}
                for block in blocks:
                    cells_with_candidate = {cell for cell in block if candidate in self.knowledges[cell]}
                    aligned_cells = {cell for cell in cells_with_candidate if cell[to_lookup] == cell_to_follow[to_lookup]}
                    un_aligned_cells = cells_with_candidate.difference(aligned_cells)
                    if len({cell[inverse_lookup] for cell in un_aligned_cells}) == 1:
                        to_return.append((list(un_aligned_cells)[0][inverse_lookup], cell_not_to_follow[to_lookup]))
            return to_return
        
        for row_or_column in [0, 1]:
            for line in {cell[row_or_column] for cell in self.knowledges}:
                cells_in_line = {cell: value for cell, value in self.knowledges.items() if cell[row_or_column] == line}
                candidates_in_check = [value[0] for value in Counter([possible for cell in cells_in_line for possible in cells_in_line[cell]]).most_common() if value[1] == 2]
                for candidate in candidates_in_check:
                    pair = {cell for cell in cells_in_line if candidate in cells_in_line[cell]}
                    if not self.is_same_block(tuple(pair)):
                        directions = lookup_empty_rectangle(row_or_column, candidate, *pair)
                        for direction in directions:
                            row, column = direction if row_or_column == 0 else direction[::-1]
                            if (row, column) in self.knowledges and candidate in self.knowledges[(row, column)]:
                                self.remove_numbers((row, column), set([candidate]))
            self.hidden_single()

    def x_wings(self):
        '''
        If a candidate appears in four cells forming a rectangle and it appears only in 2 cells of each row then all other appearances of the candidate
        lying in the two columns can be eliminated. Also applies if row and column are switched
        '''
        if len(self.knowledges) == 0:
            return

        for line, line_perpen in [(0, 1), (1, 0)]:
            for align in {cell[line] for cell in self.knowledges}:
                all_values = [value for cell in self.knowledges if cell[line] == align for value in self.knowledges[cell]]
                candidates = [value[0] for value in Counter(all_values).most_common() if value[1] == 2]
                for candidate in candidates:
                    all_cells_with_candidates = {cell: value for cell, value in self.knowledges.items() if candidate in self.knowledges[cell]}
                    cells_with_candidates = [cell for cell in all_cells_with_candidates if cell[line] == align]
                    aligned_perpens = {cell[line_perpen] for cell in cells_with_candidates}
                    all_aligned_cells = {cell for cell in self.knowledges if cell[line_perpen] in aligned_perpens and candidate in self.knowledges[cell] and not self.is_same_block((cell, *cells_with_candidates), any_pair=True)}
                    aligns_of_aligned_cells = {counter[0] for counter in Counter([cell[line] for cell in all_aligned_cells]).most_common() if counter[1] == 2}
                    for align_of_aligned_cells in aligns_of_aligned_cells:
                        if len([cell for cell in all_cells_with_candidates if cell[line] == align_of_aligned_cells and candidate in all_cells_with_candidates[cell] and cell not in cells_with_candidates]) != 2:
                            continue
                        aligned_cells = {cell for cell in all_aligned_cells if cell[line] == align_of_aligned_cells}
                        cells_to_remove_candidates = {cell for cell in self.knowledges if cell[line_perpen] in aligned_perpens and candidate in self.knowledges[cell] and cell not in cells_with_candidates and cell not in aligned_cells}
                        for cell_to_remove_candidate in cells_to_remove_candidates:
                            self.remove_numbers(cell_to_remove_candidate, {candidate})
            self.hidden_single()

    def y_wings(self):
        '''
        Find a cell with exactly two candidates. We'll call this cell a pivot.
        Look for two more cells with 2 candidates as well. These cells (called pincers) should be in the same row, column or block as the pivot.
        One of the two numbers in each pincer should be the same as in the pivot. The other number is the same for both pincers.
        Look where the both pincers intersect. If that cell contains a candidate that is shared by both pincers, we can eliminate it.
        '''
        if len(self.knowledges) == 0:
            return

        def find_pivot(cell_1, cell_2, cell_3):
            pivot, wings = None, None
            if self.is_peer((cell_1, cell_2)) and self.is_peer((cell_1, cell_3)) and not self.is_peer((cell_2, cell_3)):
                pivot, wings = cell_1, (cell_2, cell_3)
            elif self.is_peer((cell_2, cell_1)) and self.is_peer((cell_2, cell_3)) and not self.is_peer((cell_1, cell_3)):
                pivot, wings = cell_2, (cell_1, cell_3)
            elif self.is_peer((cell_3, cell_1)) and self.is_peer((cell_3, cell_2)) and not self.is_peer((cell_1, cell_2)):
                pivot, wings = cell_3, (cell_1, cell_2)
            return pivot, wings

        two_value_cells = {cell: values for cell, values in self.knowledges.items() if len(values) == 2}
        groups = [group for group in combinations(two_value_cells.keys(), 3) if not (self.is_same_block(group) or self.is_same_row(group) or self.is_same_column(group))]
        for group in groups:
            if len({tuple(sorted(list(two_value_cells[cell]))) for cell in group}) != 3 or len({value for cell in group for value in two_value_cells[cell]}) != 3:
                continue
            pivot, wings = find_pivot(*group)
            if not pivot:
                continue
            wings_value = two_value_cells[wings[0]].intersection(two_value_cells[wings[1]])
            if len(wings_value) != 1:
                continue
            for cell in self.knowledges:
                if cell in group:
                    continue
                if list(wings_value)[0] in self.knowledges[cell] and self.is_peer((cell, wings[0])) and self.is_peer((cell, wings[1])):
                    self.remove_numbers(cell, wings_value)
        self.hidden_single()

    def is_same_row(self, cells, any_pair=False):
        return len(set([cell[0] for cell in cells])) == 1

    def is_same_column(self, cells, any_pair=False):
        return len(set([cell[1] for cell in cells])) == 1

    def is_same_block(self, cells, any_pair=False):
        row, column = cells[0]
        if any_pair:
            return any([cell[0] in range((row//3)*3, (row//3)*3+3) and cell[1] in range((column//3)*3, (column//3)*3+3) for cell in cells[1:]])
        return all([cell[0] in range((row//3)*3, (row//3)*3+3) and cell[1] in range((column//3)*3, (column//3)*3+3) for cell in cells[1:]])
    
    def is_peer(self, cells, any_pair=False):
        return self.is_same_row(cells, any_pair) or self.is_same_column(cells, any_pair) or self.is_same_block(cells, any_pair)