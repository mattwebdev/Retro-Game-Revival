# Lunar Lander
# Author: ZineGames
# Original Publication Date: 2024
# Description: A physics-based landing game with particle effects

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
YELLOW = (255, 255, 0)
GRAY = (128, 128, 128)

# Physics Settings
GRAVITY = 0.1
THRUST_POWER = 0.2
ROTATION_SPEED = 3
MAX_LANDING_SPEED = 3
MAX_LANDING_ANGLE = 20
WIND_FORCE = 0.02

# Particle Settings
PARTICLE_COUNT = 10
PARTICLE_LIFETIME = 30
PARTICLE_SPEED = 2

# Game Settings
INITIAL_FUEL = 1000
FUEL_CONSUMPTION = 1
STARTING_LIVES = 3

class Particle:
    def __init__(self, x, y, angle):
        self.x = x
        self.y = y
        speed = random.uniform(1, PARTICLE_SPEED)
        self.dx = speed * math.cos(math.radians(angle + random.uniform(-20, 20)))
        self.dy = speed * math.sin(math.radians(angle + random.uniform(-20, 20)))
        self.lifetime = random.randint(10, PARTICLE_LIFETIME)
        self.color = YELLOW

    def update(self):
        self.x += self.dx
        self.y += self.dy
        self.lifetime -= 1
        # Fade from yellow to red
        fade = self.lifetime / PARTICLE_LIFETIME
        self.color = (255, int(255 * fade), 0)

    def draw(self, screen):
        if self.lifetime > 0:
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), 2)

class LandingZone:
    def __init__(self, x, y, width, bonus):
        self.x = x
        self.y = y
        self.width = width
        self.height = 10
        self.bonus = bonus
        self.color = GREEN if bonus > 1 else BLUE

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        # Draw bonus multiplier
        if self.bonus > 1:
            font = pygame.font.Font(None, 24)
            text = font.render(f"{self.bonus}x", True, WHITE)
            screen.blit(text, (self.x + self.width//2 - 10, self.y - 20))

class Terrain:
    def __init__(self):
        self.points = []
        self.landing_zones = []
        self.generate()

    def generate(self):
        # Generate terrain points
        x = 0
        y = WINDOW_HEIGHT - 100
        self.points = [(0, WINDOW_HEIGHT)]  # Start at bottom left
        
        while x < WINDOW_WIDTH:
            if len(self.landing_zones) < 3 and random.random() < 0.2:
                # Create landing zone
                width = random.choice([40, 60, 80])
                bonus = 4 if width == 40 else (2 if width == 60 else 1)
                self.landing_zones.append(LandingZone(x, y, width, bonus))
                self.points.append((x, y))
                self.points.append((x + width, y))
                x += width
            else:
                x += random.randint(30, 70)
                y = min(max(y + random.randint(-50, 50), WINDOW_HEIGHT - 200), WINDOW_HEIGHT - 50)
                self.points.append((x, y))

        self.points.append((WINDOW_WIDTH, y))
        self.points.append((WINDOW_WIDTH, WINDOW_HEIGHT))

    def draw(self, screen):
        # Draw terrain
        pygame.draw.polygon(screen, GRAY, self.points)
        # Draw landing zones
        for zone in self.landing_zones:
            zone.draw(screen)

class Lander:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.dx = 0
        self.dy = 0
        self.angle = 0
        self.thrusting = False
        self.fuel = INITIAL_FUEL
        self.crashed = False
        self.landed = False
        self.particles = []
        self.width = 20
        self.height = 30

    def thrust(self):
        if self.fuel > 0 and not (self.crashed or self.landed):
            self.thrusting = True
            # Apply thrust force
            self.dx += THRUST_POWER * math.sin(math.radians(self.angle))
            self.dy -= THRUST_POWER * math.cos(math.radians(self.angle))
            self.fuel -= FUEL_CONSUMPTION
            # Create particles
            thrust_x = self.x + self.width//2 - 5 * math.sin(math.radians(self.angle))
            thrust_y = self.y + self.height//2 + 5 * math.cos(math.radians(self.angle))
            for _ in range(PARTICLE_COUNT):
                self.particles.append(Particle(thrust_x, thrust_y, self.angle + 180))
        else:
            self.thrusting = False

    def rotate(self, direction):
        if not (self.crashed or self.landed):
            self.angle = (self.angle + direction * ROTATION_SPEED) % 360

    def update(self, wind_direction):
        if self.crashed or self.landed:
            return

        # Apply gravity and wind
        self.dy += GRAVITY
        self.dx += WIND_FORCE * wind_direction
        
        # Update position
        self.x += self.dx
        self.y += self.dy

        # Update particles
        for particle in self.particles:
            particle.update()
        self.particles = [p for p in self.particles if p.lifetime > 0]

        # Screen boundaries
        self.x = max(0, min(self.x, WINDOW_WIDTH - self.width))

    def check_collision(self, terrain):
        if self.crashed or self.landed:
            return

        # Check landing zones
        for zone in terrain.landing_zones:
            if (self.x + self.width > zone.x and 
                self.x < zone.x + zone.width and 
                self.y + self.height > zone.y and 
                self.y + self.height < zone.y + zone.height + 5):
                
                # Check landing conditions
                speed = math.sqrt(self.dx * self.dx + self.dy * self.dy)
                if speed < MAX_LANDING_SPEED and abs(self.angle) < MAX_LANDING_ANGLE:
                    self.landed = True
                    self.dx = 0
                    self.dy = 0
                    self.y = zone.y - self.height
                    return zone.bonus
                else:
                    self.crashed = True
                    return 0

        # Check terrain collision
        lander_points = [(self.x + self.width//2, self.y + self.height)]
        for point in lander_points:
            for i in range(len(terrain.points) - 1):
                p1 = terrain.points[i]
                p2 = terrain.points[i + 1]
                if (point[0] > p1[0] and point[0] < p2[0] and 
                    point[1] > min(p1[1], p2[1])):
                    self.crashed = True
                    return 0
        return None

    def draw(self, screen):
        # Draw particles
        for particle in self.particles:
            particle.draw(screen)

        # Draw lander
        color = RED if self.crashed else (GREEN if self.landed else WHITE)
        
        # Calculate points for lander shape
        center_x = self.x + self.width//2
        center_y = self.y + self.height//2
        
        # Main body
        points = [
            (center_x - 10, center_y - 15),  # Top left
            (center_x + 10, center_y - 15),  # Top right
            (center_x + 15, center_y + 5),   # Bottom right
            (center_x - 15, center_y + 5),   # Bottom left
        ]
        
        # Rotate points
        rotated_points = []
        for px, py in points:
            dx = px - center_x
            dy = py - center_y
            rx = dx * math.cos(math.radians(self.angle)) - dy * math.sin(math.radians(self.angle))
            ry = dx * math.sin(math.radians(self.angle)) + dy * math.cos(math.radians(self.angle))
            rotated_points.append((rx + center_x, ry + center_y))
        
        # Draw lander body
        pygame.draw.polygon(screen, color, rotated_points)
        
        # Draw legs
        leg_points = [
            (center_x - 15, center_y + 5),   # Left leg top
            (center_x - 20, center_y + 15),  # Left leg bottom
            (center_x + 15, center_y + 5),   # Right leg top
            (center_x + 20, center_y + 15),  # Right leg bottom
        ]
        
        # Rotate legs
        rotated_legs = []
        for px, py in leg_points:
            dx = px - center_x
            dy = py - center_y
            rx = dx * math.cos(math.radians(self.angle)) - dy * math.sin(math.radians(self.angle))
            ry = dx * math.sin(math.radians(self.angle)) + dy * math.cos(math.radians(self.angle))
            rotated_legs.append((rx + center_x, ry + center_y))
        
        # Draw legs
        pygame.draw.line(screen, color, rotated_legs[0], rotated_legs[1], 2)
        pygame.draw.line(screen, color, rotated_legs[2], rotated_legs[3], 2)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Lunar Lander")
        self.clock = pygame.time.Clock()
        self.reset()

    def reset(self):
        self.terrain = Terrain()
        self.lander = Lander(WINDOW_WIDTH//2, 50)
        self.score = 0
        self.lives = STARTING_LIVES
        self.wind_direction = random.choice([-1, 1])
        self.game_over = False

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and (self.lander.crashed or self.lander.landed or self.game_over):
                    if self.lives > 0 or self.game_over:
                        self.reset()

        if not (self.lander.crashed or self.lander.landed or self.game_over):
            keys = pygame.key.get_pressed()
            if keys[pygame.K_UP]:
                self.lander.thrust()
            else:
                self.lander.thrusting = False
            if keys[pygame.K_LEFT]:
                self.lander.rotate(-1)
            if keys[pygame.K_RIGHT]:
                self.lander.rotate(1)

    def update(self):
        if not self.game_over:
            self.lander.update(self.wind_direction)
            result = self.lander.check_collision(self.terrain)
            
            if result is not None:  # Collision occurred
                if result > 0:  # Successful landing
                    self.score += 100 * result
                else:  # Crash
                    self.lives -= 1
                    if self.lives <= 0:
                        self.game_over = True

    def draw(self):
        self.screen.fill(BLACK)
        
        # Draw terrain and lander
        self.terrain.draw(self.screen)
        self.lander.draw(self.screen)
        
        # Draw HUD
        font = pygame.font.Font(None, 36)
        
        # Draw score
        score_text = font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))
        
        # Draw lives
        lives_text = font.render(f"Lives: {self.lives}", True, WHITE)
        self.screen.blit(lives_text, (10, 50))
        
        # Draw fuel
        fuel_text = font.render(f"Fuel: {max(0, self.lander.fuel)}", True, WHITE)
        self.screen.blit(fuel_text, (WINDOW_WIDTH - 150, 10))
        
        # Draw wind indicator
        wind_text = font.render("Wind →" if self.wind_direction > 0 else "← Wind", True, WHITE)
        self.screen.blit(wind_text, (WINDOW_WIDTH - 150, 50))
        
        # Draw velocity
        speed = math.sqrt(self.lander.dx * self.lander.dx + self.lander.dy * self.lander.dy)
        speed_color = GREEN if speed < MAX_LANDING_SPEED else (YELLOW if speed < MAX_LANDING_SPEED * 1.5 else RED)
        speed_text = font.render(f"Speed: {speed:.1f}", True, speed_color)
        self.screen.blit(speed_text, (WINDOW_WIDTH//2 - 50, 10))
        
        # Draw game over
        if self.game_over:
            font = pygame.font.Font(None, 72)
            game_over_text = font.render("GAME OVER", True, RED)
            text_rect = game_over_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2))
            self.screen.blit(game_over_text, text_rect)
            
            font = pygame.font.Font(None, 36)
            restart_text = font.render("Press R to restart", True, WHITE)
            restart_rect = restart_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + 50))
            self.screen.blit(restart_text, restart_rect)
        
        pygame.display.flip()

    def run(self):
        while True:
            self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(FPS)

def main():
    game = Game()
    game.run()

if __name__ == "__main__":
    main() 