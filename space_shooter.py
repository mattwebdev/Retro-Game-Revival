# Space Shooter
# Author: ShortFuseGames
# Original Publication Date: 2025
# Description: A classic space shooter where you defend against geometric invaders

import pygame
import sys

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Player Settings
PLAYER_SIZE = 40
PLAYER_SPEED = 5
PLAYER_COLOR = GREEN

# Enemy Settings
ENEMY_SIZE = 30
ENEMY_SPEED = 2
ENEMY_COLOR = RED
ENEMY_ROWS = 4
ENEMY_COLS = 8
ENEMY_SPACING = 60
ENEMY_MOVE_DOWN = 20

# Bullet Settings
BULLET_SIZE = 5
BULLET_SPEED = 7
BULLET_COLOR = WHITE

# Setup Display
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Space Shooter")
clock = pygame.time.Clock()

class Player:
    def __init__(self):
        self.width = PLAYER_SIZE
        self.height = PLAYER_SIZE
        self.x = WINDOW_WIDTH // 2
        self.y = WINDOW_HEIGHT - self.height - 10
        self.speed = PLAYER_SPEED
        self.color = PLAYER_COLOR

    def draw(self):
        # Draw player as a triangle
        points = [
            (self.x, self.y - self.height),  # Top
            (self.x - self.width//2, self.y),  # Bottom left
            (self.x + self.width//2, self.y)   # Bottom right
        ]
        pygame.draw.polygon(screen, self.color, points)

    def move(self, direction):
        self.x += direction * self.speed
        # Keep player within screen bounds
        self.x = max(self.width//2, min(self.x, WINDOW_WIDTH - self.width//2))

class Enemy:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = ENEMY_SIZE
        self.speed = ENEMY_SPEED
        self.direction = 1
        self.color = ENEMY_COLOR

    def draw(self):
        # Draw enemy as a square with a smaller square inside
        pygame.draw.rect(screen, self.color, 
                        (self.x - self.size//2, self.y - self.size//2, 
                         self.size, self.size))
        pygame.draw.rect(screen, BLACK,
                        (self.x - self.size//4, self.y - self.size//4,
                         self.size//2, self.size//2))

class Bullet:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = BULLET_SIZE
        self.speed = BULLET_SPEED
        self.color = BULLET_COLOR

    def draw(self):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.size)

    def move(self):
        self.y -= self.speed

class Game:
    def __init__(self):
        self.player = Player()
        self.enemies = []
        self.bullets = []
        self.score = 0
        self.game_over = False
        self.create_enemies()

    def create_enemies(self):
        for row in range(ENEMY_ROWS):
            for col in range(ENEMY_COLS):
                x = col * ENEMY_SPACING + ENEMY_SPACING
                y = row * ENEMY_SPACING + ENEMY_SPACING
                self.enemies.append(Enemy(x, y))

    def handle_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.player.move(-1)
        if keys[pygame.K_RIGHT]:
            self.player.move(1)
        if keys[pygame.K_SPACE]:
            # Limit bullet firing rate
            if len(self.bullets) < 3:
                self.bullets.append(Bullet(self.player.x, self.player.y - self.player.height))

    def update(self):
        if self.game_over:
            return

        # Update bullets
        for bullet in self.bullets[:]:
            bullet.move()
            if bullet.y < 0:
                self.bullets.remove(bullet)

        # Move enemies
        move_down = False
        for enemy in self.enemies:
            enemy.x += enemy.speed * enemy.direction
            if enemy.x >= WINDOW_WIDTH - ENEMY_SIZE or enemy.x <= ENEMY_SIZE:
                move_down = True

        if move_down:
            for enemy in self.enemies:
                enemy.direction *= -1
                enemy.y += ENEMY_MOVE_DOWN
                if enemy.y >= self.player.y:
                    self.game_over = True

        # Check collisions
        for bullet in self.bullets[:]:
            for enemy in self.enemies[:]:
                if (abs(bullet.x - enemy.x) < ENEMY_SIZE//2 and
                    abs(bullet.y - enemy.y) < ENEMY_SIZE//2):
                    if bullet in self.bullets:
                        self.bullets.remove(bullet)
                    if enemy in self.enemies:
                        self.enemies.remove(enemy)
                        self.score += 10

    def draw(self):
        screen.fill(BLACK)
        
        # Draw game objects
        self.player.draw()
        for enemy in self.enemies:
            enemy.draw()
        for bullet in self.bullets:
            bullet.draw()

        # Draw score
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Score: {self.score}", True, WHITE)
        screen.blit(score_text, (10, 10))

        # Draw game over
        if self.game_over:
            game_over_text = font.render("GAME OVER", True, RED)
            text_rect = game_over_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2))
            screen.blit(game_over_text, text_rect)

        pygame.display.flip()

def main():
    game = Game()
    running = True

    while running:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        game.handle_input()
        game.update()
        game.draw()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main() 