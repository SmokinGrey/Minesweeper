import pygame
import random
import time

# --- Constants ---
DIFFICULTY_LEVELS = {
    "Easy": {"size": (9, 9), "mines": 10},
    "Normal": {"size": (16, 16), "mines": 40},
    "Hard": {"size": (30, 16), "mines": 99}
}
current_difficulty = "Easy"

GRID_WIDTH = DIFFICULTY_LEVELS[current_difficulty]["size"][0]
GRID_HEIGHT = DIFFICULTY_LEVELS[current_difficulty]["size"][1]
NUM_MINES = DIFFICULTY_LEVELS[current_difficulty]["mines"]
TILE_SIZE = 30
PANEL_HEIGHT = 60

# Screen dimensions
SCREEN_WIDTH = GRID_WIDTH * TILE_SIZE
SCREEN_HEIGHT = GRID_HEIGHT * TILE_SIZE + PANEL_HEIGHT

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (192, 192, 192)
LIGHT_GRAY = (211, 211, 211)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

def create_board():
    """Creates the game board."""
    board = [[{'is_mine': False, 'is_revealed': False, 'is_flagged': False, 'neighbor_mines': 0} for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
    return board

def place_mines(board, first_click_pos):
    """Places mines randomly on the board, avoiding the first click area."""
    mines_placed = 0
    while mines_placed < NUM_MINES:
        x = random.randint(0, GRID_WIDTH - 1)
        y = random.randint(0, GRID_HEIGHT - 1)
        if (x, y) != first_click_pos and not board[y][x]['is_mine']:
            board[y][x]['is_mine'] = True
            mines_placed += 1
    return board

def calculate_neighbor_mines(board):
    """Calculates the number of neighboring mines for each tile."""
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            if not board[y][x]['is_mine']:
                count = 0
                for i in range(-1, 2):
                    for j in range(-1, 2):
                        if 0 <= y + i < GRID_HEIGHT and 0 <= x + j < GRID_WIDTH:
                            if board[y + i][x + j]['is_mine']:
                                count += 1
                board[y][x]['neighbor_mines'] = count
    return board

def reveal_tile(board, x, y):
    """Reveals a tile and recursively reveals neighbors if it's empty."""
    if not (0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT):
        return

    tile = board[y][x]
    if tile['is_revealed'] or tile['is_flagged']:
        return

    tile['is_revealed'] = True

    if tile['is_mine']:
        return

    if tile['neighbor_mines'] == 0:
        for i in range(-1, 2):
            for j in range(-1, 2):
                if i == 0 and j == 0:
                    continue
                reveal_tile(board, x + j, y + i)

def draw_board(screen, font, board):
    """Draws the game board."""
    board_start_x = (SCREEN_WIDTH - GRID_WIDTH * TILE_SIZE) // 2
    board_start_y = (SCREEN_HEIGHT - PANEL_HEIGHT - GRID_HEIGHT * TILE_SIZE) // 2 + PANEL_HEIGHT

    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            rect = pygame.Rect(board_start_x + x * TILE_SIZE, board_start_y + y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            if board[y][x]['is_revealed']:
                pygame.draw.rect(screen, LIGHT_GRAY, rect)
                if board[y][x]['is_mine']:
                    pygame.draw.circle(screen, RED, rect.center, TILE_SIZE // 3)
                elif board[y][x]['neighbor_mines'] > 0:
                    text = font.render(str(board[y][x]['neighbor_mines']), True, BLACK)
                    screen.blit(text, (rect.x + (TILE_SIZE - text.get_width()) // 2, rect.y + (TILE_SIZE - text.get_height()) // 2))
            else:
                pygame.draw.rect(screen, GRAY, rect)
                if board[y][x]['is_flagged']:
                    flag_text = font.render('F', True, BLUE)
                    screen.blit(flag_text, (rect.x + (TILE_SIZE - flag_text.get_width()) // 2, rect.y + (TILE_SIZE - flag_text.get_height()) // 2))

            pygame.draw.rect(screen, BLACK, rect, 1)

def draw_panel(screen, font, elapsed_time, mines_left):
    """Draws the top panel with timer and mine counter."""
    pygame.draw.rect(screen, GRAY, (0, 0, SCREEN_WIDTH, PANEL_HEIGHT))

    timer_text = font.render(f"Time: {int(elapsed_time)}", True, BLACK)
    screen.blit(timer_text, (10, 10))

    mines_text = font.render(f"Mines: {mines_left}", True, BLACK)
    screen.blit(mines_text, (SCREEN_WIDTH - mines_text.get_width() - 10, 10))

def check_game_clear(board):
    """Checks if all non-mine tiles have been revealed."""
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            if not board[y][x]['is_mine'] and not board[y][x]['is_revealed']:
                return False
    return True

def reset_game():
    """Resets the game to its initial state based on the current difficulty."""
    global GRID_WIDTH, GRID_HEIGHT, NUM_MINES, SCREEN_WIDTH, SCREEN_HEIGHT, screen, restart_button_rect

    GRID_WIDTH = DIFFICULTY_LEVELS[current_difficulty]["size"][0]
    GRID_HEIGHT = DIFFICULTY_LEVELS[current_difficulty]["size"][1]
    NUM_MINES = DIFFICULTY_LEVELS[current_difficulty]["mines"]

    SCREEN_WIDTH = GRID_WIDTH * TILE_SIZE
    SCREEN_HEIGHT = GRID_HEIGHT * TILE_SIZE + PANEL_HEIGHT
    
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
    restart_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 50, 10, 100, 40)

    board = create_board()
    first_click = True
    game_over = False
    game_won = False
    start_time = 0
    return board, first_click, game_over, game_won, start_time

# --- Main Function ---
def main():
    """ Main function for the game. """
    pygame.init()

    pygame.display.set_caption("Minesweeper")
    font = pygame.font.Font(None, 36)
    tile_font = pygame.font.Font(None, TILE_SIZE)

    global SCREEN_WIDTH, SCREEN_HEIGHT, screen # Declare global variables here

    game_state = "main_menu"  # Possible states: main_menu, in_game
    board, first_click, game_over, game_won, start_time = reset_game()
    
    restart_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 50, 10, 100, 40)

    done = False
    clock = pygame.time.Clock()

    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            elif event.type == pygame.VIDEORESIZE:
                SCREEN_WIDTH = event.w
                SCREEN_HEIGHT = event.h
                screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
                restart_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 50, 10, 100, 40)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()

                if game_state == "main_menu":
                    # Define buttons for click detection
                    easy_button = pygame.Rect(SCREEN_WIDTH // 2 - 75, SCREEN_HEIGHT // 2, 150, 50)
                    normal_button = pygame.Rect(SCREEN_WIDTH // 2 - 75, SCREEN_HEIGHT // 2 + 60, 150, 50)
                    hard_button = pygame.Rect(SCREEN_WIDTH // 2 - 75, SCREEN_HEIGHT // 2 + 120, 150, 50)

                    if easy_button.collidepoint(pos):
                        current_difficulty = "Easy"
                        game_state = "in_game"
                        board, first_click, game_over, game_won, start_time = reset_game()
                    elif normal_button.collidepoint(pos):
                        current_difficulty = "Normal"
                        game_state = "in_game"
                        board, first_click, game_over, game_won, start_time = reset_game()
                    elif hard_button.collidepoint(pos):
                        current_difficulty = "Hard"
                        game_state = "in_game"
                        board, first_click, game_over, game_won, start_time = reset_game()

                elif game_state == "in_game":
                    if restart_button_rect.collidepoint(pos):
                        board, first_click, game_over, game_won, start_time = reset_game()
                        continue

                    if not game_over and not game_won:
                        x = pos[0] // TILE_SIZE
                        y = (pos[1] - PANEL_HEIGHT) // TILE_SIZE

                        if 0 <= y < GRID_HEIGHT:
                            if event.button == 1:  # Left click
                                if first_click:
                                    start_time = time.time()
                                    board = place_mines(board, (x, y))
                                    board = calculate_neighbor_mines(board)
                                    first_click = False

                                reveal_tile(board, x, y)

                                if board[y][x]['is_mine'] and not board[y][x]['is_flagged']:
                                    game_over = True
                                    for row in board:
                                        for tile in row:
                                            if tile['is_mine']:
                                                tile['is_revealed'] = True

                            elif event.button == 3:  # Right click
                                if not board[y][x]['is_revealed']:
                                    board[y][x]['is_flagged'] = not board[y][x]['is_flagged']

        if game_state == "main_menu":
            # --- Drawing Main Menu ---
            screen.fill(WHITE)
            title_font = pygame.font.Font(None, 72)
            title_text = title_font.render("Minesweeper", True, BLACK)
            screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, SCREEN_HEIGHT // 4))

            easy_button = pygame.Rect(SCREEN_WIDTH // 2 - 75, SCREEN_HEIGHT // 2, 150, 50)
            normal_button = pygame.Rect(SCREEN_WIDTH // 2 - 75, SCREEN_HEIGHT // 2 + 60, 150, 50)
            hard_button = pygame.Rect(SCREEN_WIDTH // 2 - 75, SCREEN_HEIGHT // 2 + 120, 150, 50)

            pygame.draw.rect(screen, LIGHT_GRAY, easy_button)
            pygame.draw.rect(screen, LIGHT_GRAY, normal_button)
            pygame.draw.rect(screen, LIGHT_GRAY, hard_button)

            easy_text = font.render("Easy", True, BLACK)
            normal_text = font.render("Normal", True, BLACK)
            hard_text = font.render("Hard", True, BLACK)

            screen.blit(easy_text, (easy_button.x + (easy_button.width - easy_text.get_width()) // 2, easy_button.y + (easy_button.height - easy_text.get_height()) // 2))
            screen.blit(normal_text, (normal_button.x + (normal_button.width - normal_text.get_width()) // 2, normal_button.y + (normal_button.height - normal_text.get_height()) // 2))
            screen.blit(hard_text, (hard_button.x + (hard_button.width - hard_text.get_width()) // 2, hard_button.y + (hard_button.height - hard_text.get_height()) // 2))

        elif game_state == "in_game":
            # --- In-Game Logic ---
            elapsed_time = time.time() - start_time if start_time > 0 and not game_over and not game_won else 0

            if not game_over and not first_click:
                if check_game_clear(board):
                    game_won = True

            screen.fill(WHITE)
            
            mines_left = NUM_MINES - sum(tile['is_flagged'] for row in board for tile in row)
            draw_panel(screen, font, elapsed_time, mines_left)
            
            pygame.draw.rect(screen, LIGHT_GRAY, restart_button_rect)
            restart_text = font.render("Restart", True, BLACK)
            screen.blit(restart_text, (restart_button_rect.x + 10, restart_button_rect.y + 5))

            draw_board(screen, tile_font, board)

            if game_over:
                text = font.render("Game Over", True, RED)
                text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, (SCREEN_HEIGHT + PANEL_HEIGHT) // 2))
                screen.blit(text, text_rect)
            elif game_won:
                text = font.render("You Win!", True, BLUE)
                text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, (SCREEN_HEIGHT + PANEL_HEIGHT) // 2))
                screen.blit(text, text_rect)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
