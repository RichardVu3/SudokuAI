import pygame, sys, time, random
from sudoku import *

ROW = 9
COLUMN = 9
sleep_time = 0

# RGB of Colors
BLACK = (0, 0, 0)
GRAY = (210, 210, 210)
WHITE = (255, 255, 255)
BLUE = (143, 252, 255)
RED = (255, 176, 156)
GREEN = (0, 150, 0)

# Start game
pygame.init()
width = 1000
height = int(round(width * 2 / 3))
size = width, height
screen = pygame.display.set_mode(size)

# Define Fonts
OPEN_SANS = "assets/fonts/OpenSans-Regular.ttf"
large_font = pygame.font.Font(OPEN_SANS, int(round(width / 18)))
medium_font = pygame.font.Font(OPEN_SANS, int(round(width / 25)))
small_font = pygame.font.Font(OPEN_SANS, int(round(width / 35)))

# Compute board size
BOARD_PADDING = int(round(width / 30))
board_width = (int(round(2 / 3)) * width) - (BOARD_PADDING * 2)
board_height = height - (BOARD_PADDING * 2)
cell_size = int(min(board_width / ROW, board_height / COLUMN))
board_origin = (BOARD_PADDING, BOARD_PADDING)

# Create board game and AI agent
game_id = random.randint(0, 8999999)
id, puzzle, solution = SuDokuCollection().query_data(f"select id,  puzzle, solution from sudoku where id = {game_id}", get_all=False)
game = Board(puzzle, solution)
original_puzzle = game.get_given_cells()
ai = SuDokuAI(game.get_puzzle())

# Keep track of puzzle
ai_infer = False
violation = False
ai_could_continue = True

# Show welcome screen initially
welcome = True

#### Start a Game Session ####

while True:
    # Check if game is quit
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

    screen.fill(BLACK)

    if welcome:
        # Show Title
        title = large_font.render("Play Sudoku with an AI assistant", True, WHITE)
        title_rect = title.get_rect()
        title_rect.center = ((width / 2), (height / 4))
        screen.blit(title, title_rect)

        # Show Intro
        sentences = [
            "You wanna play against AI?",
            "Click AI Move to watch AI solving the puzzle.",
            "Click Reset to start a new game."
        ]
        for i, sentence in enumerate(sentences):
            line = small_font.render(sentence, True, WHITE)
            line_rect = line.get_rect()
            line_rect.center = ((width / 2), (height / 4) * 1.5 + (width / 30) * 1.5 * i)
            screen.blit(line, line_rect)

        # Create Let's go button
        button_rect = pygame.Rect((width / 4), (5 / 8) * height, width / 2, height / 6)
        button_text = medium_font.render("LET'S GO", True, BLACK)
        button_text_rect = button_text.get_rect()
        button_text_rect.center = button_rect.center
        pygame.draw.rect(screen, WHITE, button_rect)
        screen.blit(button_text, button_text_rect)

        click, _, _ = pygame.mouse.get_pressed()
        if click == 1: # Clicked something
            mouse = pygame.mouse.get_pos()
            if button_rect.collidepoint(mouse): # Clicked Let's go
                welcome = False

        pygame.display.flip()
        continue

    # Draw board
    cells = []
    for i in range(ROW):
        row = []
        for j in range(COLUMN):

            # Draw rectangle for cell
            rect = pygame.Rect(
                board_origin[0] + j * cell_size,
                board_origin[1] + i * cell_size,
                cell_size, cell_size
            )
            pygame.draw.rect(screen, GRAY, rect)
            pygame.draw.rect(screen, WHITE, rect, 3)

            pygame.draw.line(screen, BLACK, (BOARD_PADDING, BOARD_PADDING+3*cell_size), (BOARD_PADDING*9*cell_size, BOARD_PADDING+3*cell_size), width=6)
            pygame.draw.line(screen, BLACK, (BOARD_PADDING, BOARD_PADDING+6*cell_size), (BOARD_PADDING*9*cell_size, BOARD_PADDING+6*cell_size), width=6)
            pygame.draw.line(screen, BLACK, (BOARD_PADDING+3*cell_size, BOARD_PADDING), (BOARD_PADDING+3*cell_size, BOARD_PADDING*9*cell_size), width=6)
            pygame.draw.line(screen, BLACK, (BOARD_PADDING+6*cell_size, BOARD_PADDING), (BOARD_PADDING+6*cell_size, BOARD_PADDING*9*cell_size), width=6)

            # Add a number to the cells
            cell_value = game.get_cell_value((i, j))
            if cell_value is not None:
                color = BLACK if (i, j) in original_puzzle else GREEN
                number = small_font.render(str(cell_value), True, color)
                number_text_rect = number.get_rect()
                number_text_rect.center = rect.center
                screen.blit(number, number_text_rect)

            row.append(rect)
        cells.append(row)

    # AI Move button
    ai_button = pygame.Rect(
        (2 / 3) * width + BOARD_PADDING / 2, (1 / 3) * height - height / 6,
        (width / 3) - BOARD_PADDING * 2, height / 6
    )
    button_text = medium_font.render("AI Play", True, BLACK)
    button_rect = button_text.get_rect()
    button_rect.center = ai_button.center
    pygame.draw.rect(screen, WHITE, ai_button)
    screen.blit(button_text, button_rect)

    # Reset button
    reset_button = pygame.Rect(
        (2 / 3) * width + BOARD_PADDING / 2, (1 / 3) * height + height / 18,
        (width / 3) - BOARD_PADDING * 2, height / 6
    )
    button_text = medium_font.render("Reset", True, BLACK)
    button_rect = button_text.get_rect()
    button_rect.center = reset_button.center
    pygame.draw.rect(screen, WHITE, reset_button)
    screen.blit(button_text, button_rect)

    # Display text
    if violation:
        text, color = "VIOLATION!!!", WHITE
    elif game.is_solved():
        text, color = "!!! YAY !!!", WHITE
    elif not ai_could_continue:
        text, color = "SORRY DUDE", WHITE
    else:
        text, color = "", WHITE
    text = medium_font.render(text, True, color)
    text_rect = text.get_rect()
    text_rect.center = ((5 / 6) * width, (2 / 3) * height + height / 18)
    screen.blit(text, text_rect)
    
    # User needs to click either the AI Play or Reset button
    left, _, right = pygame.mouse.get_pressed()

    if left == 1:
        mouse = pygame.mouse.get_pos()

        # If AI button clicked, activate AI
        if ai_button.collidepoint(mouse) and not ai_infer and not violation and ai_could_continue:
            ai.infer_knowledge()
            ai_infer = True

        # Reset game state
        elif reset_button.collidepoint(mouse):
            # Create game and AI agent
            game_id = random.randint(0, 8999999)
            id, puzzle, solution = SuDokuCollection().query_data(f"select id,  puzzle, solution from sudoku where id = {game_id}", get_all=False)
            game = Board(puzzle, solution)
            original_puzzle = game.get_given_cells()
            ai = SuDokuAI(game.get_puzzle())

            # Keep track of puzzle
            ai_infer = False
            violation = False
            ai_could_continue = True
            
            continue

    if ai_infer and not violation and ai_could_continue:
        cell, value = ai.fill()
        if cell == "No more cell to be inferred.":
            if not game.is_solved():
                print(cell)
            ai_could_continue = False
        else:
            try:
                game.is_violating(cell, value)
            except GameViolation:
                violation = True
            else:
                game.update(cell, value)
        
        time.sleep(sleep_time)
    
    pygame.display.flip()