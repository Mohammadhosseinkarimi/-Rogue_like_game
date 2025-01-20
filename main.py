import pygame
import random
from collections import deque

# تنظیمات اولیه
WIDTH, HEIGHT = 800, 600  # ابعاد پنجره بازی
TILE_SIZE = 40  # اندازه هر بلوک در هزارتو
ROWS, COLS = HEIGHT // TILE_SIZE, WIDTH // TILE_SIZE

# رنگ‌ها
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (100, 100, 100)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

def is_room_valid(maze, top_left_x, top_left_y, room_width, room_height):
    """بررسی اینکه آیا اتاق در این موقعیت قرار می‌گیرد و تداخلی با اتاق‌های قبلی ندارد"""
    if top_left_x + room_width > len(maze[0]) or top_left_y + room_height > len(maze):
        return False  # اتاق از مرزهای نقشه بیرون می‌رود
    for r in range(top_left_y, top_left_y + room_height):
        for c in range(top_left_x, top_left_x + room_width):
            if maze[r][c] == 0:  # اگر جایی که باید اتاق باشد قبلاً باز است (به معنی تداخل با اتاق دیگر)
                return False
    return True

def generate_room_based_maze(rows, cols):
    """تولید هزارتو به صورت اتاق‌های متصل با یک مسیر یکتا بین اتاق‌ها"""
    maze = [[1 for _ in range(cols)] for _ in range(rows)]

    # اطلاعات اتاق‌ها
    rooms = []
    room_count = random.randint(10, 15)
    room_size = (3, 5)  # حداقل و حداکثر اندازه اتاق‌ها

    for _ in range(room_count):
        room_width = random.randint(room_size[0], room_size[1])
        room_height = random.randint(room_size[0], room_size[1])

        # انتخاب مکان تصادفی برای اتاق
        placed = False
        attempts = 0  # حداکثر تلاش برای پیدا کردن مکان بدون تداخل
        while not placed and attempts < 100:
            top_left_x = random.randint(1, cols - room_width - 2)
            top_left_y = random.randint(1, rows - room_height - 2)

            if is_room_valid(maze, top_left_x, top_left_y, room_width, room_height):
                placed = True
                rooms.append((top_left_x, top_left_y, room_width, room_height))
                for r in range(top_left_y, top_left_y + room_height):
                    for c in range(top_left_x, top_left_x + room_width):
                        maze[r][c] = 0
            attempts += 1

        # اتصال اتاق‌ها با یک مسیر یکتا
    for i in range(len(rooms) - 1):
        x1, y1 = rooms[i][0] + rooms[i][2] // 2, rooms[i][1] + rooms[i][3] // 2
        x2, y2 = rooms[i + 1][0] + rooms[i + 1][2] // 2, rooms[i + 1][1] + rooms[i + 1][3] // 2

        # انتخاب یک مسیر مستقیم بین دو اتاق
        if random.choice([True, False]):
            # ابتدا افقی سپس عمودی
            for x in range(min(x1, x2), max(x1, x2) + 1):
                maze[y1][x] = 0
            for y in range(min(y1, y2), max(y1, y2) + 1):
                maze[y][x2] = 0
        else:
            # ابتدا عمودی سپس افقی
            for y in range(min(y1, y2), max(y1, y2) + 1):
                maze[y][x1] = 0
            for x in range(min(x1, x2), max(x1, x2) + 1):
                maze[y2][x] = 0
    # ایجاد مسیر از شروع تا اولین اتاق و از آخرین اتاق به انتها
    start_x, start_y = 0, 0
    end_x, end_y = cols - 1, rows - 1

    first_room_x, first_room_y = rooms[0][0] + rooms[0][2] // 2, rooms[0][1] + rooms[0][3] // 2
    last_room_x, last_room_y = rooms[-1][0] + rooms[-1][2] // 2, rooms[-1][1] + rooms[-1][3] // 2

    for x in range(min(start_x, first_room_x), max(start_x, first_room_x) + 1):
        maze[start_y][x] = 0
    for y in range(min(start_y, first_room_y), max(start_y, first_room_y) + 1):
        maze[y][first_room_x] = 0

    for x in range(min(end_x, last_room_x), max(end_x, last_room_x) + 1):
        maze[end_y][x] = 0
    for y in range(min(end_y, last_room_y), max(end_y, last_room_y) + 1):
        maze[y][last_room_x] = 0

    return maze


def draw_maze(screen, maze, offset_y):
    """رسم هزارتو روی صفحه با در نظر گرفتن جابجایی عمودی"""
    for row in range(len(maze)):
        for col in range(len(maze[row])):
            color = BLACK if maze[row][col] == 1 else WHITE
            pygame.draw.rect(screen, color, (col * TILE_SIZE, (row - offset_y) * TILE_SIZE, TILE_SIZE, TILE_SIZE))
            pygame.draw.rect(screen, GRAY, (col * TILE_SIZE, (row - offset_y) * TILE_SIZE, TILE_SIZE, TILE_SIZE), 1)

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("هزارتوی کابوس")

    clock = pygame.time.Clock()
    maze = generate_room_based_maze(ROWS * 5, COLS)  # نقشه سه برابر بلندتر

    # موقعیت بازیکن
    player_x, player_y = 0, 0
    offset_y = 0

    # کنترل سرعت حرکت
    move_delay = 200  # میلی‌ثانیه
    last_move_time = pygame.time.get_ticks()

    running = True
    while running:
        keys = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # کنترل حرکت بازیکن با محدودیت زمانی
        current_time = pygame.time.get_ticks()
        if current_time - last_move_time > move_delay:
            if keys[pygame.K_UP] and player_y > 0 and maze[player_y - 1][player_x] == 0:
                player_y -= 1
                last_move_time = current_time
            if keys[pygame.K_DOWN] and player_y < len(maze) - 1 and maze[player_y + 1][player_x] == 0:
                player_y += 1
                last_move_time = current_time
            if keys[pygame.K_LEFT] and player_x > 0 and maze[player_y][player_x - 1] == 0:
                player_x -= 1
                last_move_time = current_time
            if keys[pygame.K_RIGHT] and player_x < COLS - 1 and maze[player_y][player_x + 1] == 0:
                player_x += 1
                last_move_time = current_time

        # جابجایی صفحه در صورت حرکت به پایین
        if player_y - offset_y >= ROWS:
            offset_y += ROWS
        if player_y < offset_y:
            offset_y -= ROWS

        screen.fill(BLACK)
        draw_maze(screen, maze, offset_y)

        # رسم بازیکن
        pygame.draw.rect(screen, RED, (player_x * TILE_SIZE, (player_y - offset_y) * TILE_SIZE, TILE_SIZE, TILE_SIZE))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
