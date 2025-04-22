# Cave Runner
# Author: ZineGames
# Original Publication Date: 2024
# Description: A geometric platformer with procedural cave generation

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
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
BROWN = (139, 69, 19)
YELLOW = (255, 255, 0)

# Player Settings
PLAYER_WIDTH = 20
PLAYER_HEIGHT = 45
PLAYER_SPEED = 5
JUMP_POWER = -15
GRAVITY = 0.8
TERMINAL_VELOCITY = 15

# Calculate maximum jump distance
# Using simplified physics for a more generous jump distance
# This accounts for player speed and jump height
PEAK_HEIGHT = (-JUMP_POWER * -JUMP_POWER) / (2 * GRAVITY)
MAX_JUMP_DISTANCE = 300  # Fixed maximum jump distance that feels good for gameplay

# Platform Settings
PLATFORM_HEIGHT = 40
MIN_PLATFORM_WIDTH = 60
MAX_PLATFORM_WIDTH = 200
MIN_GAP = 50  # Minimum gap between platforms
MAX_GAP = 200  # Maximum gap between platforms
PLATFORM_Y_VARIANCE = 100  # Maximum vertical difference between platforms
PLATFORM_SPACING = min(200, MAX_JUMP_DISTANCE * 0.7)  # Never more than 70% of max jump
PLATFORM_VARIANCE = min(100, PLATFORM_SPACING * 0.3)  # Adjust variance to be proportional but limited

# Collectible Settings
GEM_SIZE = 20
GEMS_PER_PLATFORM = 2
GEM_POINTS = 10

# Hazard Settings
SPIKE_WIDTH = 20
SPIKE_HEIGHT = 20
SPIKES_PER_PLATFORM = 2

# Camera Settings
CAMERA_SLACK = 200

# Setup Display
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Cave Runner")
clock = pygame.time.Clock()

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = PLAYER_WIDTH
        self.height = PLAYER_HEIGHT
        self.dx = 0
        self.dy = 0
        self.on_ground = False
        self.facing_right = True
        self.score = 0
        self.lives = 3
        self.invulnerable = 0

    def move(self, platforms):
        # Horizontal movement
        self.x += self.dx
        
        # Vertical movement
        self.dy = min(self.dy + GRAVITY, TERMINAL_VELOCITY)
        self.y += self.dy
        self.on_ground = False

        # Platform collisions
        for platform in platforms:
            if self.check_collision(platform):
                if self.dy > 0 and self.y < platform.y + platform.height:  # Landing
                    self.y = platform.y - self.height
                    self.dy = 0
                    self.on_ground = True
                elif self.dy < 0:  # Hitting ceiling
                    self.y = platform.y + platform.height
                    self.dy = 0

    def jump(self):
        if self.on_ground:
            self.dy = JUMP_POWER
            self.on_ground = False

    def check_collision(self, other):
        return (self.x < other.x + other.width and
                self.x + self.width > other.x and
                self.y < other.y + other.height and
                self.y + self.height > other.y)

    def draw(self, camera_x):
        screen_x = self.x - camera_x
        
        # Don't draw if off screen
        if screen_x + self.width < 0 or screen_x > WINDOW_WIDTH:
            return

        # Draw body
        if self.invulnerable == 0 or pygame.time.get_ticks() % 200 < 100:
            # Draw legs
            leg_time = (pygame.time.get_ticks() // 100) % 4
            if self.on_ground and self.dx != 0:
                leg_spread = 8
                if leg_time < 2:
                    # Left leg back, right leg forward
                    pygame.draw.line(screen, GREEN,
                                   (screen_x + self.width//2, self.y + self.height * 0.6),
                                   (screen_x + self.width//2 - leg_spread, self.y + self.height), 2)
                    pygame.draw.line(screen, GREEN,
                                   (screen_x + self.width//2, self.y + self.height * 0.6),
                                   (screen_x + self.width//2 + leg_spread, self.y + self.height - 5), 2)
                else:
                    # Left leg forward, right leg back
                    pygame.draw.line(screen, GREEN,
                                   (screen_x + self.width//2, self.y + self.height * 0.6),
                                   (screen_x + self.width//2 - leg_spread, self.y + self.height - 5), 2)
                    pygame.draw.line(screen, GREEN,
                                   (screen_x + self.width//2, self.y + self.height * 0.6),
                                   (screen_x + self.width//2 + leg_spread, self.y + self.height), 2)
            else:
                # Standing or jumping legs
                pygame.draw.line(screen, GREEN,
                               (screen_x + self.width//2 - 4, self.y + self.height * 0.6),
                               (screen_x + self.width//2 - 4, self.y + self.height), 2)
                pygame.draw.line(screen, GREEN,
                               (screen_x + self.width//2 + 4, self.y + self.height * 0.6),
                               (screen_x + self.width//2 + 4, self.y + self.height), 2)

            # Draw body (torso)
            pygame.draw.rect(screen, GREEN,
                           (screen_x + self.width * 0.2, self.y + self.height * 0.2,
                            self.width * 0.6, self.height * 0.4))
            
            # Draw head
            head_size = self.width * 0.8
            pygame.draw.circle(screen, GREEN,
                             (int(screen_x + self.width//2),
                              int(self.y + self.height * 0.2)),
                             int(head_size/2))
            
            # Draw face
            eye_x = screen_x + (self.width * 0.6 if self.facing_right else self.width * 0.4)
            pygame.draw.circle(screen, BLACK,
                             (int(eye_x),
                              int(self.y + self.height * 0.15)),
                             2)
            
            # Draw arms
            arm_y = self.y + self.height * 0.3
            if self.dx != 0 and self.on_ground:
                # Swinging arms while running
                arm_swing = math.sin(pygame.time.get_ticks() * 0.02) * 5
                pygame.draw.line(screen, GREEN,
                               (screen_x + self.width//2, arm_y),
                               (screen_x + self.width//2 - 8, arm_y + arm_swing), 2)
                pygame.draw.line(screen, GREEN,
                               (screen_x + self.width//2, arm_y),
                               (screen_x + self.width//2 + 8, arm_y - arm_swing), 2)
            else:
                # Normal arms
                pygame.draw.line(screen, GREEN,
                               (screen_x + self.width//2, arm_y),
                               (screen_x + self.width//2 - 8, arm_y + 5), 2)
                pygame.draw.line(screen, GREEN,
                               (screen_x + self.width//2, arm_y),
                               (screen_x + self.width//2 + 8, arm_y + 5), 2)

class Platform:
    def __init__(self, x, y, width):
        self.x = x
        self.y = y
        self.width = width
        self.height = PLATFORM_HEIGHT
        self.gems = []
        self.spikes = []
        self.generate_hazards()

    def generate_hazards(self):
        # Add gems
        for _ in range(GEMS_PER_PLATFORM):
            gem_x = random.randint(int(self.x + GEM_SIZE),
                                 int(self.x + self.width - GEM_SIZE))
            gem_y = self.y - GEM_SIZE - 10
            self.gems.append(Gem(gem_x, gem_y))

        # Add spikes - ensure they're not at the edges
        safe_edge = PLAYER_WIDTH * 1.5  # Safe zone at edges
        if self.width > safe_edge * 2 + SPIKE_WIDTH * 2:  # Only add spikes if platform is wide enough
            for _ in range(SPIKES_PER_PLATFORM):
                spike_x = random.randint(int(self.x + safe_edge),
                                      int(self.x + self.width - safe_edge - SPIKE_WIDTH))
                self.spikes.append(Spike(spike_x, self.y - SPIKE_HEIGHT))

    def draw(self, camera_x):
        screen_x = self.x - camera_x
        
        # Don't draw if off screen
        if screen_x + self.width < 0 or screen_x > WINDOW_WIDTH:
            return

        # Draw platform
        pygame.draw.rect(screen, BROWN, (screen_x, self.y, self.width, self.height))
        # Draw platform detail
        for i in range(0, self.width, 20):
            pygame.draw.line(screen, BLACK,
                           (screen_x + i, self.y),
                           (screen_x + i, self.y + self.height), 1)

        # Draw hazards
        for gem in self.gems:
            gem.draw(camera_x)
        for spike in self.spikes:
            spike.draw(camera_x)

class Gem:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = GEM_SIZE
        self.width = self.size  # Add width for collision detection
        self.height = self.size  # Add height for collision detection
        self.collected = False
        self.bob_offset = random.randint(0, 360)  # For floating animation

    def draw(self, camera_x):
        if self.collected:
            return
            
        screen_x = self.x - camera_x
        
        # Don't draw if off screen
        if screen_x + self.size < 0 or screen_x > WINDOW_WIDTH:
            return

        # Floating animation
        bob_y = math.sin((pygame.time.get_ticks() + self.bob_offset) * 0.005) * 5
        
        # Draw gem as a diamond
        points = [
            (screen_x + self.size//2, self.y + bob_y),  # Top
            (screen_x + self.size, self.y + self.size//2 + bob_y),  # Right
            (screen_x + self.size//2, self.y + self.size + bob_y),  # Bottom
            (screen_x, self.y + self.size//2 + bob_y),  # Left
        ]
        pygame.draw.polygon(screen, YELLOW, points)
        # Inner detail
        smaller_points = [
            (screen_x + self.size//2, self.y + 4 + bob_y),
            (screen_x + self.size - 4, self.y + self.size//2 + bob_y),
            (screen_x + self.size//2, self.y + self.size - 4 + bob_y),
            (screen_x + 4, self.y + self.size//2 + bob_y),
        ]
        pygame.draw.polygon(screen, BLACK, smaller_points)

class Spike:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = SPIKE_WIDTH
        self.height = SPIKE_HEIGHT

    def draw(self, camera_x):
        screen_x = self.x - camera_x
        
        # Don't draw if off screen
        if screen_x + self.width < 0 or screen_x > WINDOW_WIDTH:
            return

        # Draw spike as a triangle
        points = [
            (screen_x, self.y + self.height),  # Bottom left
            (screen_x + self.width//2, self.y),  # Top
            (screen_x + self.width, self.y + self.height),  # Bottom right
        ]
        pygame.draw.polygon(screen, RED, points)
        # Inner detail
        inner_points = [
            (screen_x + 4, self.y + self.height - 4),
            (screen_x + self.width//2, self.y + 4),
            (screen_x + self.width - 4, self.y + self.height - 4),
        ]
        pygame.draw.polygon(screen, BLACK, inner_points)

class Game:
    def __init__(self):
        self.reset()

    def find_safe_spawn_point(self):
        # Find the leftmost visible platform
        visible_platforms = [p for p in self.platforms 
                           if p.x + p.width > self.camera_x - 100 and p.x < self.camera_x + WINDOW_WIDTH]
        if not visible_platforms:
            return self.camera_x + 100, WINDOW_HEIGHT // 2
        
        # Choose the most suitable platform (prefer wider platforms)
        spawn_platform = max(visible_platforms, key=lambda p: p.width)
        
        # Find a safe spot (away from spikes)
        safe_edge = PLAYER_WIDTH * 1.5
        # Try middle of platform first
        spawn_x = spawn_platform.x + spawn_platform.width // 2
        
        # If middle is not safe (has spikes), try left side
        if any(abs(spike.x - spawn_x) < safe_edge for spike in spawn_platform.spikes):
            spawn_x = spawn_platform.x + safe_edge
        
        return spawn_x, spawn_platform.y - PLAYER_HEIGHT

    def reset(self):
        self.platforms = []
        self.camera_x = 0
        self.generate_initial_platforms()
        spawn_x, spawn_y = self.find_safe_spawn_point()
        self.player = Player(spawn_x, spawn_y)
        self.game_over = False
        self.distance = 0
        self.high_score = 0

    def generate_initial_platforms(self):
        # Starting platform
        self.platforms.append(Platform(0, WINDOW_HEIGHT - 100, 300))
        
        # Generate initial set of platforms
        last_x = 300
        for _ in range(10):
            last_x = self.generate_platform(last_x)

    def generate_platform(self, last_x):
        width = random.randint(MIN_PLATFORM_WIDTH, MAX_PLATFORM_WIDTH)
        
        # Calculate gap size
        actual_max_gap = min(MAX_GAP, MAX_JUMP_DISTANCE - width)
        gap = random.randint(MIN_GAP, max(MIN_GAP + 1, int(actual_max_gap)))
        x = last_x + gap
        
        # Get previous platform height
        prev_platform = self.platforms[-1]
        
        # Limit vertical difference based on jump height
        max_height_diff = PEAK_HEIGHT * 0.8  # 80% of maximum jump height
        min_y = max(WINDOW_HEIGHT - 200, prev_platform.y - max_height_diff)
        max_y = min(WINDOW_HEIGHT - 100, prev_platform.y + max_height_diff)
        y = random.randint(int(min_y), int(max_y))
        
        self.platforms.append(Platform(x, y, width))
        return x + width

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.player.jump()
                elif event.key == pygame.K_r and self.game_over:
                    self.reset()

        if not self.game_over:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                self.player.dx = -PLAYER_SPEED
                self.player.facing_right = False
            elif keys[pygame.K_RIGHT]:
                self.player.dx = PLAYER_SPEED
                self.player.facing_right = True
            else:
                self.player.dx = 0

    def update(self):
        if self.game_over:
            return

        # Update player
        self.player.move(self.platforms)
        
        # Update camera
        target_x = self.player.x - CAMERA_SLACK
        self.camera_x += (target_x - self.camera_x) * 0.1

        # Check if player fell
        if self.player.y > WINDOW_HEIGHT:
            self.player.lives -= 1
            if self.player.lives <= 0:
                self.game_over = True
                self.high_score = max(self.high_score, self.player.score)
            else:
                # Respawn player at safe location
                spawn_x, spawn_y = self.find_safe_spawn_point()
                self.player.x = spawn_x
                self.player.y = spawn_y
                self.player.dx = 0
                self.player.dy = 0
                self.player.invulnerable = 180  # 3 seconds

        # Update invulnerability
        if self.player.invulnerable > 0:
            self.player.invulnerable -= 1

        # Check gem collisions
        for platform in self.platforms:
            for gem in platform.gems:
                if not gem.collected and self.check_collision(self.player, gem):
                    gem.collected = True
                    self.player.score += GEM_POINTS

            # Check spike collisions
            if self.player.invulnerable <= 0:
                for spike in platform.spikes:
                    if self.check_collision(self.player, spike):
                        self.player.lives -= 1
                        if self.player.lives <= 0:
                            self.game_over = True
                            self.high_score = max(self.high_score, self.player.score)
                        else:
                            self.player.x = self.camera_x + 100
                            self.player.y = 0
                            self.player.dy = 0
                            self.player.invulnerable = 180  # 3 seconds

        # Generate new platforms
        rightmost_x = max(p.x + p.width for p in self.platforms)
        if rightmost_x - self.camera_x < WINDOW_WIDTH * 2:
            self.generate_platform(rightmost_x)

        # Remove old platforms
        self.platforms = [p for p in self.platforms if p.x + p.width > self.camera_x - 300]

        # Update distance
        self.distance = max(self.distance, int(self.player.x / 100))

    def check_collision(self, obj1, obj2):
        # Special case for gems since they're diamond-shaped
        if isinstance(obj2, Gem):
            # Use a smaller collision box for gems (70% of size)
            effective_size = obj2.size * 0.7
            return (obj1.x < obj2.x + effective_size and
                    obj1.x + obj1.width > obj2.x and
                    obj1.y < obj2.y + effective_size and
                    obj1.y + obj1.height > obj2.y)
        # Regular rectangle collision for other objects
        return (obj1.x < obj2.x + obj2.width and
                obj1.x + obj1.width > obj2.x and
                obj1.y < obj2.y + obj2.height and
                obj1.y + obj1.height > obj2.y)

    def draw(self):
        screen.fill(BLACK)
        
        # Draw platforms and hazards
        for platform in self.platforms:
            platform.draw(self.camera_x)

        # Draw player
        self.player.draw(self.camera_x)

        # Draw HUD
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Score: {self.player.score}", True, WHITE)
        lives_text = font.render(f"Lives: {self.player.lives}", True, WHITE)
        distance_text = font.render(f"Distance: {self.distance}m", True, WHITE)
        screen.blit(score_text, (10, 10))
        screen.blit(lives_text, (10, 50))
        screen.blit(distance_text, (WINDOW_WIDTH - 200, 10))

        # Draw game over
        if self.game_over:
            font = pygame.font.Font(None, 72)
            game_over_text = font.render("GAME OVER", True, RED)
            text_rect = game_over_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2))
            screen.blit(game_over_text, text_rect)
            
            font = pygame.font.Font(None, 36)
            score_text = font.render(f"Final Score: {self.player.score}", True, WHITE)
            high_score_text = font.render(f"High Score: {self.high_score}", True, WHITE)
            restart_text = font.render("Press R to restart", True, WHITE)
            
            screen.blit(score_text, 
                       score_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + 50)))
            screen.blit(high_score_text,
                       high_score_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + 90)))
            screen.blit(restart_text,
                       restart_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + 130)))

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