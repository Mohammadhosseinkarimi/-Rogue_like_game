import pygame
import random

BLUE = (0, 0, 255)
TILE_SIZE = 40

class Enemy:
    def __init__(self, x, y, room_left, room_top, room_width, room_height):
        self.x = x
        self.y = y
        self.room_left = room_left
        self.room_top = room_top
        self.room_right = room_left + room_width - 1
        self.room_bottom = room_top + room_height - 1

        # Set initial movement direction (random horizontal/vertical)
        self.movement_type = random.choice(['horizontal', 'vertical'])
        self.dx = 1 if self.movement_type == 'horizontal' else 0
        self.dy = 1 if self.movement_type == 'vertical' else 0

        self.last_update = pygame.time.get_ticks()
        self.update_interval = 300  # Slower speed than player

    def update(self, maze):
        now = pygame.time.get_ticks()
        if now - self.last_update < self.update_interval:
            return
        self.last_update = now

        # Horizontal ping-pong movement
        if self.movement_type == 'horizontal':
            new_x = self.x + self.dx
            if self.room_left <= new_x <= self.room_right:
                self.x = new_x
            else:
                self.dx *= -1  # Reverse direction

        # Vertical ping-pong movement
        elif self.movement_type == 'vertical':
            new_y = self.y + self.dy
            if self.room_top <= new_y <= self.room_bottom:
                self.y = new_y
            else:
                self.dy *= -1  # Reverse direction

    def draw(self, screen, offset_y, fog_of_war):
        """Draw enemy only in visible areas (based on fog of war)"""
        if fog_of_war[self.y][self.x] != 0:
            pygame.draw.rect(
                screen,
                BLUE,
                (
                    self.x * TILE_SIZE,
                    (self.y - offset_y) * TILE_SIZE,
                    TILE_SIZE,
                    TILE_SIZE
                )
            )