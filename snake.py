# Snake
# Author: ZineGames
# Original Publication Date: 2024
# Description: A classic snake game where you grow longer as you eat food

import pygame
import sys
import random

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
GRID_SIZE = 20
GRID_WIDTH = WINDOW_WIDTH // GRID_SIZE
GRID_HEIGHT = WINDOW_HEIGHT // GRID_SIZE
FPS = 10

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
DARK_GREEN = (0, 200, 0)

# Direction vectors
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Setup Display
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Snake")
clock = pygame.time.Clock()

class Snake:
    def __init__(self):
        self.length = 1
        self.positions = [(GRID_WIDTH//2, GRID_HEIGHT//2)]
        self.direction = RIGHT
        self.color = GREEN
        self.score = 0
        # Store the last direction to prevent 180-degree turns
        self.last_direction = self.direction

    def get_head_position(self):
        return self.positions[0]

    def update(self):
        cur = self.get_head_position()
        x, y = self.direction
        new = ((cur[0] + x) % GRID_WIDTH, (cur[1] + y) % GRID_HEIGHT)
        
        # Prevent the snake from reversing into itself
        if len(self.positions) > 1 and new == self.positions[1]:
            self.direction = self.last_direction
            x, y = self.direction
            new = ((cur[0] + x) % GRID_WIDTH, (cur[1] + y) % GRID_HEIGHT)
        else:
            self.last_direction = self.direction
        
        # Check for collision with self
        if new in self.positions[2:]:
            return True  # Game Over
            
        self.positions.insert(0, new)
        if len(self.positions) > self.length:
            self.positions.pop()
        return False

    def draw(self):
        for i, p in enumerate(self.positions):
            # Draw each segment as a square with a smaller square inside
            x, y = p
            rect = pygame.Rect(x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE)
            pygame.draw.rect(screen, self.color, rect)
            
            # Inner square (darker) for visual effect
            inner_rect = pygame.Rect(
                x * GRID_SIZE + 4, 
                y * GRID_SIZE + 4, 
                GRID_SIZE - 8, 
                GRID_SIZE - 8
            )
            pygame.draw.rect(screen, DARK_GREEN, inner_rect)
            
            # Draw eyes on the head
            if i == 0:
                # Determine eye positions based on direction
                if self.direction == RIGHT:
                    eye_positions = [(x * GRID_SIZE + 15, y * GRID_SIZE + 5),
                                   (x * GRID_SIZE + 15, y * GRID_SIZE + 15)]
                elif self.direction == LEFT:
                    eye_positions = [(x * GRID_SIZE + 5, y * GRID_SIZE + 5),
                                   (x * GRID_SIZE + 5, y * GRID_SIZE + 15)]
                elif self.direction == UP:
                    eye_positions = [(x * GRID_SIZE + 5, y * GRID_SIZE + 5),
                                   (x * GRID_SIZE + 15, y * GRID_SIZE + 5)]
                else:  # DOWN
                    eye_positions = [(x * GRID_SIZE + 5, y * GRID_SIZE + 15),
                                   (x * GRID_SIZE + 15, y * GRID_SIZE + 15)]
                
                # Draw the eyes
                for eye_pos in eye_positions:
                    pygame.draw.circle(screen, WHITE, eye_pos, 2)

class Food:
    def __init__(self):
        self.position = (0, 0)
        self.color = RED
        self.randomize_position()

    def randomize_position(self):
        self.position = (
            random.randint(0, GRID_WIDTH-1),
            random.randint(0, GRID_HEIGHT-1)
        )

    def draw(self):
        x, y = self.position
        # Draw food as a circle
        center = (int(x * GRID_SIZE + GRID_SIZE/2),
                 int(y * GRID_SIZE + GRID_SIZE/2))
        pygame.draw.circle(screen, self.color, center, int(GRID_SIZE/2))

class Game:
    def __init__(self):
        self.snake = Snake()
        self.food = Food()
        self.game_over = False

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if self.game_over:
                    if event.key == pygame.K_SPACE:
                        self.__init__()  # Reset game
                    return

                if event.key == pygame.K_UP and self.snake.direction != DOWN:
                    self.snake.direction = UP
                elif event.key == pygame.K_DOWN and self.snake.direction != UP:
                    self.snake.direction = DOWN
                elif event.key == pygame.K_LEFT and self.snake.direction != RIGHT:
                    self.snake.direction = LEFT
                elif event.key == pygame.K_RIGHT and self.snake.direction != LEFT:
                    self.snake.direction = RIGHT

    def update(self):
        if self.game_over:
            return

        # Update snake position
        self.game_over = self.snake.update()

        # Check for food collision
        if self.snake.get_head_position() == self.food.position:
            self.snake.length += 1
            self.snake.score += 10
            self.food.randomize_position()
            # Make sure food doesn't appear on snake
            while self.food.position in self.snake.positions:
                self.food.randomize_position()

    def draw(self):
        screen.fill(BLACK)
        
        # Draw game objects
        self.snake.draw()
        self.food.draw()

        # Draw score
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Score: {self.snake.score}", True, WHITE)
        screen.blit(score_text, (10, 10))

        # Draw game over
        if self.game_over:
            font = pygame.font.Font(None, 72)
            game_over_text = font.render("GAME OVER", True, RED)
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