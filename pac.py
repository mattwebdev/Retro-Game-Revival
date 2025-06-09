import pygame
import sys
import random
from enum import Enum
import math
from collections import deque

# Initialize Pygame
pygame.init()

# Constants
WINDOW_SIZE = 600
CELL_SIZE = 20
GRID_WIDTH = WINDOW_SIZE // CELL_SIZE
GRID_HEIGHT = WINDOW_SIZE // CELL_SIZE

# Colors
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
PINK = (255, 192, 203)
CYAN = (0, 255, 255)
ORANGE = (255, 165, 0)
DOT_COLOR = (255, 255, 255)
POWER_PELLET_COLOR = (255, 255, 255)

# Game settings
GHOST_SPEED = 1
PACMAN_SPEED = 2
POWER_PELLET_DURATION = 5000  # milliseconds
GHOST_SCORE = 200
DOT_SCORE = 10
POWER_PELLET_SCORE = 50

class Direction(Enum):
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)

class GameState(Enum):
    START = 1
    PLAYING = 2
    GAME_OVER = 3
    PAUSED = 4

class Node:
    def __init__(self, x, y, g_cost=0, h_cost=0):
        self.x = x
        self.y = y
        self.g_cost = g_cost
        self.h_cost = h_cost
        self.f_cost = g_cost + h_cost
        self.parent = None

    def __lt__(self, other):
        return self.f_cost < other.f_cost

class Ghost:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.direction = Direction.UP
        self.speed = GHOST_SPEED
        self.is_frightened = False
        self.frightened_timer = 0
        self.radius = CELL_SIZE // 2 - 2
        self.target_x = x
        self.target_y = y
        self.mode = "house"
        self.mode_timer = 0
        self.scatter_target = self.get_scatter_target()
        self.start_x = x
        self.start_y = y
        self.leaving_house = False
        self.leave_timer = 0
        self.path = []
        self.next_node = None
        print(f"Ghost {color} initialized at ({x}, {y})")

    def get_scatter_target(self):
        if self.color == RED:
            return (GRID_WIDTH * CELL_SIZE - CELL_SIZE, 0)
        elif self.color == PINK:
            return (0, 0)
        elif self.color == CYAN:
            return (GRID_WIDTH * CELL_SIZE - CELL_SIZE, GRID_HEIGHT * CELL_SIZE - CELL_SIZE)
        else:  # Orange
            return (0, GRID_HEIGHT * CELL_SIZE - CELL_SIZE)

    def get_grid_position(self):
        return (int(self.x // CELL_SIZE), int(self.y // CELL_SIZE))

    def get_pixel_position(self, grid_x, grid_y):
        return (grid_x * CELL_SIZE + CELL_SIZE // 2, grid_y * CELL_SIZE + CELL_SIZE // 2)

    def find_path(self, maze, target_x, target_y):
        # Get current position
        start_x, start_y = self.get_grid_position()
        
        # Convert target to grid coordinates and ensure they're within bounds
        target_grid_x = max(0, min(int(target_x // CELL_SIZE), GRID_WIDTH - 1))
        target_grid_y = max(0, min(int(target_y // CELL_SIZE), GRID_HEIGHT - 1))

        # If start position is invalid, return empty path
        if not (0 <= start_x < GRID_WIDTH and 0 <= start_y < GRID_HEIGHT):
            return []

        # Create open and closed lists
        open_list = []
        closed_set = set()

        # Create start node
        start_node = Node(start_x, start_y)
        start_node.h_cost = self.heuristic(start_x, start_y, target_grid_x, target_grid_y)
        open_list.append(start_node)

        while open_list:
            # Get node with lowest f_cost
            current = min(open_list, key=lambda x: x.f_cost)
            open_list.remove(current)

            # If we reached the target
            if current.x == target_grid_x and current.y == target_grid_y:
                path = []
                while current:
                    path.append((current.x, current.y))
                    current = current.parent
                return path[::-1]  # Reverse path to get start to end

            closed_set.add((current.x, current.y))

            # Check neighbors
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                neighbor_x = current.x + dx
                neighbor_y = current.y + dy

                # Skip if out of bounds
                if not (0 <= neighbor_x < GRID_WIDTH and 0 <= neighbor_y < GRID_HEIGHT):
                    continue

                # Skip if already visited
                if (neighbor_x, neighbor_y) in closed_set:
                    continue

                # Skip if wall
                try:
                    if maze[neighbor_y][neighbor_x] == 1:
                        continue
                except IndexError:
                    continue

                # Calculate costs
                g_cost = current.g_cost + 1
                h_cost = self.heuristic(neighbor_x, neighbor_y, target_grid_x, target_grid_y)

                # Check if neighbor is in open list
                neighbor = next((node for node in open_list if node.x == neighbor_x and node.y == neighbor_y), None)
                if neighbor is None:
                    neighbor = Node(neighbor_x, neighbor_y, g_cost, h_cost)
                    neighbor.parent = current
                    open_list.append(neighbor)
                elif g_cost < neighbor.g_cost:
                    neighbor.g_cost = g_cost
                    neighbor.f_cost = g_cost + h_cost
                    neighbor.parent = current

        return []  # No path found

    def heuristic(self, x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def get_valid_directions(self, maze):
        """Get all valid directions that don't lead into walls"""
        valid_directions = []
        for direction in Direction:
            if self.can_move(maze, direction):
                valid_directions.append(direction)
        return valid_directions

    def get_best_direction(self, maze, target_x, target_y):
        """Get the best direction to move towards the target"""
        valid_directions = self.get_valid_directions(maze)
        if not valid_directions:
            return None

        # Don't allow 180-degree turns unless necessary
        valid_directions = [d for d in valid_directions 
                          if d.value[0] != -self.direction.value[0] or 
                             d.value[1] != -self.direction.value[1]]
        
        if not valid_directions:
            # If no valid directions without 180-degree turn, allow it
            valid_directions = self.get_valid_directions(maze)

        # Calculate distance to target for each valid direction
        best_direction = None
        min_distance = float('inf')
        
        for direction in valid_directions:
            dx, dy = direction.value
            next_x = self.x + dx * self.speed
            next_y = self.y + dy * self.speed
            distance = math.sqrt((next_x - target_x)**2 + (next_y - target_y)**2)
            
            if distance < min_distance:
                min_distance = distance
                best_direction = direction

        return best_direction

    def update(self, maze, pacman):
        # Update mode timer
        self.mode_timer += 1
        
        # Handle leaving the ghost house
        if self.mode == "house":
            self.leave_timer += 1
            print(f"Ghost {self.color} in house mode, timer: {self.leave_timer}")
            
            # Start moving after 1 second (60 frames)
            if self.leave_timer >= 60:
                # Move up to exit
                if self.y > GRID_HEIGHT * CELL_SIZE // 2 - CELL_SIZE * 2:
                    self.y -= self.speed
                    print(f"Ghost {self.color} moving up: y={self.y}")
                else:
                    # Once at the door, move left or right to exit
                    if self.x < GRID_WIDTH * CELL_SIZE // 2:
                        self.x += self.speed
                    else:
                        self.x -= self.speed
                    
                    # If we've moved far enough from the center, switch to scatter mode
                    if abs(self.x - GRID_WIDTH * CELL_SIZE // 2) > CELL_SIZE * 2:
                        self.mode = "scatter"
                        self.leave_timer = 0
                        print(f"Ghost {self.color} switching to scatter mode")
            return

        if self.mode_timer >= 300:  # Change mode every 5 seconds
            self.mode_timer = 0
            if self.mode == "chase":
                self.mode = "scatter"
                print(f"Ghost {self.color} switching to scatter mode")
            else:
                self.mode = "chase"
                print(f"Ghost {self.color} switching to chase mode")

        if self.is_frightened:
            self.frightened_timer -= 16
            if self.frightened_timer <= 0:
                self.is_frightened = False
                self.mode = "chase"
                print(f"Ghost {self.color} no longer frightened")

        # Update target based on mode and ghost color
        if self.is_frightened:
            self.mode = "frightened"
            # Random movement when frightened
            if random.random() < 0.1 or not self.can_move(maze, self.direction):
                possible_directions = self.get_valid_directions(maze)
                if possible_directions:
                    self.direction = random.choice(possible_directions)
                    print(f"Ghost {self.color} choosing random direction: {self.direction}")
        else:
            if self.mode == "chase":
                if self.color == RED:  # Blinky - Directly targets Pac-Man
                    self.target_x = pacman.x
                    self.target_y = pacman.y
                elif self.color == PINK:  # Pinky - Targets 4 spaces ahead of Pac-Man
                    dx, dy = pacman.direction.value
                    self.target_x = pacman.x + dx * CELL_SIZE * 4
                    self.target_y = pacman.y + dy * CELL_SIZE * 4
                elif self.color == CYAN:  # Inky - Complex targeting based on Blinky's position
                    dx, dy = pacman.direction.value
                    target_x = pacman.x + dx * CELL_SIZE * 2
                    target_y = pacman.y + dy * CELL_SIZE * 2
                    blinky_x = self.x
                    blinky_y = self.y
                    self.target_x = target_x + (target_x - blinky_x)
                    self.target_y = target_y + (target_y - blinky_y)
                else:  # Orange - Clyde - Targets Pac-Man when far, scatter when close
                    distance = math.sqrt((self.x - pacman.x)**2 + (self.y - pacman.y)**2)
                    if distance > CELL_SIZE * 8:
                        self.target_x = pacman.x
                        self.target_y = pacman.y
                    else:
                        self.target_x, self.target_y = self.scatter_target

                # Ensure target coordinates are within bounds
                self.target_x = max(0, min(self.target_x, WINDOW_SIZE - CELL_SIZE))
                self.target_y = max(0, min(self.target_y, WINDOW_SIZE - CELL_SIZE))
            else:  # Scatter mode
                self.target_x, self.target_y = self.scatter_target

            # Get best direction to move
            best_direction = self.get_best_direction(maze, self.target_x, self.target_y)
            if best_direction:
                self.direction = best_direction
                print(f"Ghost {self.color} moving towards target: {self.target_x}, {self.target_y}")

        # Move in current direction
        if self.can_move(maze, self.direction):
            dx, dy = self.direction.value
            self.x += dx * self.speed
            self.y += dy * self.speed
            print(f"Ghost {self.color} moving: dx={dx}, dy={dy}, pos=({self.x}, {self.y})")
        else:
            print(f"Ghost {self.color} cannot move in direction {self.direction}")
            # Try to find a new direction
            best_direction = self.get_best_direction(maze, self.target_x, self.target_y)
            if best_direction:
                self.direction = best_direction
                print(f"Ghost {self.color} choosing new direction: {self.direction}")

    def can_move(self, maze, direction):
        """Check if the ghost can move in the given direction"""
        dx, dy = direction.value
        next_x = self.x + dx * self.speed
        next_y = self.y + dy * self.speed
        
        # Convert pixel coordinates to grid coordinates
        grid_x = int(next_x // CELL_SIZE)
        grid_y = int(next_y // CELL_SIZE)
        
        # Check if the next position is within bounds
        if not (0 <= grid_x < GRID_WIDTH and 0 <= grid_y < GRID_HEIGHT):
            return False
            
        # Check if the next position is a wall
        if maze[grid_y][grid_x] == 1:
            return False
            
        # Ghosts can pass through the ghost house door (value 2)
        if maze[grid_y][grid_x] == 2:
            return True
            
        return True

    def draw(self, screen):
        # Draw ghost body
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        
        # Draw eyes
        eye_radius = self.radius // 3
        eye_offset = self.radius // 2
        
        # Left eye
        pygame.draw.circle(screen, WHITE, 
                         (int(self.x - eye_offset), int(self.y - eye_offset)), 
                         eye_radius)
        
        # Right eye
        pygame.draw.circle(screen, WHITE, 
                         (int(self.x + eye_offset), int(self.y - eye_offset)), 
                         eye_radius)
        
        # Pupils
        pupil_radius = eye_radius // 2
        pupil_offset = eye_radius // 2
        
        # Determine pupil direction based on ghost's direction
        if self.direction == Direction.UP:
            pupil_dx, pupil_dy = 0, -pupil_offset
        elif self.direction == Direction.DOWN:
            pupil_dx, pupil_dy = 0, pupil_offset
        elif self.direction == Direction.LEFT:
            pupil_dx, pupil_dy = -pupil_offset, 0
        else:  # RIGHT
            pupil_dx, pupil_dy = pupil_offset, 0
        
        # Draw pupils
        pygame.draw.circle(screen, BLACK, 
                         (int(self.x - eye_offset + pupil_dx), 
                          int(self.y - eye_offset + pupil_dy)), 
                         pupil_radius)
        pygame.draw.circle(screen, BLACK, 
                         (int(self.x + eye_offset + pupil_dx), 
                          int(self.y - eye_offset + pupil_dy)), 
                         pupil_radius)

    def reset_position(self):
        """Reset the ghost to its starting position"""
        self.x = self.start_x
        self.y = self.start_y
        self.direction = Direction.UP
        self.mode = "house"
        self.leave_timer = 0
        self.is_frightened = False
        self.frightened_timer = 0
        print(f"Ghost {self.color} reset to position ({self.x}, {self.y})")

class Pacman:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.direction = Direction.RIGHT
        self.next_direction = Direction.RIGHT
        self.speed = PACMAN_SPEED
        self.radius = CELL_SIZE // 2 - 2
        self.mouth_open = 0
        self.mouth_speed = 0.2
        self.lives = 3
        self.score = 0
        self.is_powered = False
        self.power_timer = 0

    def update(self, maze, dots, power_pellets, ghosts):
        # Try to change direction if requested
        if self.can_move(maze, self.next_direction):
            self.direction = self.next_direction

        # Move in current direction if possible
        if self.can_move(maze, self.direction):
            dx, dy = self.direction.value
            self.x += dx * self.speed
            self.y += dy * self.speed

        # Update mouth animation
        self.mouth_open += self.mouth_speed
        if self.mouth_open > 0.5 or self.mouth_open < 0:
            self.mouth_speed = -self.mouth_speed

        # Check for dot collection
        grid_x = int(self.x // CELL_SIZE)
        grid_y = int(self.y // CELL_SIZE)
        if 0 <= grid_x < GRID_WIDTH and 0 <= grid_y < GRID_HEIGHT:
            if dots[grid_y][grid_x]:
                dots[grid_y][grid_x] = False
                self.score += DOT_SCORE

        # Check for power pellet collection
        for pellet in power_pellets[:]:
            if (abs(self.x - pellet[0]) < CELL_SIZE and 
                abs(self.y - pellet[1]) < CELL_SIZE):
                power_pellets.remove(pellet)
                self.score += POWER_PELLET_SCORE
                self.is_powered = True
                self.power_timer = POWER_PELLET_DURATION
                for ghost in ghosts:
                    ghost.is_frightened = True
                    ghost.frightened_timer = POWER_PELLET_DURATION

        # Update power timer
        if self.is_powered:
            self.power_timer -= 16  # Approximate milliseconds per frame
            if self.power_timer <= 0:
                self.is_powered = False
                for ghost in ghosts:
                    ghost.is_frightened = False

        # Check ghost collisions
        for ghost in ghosts:
            if (abs(self.x - ghost.x) < CELL_SIZE and 
                abs(self.y - ghost.y) < CELL_SIZE):
                if self.is_powered:
                    # Eat ghost
                    ghost.x = GRID_WIDTH * CELL_SIZE // 2
                    ghost.y = GRID_HEIGHT * CELL_SIZE // 2
                    self.score += GHOST_SCORE
                else:
                    # Lose life
                    self.lives -= 1
                    self.reset_position()
                    for ghost in ghosts:
                        ghost.reset_position()

    def reset_position(self):
        self.x = CELL_SIZE * 1.5
        self.y = CELL_SIZE * 1.5
        self.direction = Direction.RIGHT
        self.next_direction = Direction.RIGHT

    def can_move(self, maze, direction):
        dx, dy = direction.value
        next_x = self.x + dx * self.speed
        next_y = self.y + dy * self.speed
        
        grid_x = int(next_x // CELL_SIZE)
        grid_y = int(next_y // CELL_SIZE)
        
        if 0 <= grid_x < GRID_WIDTH and 0 <= grid_y < GRID_HEIGHT:
            return maze[grid_y][grid_x] != 1
        return False

    def draw(self, screen):
        center = (int(self.x), int(self.y))
        start_angle = 30 + self.mouth_open * 30
        end_angle = 330 - self.mouth_open * 30
        
        if self.direction == Direction.UP:
            start_angle, end_angle = 120 + start_angle, 120 + end_angle
        elif self.direction == Direction.DOWN:
            start_angle, end_angle = 300 + start_angle, 300 + end_angle
        elif self.direction == Direction.LEFT:
            start_angle, end_angle = 210 + start_angle, 210 + end_angle
        
        pygame.draw.arc(screen, YELLOW, 
                       (center[0] - self.radius, center[1] - self.radius,
                        self.radius * 2, self.radius * 2),
                       math.radians(start_angle),
                       math.radians(end_angle),
                       self.radius)

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
        pygame.display.set_caption("Pac-Man")
        self.clock = pygame.time.Clock()
        self.running = True
        self.game_state = "start"
        self.score = 0
        self.lives = 3
        self.power_pellet_active = False
        self.power_pellet_timer = 0
        
        # Initialize fonts
        self.font = pygame.font.Font(None, 36)
        self.title_font = pygame.font.Font(None, 72)
        self.instructions_font = pygame.font.Font(None, 24)
        
        # Initialize start screen variables
        self.blink_timer = 0
        self.show_press_key = True
        
        # Initialize maze and game elements
        self.maze = self.create_maze()
        self.dots = self.create_dots()
        self.power_pellets = self.create_power_pellets()
        
        # Initialize Pac-Man
        self.pacman = Pacman(GRID_WIDTH * CELL_SIZE // 2, GRID_HEIGHT * CELL_SIZE // 2)
        
        # Initialize ghosts in the ghost house
        ghost_house_center_x = GRID_WIDTH * CELL_SIZE // 2
        ghost_house_center_y = GRID_HEIGHT * CELL_SIZE // 2
        
        # Initialize ghosts in a cross pattern in the ghost house
        self.ghosts = [
            Ghost(ghost_house_center_x, ghost_house_center_y, RED),  # Blinky
            Ghost(ghost_house_center_x - CELL_SIZE, ghost_house_center_y, PINK),  # Pinky
            Ghost(ghost_house_center_x + CELL_SIZE, ghost_house_center_y, CYAN),  # Inky
            Ghost(ghost_house_center_x, ghost_house_center_y - CELL_SIZE, ORANGE)  # Clyde
        ]
        
        # Set initial directions
        self.ghosts[0].direction = Direction.RIGHT  # Blinky
        self.ghosts[1].direction = Direction.LEFT   # Pinky
        self.ghosts[2].direction = Direction.RIGHT  # Inky
        self.ghosts[3].direction = Direction.UP     # Clyde
        
        # Set initial mode to house
        for ghost in self.ghosts:
            ghost.mode = "house"
            ghost.leave_timer = 0
            print(f"Ghost {ghost.color} initialized at ({ghost.x}, {ghost.y})")

    def update(self):
        if self.game_state == "playing":
            self.pacman.update(self.maze, self.dots, self.power_pellets, self.ghosts)
            
            # Update power pellet timer
            if self.power_pellet_active:
                self.power_pellet_timer -= 16
                if self.power_pellet_timer <= 0:
                    self.power_pellet_active = False
                    for ghost in self.ghosts:
                        ghost.is_frightened = False
            
            # Update ghosts
            for ghost in self.ghosts:
                ghost.update(self.maze, self.pacman)
                
                # Check collision with Pac-Man
                if (abs(ghost.x - self.pacman.x) < CELL_SIZE and 
                    abs(ghost.y - self.pacman.y) < CELL_SIZE):
                    if ghost.is_frightened:
                        # Ghost is eaten
                        ghost.x = GRID_WIDTH * CELL_SIZE // 2
                        ghost.y = GRID_HEIGHT * CELL_SIZE // 2
                        ghost.mode = "house"
                        ghost.leave_timer = 0
                        ghost.is_frightened = False
                        self.score += GHOST_SCORE
                    else:
                        # Pac-Man is eaten
                        self.lives -= 1
                        if self.lives <= 0:
                            self.game_state = "game_over"
                        else:
                            self.reset_positions()
            
            # Check if all dots are eaten
            if all(cell != 0 for row in self.maze for cell in row):
                self.game_state = "win"

    def draw(self):
        if self.game_state == "start":
            self.draw_start_screen()
        elif self.game_state == "playing":
            self.screen.fill(BLACK)
            
            # Draw maze
            for y in range(len(self.maze)):
                for x in range(len(self.maze[y])):
                    if self.maze[y][x] == 1:
                        pygame.draw.rect(self.screen, BLUE,
                                       (x * CELL_SIZE, y * CELL_SIZE,
                                        CELL_SIZE, CELL_SIZE))
                    elif self.maze[y][x] == 2:  # Ghost house door
                        pygame.draw.rect(self.screen, (255, 192, 203),  # Pink color for ghost door
                                       (x * CELL_SIZE, y * CELL_SIZE,
                                        CELL_SIZE, CELL_SIZE))

            # Draw dots
            for y in range(GRID_HEIGHT):
                for x in range(GRID_WIDTH):
                    if self.dots[y][x]:
                        pygame.draw.circle(self.screen, DOT_COLOR,
                                         (x * CELL_SIZE + CELL_SIZE // 2,
                                          y * CELL_SIZE + CELL_SIZE // 2),
                                         2)

            # Draw power pellets
            for pellet in self.power_pellets:
                pygame.draw.circle(self.screen, POWER_PELLET_COLOR,
                                 (int(pellet[0]), int(pellet[1])),
                                 CELL_SIZE // 4)

            # Draw Pac-Man
            self.pacman.draw(self.screen)

            # Draw ghosts
            for ghost in self.ghosts:
                ghost.draw(self.screen)

            # Draw score and lives
            score_text = self.font.render(f'Score: {self.score}', True, WHITE)
            lives_text = self.font.render(f'Lives: {self.lives}', True, WHITE)
            self.screen.blit(score_text, (10, 10))
            self.screen.blit(lives_text, (WINDOW_SIZE - 100, 10))
            
            pygame.display.flip()
        elif self.game_state == "paused":
            self.draw_pause_screen()
        elif self.game_state == "game_over":
            self.screen.fill(BLACK)
            game_over_text = self.title_font.render('GAME OVER', True, RED)
            text_rect = game_over_text.get_rect(center=(WINDOW_SIZE // 2, WINDOW_SIZE // 2 - 50))
            self.screen.blit(game_over_text, text_rect)
            
            final_score_text = self.font.render(f'Final Score: {self.score}', True, WHITE)
            score_rect = final_score_text.get_rect(center=(WINDOW_SIZE // 2, WINDOW_SIZE // 2 + 50))
            self.screen.blit(final_score_text, score_rect)
            
            restart_text = self.font.render('Press SPACE to restart', True, WHITE)
            restart_rect = restart_text.get_rect(center=(WINDOW_SIZE // 2, WINDOW_SIZE // 2 + 100))
            self.screen.blit(restart_text, restart_rect)
            
            pygame.display.flip()

    def draw_start_screen(self):
        self.screen.fill(BLACK)
        
        # Draw title
        title_text = self.title_font.render("PAC-MAN", True, YELLOW)
        title_rect = title_text.get_rect(center=(WINDOW_SIZE // 2, WINDOW_SIZE // 4))
        self.screen.blit(title_text, title_rect)
        
        # Draw instructions
        instructions = [
            "Use arrow keys to move",
            "Eat all dots to complete the level",
            "Power pellets let you eat ghosts",
            "Avoid ghosts when not powered up",
            f"Score: {DOT_SCORE} per dot, {POWER_PELLET_SCORE} per power pellet",
            f"Eat ghosts for {GHOST_SCORE} points when powered up"
        ]
        
        for i, instruction in enumerate(instructions):
            text = self.instructions_font.render(instruction, True, WHITE)
            rect = text.get_rect(center=(WINDOW_SIZE // 2, WINDOW_SIZE // 2 + i * 30))
            self.screen.blit(text, rect)
        
        # Blinking "Press any key" text
        self.blink_timer += 1
        if self.blink_timer >= 30:  # Blink every half second
            self.show_press_key = not self.show_press_key
            self.blink_timer = 0
            
        if self.show_press_key:
            press_key_text = self.font.render("Press any key to start", True, WHITE)
            press_key_rect = press_key_text.get_rect(center=(WINDOW_SIZE // 2, WINDOW_SIZE * 3 // 4))
            self.screen.blit(press_key_text, press_key_rect)
        
        pygame.display.flip()

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p and self.game_state == "playing":
                    self.game_state = "paused"
                elif event.key == pygame.K_p and self.game_state == "paused":
                    self.game_state = "playing"
                elif self.game_state == "start":
                    self.game_state = "playing"
                elif self.game_state == "playing":
                    if event.key == pygame.K_UP:
                        self.pacman.next_direction = Direction.UP
                    elif event.key == pygame.K_DOWN:
                        self.pacman.next_direction = Direction.DOWN
                    elif event.key == pygame.K_LEFT:
                        self.pacman.next_direction = Direction.LEFT
                    elif event.key == pygame.K_RIGHT:
                        self.pacman.next_direction = Direction.RIGHT
                elif self.game_state == "game_over":
                    if event.key == pygame.K_SPACE:
                        self.reset_game()

    def reset_game(self):
        self.game_state = "start"
        self.maze = self.create_maze()
        self.dots = self.create_dots()
        self.power_pellets = self.create_power_pellets()
        self.pacman = Pacman(GRID_WIDTH * CELL_SIZE // 2, GRID_HEIGHT * CELL_SIZE // 2)
        
        # Reset ghosts with proper starting positions
        ghost_house_center_x = GRID_WIDTH * CELL_SIZE // 2
        ghost_house_center_y = GRID_HEIGHT * CELL_SIZE // 2
        self.ghosts = [
            Ghost(ghost_house_center_x, ghost_house_center_y, RED),  # Blinky
            Ghost(ghost_house_center_x - CELL_SIZE, ghost_house_center_y, PINK),  # Pinky
            Ghost(ghost_house_center_x + CELL_SIZE, ghost_house_center_y, CYAN),  # Inky
            Ghost(ghost_house_center_x, ghost_house_center_y - CELL_SIZE, ORANGE)  # Clyde
        ]

    def create_maze(self):
        # More authentic Pac-Man maze layout with ghost house
        maze = [
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 0, 1, 1, 1, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 0, 1, 1, 1, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 1, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 0, 1, 1, 1, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 1, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 2, 2, 1, 1, 1, 1, 0, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 0, 1, 1, 0, 1, 2, 2, 2, 2, 2, 2, 1, 1, 0, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 2, 2, 2, 2, 2, 2, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 1, 1, 1, 1, 0, 1, 1, 0, 1, 2, 2, 2, 2, 2, 2, 1, 0, 1, 1, 1, 1, 0, 1, 1, 1, 1, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        ]
        print("Maze created with ghost house")
        return maze

    def create_dots(self):
        dots = [[False for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        for y in range(min(GRID_HEIGHT, len(self.maze))):
            for x in range(min(GRID_WIDTH, len(self.maze[y]))):
                if self.maze[y][x] == 0:
                    dots[y][x] = True
        return dots

    def create_power_pellets(self):
        return [
            (CELL_SIZE * 1.5, CELL_SIZE * 1.5),
            (CELL_SIZE * 28.5, CELL_SIZE * 1.5),
            (CELL_SIZE * 1.5, CELL_SIZE * 15.5),
            (CELL_SIZE * 28.5, CELL_SIZE * 15.5)
        ]

    def draw_pause_screen(self):
        # Create a semi-transparent overlay
        overlay = pygame.Surface((WINDOW_SIZE, WINDOW_SIZE), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))  # Black with 50% opacity
        self.screen.blit(overlay, (0, 0))
        
        # Draw pause text
        pause_text = self.title_font.render("PAUSED", True, YELLOW)
        text_rect = pause_text.get_rect(center=(WINDOW_SIZE // 2, WINDOW_SIZE // 2 - 50))
        self.screen.blit(pause_text, text_rect)
        
        # Draw instructions
        continue_text = self.font.render("Press P to continue", True, WHITE)
        continue_rect = continue_text.get_rect(center=(WINDOW_SIZE // 2, WINDOW_SIZE // 2 + 50))
        self.screen.blit(continue_text, continue_rect)
        
        pygame.display.flip()

    def run(self):
        while True:
            self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(60)

if __name__ == "__main__":
    game = Game()
    game.run() 