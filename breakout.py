# Block Breaker
# Author: ZineGames
# Original Publication Date: 2024
# Description: A geometric block breaking game with power-ups

import pygame
import sys
import random
import math

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
ORANGE = (255, 165, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (255, 0, 255)
CYAN = (0, 255, 255)

# Paddle Settings
PADDLE_WIDTH = 100
PADDLE_HEIGHT = 15
PADDLE_SPEED = 8
PADDLE_COLOR = WHITE

# Ball Settings
BALL_SIZE = 8
BALL_SPEED = 5
BALL_COLOR = WHITE

# Block Settings
BLOCK_WIDTH = 80
BLOCK_HEIGHT = 30
BLOCK_ROWS = 5
BLOCK_COLS = 8
BLOCK_SPACING = 10
BLOCK_TOP_OFFSET = 50

# Setup Display
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Block Breaker")
clock = pygame.time.Clock()

class Paddle:
    def __init__(self):
        self.width = PADDLE_WIDTH
        self.height = PADDLE_HEIGHT
        self.x = WINDOW_WIDTH // 2 - self.width // 2
        self.y = WINDOW_HEIGHT - 40
        self.speed = PADDLE_SPEED
        self.color = PADDLE_COLOR

    def draw(self):
        # Draw paddle as rectangle with inner line
        pygame.draw.rect(screen, self.color, 
                        (self.x, self.y, self.width, self.height))
        pygame.draw.rect(screen, BLACK,
                        (self.x + 2, self.y + 2, self.width - 4, self.height - 4))
        pygame.draw.rect(screen, self.color,
                        (self.x + 4, self.y + 4, self.width - 8, self.height - 8))

    def move(self, direction):
        self.x += direction * self.speed
        # Keep paddle within screen bounds
        self.x = max(0, min(self.x, WINDOW_WIDTH - self.width))

class Ball:
    def __init__(self):
        self.reset()
        
    def reset(self):
        self.x = WINDOW_WIDTH // 2
        self.y = WINDOW_HEIGHT - 60
        self.size = BALL_SIZE
        self.speed = BALL_SPEED
        self.color = BALL_COLOR
        # Random angle between -45 and 45 degrees
        angle = random.uniform(-math.pi/4, math.pi/4)
        self.dx = math.sin(angle) * self.speed
        self.dy = -math.cos(angle) * self.speed
        self.moving = False

    def draw(self):
        # Draw ball as circle with inner circle
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.size)
        pygame.draw.circle(screen, BLACK, (int(self.x), int(self.y)), self.size - 2)
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.size - 4)

    def update(self, paddle):
        if not self.moving:
            self.x = paddle.x + paddle.width // 2
            self.y = WINDOW_HEIGHT - 60
            return False

        self.x += self.dx
        self.y += self.dy

        # Wall collisions
        if self.x <= self.size or self.x >= WINDOW_WIDTH - self.size:
            self.dx *= -1
        if self.y <= self.size:
            self.dy *= -1

        # Paddle collision
        if (self.y >= paddle.y - self.size and 
            paddle.x <= self.x <= paddle.x + paddle.width):
            # Calculate reflection angle based on where ball hits paddle
            relative_intersect_x = (paddle.x + (paddle.width / 2)) - self.x
            normalized_intersect = relative_intersect_x / (paddle.width / 2)
            bounce_angle = normalized_intersect * math.pi/3  # 60 degrees max angle
            
            self.dx = -math.sin(bounce_angle) * self.speed
            self.dy = -math.cos(bounce_angle) * self.speed
            
            # Ensure ball doesn't get stuck in paddle
            self.y = paddle.y - self.size

        # Check if ball is lost
        if self.y >= WINDOW_HEIGHT + self.size:
            return True
        
        return False

class Block:
    def __init__(self, x, y, color, points):
        self.x = x
        self.y = y
        self.width = BLOCK_WIDTH
        self.height = BLOCK_HEIGHT
        self.color = color
        self.points = points
        self.active = True

    def draw(self):
        if not self.active:
            return
        # Draw block as rectangle with inner rectangle
        pygame.draw.rect(screen, self.color,
                        (self.x, self.y, self.width, self.height))
        pygame.draw.rect(screen, BLACK,
                        (self.x + 2, self.y + 2, self.width - 4, self.height - 4))
        pygame.draw.rect(screen, self.color,
                        (self.x + 4, self.y + 4, self.width - 8, self.height - 8))

    def check_collision(self, ball):
        if not self.active:
            return False

        if (ball.x + ball.size > self.x and
            ball.x - ball.size < self.x + self.width and
            ball.y + ball.size > self.y and
            ball.y - ball.size < self.y + self.height):
            
            # Determine which side was hit
            if ball.x < self.x or ball.x > self.x + self.width:
                ball.dx *= -1
            else:
                ball.dy *= -1
                
            self.active = False
            return True
        return False

class Game:
    def __init__(self):
        self.paddle = Paddle()
        self.ball = Ball()
        self.blocks = []
        self.score = 0
        self.lives = 3
        self.game_over = False
        self.create_blocks()

    def create_blocks(self):
        colors = [RED, ORANGE, YELLOW, GREEN, CYAN]
        points = [50, 40, 30, 20, 10]
        
        for row in range(BLOCK_ROWS):
            y = row * (BLOCK_HEIGHT + BLOCK_SPACING) + BLOCK_TOP_OFFSET
            for col in range(BLOCK_COLS):
                x = col * (BLOCK_WIDTH + BLOCK_SPACING) + (WINDOW_WIDTH - (BLOCK_COLS * (BLOCK_WIDTH + BLOCK_SPACING) - BLOCK_SPACING)) // 2
                self.blocks.append(Block(x, y, colors[row], points[row]))

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if self.game_over:
                        self.__init__()
                    else:
                        self.ball.moving = True

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.paddle.move(-1)
        if keys[pygame.K_RIGHT]:
            self.paddle.move(1)

    def update(self):
        if self.game_over:
            return

        # Update ball
        if self.ball.update(self.paddle):
            self.lives -= 1
            if self.lives <= 0:
                self.game_over = True
            else:
                self.ball.reset()

        # Check block collisions
        for block in self.blocks:
            if block.check_collision(self.ball):
                self.score += block.points

        # Check win condition
        if all(not block.active for block in self.blocks):
            self.game_over = True

    def draw(self):
        screen.fill(BLACK)
        
        # Draw game objects
        self.paddle.draw()
        self.ball.draw()
        for block in self.blocks:
            block.draw()

        # Draw score and lives
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Score: {self.score}", True, WHITE)
        lives_text = font.render(f"Lives: {self.lives}", True, WHITE)
        screen.blit(score_text, (10, 10))
        screen.blit(lives_text, (WINDOW_WIDTH - 100, 10))

        # Draw game over or win
        if self.game_over:
            font = pygame.font.Font(None, 72)
            if self.lives <= 0:
                text = "GAME OVER"
                color = RED
            else:
                text = "YOU WIN!"
                color = GREEN
            
            game_over_text = font.render(text, True, color)
            text_rect = game_over_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2))
            screen.blit(game_over_text, text_rect)
            
            font = pygame.font.Font(None, 36)
            restart_text = font.render("Press SPACE to restart", True, WHITE)
            restart_rect = restart_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + 50))
            screen.blit(restart_text, restart_rect)

        pygame.display.flip()

def main():
    game = Game()

    while True:
        game.handle_input()
        game.update()
        game.draw()
        clock.tick(FPS)

if __name__ == "__main__":
    main() 