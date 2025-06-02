# Enhanced Asteroids
# Author: ZineGames
# Original Publication Date: 2024
# Description: A vector-based space shooter with physics, particle effects, power-ups, and high scores

import pygame
import sys
import math
import random
import json
import os
from enum import Enum

# Initialize Pygame
pygame.init()
pygame.mixer.init()

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

# Ship Settings
SHIP_SIZE = 20
SHIP_SPEED = 0.5
ROTATION_SPEED = 5
FRICTION = 0.99
MAX_SPEED = 10
INVULNERABILITY_TIME = 180  # 3 seconds at 60 FPS

# Bullet Settings
BULLET_SPEED = 10
BULLET_LIFETIME = 60  # frames
MAX_BULLETS = 5
SPREAD_SHOT_ANGLE = 15  # degrees

# Asteroid Settings
ASTEROID_SPEEDS = [2, 3, 4]  # Speed for each size
ASTEROID_SIZES = [40, 20, 10]  # Large, medium, small
ASTEROID_POINTS = [20, 50, 100]  # Points for each size
INITIAL_ASTEROIDS = 4
ASTEROID_SPAWN_INTERVAL = 300  # frames
ASTEROID_SPEED_INCREASE = 0.1  # per wave

# Power-up Settings
POWERUP_TYPES = ['spread', 'shield', 'speed', 'life']
POWERUP_DURATION = 600  # 10 seconds at 60 FPS
POWERUP_SPAWN_CHANCE = 0.1  # 10% chance when asteroid is destroyed
POWERUP_SPEED = 2

# Particle Settings
PARTICLE_COUNT = 10
PARTICLE_LIFETIME = 20  # frames
PARTICLE_SPEED = 3
SCREEN_SHAKE_DURATION = 10  # frames
SCREEN_SHAKE_INTENSITY = 5

# Setup Display
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Enhanced Asteroids")
clock = pygame.time.Clock()

# Load or create high scores
def load_high_scores():
    try:
        with open('high_scores.json', 'r') as f:
            return json.load(f)
    except:
        return {'scores': []}

def save_high_score(score):
    scores = load_high_scores()
    scores['scores'].append(score)
    scores['scores'].sort(reverse=True)
    scores['scores'] = scores['scores'][:10]  # Keep top 10
    with open('high_scores.json', 'w') as f:
        json.dump(scores, f)

class PowerUpType(Enum):
    SPREAD = 'spread'
    SHIELD = 'shield'
    SPEED = 'speed'
    LIFE = 'life'

class GameObject:
    def __init__(self, x, y, size):
        self.x = x
        self.y = y
        self.dx = 0
        self.dy = 0
        self.size = size
        self.angle = 0
        self.shape = []
        self.active = True

    def move(self):
        self.x = (self.x + self.dx) % WINDOW_WIDTH
        self.y = (self.y + self.dy) % WINDOW_HEIGHT

    def get_vertices(self):
        vertices = []
        for point in self.shape:
            x = point[0]
            y = point[1]
            # Rotate
            rx = x * math.cos(math.radians(self.angle)) - y * math.sin(math.radians(self.angle))
            ry = x * math.sin(math.radians(self.angle)) + y * math.cos(math.radians(self.angle))
            # Translate
            vertices.append((rx + self.x, ry + self.y))
        return vertices

    def draw(self):
        if not self.active:
            return
        vertices = self.get_vertices()
        # Draw shape
        pygame.draw.lines(screen, WHITE, True, vertices, 2)

    def check_collision(self, other):
        if not (self.active and other.active):
            return False
        # Simple circle collision
        dx = self.x - other.x
        dy = self.y - other.y
        distance = math.sqrt(dx * dx + dy * dy)
        return distance < (self.size + other.size)

class Ship(GameObject):
    def __init__(self):
        super().__init__(WINDOW_WIDTH//2, WINDOW_HEIGHT//2, SHIP_SIZE)
        self.shape = [
            (0, -self.size),  # Nose
            (-self.size, self.size),  # Left
            (0, self.size/2),  # Back center
            (self.size, self.size),  # Right
        ]
        self.thrusting = False
        self.lives = 3
        self.invulnerable = 0
        self.powerups = {
            PowerUpType.SPREAD: 0,
            PowerUpType.SHIELD: 0,
            PowerUpType.SPEED: 0
        }
        self.base_speed = SHIP_SPEED

    def thrust(self):
        speed = self.base_speed * (1.5 if self.powerups[PowerUpType.SPEED] > 0 else 1.0)
        self.dx += speed * math.sin(math.radians(self.angle))
        self.dy -= speed * math.cos(math.radians(self.angle))
        # Limit speed
        current_speed = math.sqrt(self.dx * self.dx + self.dy * self.dy)
        if current_speed > MAX_SPEED:
            self.dx = (self.dx / current_speed) * MAX_SPEED
            self.dy = (self.dy / current_speed) * MAX_SPEED

    def rotate(self, direction):
        self.angle = (self.angle + direction * ROTATION_SPEED) % 360

    def move(self):
        super().move()
        # Apply friction
        self.dx *= FRICTION
        self.dy *= FRICTION
        if self.invulnerable > 0:
            self.invulnerable -= 1
        # Update powerup timers
        for powerup in self.powerups:
            if self.powerups[powerup] > 0:
                self.powerups[powerup] -= 1

    def draw(self):
        if not self.active or (self.invulnerable > 0 and pygame.time.get_ticks() % 200 < 100):
            return
        super().draw()
        # Draw thrust
        if self.thrusting:
            thrust_points = [
                (-self.size/2, self.size),  # Left
                (0, self.size * 1.5),  # Tip
                (self.size/2, self.size),  # Right
            ]
            vertices = []
            for point in thrust_points:
                x = point[0]
                y = point[1]
                rx = x * math.cos(math.radians(self.angle)) - y * math.sin(math.radians(self.angle))
                ry = x * math.sin(math.radians(self.angle)) + y * math.cos(math.radians(self.angle))
                vertices.append((rx + self.x, ry + self.y))
            pygame.draw.lines(screen, RED, True, vertices, 2)
        
        # Draw shield if active
        if self.powerups[PowerUpType.SHIELD] > 0:
            pygame.draw.circle(screen, BLUE, (int(self.x), int(self.y)), self.size * 1.5, 2)

class Bullet(GameObject):
    def __init__(self, x, y, angle):
        super().__init__(x, y, 2)
        self.dx = BULLET_SPEED * math.sin(math.radians(angle))
        self.dy = -BULLET_SPEED * math.cos(math.radians(angle))
        self.lifetime = BULLET_LIFETIME
        self.shape = [(-1, -1), (1, -1), (1, 1), (-1, 1)]

    def move(self):
        super().move()
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.active = False

class Asteroid(GameObject):
    def __init__(self, x, y, size_index, speed_multiplier=1.0):
        size = ASTEROID_SIZES[size_index]
        super().__init__(x, y, size)
        self.size_index = size_index
        self.points = ASTEROID_POINTS[size_index]
        # Create irregular polygon shape
        self.shape = []
        num_vertices = random.randint(8, 12)
        for i in range(num_vertices):
            angle = (i / num_vertices) * 2 * math.pi
            radius = size * random.uniform(0.8, 1.2)
            self.shape.append((
                radius * math.cos(angle),
                radius * math.sin(angle)
            ))
        # Random movement
        speed = ASTEROID_SPEEDS[size_index] * speed_multiplier
        angle = random.uniform(0, 2 * math.pi)
        self.dx = speed * math.cos(angle)
        self.dy = speed * math.sin(angle)
        self.rotation_speed = random.uniform(-3, 3)

    def move(self):
        super().move()
        self.angle = (self.angle + self.rotation_speed) % 360

class PowerUp(GameObject):
    def __init__(self, x, y, powerup_type):
        super().__init__(x, y, 10)
        self.powerup_type = powerup_type
        self.lifetime = POWERUP_DURATION
        # Create diamond shape
        self.shape = [
            (0, -self.size),  # Top
            (self.size, 0),   # Right
            (0, self.size),   # Bottom
            (-self.size, 0),  # Left
        ]
        # Random movement
        angle = random.uniform(0, 2 * math.pi)
        self.dx = POWERUP_SPEED * math.cos(angle)
        self.dy = POWERUP_SPEED * math.sin(angle)

    def move(self):
        super().move()
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.active = False

    def draw(self):
        if not self.active:
            return
        vertices = self.get_vertices()
        color = {
            PowerUpType.SPREAD: YELLOW,
            PowerUpType.SHIELD: BLUE,
            PowerUpType.SPEED: GREEN,
            PowerUpType.LIFE: RED
        }[self.powerup_type]
        pygame.draw.lines(screen, color, True, vertices, 2)

class Particle(GameObject):
    def __init__(self, x, y, angle, color=WHITE):
        super().__init__(x, y, 1)
        speed = random.uniform(1, PARTICLE_SPEED)
        self.dx = speed * math.cos(math.radians(angle))
        self.dy = speed * math.sin(math.radians(angle))
        self.lifetime = random.randint(10, PARTICLE_LIFETIME)
        self.shape = [(-1, -1), (1, -1), (1, 1), (-1, 1)]
        self.color = color

    def move(self):
        super().move()
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.active = False

    def draw(self):
        if not self.active:
            return
        vertices = self.get_vertices()
        pygame.draw.lines(screen, self.color, True, vertices, 1)

class Game:
    def __init__(self):
        self.reset_game()

    def reset_game(self):
        self.ship = Ship()
        self.bullets = []
        self.asteroids = []
        self.powerups = []
        self.particles = []
        self.score = 0
        self.wave = 1
        self.game_over = False
        self.screen_shake = 0
        self.spawn_asteroids(INITIAL_ASTEROIDS)
        self.show_high_scores = False

    def spawn_asteroids(self, count):
        speed_multiplier = 1.0 + (self.wave - 1) * ASTEROID_SPEED_INCREASE
        for _ in range(count):
            # Spawn away from the ship
            while True:
                x = random.randint(0, WINDOW_WIDTH)
                y = random.randint(0, WINDOW_HEIGHT)
                if math.sqrt((x - self.ship.x)**2 + (y - self.ship.y)**2) > 200:
                    break
            self.asteroids.append(Asteroid(x, y, 0, speed_multiplier))

    def create_particles(self, x, y, count, color=WHITE):
        for _ in range(count):
            angle = random.uniform(0, 360)
            self.particles.append(Particle(x, y, angle, color))

    def apply_screen_shake(self):
        self.screen_shake = SCREEN_SHAKE_DURATION

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if not self.game_over:
                        # Create bullet(s) at ship's nose
                        nose_x = self.ship.x + SHIP_SIZE * math.sin(math.radians(self.ship.angle))
                        nose_y = self.ship.y - SHIP_SIZE * math.cos(math.radians(self.ship.angle))
                        if self.ship.powerups[PowerUpType.SPREAD] > 0:
                            # Create spread shot
                            for angle_offset in [-SPREAD_SHOT_ANGLE, 0, SPREAD_SHOT_ANGLE]:
                                self.bullets.append(Bullet(nose_x, nose_y, self.ship.angle + angle_offset))
                        else:
                            self.bullets.append(Bullet(nose_x, nose_y, self.ship.angle))
                elif event.key == pygame.K_r and self.game_over:
                    self.reset_game()
                elif event.key == pygame.K_h:
                    self.show_high_scores = not self.show_high_scores

        if not self.game_over:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                self.ship.rotate(-1)
            if keys[pygame.K_RIGHT]:
                self.ship.rotate(1)
            self.ship.thrusting = keys[pygame.K_UP]
            if self.ship.thrusting:
                self.ship.thrust()

    def update(self):
        if self.game_over:
            return

        # Update positions
        self.ship.move()
        for bullet in self.bullets:
            bullet.move()
        for asteroid in self.asteroids:
            asteroid.move()
        for powerup in self.powerups:
            powerup.move()
        for particle in self.particles:
            particle.move()

        # Remove inactive objects
        self.bullets = [b for b in self.bullets if b.active]
        self.asteroids = [a for a in self.asteroids if a.active]
        self.powerups = [p for p in self.powerups if p.active]
        self.particles = [p for p in self.particles if p.active]

        # Check bullet-asteroid collisions
        for bullet in self.bullets:
            for asteroid in self.asteroids:
                if bullet.check_collision(asteroid):
                    bullet.active = False
                    asteroid.active = False
                    self.score += asteroid.points
                    self.create_particles(asteroid.x, asteroid.y, PARTICLE_COUNT)
                    self.apply_screen_shake()
                    
                    # Chance to spawn powerup
                    if random.random() < POWERUP_SPAWN_CHANCE:
                        powerup_type = random.choice(POWERUP_TYPES)
                        self.powerups.append(PowerUp(asteroid.x, asteroid.y, PowerUpType(powerup_type)))
                    
                    # Split asteroid if not smallest size
                    if asteroid.size_index < len(ASTEROID_SIZES) - 1:
                        for _ in range(2):
                            new_asteroid = Asteroid(
                                asteroid.x, asteroid.y, asteroid.size_index + 1)
                            self.asteroids.append(new_asteroid)

        # Check ship-asteroid collisions
        if self.ship.invulnerable <= 0 and not self.ship.powerups[PowerUpType.SHIELD]:
            for asteroid in self.asteroids:
                if self.ship.check_collision(asteroid):
                    self.ship.lives -= 1
                    self.create_particles(self.ship.x, self.ship.y, PARTICLE_COUNT * 2, RED)
                    self.apply_screen_shake()
                    if self.ship.lives <= 0:
                        self.game_over = True
                        save_high_score(self.score)
                    else:
                        self.ship.x = WINDOW_WIDTH // 2
                        self.ship.y = WINDOW_HEIGHT // 2
                        self.ship.dx = 0
                        self.ship.dy = 0
                        self.ship.angle = 0
                        self.ship.invulnerable = INVULNERABILITY_TIME

        # Check ship-powerup collisions
        for powerup in self.powerups:
            if self.ship.check_collision(powerup):
                powerup.active = False
                if powerup.powerup_type == PowerUpType.LIFE:
                    self.ship.lives += 1
                else:
                    self.ship.powerups[powerup.powerup_type] = POWERUP_DURATION
                self.create_particles(powerup.x, powerup.y, PARTICLE_COUNT, GREEN)

        # Spawn new wave if no asteroids
        if not self.asteroids:
            self.wave += 1
            self.spawn_asteroids(INITIAL_ASTEROIDS + self.wave - 1)

        # Update screen shake
        if self.screen_shake > 0:
            self.screen_shake -= 1

    def draw(self):
        # Apply screen shake
        shake_offset = (0, 0)
        if self.screen_shake > 0:
            shake_offset = (
                random.randint(-SCREEN_SHAKE_INTENSITY, SCREEN_SHAKE_INTENSITY),
                random.randint(-SCREEN_SHAKE_INTENSITY, SCREEN_SHAKE_INTENSITY)
            )

        screen.fill(BLACK)
        
        # Draw game objects with shake offset
        screen.blit(screen, shake_offset)
        
        # Draw game objects
        self.ship.draw()
        for bullet in self.bullets:
            bullet.draw()
        for asteroid in self.asteroids:
            asteroid.draw()
        for powerup in self.powerups:
            powerup.draw()
        for particle in self.particles:
            particle.draw()

        # Draw HUD
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Score: {self.score}", True, WHITE)
        lives_text = font.render(f"Lives: {self.ship.lives}", True, WHITE)
        wave_text = font.render(f"Wave: {self.wave}", True, WHITE)
        screen.blit(score_text, (10, 10))
        screen.blit(lives_text, (WINDOW_WIDTH - 100, 10))
        screen.blit(wave_text, (WINDOW_WIDTH - 100, 50))

        # Draw powerup indicators
        y_offset = 90
        for powerup, duration in self.ship.powerups.items():
            if duration > 0:
                color = {
                    PowerUpType.SPREAD: YELLOW,
                    PowerUpType.SHIELD: BLUE,
                    PowerUpType.SPEED: GREEN
                }[powerup]
                powerup_text = font.render(f"{powerup.value}: {duration//60}s", True, color)
                screen.blit(powerup_text, (WINDOW_WIDTH - 150, y_offset))
                y_offset += 30

        # Draw game over
        if self.game_over:
            font = pygame.font.Font(None, 72)
            game_over_text = font.render("GAME OVER", True, RED)
            text_rect = game_over_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2))
            screen.blit(game_over_text, text_rect)
            
            font = pygame.font.Font(None, 36)
            restart_text = font.render("Press R to restart", True, WHITE)
            restart_rect = restart_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + 50))
            screen.blit(restart_text, restart_rect)

        # Draw high scores
        if self.show_high_scores:
            scores = load_high_scores()
            font = pygame.font.Font(None, 36)
            title_text = font.render("High Scores", True, WHITE)
            screen.blit(title_text, (WINDOW_WIDTH//2 - 100, 100))
            for i, score in enumerate(scores['scores']):
                score_text = font.render(f"{i+1}. {score}", True, WHITE)
                screen.blit(score_text, (WINDOW_WIDTH//2 - 100, 150 + i*30))

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