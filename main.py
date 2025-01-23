import pygame
import random
from player import Player
from enemies import Enemy

# Initial settings
WIDTH, HEIGHT = 800, 600  # Game window dimensions
TILE_SIZE = 40  # Size of each maze block
ROWS, COLS = HEIGHT // TILE_SIZE, WIDTH // TILE_SIZE

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

VIEW_DISTANCE = 1  # Player's visible range (in cells)
fog_of_war = []  # Fog of war matrix (0: unseen, 1: seen, 2: currently visible)

def show_lose_message(screen):
    """Display game over message"""
    font = pygame.font.SysFont('arial', 72, bold=True)
    text = font.render('Game Over! You Lost!', True, (255, 0, 0), BLACK)
    text_rect = text.get_rect(center=(WIDTH//2, HEIGHT//2))
    screen.blit(text, text_rect)
    pygame.display.update()

def connect_two_points(maze, x1, y1, x2, y2):
    """Connect two points with straight path"""
    # Horizontal connection
    for x in range(min(x1, x2), max(x1, x2) + 1):
        maze[y1][x] = 0
    # Vertical connection
    for y in range(min(y1, y2), max(y1, y2) + 1):
        maze[y][x2] = 0

def is_room_valid(maze, top_left_x, top_left_y, room_width, room_height, buffer=1):
    """
    Check if a room can be placed without overlapping existing structures
    buffer: empty space around the room
    """
    for r in range(top_left_y - buffer, top_left_y + room_height + buffer):
        for c in range(top_left_x - buffer, top_left_x + room_width + buffer):
            if r < 0 or r >= len(maze) or c < 0 or c >= len(maze[0]):  # Out of bounds
                continue
            if maze[r][c] == 0:  # Overlapping with empty space
                return False
    return True

def generate_room_based_maze(rows, cols):
    global fog_of_war
    maze = [[1 for _ in range(cols)] for _ in range(rows)]
    enemies = []

    rooms = []
    room_count = random.randint(12, 18)  # Reduced number of rooms
    min_room_width, max_room_width = 2, 10
    min_room_height, max_room_height = 2, 4

    for _ in range(room_count):
        room_width = random.randint(min_room_width, max_room_width)
        room_height = random.randint(min_room_height, max_room_height)
        placed = False
        attempts = 0

        while not placed and attempts < 200:  # Increased placement attempts
            top_left_x = random.randint(1, cols - room_width - 1)
            top_left_y = random.randint(1, rows - room_height - 1)

            if is_room_valid(maze, top_left_x, top_left_y, room_width, room_height):
                # Draw room
                for r in range(top_left_y, top_left_y + room_height):
                    for c in range(top_left_x, top_left_x + room_width):
                        maze[r][c] = 0

                # Add enemy in room center
                enemy_x = top_left_x + room_width // 2
                enemy_y = top_left_y + room_height // 2
                enemies.append(Enemy(
                    enemy_x,
                    enemy_y,
                    top_left_x,
                    top_left_y,
                    room_width,
                    room_height
                ))

                rooms.append((top_left_x, top_left_y, room_width, room_height))
                placed = True
            attempts += 1

    # Connect rooms with paths
    for i in range(len(rooms) - 1):
        x1 = rooms[i][0] + rooms[i][2] // 2
        y1 = rooms[i][1] + rooms[i][3] // 2
        x2 = rooms[i + 1][0] + rooms[i + 1][2] // 2
        y2 = rooms[i + 1][1] + rooms[i + 1][3] // 2
        connect_two_points(maze, x1, y1, x2, y2)

    # Create path from start to first room
    start_x, start_y = 0, 0
    first_room_x, first_room_y = rooms[0][0] + rooms[0][2] // 2, rooms[0][1] + rooms[0][3] // 2
    for x in range(min(start_x, first_room_x), max(start_x, first_room_x) + 1):
        maze[start_y][x] = 0
    for y in range(min(start_y, first_room_y), max(start_y, first_room_y) + 1):
        maze[y][first_room_x] = 0

    # Create exit path from last room
    end_x, end_y = cols - 1, rows - 1
    last_room_x, last_room_y = rooms[-1][0] + rooms[-1][2] // 2, rooms[-1][1] + rooms[-1][3] // 2
    for x in range(min(end_x, last_room_x), max(end_x, last_room_x) + 1):
        maze[end_y][x] = 0
    for y in range(min(end_y, last_room_y), max(end_y, last_room_y) + 1):
        maze[y][last_room_x] = 0

    # Initialize fog of war
    fog_of_war = [[0 for _ in range(cols)] for _ in range(rows)]

    return maze, enemies

def update_vision(player_x, player_y):
    global fog_of_war
    # Calculate square vision range
    for y in range(max(0, player_y - VIEW_DISTANCE), min(len(fog_of_war), player_y + VIEW_DISTANCE + 1)):
        for x in range(max(0, player_x - VIEW_DISTANCE), min(len(fog_of_war[0]), player_x + VIEW_DISTANCE + 1)):
            fog_of_war[y][x] = 1  # Mark as seen

    # Update vision with circular pattern
    vision_radius = VIEW_DISTANCE
    for dy in range(-vision_radius, vision_radius+1):
        for dx in range(-vision_radius, vision_radius+1):
            if dx*dx + dy*dy <= vision_radius**2:
                x = player_x + dx
                y = player_y + dy
                if 0 <= x < COLS and 0 <= y < len(fog_of_war):
                    fog_of_war[y][x] = 2

    # def draw_maze(screen, maze, offset_y, enemies):
    #     for row in range(len(maze)):
    #         for col in range(len(maze[row])):
    #             color = BLACK if maze[row][col] == 1 else WHITE
    #             pygame.draw.rect(screen, color, (col * TILE_SIZE, (row - offset_y) * TILE_SIZE, TILE_SIZE, TILE_SIZE))
    #             pygame.draw.rect(screen, GRAY, (col * TILE_SIZE, (row - offset_y) * TILE_SIZE, TILE_SIZE, TILE_SIZE), 1)
    #

    #     for enemy in enemies:
    #         enemy.draw(screen, offset_y)

def draw_maze(screen, maze, offset_y, enemies, bullets, player_x, player_y):
    """Draw maze without grid lines"""
    update_vision(player_x, player_y)

    for row in range(len(maze)):
        for col in range(len(maze[row])):
            if fog_of_war[row][col] == 0:
                continue

            # Draw cell without borders
            color = WHITE if maze[row][col] == 0 else BLACK
            pygame.draw.rect(
                screen,
                color,
                (
                    col * TILE_SIZE,
                    (row - offset_y) * TILE_SIZE,
                    TILE_SIZE,
                    TILE_SIZE
                )
            )

    # Draw enemies in visible cells
    for enemy in enemies:
        enemy.draw(screen, offset_y, fog_of_war)

    # Draw bullets
    for bullet in bullets:
        bullet.draw(screen, offset_y)

def show_win_message(screen):
    """Display victory message"""
    font = pygame.font.SysFont('arial', 40, bold=True)
    text = font.render('Congratulations! You won!', True, GREEN, BLACK)
    text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    screen.blit(text, text_rect)
    pygame.display.update()

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Nightmare Maze")  # Translated window title

    clock = pygame.time.Clock()
    maze, enemies = generate_room_based_maze(ROWS * 5, COLS)

    # Create player object
    player = Player(0, 0)
    offset_y = 0  # Vertical screen offset

    # Exit position
    end_x = COLS - 1
    end_y = ROWS * 5 - 1

    # Movement speed control
    move_delay = 200  # milliseconds between moves
    last_move_time = pygame.time.get_ticks()

    game_won = False
    game_over = False

    running = True
    while running:
        keys = pygame.key.get_pressed()

        # Update player's vision
        update_vision(player.grid_x, player.grid_y)

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Enemy collision detection
        if not game_won and not game_over:
            for enemy in enemies:
                if player.grid_x == enemy.x and player.grid_y == enemy.y:
                    game_over = True
                    break

        # Check win condition
        if (player.grid_x, player.grid_y) == (end_x, end_y):
            game_won = True

        # Gameplay controls
        if not game_won and not game_over:
            current_time = pygame.time.get_ticks()
            if current_time - last_move_time > move_delay:
                # Player movement
                if keys[pygame.K_UP] and player.grid_y > 0 and maze[player.grid_y - 1][player.grid_x] == 0:
                    player.grid_y -= 1
                    last_move_time = current_time
                if keys[pygame.K_DOWN] and player.grid_y < len(maze) - 1 and maze[player.grid_y + 1][player.grid_x] == 0:
                    player.grid_y += 1
                    last_move_time = current_time
                if keys[pygame.K_LEFT] and player.grid_x > 0 and maze[player.grid_y][player.grid_x - 1] == 0:
                    player.grid_x -= 1
                    last_move_time = current_time
                if keys[pygame.K_RIGHT] and player.grid_x < COLS - 1 and maze[player.grid_y][player.grid_x + 1] == 0:
                    player.grid_x += 1
                    last_move_time = current_time

            # Shooting with WASD keys
            if keys[pygame.K_w]:
                player.shoot('up')
            if keys[pygame.K_s]:
                player.shoot('down')
            if keys[pygame.K_a]:
                player.shoot('left')
            if keys[pygame.K_d]:
                player.shoot('right')

            # Update enemy positions
            for enemy in enemies:
                enemy.update(maze)

        # Update bullets and check collisions
        player.update_bullets(maze, enemies)

        # Screen scrolling
        if player.grid_y - offset_y >= ROWS:
            offset_y += ROWS
        if player.grid_y < offset_y:
            offset_y -= ROWS

        # Render game elements
        screen.fill(BLACK)
        draw_maze(screen, maze, offset_y, enemies, player.bullets, player.grid_x, player.grid_y)

        # Draw exit point
        pygame.draw.rect(
            screen,
            GREEN,
            (
                end_x * TILE_SIZE,
                (end_y - offset_y) * TILE_SIZE,
                TILE_SIZE,
                TILE_SIZE
            )
        )

        # Draw bullets and player
        player.draw_bullets(screen, offset_y)
        player_rect = pygame.Rect(
            player.grid_x * TILE_SIZE,
            (player.grid_y - offset_y) * TILE_SIZE,
            TILE_SIZE,
            TILE_SIZE
        )
        pygame.draw.rect(screen, RED, player_rect)

        # Show game state messages
        if game_won:
            show_win_message(screen)
        elif game_over:
            show_lose_message(screen)

        pygame.display.flip()
        clock.tick(60)  # 60 FPS cap

    pygame.quit()

if __name__ == "__main__":
    main()

