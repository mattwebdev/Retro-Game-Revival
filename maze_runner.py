# Maze Runner
# Author: ZineGames
# Original Publication Date: 2024
# Description: A procedurally generated maze game with timer and collectibles

import pygame
import sys
import random
from enum import Enum

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
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)

# Maze Settings
CELL_SIZE = 40
GRID_WIDTH = WINDOW_WIDTH // CELL_SIZE
GRID_HEIGHT = WINDOW_HEIGHT // CELL_SIZE
WALL_THICKNESS = 4

# Player Settings
PLAYER_SIZE = CELL_SIZE - 10
PLAYER_SPEED = 5
PLAYER_COLOR = GREEN

# Collectible Settings
COIN_SIZE = 10
COIN_COLOR = YELLOW
COINS_COUNT = 5

# Setup Display
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Maze Runner")
clock = pygame.time.Clock()

class Cell:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.walls = {"top": True, "right": True, "bottom": True, "left": True}
        self.visited = False

    def get_pos(self):
        return (self.x * CELL_SIZE, self.y * CELL_SIZE)

    def draw(self):
        x, y = self.get_pos()
        
        if self.walls["top"]:
            pygame.draw.line(screen, WHITE, (x, y), 
                           (x + CELL_SIZE, y), WALL_THICKNESS)
        if self.walls["right"]:
            pygame.draw.line(screen, WHITE, (x + CELL_SIZE, y),
                           (x + CELL_SIZE, y + CELL_SIZE), WALL_THICKNESS)
        if self.walls["bottom"]:
            pygame.draw.line(screen, WHITE, (x + CELL_SIZE, y + CELL_SIZE),
                           (x, y + CELL_SIZE), WALL_THICKNESS)
        if self.walls["left"]:
            pygame.draw.line(screen, WHITE, (x, y + CELL_SIZE),
                           (x, y), WALL_THICKNESS)

class Player:
    def __init__(self, maze):
        self.size = PLAYER_SIZE
        self.speed = PLAYER_SPEED
        self.color = PLAYER_COLOR
        self.maze = maze
        self.reset()

    def reset(self):
        self.x = CELL_SIZE // 2
        self.y = CELL_SIZE // 2
        self.cell_x = 0
        self.cell_y = 0

    def draw(self):
        # Draw player as a square with inner square
        pygame.draw.rect(screen, self.color,
                        (self.x - self.size//2, self.y - self.size//2,
                         self.size, self.size))
        pygame.draw.rect(screen, BLACK,
                        (self.x - self.size//4, self.y - self.size//4,
                         self.size//2, self.size//2))

    def move(self, dx, dy):
        new_x = self.x + dx * self.speed
        new_y = self.y + dy * self.speed
        
        # Calculate current and new cell positions
        current_cell = self.maze.grid[self.cell_y][self.cell_x]
        new_cell_x = int(new_x // CELL_SIZE)
        new_cell_y = int(new_y // CELL_SIZE)
        
        # Check wall collisions
        if dx > 0 and current_cell.walls["right"]:  # Moving right
            new_x = min(new_x, (self.cell_x + 1) * CELL_SIZE - self.size//2)
        elif dx < 0 and current_cell.walls["left"]:  # Moving left
            new_x = max(new_x, self.cell_x * CELL_SIZE + self.size//2)
        
        if dy > 0 and current_cell.walls["bottom"]:  # Moving down
            new_y = min(new_y, (self.cell_y + 1) * CELL_SIZE - self.size//2)
        elif dy < 0 and current_cell.walls["top"]:  # Moving up
            new_y = max(new_y, self.cell_y * CELL_SIZE + self.size//2)
        
        # Update position
        self.x = max(self.size//2, min(new_x, WINDOW_WIDTH - self.size//2))
        self.y = max(self.size//2, min(new_y, WINDOW_HEIGHT - self.size//2))
        
        # Update cell position
        self.cell_x = int(self.x // CELL_SIZE)
        self.cell_y = int(self.y // CELL_SIZE)

class Coin:
    def __init__(self, x, y):
        self.x = x * CELL_SIZE + CELL_SIZE // 2
        self.y = y * CELL_SIZE + CELL_SIZE // 2
        self.size = COIN_SIZE
        self.color = COIN_COLOR
        self.collected = False

    def draw(self):
        if not self.collected:
            # Draw coin as a circle with inner circle
            pygame.draw.circle(screen, self.color, (self.x, self.y), self.size)
            pygame.draw.circle(screen, BLACK, (self.x, self.y), self.size - 2)
            pygame.draw.circle(screen, self.color, (self.x, self.y), self.size - 4)

    def check_collision(self, player):
        if not self.collected:
            dx = abs(self.x - player.x)
            dy = abs(self.y - player.y)
            if dx < (player.size + self.size)//2 and dy < (player.size + self.size)//2:
                self.collected = True
                return True
        return False

class Maze:
    def __init__(self):
        self.grid = [[Cell(x, y) for x in range(GRID_WIDTH)]
                    for y in range(GRID_HEIGHT)]
        self.generate()

    def get_neighbors(self, cell):
        neighbors = []
        directions = [(0, -1), (1, 0), (0, 1), (-1, 0)]  # top, right, bottom, left
        
        for dx, dy in directions:
            new_x = cell.x + dx
            new_y = cell.y + dy
            
            if (0 <= new_x < GRID_WIDTH and 0 <= new_y < GRID_HEIGHT and
                not self.grid[new_y][new_x].visited):
                neighbors.append((self.grid[new_y][new_x], dx, dy))
                
        return neighbors

    def remove_walls(self, current, next_cell, dx, dy):
        if dx == 1:  # Moving right
            current.walls["right"] = False
            next_cell.walls["left"] = False
        elif dx == -1:  # Moving left
            current.walls["left"] = False
            next_cell.walls["right"] = False
        elif dy == 1:  # Moving down
            current.walls["bottom"] = False
            next_cell.walls["top"] = False
        elif dy == -1:  # Moving up
            current.walls["top"] = False
            next_cell.walls["bottom"] = False

    def generate(self):
        # Recursive Backtracking Algorithm
        stack = []
        current = self.grid[0][0]
        current.visited = True
        
        while True:
            neighbors = self.get_neighbors(current)
            
            if neighbors:
                next_cell, dx, dy = random.choice(neighbors)
                stack.append(current)
                
                self.remove_walls(current, next_cell, dx, dy)
                
                current = next_cell
                current.visited = True
            elif stack:
                current = stack.pop()
            else:
                break

        # Reset visited flags
        for row in self.grid:
            for cell in row:
                cell.visited = False

    def draw(self):
        for row in self.grid:
            for cell in row:
                cell.draw()

class Game:
    def __init__(self):
        self.maze = Maze()
        self.player = Player(self.maze)
        self.coins = []
        self.start_time = pygame.time.get_ticks()
        self.game_over = False
        self.won = False
        self.create_coins()

    def create_coins(self):
        self.coins = []
        available_cells = [(x, y) for x in range(GRID_WIDTH) 
                          for y in range(GRID_HEIGHT) if not (x == 0 and y == 0)]
        coin_positions = random.sample(available_cells, COINS_COUNT)
        
        for x, y in coin_positions:
            self.coins.append(Coin(x, y))

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and self.game_over:
                    self.__init__()

        if not self.game_over:
            keys = pygame.key.get_pressed()
            dx = keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]
            dy = keys[pygame.K_DOWN] - keys[pygame.K_UP]
            self.player.move(dx, dy)

    def update(self):
        if self.game_over:
            return

        # Check coin collisions
        coins_collected = 0
        for coin in self.coins:
            if coin.check_collision(self.player):
                coins_collected += 1

        # Check win condition
        if all(coin.collected for coin in self.coins):
            self.game_over = True
            self.won = True

    def draw(self):
        screen.fill(BLACK)
        
        # Draw maze and game objects
        self.maze.draw()
        for coin in self.coins:
            coin.draw()
        self.player.draw()

        # Draw time and coins
        font = pygame.font.Font(None, 36)
        elapsed_time = (pygame.time.get_ticks() - self.start_time) // 1000
        time_text = font.render(f"Time: {elapsed_time}s", True, WHITE)
        coins_text = font.render(f"Coins: {sum(coin.collected for coin in self.coins)}/{COINS_COUNT}", 
                               True, WHITE)
        screen.blit(time_text, (10, 10))
        screen.blit(coins_text, (WINDOW_WIDTH - 150, 10))

        # Draw game over
        if self.game_over:
            font = pygame.font.Font(None, 72)
            if self.won:
                text = f"YOU WIN! Time: {elapsed_time}s"
                color = GREEN
            else:
                text = "GAME OVER"
                color = RED
            
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