import pygame
import random
import math

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 600
WINDOW_HEIGHT = 600
GRID_SIZE = 40
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
DARK_GREEN = (0, 180, 0)
BLUE = (0, 100, 255)
DARK_BLUE = (0, 70, 180)
RED = (255, 50, 50)
DARK_RED = (180, 35, 35)
YELLOW = (255, 255, 0)
DARK_YELLOW = (180, 180, 0)
BROWN = (139, 69, 19)
DARK_BROWN = (99, 49, 14)
GRASS_GREEN = (34, 139, 34)
ROAD_GRAY = (50, 50, 50)
LIGHT_GRAY = (70, 70, 70)

# Game settings
FROG_SIZE = GRID_SIZE - 4
CAR_WIDTH = GRID_SIZE * 2
LOG_WIDTH = GRID_SIZE * 3
STARTING_LIVES = 3

class Frog:
    def __init__(self):
        self.reset_position()
        self.size = FROG_SIZE
        self.on_log = None
        self.hop_animation = 0  # For jump animation
    
    def reset_position(self):
        self.x = WINDOW_WIDTH // 2
        self.y = WINDOW_HEIGHT - GRID_SIZE // 2
        self.on_log = None
    
    def move(self, dx, dy):
        new_x = self.x + dx * GRID_SIZE
        new_y = self.y + dy * GRID_SIZE
        
        if 0 <= new_x <= WINDOW_WIDTH and 0 <= new_y <= WINDOW_HEIGHT:
            self.x = new_x
            self.y = new_y
            self.hop_animation = 5  # Start hop animation
            return True
        return False
    
    def update(self):
        if self.on_log:
            self.x += self.on_log.speed
            if self.x < 0 or self.x > WINDOW_WIDTH:
                return False
        
        # Update hop animation
        if self.hop_animation > 0:
            self.hop_animation -= 1
        
        return True
    
    def draw(self, screen):
        # Calculate hop offset for animation
        hop_offset = math.sin(self.hop_animation * math.pi / 5) * 5 if self.hop_animation > 0 else 0
        
        # Draw frog body (oval)
        pygame.draw.ellipse(screen, DARK_GREEN,
                          (self.x - self.size//2, self.y - self.size//2 - hop_offset,
                           self.size, self.size))
        pygame.draw.ellipse(screen, GREEN,
                          (self.x - self.size//2 + 2, self.y - self.size//2 - hop_offset + 2,
                           self.size - 4, self.size - 4))
        
        # Draw eyes
        eye_radius = self.size // 8
        pygame.draw.circle(screen, WHITE,
                         (self.x - self.size//4, self.y - self.size//4 - hop_offset),
                         eye_radius)
        pygame.draw.circle(screen, WHITE,
                         (self.x + self.size//4, self.y - self.size//4 - hop_offset),
                         eye_radius)
        pygame.draw.circle(screen, BLACK,
                         (self.x - self.size//4, self.y - self.size//4 - hop_offset),
                         eye_radius//2)
        pygame.draw.circle(screen, BLACK,
                         (self.x + self.size//4, self.y - self.size//4 - hop_offset),
                         eye_radius//2)

class Vehicle:
    def __init__(self, x, y, speed, lane):
        self.x = x
        self.y = y
        self.width = CAR_WIDTH
        self.height = GRID_SIZE - 8
        self.speed = speed
        self.lane = lane
        self.is_truck = random.random() > 0.7
        if self.is_truck:
            self.width = CAR_WIDTH * 1.5
        self.color = RED if lane % 2 == 0 else YELLOW
        self.dark_color = DARK_RED if lane % 2 == 0 else DARK_YELLOW
    
    def update(self):
        self.x += self.speed
        # Wrap around when off screen
        if self.speed > 0 and self.x > WINDOW_WIDTH + self.width:
            self.x = -self.width
        elif self.speed < 0 and self.x < -self.width:
            self.x = WINDOW_WIDTH + self.width
    
    def draw(self, screen):
        # Draw vehicle body
        pygame.draw.rect(screen, self.dark_color,
                        (self.x, self.y - self.height//2,
                         self.width, self.height))
        pygame.draw.rect(screen, self.color,
                        (self.x + 2, self.y - self.height//2 + 2,
                         self.width - 4, self.height - 4))
        
        # Draw windows
        if self.is_truck:
            window_width = self.width // 4
        else:
            window_width = self.width // 3
        
        pygame.draw.rect(screen, LIGHT_GRAY,
                        (self.x + 4, self.y - self.height//2 + 4,
                         window_width, self.height - 8))
        
        # Draw wheels
        wheel_radius = self.height // 4
        wheel_positions = [(self.x + wheel_radius + 2, self.y + self.height//3),
                         (self.x + self.width - wheel_radius - 2, self.y + self.height//3)]
        if self.is_truck:
            wheel_positions.append((self.x + self.width//2, self.y + self.height//3))
        
        for wx, wy in wheel_positions:
            pygame.draw.circle(screen, BLACK, (int(wx), int(wy)), wheel_radius)
            pygame.draw.circle(screen, LIGHT_GRAY, (int(wx), int(wy)), wheel_radius-2)

class Log:
    def __init__(self, x, y, speed, lane):
        self.x = x
        self.y = y
        self.width = LOG_WIDTH
        self.height = GRID_SIZE - 8
        self.speed = speed
        self.lane = lane
    
    def update(self):
        self.x += self.speed
        # Wrap around when off screen
        if self.speed > 0 and self.x > WINDOW_WIDTH + self.width:
            self.x = -self.width
        elif self.speed < 0 and self.x < -self.width:
            self.x = WINDOW_WIDTH + self.width
    
    def draw(self, screen):
        # Draw main log body
        pygame.draw.rect(screen, DARK_BROWN,
                        (self.x, self.y - self.height//2,
                         self.width, self.height))
        
        # Draw wood grain lines
        num_lines = self.width // 10
        for i in range(num_lines):
            x_pos = self.x + (i * 10)
            curve_offset = math.sin(i * 0.5) * 3
            pygame.draw.line(screen, BROWN,
                           (x_pos, self.y - self.height//2 + curve_offset),
                           (x_pos, self.y + self.height//2 + curve_offset),
                           2)
        
        # Draw highlights
        pygame.draw.line(screen, BROWN,
                        (self.x, self.y - self.height//2),
                        (self.x + self.width, self.y - self.height//2),
                        3)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Frogger")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.reset()
    
    def reset(self):
        self.frog = Frog()
        self.lives = STARTING_LIVES
        self.score = 0
        self.reached_spots = [False] * 5  # 5 spots to reach at top
        
        # Create vehicles in lanes
        self.vehicles = []
        vehicle_lanes = range(7, 11)  # 4 lanes of traffic
        for lane in vehicle_lanes:
            y = lane * GRID_SIZE
            speed = (2 + lane % 2) * (1 if lane % 2 == 0 else -1)
            # Add multiple vehicles per lane
            for i in range(3):
                x = (WINDOW_WIDTH // 3) * i
                self.vehicles.append(Vehicle(x, y, speed, lane))
        
        # Create logs in river
        self.logs = []
        log_lanes = range(2, 6)  # 4 lanes of river
        for lane in log_lanes:
            y = lane * GRID_SIZE
            speed = (1 + lane % 2) * (1 if lane % 2 == 0 else -1)
            # Add multiple logs per lane
            for i in range(2):
                x = (WINDOW_WIDTH // 2) * i
                self.logs.append(Log(x, y, speed, lane))
    
    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    self.reset()
                    return True
                
                # Move frog with arrow keys
                dx = dy = 0
                if event.key == pygame.K_LEFT:
                    dx = -1
                elif event.key == pygame.K_RIGHT:
                    dx = 1
                elif event.key == pygame.K_UP:
                    dy = -1
                elif event.key == pygame.K_DOWN:
                    dy = 1
                
                if dx != 0 or dy != 0:
                    self.frog.move(dx, dy)
                    self.frog.on_log = None  # Reset log attachment when jumping
        
        return True
    
    def check_collisions(self):
        # Get frog hitbox
        frog_rect = pygame.Rect(
            self.frog.x - self.frog.size//2,
            self.frog.y - self.frog.size//2,
            self.frog.size,
            self.frog.size
        )
        
        # Check vehicle collisions
        for vehicle in self.vehicles:
            vehicle_rect = pygame.Rect(
                vehicle.x, vehicle.y - vehicle.height//2,
                vehicle.width, vehicle.height
            )
            if frog_rect.colliderect(vehicle_rect):
                return False
        
        # Check if in river
        if 2 * GRID_SIZE < self.frog.y < 6 * GRID_SIZE:
            on_any_log = False
            for log in self.logs:
                log_rect = pygame.Rect(
                    log.x, log.y - log.height//2,
                    log.width, log.height
                )
                if frog_rect.colliderect(log_rect):
                    self.frog.on_log = log
                    on_any_log = True
                    break
            if not on_any_log:
                return False
        
        # Check if reached top
        if self.frog.y < GRID_SIZE:
            spot_index = int(self.frog.x // (WINDOW_WIDTH // 5))
            if 0 <= spot_index < 5 and not self.reached_spots[spot_index]:
                self.reached_spots[spot_index] = True
                self.score += 100
                self.frog.reset_position()
                # Check if all spots are reached
                if all(self.reached_spots):
                    self.score += 1000
                    self.reached_spots = [False] * 5
        
        return True
    
    def update(self):
        # Update vehicles
        for vehicle in self.vehicles:
            vehicle.update()
        
        # Update logs
        for log in self.logs:
            log.update()
        
        # Update frog
        if not self.frog.update() or not self.check_collisions():
            self.lives -= 1
            if self.lives > 0:
                self.frog.reset_position()
            return self.lives > 0
        
        return True
    
    def draw(self):
        self.screen.fill(GRASS_GREEN)
        
        # Draw river with wave effect
        pygame.draw.rect(self.screen, DARK_BLUE,
                        (0, 2 * GRID_SIZE,
                         WINDOW_WIDTH, 4 * GRID_SIZE))
        
        # Draw waves
        for y in range(2, 6):
            wave_y = y * GRID_SIZE
            for x in range(0, WINDOW_WIDTH, 20):
                offset = math.sin((x + pygame.time.get_ticks() * 0.1) * 0.1) * 3
                pygame.draw.arc(self.screen, BLUE,
                              (x, wave_y + offset, 20, 10),
                              0, math.pi, 2)
        
        # Draw road
        pygame.draw.rect(self.screen, ROAD_GRAY,
                        (0, 7 * GRID_SIZE,
                         WINDOW_WIDTH, 4 * GRID_SIZE))
        
        # Draw road lines
        for y in range(7, 11):
            if y % 2 == 0:  # Dashed lines between lanes
                for x in range(0, WINDOW_WIDTH, GRID_SIZE):
                    pygame.draw.line(self.screen, YELLOW,
                                   (x, y * GRID_SIZE),
                                   (x + GRID_SIZE//2, y * GRID_SIZE),
                                   2)
        
        # Draw goal area with lily pads
        for i in range(5):
            x = (WINDOW_WIDTH // 5) * i + (WINDOW_WIDTH // 10)
            if self.reached_spots[i]:
                # Draw filled lily pad with frog
                pygame.draw.circle(self.screen, DARK_GREEN,
                                 (x, GRID_SIZE//2), GRID_SIZE//2)
                pygame.draw.circle(self.screen, GREEN,
                                 (x, GRID_SIZE//2), GRID_SIZE//2 - 2)
                # Draw small frog
                small_frog_size = GRID_SIZE//3
                pygame.draw.ellipse(self.screen, DARK_GREEN,
                                  (x - small_frog_size//2, GRID_SIZE//2 - small_frog_size//2,
                                   small_frog_size, small_frog_size))
            else:
                # Draw empty lily pad
                pygame.draw.circle(self.screen, DARK_GREEN,
                                 (x, GRID_SIZE//2), GRID_SIZE//2)
                pygame.draw.circle(self.screen, GREEN,
                                 (x, GRID_SIZE//2), GRID_SIZE//2 - 2)
        
        # Draw logs
        for log in self.logs:
            log.draw(self.screen)
        
        # Draw vehicles
        for vehicle in self.vehicles:
            vehicle.draw(self.screen)
        
        # Draw frog
        self.frog.draw(self.screen)
        
        # Draw HUD with shadow effect
        lives_text = self.font.render(f"Lives: {self.lives}", True, BLACK)
        score_text = self.font.render(f"Score: {self.score}", True, BLACK)
        self.screen.blit(lives_text, (11, WINDOW_HEIGHT - 29))
        self.screen.blit(score_text, (WINDOW_WIDTH - 149, WINDOW_HEIGHT - 29))
        
        lives_text = self.font.render(f"Lives: {self.lives}", True, WHITE)
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(lives_text, (10, WINDOW_HEIGHT - 30))
        self.screen.blit(score_text, (WINDOW_WIDTH - 150, WINDOW_HEIGHT - 30))
        
        pygame.display.flip()
    
    def run(self):
        running = True
        while running:
            running = self.handle_input() and self.update()
            self.draw()
            self.clock.tick(FPS)

def main():
    game = Game()
    game.run()

if __name__ == "__main__":
    main() 