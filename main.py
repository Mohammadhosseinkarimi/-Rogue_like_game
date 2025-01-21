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

def distance(x1, y1, x2, y2):
    """محاسبه فاصله منهتن بین دو نقطه"""
    return abs(x1 - x2) + abs(y1 - y2)


def connect_rooms_with_limit(maze, rooms, max_distance=20):
    """
    اتصال اتاق‌ها با محدودیت طول مسیر.
    اگر مسیر بیش از max_distance باشد، از یک یا چند اتاق واسط استفاده می‌شود.
    """
    for i in range(len(rooms) - 1):
        x1, y1 = rooms[i][0] + rooms[i][2] // 2, rooms[i][1] + rooms[i][3] // 2
        x2, y2 = rooms[i + 1][0] + rooms[i + 1][2] // 2, rooms[i + 1][1] + rooms[i + 1][3] // 2

        if distance(x1, y1, x2, y2) > max_distance:
            # اگر فاصله بین دو اتاق بزرگ باشد، اتاق واسط پیدا می‌شود
            intermediate_room = random.choice(rooms)
            ix, iy = intermediate_room[0] + intermediate_room[2] // 2, intermediate_room[1] + intermediate_room[3] // 2
            connect_two_points(maze, x1, y1, ix, iy)
            connect_two_points(maze, ix, iy, x2, y2)
        else:
            # اتصال مستقیم بین اتاق‌ها
            connect_two_points(maze, x1, y1, x2, y2)


def connect_two_points(maze, x1, y1, x2, y2):
    """
    اتصال دو نقطه در هزارتو با مسیرهایی که عرض آن‌ها ۱ باشد.
    """
    if random.choice([True, False]):
        # ابتدا افقی سپس عمودی
        for x in range(min(x1, x2), max(x1, x2) + 1):
            if is_valid_path(maze, x, y1):
                maze[y1][x] = 0
        for y in range(min(y1, y2), max(y1, y2) + 1):
            if is_valid_path(maze, x2, y):
                maze[y][x2] = 0
    else:
        # ابتدا عمودی سپس افقی
        for y in range(min(y1, y2), max(y1, y2) + 1):
            if is_valid_path(maze, x1, y):
                maze[y][x1] = 0
        for x in range(min(x1, x2), max(x1, x2) + 1):
            if is_valid_path(maze, x, y2):
                maze[y2][x] = 0


def is_valid_path(maze, x, y):
    """
    بررسی می‌کند که آیا اضافه کردن یک سلول به مسیر، عرض بیشتر از ۱ ایجاد می‌کند یا خیر.
    """
    if maze[y][x] == 0:  # اگر سلول قبلاً بخشی از مسیر باشد
        return False

    # بررسی وجود عرض ۲ یا ۳ در جهت افقی و عمودی
    directions = [
        [(x - 1, y), (x + 1, y)],  # افقی
        [(x, y - 1), (x, y + 1)],  # عمودی
    ]

    for direction in directions:
        count = 0
        for nx, ny in direction:
            if 0 <= ny < len(maze) and 0 <= nx < len(maze[0]) and maze[ny][nx] == 0:
                count += 1
        if count > 1:  # اگر عرض ۲ یا بیشتر در یک جهت پیدا شود
            return False

    # بررسی وجود عرض بیشتر از ۱ در همسایگی
    neighbors = [
        (x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)
    ]

    for nx, ny in neighbors:
        if 0 <= ny < len(maze) and 0 <= nx < len(maze[0]) and maze[ny][nx] == 0:
            # بررسی سلول‌های دیگر کنار این سلول
            if not check_adjacent_cells(maze, nx, ny):
                return False

    return True


def check_adjacent_cells(maze, x, y):
    """
    بررسی می‌کند که آیا سلول همسایه باعث ایجاد عرض بیشتر از ۱ می‌شود یا خیر.
    """
    adjacent_neighbors = [
        (x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)
    ]
    count = 0
    for nx, ny in adjacent_neighbors:
        if 0 <= ny < len(maze) and 0 <= nx < len(maze[0]) and maze[ny][nx] == 0:
            count += 1
    return count <= 1

def is_room_valid(maze, top_left_x, top_left_y, room_width, room_height, buffer=1):
    """
    بررسی می‌کند که آیا یک اتاق می‌تواند در مکان مشخص قرار گیرد بدون تداخل با اتاق‌های دیگر.
    buffer: فضای حائل اطراف اتاق
    """
    for r in range(top_left_y - buffer, top_left_y + room_height + buffer):
        for c in range(top_left_x - buffer, top_left_x + room_width + buffer):
            if r < 0 or r >= len(maze) or c < 0 or c >= len(maze[0]):  # خارج از مرز
                continue
            if maze[r][c] == 0:  # تداخل با فضای خالی
                return False
    return True


def generate_room_based_maze(rows, cols):
    """تولید هزارتو به صورت اتاق‌های متصل با یک مسیر یکتا بین اتاق‌ها"""
    maze = [[1 for _ in range(cols)] for _ in range(rows)]

    # اطلاعات اتاق‌ها
    rooms = []
    room_count = random.randint(10, 15)  # تعداد اتاق‌ها به‌صورت تصادفی
    room_size = (3, 5)  # حداقل و حداکثر اندازه اتاق‌ها

    for _ in range(room_count):
        room_width = random.randint(max(3, room_size[0]), room_size[1])
        room_height = random.randint(room_size[0], min(9, room_size[1]))

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

    # اتصال اتاق‌ها با مسیرهای غیرمستقیم
    for i in range(len(rooms) - 1):
        x1, y1 = rooms[i][0] + rooms[i][2] // 2, rooms[i][1] + rooms[i][3] // 2
        x2, y2 = rooms[i + 1][0] + rooms[i + 1][2] // 2, rooms[i + 1][1] + rooms[i + 1][3] // 2

        # ایجاد مسیر زیگ‌زاگ بین اتاق‌ها
        connect_two_points(maze, x1, y1, x2, y2)

    # ایجاد مسیر از شروع به اولین اتاق
    start_x, start_y = 0, 0
    first_room_x, first_room_y = rooms[0][0] + rooms[0][2] // 2, rooms[0][1] + rooms[0][3] // 2
    for x in range(min(start_x, first_room_x), max(start_x, first_room_x) + 1):
        maze[start_y][x] = 0
    for y in range(min(start_y, first_room_y), max(start_y, first_room_y) + 1):
        maze[y][first_room_x] = 0

    # ایجاد مسیر از آخرین اتاق به انتها
    end_x, end_y = cols - 1, rows - 1
    last_room_x, last_room_y = rooms[-1][0] + rooms[-1][2] // 2, rooms[-1][1] + rooms[-1][3] // 2
    for x in range(min(end_x, last_room_x), max(end_x, last_room_x) + 1):
        maze[end_y][x] = 0
    for y in range(min(end_y, last_room_y), max(end_y, last_room_y) + 1):
        maze[y][last_room_x] = 0

    return maze



def is_room_valid(maze, x, y, width, height):
    """بررسی می‌کند که آیا اتاق می‌تواند در موقعیت داده‌شده قرار گیرد یا خیر."""
    for r in range(y - 1, y + height + 1):
        for c in range(x - 1, x + width + 1):
            if maze[r][c] == 0:
                return False
    return True

def create_curved_path(maze, x1, y1, x2, y2):
    """ایجاد مسیر غیرمستقیم و منحنی بین دو نقطه"""
    current_x, current_y = x1, y1
    while (current_x, current_y) != (x2, y2):
        maze[current_y][current_x] = 0

        # تصمیم‌گیری برای حرکت به سمت x یا y با انحراف تصادفی
        if random.choice([True, False]):
            if current_x != x2:
                step = 1 if current_x < x2 else -1
                current_x += step
                # انحراف کوچک در محور y
                if random.random() < 0.5 and current_y != y2:
                    current_y += random.choice([-1, 1])
            elif current_y != y2:
                step = 1 if current_y < y2 else -1
                current_y += step
        else:
            if current_y != y2:
                step = 1 if current_y < y2 else -1
                current_y += step
                # انحراف کوچک در محور x
                if random.random() < 0.5 and current_x != x2:
                    current_x += random.choice([-1, 1])
            elif current_x != x2:
                step = 1 if current_x < x2 else -1
                current_x += step

        # جلوگیری از برخورد به دیوارهای خارج از محدوده
        current_x = max(0, min(len(maze[0]) - 1, current_x))
        current_y = max(0, min(len(maze) - 1, current_y))

        maze[current_y][current_x] = 0



def is_valid_path(maze, x, y):
    """بررسی می‌کند که مسیر داده‌شده خارج از محدوده نباشد."""
    return 0 <= x < len(maze[0]) and 0 <= y < len(maze) and maze[y][x] == 1



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