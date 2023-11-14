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
    def __init__(self, source_data_path="~/personal/final-project-RichardVu3/sudoku.csv", re_read_data=False, db_name='sudoku.db', id=False):
        self.db_name = db_name
        # We create a database in the folder where the source data file exists
        current_dir = os.getcwd() # get the current working directory
        database_path = source_data_path[:(source_data_path.rfind("/"))]
        if '~' in source_data_path:
            database_path = database_path.replace('~', os.path.expanduser('~'))
        os.chdir(database_path) # change the working directory to the one where the source data exists
        self.connect = sqlite3.connect(self.db_name)
        self.cursor = self.connect.cursor()
        if re_read_data:
            self.source_data_path = source_data_path
            self.store_data_to_database(id)
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

    def initialize_table(self, index=False):
        '''
        This function is to create the data schema of database
        '''
        self.cursor.execute('DROP TABLE IF EXISTS sudoku')
        self.connect.commit()
        if not index:
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
        else:
            create_table = """
                CREATE TABLE IF NOT EXISTS sudoku (
                    id INTEGER PRIMARY KEY,
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

    def store_data_to_database(self, id):
        '''
        This function is to store the data from csv file to the database
        '''
        self.initialize_table(index=id)
        self.read_data()
        self.source_data.to_sql(name='sudoku', con=self.connect, if_exists='replace', index=True)
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
    
    def query_to_dataframe(self, query):
        return pd.read_sql(query, con=self.connect, index_col='id')
    

if __name__ == '__main__':

    collection = SuDokuCollection()

    texts = sys.stdin.readlines()

    ids = texts[0]

    data_1 = collection.query_to_dataframe(f"select id, puzzle, solution from sudoku where id in ({ids})")

    print("Easy: ", data_1.shape)

    ids = texts[1]

    data_2 = collection.query_to_dataframe(f"select id, puzzle, solution from sudoku where id in ({ids})")

    print("Medium: ", data_2.shape)

    ids = texts[2]

    data_3 = collection.query_to_dataframe(f"select id, puzzle, solution from sudoku where id in ({ids})")

    print("Hard: ", data_3.shape)

    data = pd.concat([data_1, data_2, data_3])

    print("Data: ", data.shape)
        
    # games = SuDokuCollection().query_data(f"select id, puzzle, solution from sudoku where id in ({ids})", get_all=True)

    # print(f'Total games: {len(games)}')

    # data = collection.query_to_dataframe(f"select id, puzzle, solution from sudoku where id in ({ids})")

    data.to_csv('unsolved_puzzle.csv', index=True)

    light_collection = SuDokuCollection(db_name='unsolved_sudoku.db', source_data_path="~/personal/final-project-RichardVu3/unsolved_puzzle.csv", re_read_data=True, id=True)
    # light_collection  = SuDokuCollection(db_name='unsolved_sudoku.db', re_read_data=False)

    print('Light Sudoku: ', light_collection.query_data("select count(*) from sudoku"))