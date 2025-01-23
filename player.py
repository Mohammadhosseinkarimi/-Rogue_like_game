import pygame

TILE_SIZE = 40
BULLET_SPEED = 20  # Increased speed for better visibility
BULLET_RADIUS = 7  # Increased bullet size
BULLET_COLOR = (255, 0, 0)  # Bright red color


class Bullet:
    def __init__(self, grid_x, grid_y, direction):
        # Convert to pixel coordinates by calculating tile center
        self.x = grid_x * TILE_SIZE + TILE_SIZE // 2
        self.y = grid_y * TILE_SIZE + TILE_SIZE // 2

        self.direction = direction
        self.active = True
        self.color = (255, 0, 0)
        self.speed = 20  # Increased speed

    def draw(self, screen, offset_y):
        if self.active:
            # Calculate real position with vertical scrolling
            draw_y = self.y - (offset_y * TILE_SIZE)
            pygame.draw.circle(
                screen,
                self.color,
                (int(self.x), int(draw_y)),
                7  # Increased size
            )

    def update(self, maze):
        if not self.active:
            return

        # Movement based on direction with new speed
        if self.direction == 'up':
            self.y -= BULLET_SPEED
        elif self.direction == 'down':
            self.y += BULLET_SPEED
        elif self.direction == 'left':
            self.x -= BULLET_SPEED
        elif self.direction == 'right':
            self.x += BULLET_SPEED

        # Wall collision detection
        grid_x = int(self.x // TILE_SIZE)
        grid_y = int(self.y // TILE_SIZE)

        # Check maze boundaries and wall presence
        if (0 <= grid_x < len(maze[0])
                and 0 <= grid_y < len(maze)):
            if maze[grid_y][grid_x] == 1:
                self.active = False
        else:
            self.active = False

class Player:
    def __init__(self, grid_x, grid_y):
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.bullets = []
        self.shoot_cooldown = 250  # Reduced delay time
        self.last_shot = 0

    def shoot(self, direction):
        now = pygame.time.get_ticks()
        if now - self.last_shot >= self.shoot_cooldown:
            new_bullet = Bullet(self.grid_x, self.grid_y, direction)
            self.bullets.append(new_bullet)
            self.last_shot = now

    def update_bullets(self, maze, enemies):
        for bullet in self.bullets[:]:
            bullet.update(maze)

            if not bullet.active:
                self.bullets.remove(bullet)
                continue

            # Enemy collision detection
            for enemy in enemies[:]:
                # Convert enemy position to pixels
                enemy_x = enemy.x * TILE_SIZE + TILE_SIZE // 2
                enemy_y = enemy.y * TILE_SIZE + TILE_SIZE // 2

                # Euclidean distance calculation
                distance = ((bullet.x - enemy_x) ** 2 + (bullet.y - enemy_y) ** 2) ** 0.5

                if distance < 20:  # Larger detection radius for easier hits
                    enemies.remove(enemy)
                    self.bullets.remove(bullet)
                    print("Enemy hit!")  # Debug message
                    break

    def draw_bullets(self, screen, offset_y):
        for bullet in self.bullets:
            bullet.draw(screen, offset_y)