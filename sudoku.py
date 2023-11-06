import random, sqlite3, os, sys
import pandas as pd
from colorama import Fore, Back, Style
from collections import Counter
from itertools import combinations


class GameViolation(Exception):
    '''
    GameViolation is raised under 2 circumstances:
    1. The input by the AI is given to a filled cell (this is to ensure that the AI always give the correct answer)
    2. The Game rule is violated
    '''
    pass


class SuDokuCollection:
    '''
    This class is to store the Sudoku puzzle and its solution to the Database
    '''
    def __init__(self, source_data_path="~/personal/final-project-RichardVu3/sudoku.csv", db_name='sudoku.db', re_read_data=False):
        # We create a database in the folder where the source data file exists
        current_dir = os.getcwd() # get the current working directory
        database_path = source_data_path[:(source_data_path.rfind("/"))]
        if '~' in source_data_path:
            database_path = database_path.replace('~', os.path.expanduser('~'))
        os.chdir(database_path) # change the working directory to the one where the source data exists
        self.connect = sqlite3.connect(db_name)
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
    This is the Sudoku game representation
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
    
    def store_solved(self):
        '''
        Store the solution of the a solved game into database
        '''
        pass
    
    def check_store_solved(self):
        '''
        Check internal database whether a sudoku game has already been solved in the past
        
        Output: return True if the sudoku is in the database
        '''
        pass
    
    def is_solved(self):
        '''
        Check whether all the cells in the Sudoku board are filled or not
        
        Output: return True if all the celss are filled, False otherwise
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
    
    
class SuDokuAI:
    '''
    This is the representation of the AI to solve the Sudoku game
    '''
    def __init__(self, board):
        '''
        There should be a set to store all known_cell, all filled_cell,
        the block, row and column to be checked
        There is an internall knowledge (a dictionary stores the unknown cells and
        their possible values)

        Highlights: The SuDoKuAI only reads the board the first time to initialize the puzzle. Afterwards, it interacts with the Board

        Input: board: a list of 9 lists with given numbers and 0s representing blank cells
        '''
        # Contains all the possible values of each unknown cells
        self.knowledges = dict()
        # Contains all the known cells
        self.known = dict()
        # This is the cell the AI sends to the Board. By default, this set contains all given cells
        self.send = set()
        # Group all the cells in the same block together
        blocks = {(row, column): [] for row in range(0,9,3) for column in range(0,9,3)}

        for row in range(9):
            for column in range(9):
                value = board[row][column]
                if value == 0:
                    self.knowledges[(row, column)] = set(range(1, 10))
                    for block in blocks:
                        if self.is_same_block((row, column), block):
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
        This is the core brain of the AI. The steps to execute:
        1. Run self.known_cell to check whether we can infer any cells
        1. For each cell in self.knowledges, check whether we can remove any numbers based on the row, column, block or the relationship between
        the knowledge
        2. For any known, send a known cell to the board to check the violation
        3. Add a cell the self.send
        '''
        times = 0
        while times <= 1:
            self.conclude_cells()
            if len(self.knowledges) == 0:
                break
            self.hidden_single()
            # self.hidden_pair()
            self.naked_pair()
            self.pointing_pair()
            self.empty_rectangle()
            # self.naked_triple()
            # self.x_wings()
            # self.naked_quad()
            # self.sword_fish()
            # self.forcing_chain()
            times += 1

    def conclude_cells(self):
        '''
        Something to be input here
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
                        self.is_same_row(cell, knowledge) or\
                        self.is_same_column(cell, knowledge) or\
                        self.is_same_block(cell, knowledge)]
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
                    if self.is_same_block(cell, (row, column)):
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
        def run_naked_pair(pair):
            '''
            Something to be input here
            '''
            cell_1, cell_2 = pair
            # Row
            if self.is_same_row(cell_1, cell_2):
                for cell in set(self.knowledges.keys()).difference(set(cells)):
                    if self.is_same_row(cell, cell_1):
                        self.remove_numbers(cell, set(possible_set))
            # Column
            elif self.is_same_column(cell_1, cell_2):
                for cell in set(self.knowledges.keys()).difference(set(cells)):
                    if self.is_same_column(cell, cell_1):
                        self.remove_numbers(cell, set(possible_set))
            # Block
            if self.is_same_block(cell_1, cell_2):
                for cell in set(self.knowledges.keys()).difference(set(cells)):
                    if self.is_same_block(cell, cell_1):
                        self.remove_numbers(cell, set(possible_set))
        
        # Get all the cells with 2 possible values
        two_values_cells = {key: value for key, value in self.knowledges.items() if len(value) == 2}
        possible_sets = set([tuple(sorted(list(value))) for value in two_values_cells.values()])
        for possible_set in possible_sets:
            cells = [key for key in two_values_cells.keys() if two_values_cells[key] == set(possible_set)]
            if len(cells) > 2:
                for pair in list(combinations(cells, 2)):
                    run_naked_pair(pair)
            if len(cells) == 2:
                run_naked_pair(cells)
        self.conclude_cells()

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
                if self.is_same_row(*candidates[candidate]):
                    row = list(candidates[candidate])[0][0]
                    for knowledge in set(self.knowledges.keys()).difference(set(cells_in_block)):
                        if knowledge[0] == row and candidate in self.knowledges[knowledge]:
                            self.remove_numbers(knowledge, set([candidate]))
                elif self.is_same_column(*candidates[candidate]):
                    column = list(candidates[candidate])[0][1]
                    for knowledge in set(self.knowledges.keys()).difference(set(cells_in_block)):
                        if knowledge[1] == column and candidate in self.knowledges[knowledge]:
                            self.remove_numbers(knowledge, set([candidate]))
            self.conclude_cells()

    def empty_rectangle(self):
        '''
        Something to be input later
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
                cells_to_check = {cell for cell in self.knowledges if (not self.is_same_block(cell, cell_to_follow)) and cell[to_lookup] == cell_to_follow[to_lookup] and candidate in self.knowledges[cell]}
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
                    if not self.is_same_block(*pair):
                        directions = lookup_empty_rectangle(row_or_column, candidate, *pair)
                        for direction in directions:
                            row, column = direction if row_or_column == 0 else direction[::-1]
                            if (row, column) in self.knowledges and candidate in self.knowledges[(row, column)]:
                                self.remove_numbers((row, column), set([candidate]))
            self.conclude_cells()
    
    def naked_triple(self):
        '''
        Three cells in the same row, column or block having only three candidates or subsets of three candidates, then other appearances of the same
        candidate in the same row, column or block can be eliminated.
        '''
        if len(self.knowledges) == 0:
            return
        self.conclude_cells()

    def x_wings(self):
        '''
        If a candidate appears in four cells forming a rectangle and it appears only in 2 cells of each row then all other appearances of the candidate
        lying in the two columns can be eliminated. Also applies if row and column are switched
        '''
        if len(self.knowledges) == 0:
            return
        self.conclude_cells()

    def hidden_pair(self):
        '''
        A pair of candidates only appears in 2 cells in a row, column or block but they aren't the only candidates in those 2 cells, then all other
        candidates other than the pair can be eliminated and yield a Naked Pair.
        '''
        if len(self.knowledges) == 0:
            return
        self.conclude_cells()

    def naked_quad(self):
        '''
        Similar to naked_pair and naked_triple but apply to 4 candidates.
        '''
        if len(self.knowledges) == 0:
            return
        self.conclude_cells()

    def sword_fish(self):
        if len(self.knowledges) == 0:
            return
        self.conclude_cells()

    def forcing_chain(self):
        if len(self.knowledges) == 0:
            return
        self.conclude_cells()

    @staticmethod
    def is_same_row(*cells):
        return len(set([cell[0] for cell in cells])) == 1

    @staticmethod
    def is_same_column(*cells):
        return len(set([cell[1] for cell in cells])) == 1

    @staticmethod
    def is_same_block(*cells):
        row, column = cells[0]
        return all([cell[0] in range((row//3)*3, (row//3)*3+3) and cell[1] in range((column//3)*3, (column//3)*3+3) for cell in cells[1:]])
