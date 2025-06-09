
import pygame
import math
import random

# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
CITY_COUNT = 6
MISSILE_BASES = 3
MISSILES_PER_BASE = 10
ENEMY_MISSILE_SPEED = 3
PLAYER_MISSILE_SPEED = 5
EXPLOSION_RADIUS = 30
EXPLOSION_DURATION = 30

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

class City:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 40
        self.height = 20
        self.destroyed = False

    def draw(self, screen):
        if not self.destroyed:
            # Draw city base
            pygame.draw.rect(screen, GREEN, (self.x, self.y, self.width, self.height))
            # Draw city buildings
            building_width = 8
            building_height = 15
            for i in range(3):
                building_x = self.x + 5 + i * 12
                pygame.draw.rect(screen, (0, 200, 0), 
                               (building_x, self.y - building_height, 
                                building_width, building_height))
            # Draw windows
            for i in range(3):
                building_x = self.x + 5 + i * 12
                for j in range(2):
                    window_x = building_x + 2
                    window_y = self.y - building_height + 5 + j * 5
                    pygame.draw.rect(screen, YELLOW, 
                                   (window_x, window_y, 4, 3))

class MissileBase:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 30
        self.height = 15
        self.missiles_left = MISSILES_PER_BASE
        self.destroyed = False
        self.out_of_missiles = False  # New flag for tracking missile status

    def draw(self, screen):
        if not self.destroyed:
            # Draw base platform
            pygame.draw.rect(screen, BLUE, (self.x, self.y, self.width, self.height))
            # Draw control tower
            tower_width = 10
            tower_height = 20
            tower_x = self.x + self.width // 2 - tower_width // 2
            pygame.draw.rect(screen, (0, 0, 200), 
                           (tower_x, self.y - tower_height, 
                            tower_width, tower_height))
            # Draw radar dish
            pygame.draw.circle(screen, (100, 100, 100), 
                             (tower_x + tower_width // 2, self.y - tower_height), 5)
            
            # Draw missiles left
            for i in range(self.missiles_left):
                missile_x = self.x + 5 + i * 3
                # Draw missile body
                pygame.draw.line(screen, YELLOW,
                               (missile_x, self.y - 5),
                               (missile_x, self.y - 15), 2)
                # Draw missile tip
                pygame.draw.polygon(screen, RED, [
                    (missile_x, self.y - 15),
                    (missile_x - 2, self.y - 18),
                    (missile_x + 2, self.y - 18)
                ])
            
            # Draw "OUT OF MISSILES" text if no missiles left
            if self.missiles_left == 0 and not self.out_of_missiles:
                self.out_of_missiles = True
                font = pygame.font.Font(None, 20)
                text = font.render("OUT", True, RED)
                text_rect = text.get_rect(center=(self.x + self.width//2, self.y - 25))
                screen.blit(text, text_rect)

class Missile:
    def __init__(self, x, y, target_x, target_y, is_enemy=False):
        self.x = x
        self.y = y
        self.target_x = target_x
        self.target_y = target_y
        self.is_enemy = is_enemy
        self.speed = ENEMY_MISSILE_SPEED if is_enemy else PLAYER_MISSILE_SPEED
        self.active = True
        self.exploded = False
        self.explosion_timer = 0
        self.trail_points = []  # Store trail points
        
        # Calculate direction
        dx = target_x - x
        dy = target_y - y
        distance = math.sqrt(dx * dx + dy * dy)
        self.dx = (dx / distance) * self.speed
        self.dy = (dy / distance) * self.speed

    def update(self):
        if not self.active:
            return

        if self.exploded:
            self.explosion_timer += 1
            if self.explosion_timer >= EXPLOSION_DURATION:
                self.active = False
            return

        # Update trail
        self.trail_points.append((self.x, self.y))
        if len(self.trail_points) > 10:  # Limit trail length
            self.trail_points.pop(0)

        self.x += self.dx
        self.y += self.dy

        # Check if missile reached target
        if (abs(self.x - self.target_x) < self.speed and 
            abs(self.y - self.target_y) < self.speed):
            self.explode()

    def explode(self):
        self.exploded = True
        self.explosion_timer = 0

    def draw(self, screen):
        if not self.active:
            return

        if self.exploded:
            # Draw explosion
            radius = EXPLOSION_RADIUS * (1 - self.explosion_timer / EXPLOSION_DURATION)
            # Draw multiple circles for better explosion effect
            for i in range(3):
                r = radius * (1 - i * 0.2)
                alpha = 255 * (1 - i * 0.3)
                color = (255, 200, 0, int(alpha))
                surf = pygame.Surface((int(r * 2), int(r * 2)), pygame.SRCALPHA)
                pygame.draw.circle(surf, color, (int(r), int(r)), int(r))
                screen.blit(surf, (int(self.x - r), int(self.y - r)))
        else:
            # Draw trail
            if len(self.trail_points) > 1:
                for i in range(len(self.trail_points) - 1):
                    alpha = int(255 * (i / len(self.trail_points)))
                    color = (255, 255, 255, alpha) if not self.is_enemy else (255, 0, 0, alpha)
                    surf = pygame.Surface((2, 2), pygame.SRCALPHA)
                    pygame.draw.line(surf, color, (0, 0), (1, 1), 1)
                    screen.blit(surf, self.trail_points[i])

            # Draw missile
            color = RED if self.is_enemy else WHITE
            # Draw missile body
            pygame.draw.line(screen, color, (int(self.x), int(self.y)),
                           (int(self.x - self.dx), int(self.y - self.dy)), 2)
            # Draw missile tip
            tip_length = 5
            tip_angle = math.atan2(self.dy, self.dx)
            tip_x = self.x - self.dx
            tip_y = self.y - self.dy
            pygame.draw.polygon(screen, color, [
                (tip_x, tip_y),
                (tip_x - tip_length * math.cos(tip_angle + math.pi/4),
                 tip_y - tip_length * math.sin(tip_angle + math.pi/4)),
                (tip_x - tip_length * math.cos(tip_angle - math.pi/4),
                 tip_y - tip_length * math.sin(tip_angle - math.pi/4))
            ])

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Missile Command")
        self.clock = pygame.time.Clock()
        self.running = True
        self.score = 0
        self.level = 1
        self.game_over = False
        
        # Initialize cities
        self.cities = []
        city_spacing = WINDOW_WIDTH // (CITY_COUNT + 1)
        for i in range(CITY_COUNT):
            x = city_spacing * (i + 1) - 20
            y = WINDOW_HEIGHT - 50
            self.cities.append(City(x, y))
        
        # Initialize missile bases
        self.missile_bases = []
        base_spacing = WINDOW_WIDTH // (MISSILE_BASES + 1)
        for i in range(MISSILE_BASES):
            x = base_spacing * (i + 1) - 15
            y = WINDOW_HEIGHT - 30
            self.missile_bases.append(MissileBase(x, y))
        
        # Initialize missiles
        self.player_missiles = []
        self.enemy_missiles = []
        
        # Enemy missile spawn timer
        self.enemy_spawn_timer = 0
        self.enemy_spawn_delay = 60  # Frames between enemy missile spawns
        
        # Font for score display
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)

    def get_total_missiles_left(self):
        return sum(base.missiles_left for base in self.missile_bases if not base.destroyed)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and not self.game_over:
                # Check if any base has missiles left
                if self.get_total_missiles_left() > 0:
                    # Find closest active base
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    closest_base = None
                    min_distance = float('inf')
                    
                    for base in self.missile_bases:
                        if not base.destroyed and base.missiles_left > 0:
                            distance = abs(base.x - mouse_x)
                            if distance < min_distance:
                                min_distance = distance
                                closest_base = base
                    
                    if closest_base:
                        closest_base.missiles_left -= 1
                        self.player_missiles.append(Missile(
                            closest_base.x + closest_base.width // 2,
                            closest_base.y,
                            mouse_x, mouse_y
                        ))
                else:
                    # No missiles left, game over
                    self.game_over = True

    def update(self):
        if self.game_over:
            return

        # Update player missiles
        for missile in self.player_missiles[:]:
            missile.update()
            if not missile.active:
                self.player_missiles.remove(missile)

        # Update enemy missiles
        for missile in self.enemy_missiles[:]:
            missile.update()
            if not missile.active:
                self.enemy_missiles.remove(missile)

        # Spawn enemy missiles
        self.enemy_spawn_timer += 1
        if self.enemy_spawn_timer >= self.enemy_spawn_delay:
            self.enemy_spawn_timer = 0
            target_x = random.randint(0, WINDOW_WIDTH)
            self.enemy_missiles.append(Missile(
                random.randint(0, WINDOW_WIDTH),
                0,
                target_x,
                WINDOW_HEIGHT,
                True
            ))

        # Check collisions
        for missile in self.player_missiles[:]:
            if missile.exploded:
                for enemy_missile in self.enemy_missiles[:]:
                    if not enemy_missile.exploded:
                        distance = math.sqrt(
                            (missile.x - enemy_missile.x) ** 2 +
                            (missile.y - enemy_missile.y) ** 2
                        )
                        if distance < EXPLOSION_RADIUS:
                            enemy_missile.explode()
                            self.score += 100

        for missile in self.enemy_missiles[:]:
            if missile.exploded:
                # Check collision with cities
                for city in self.cities:
                    if not city.destroyed:
                        if (abs(missile.x - (city.x + city.width/2)) < city.width/2 and
                            abs(missile.y - (city.y + city.height/2)) < city.height/2):
                            city.destroyed = True
                
                # Check collision with missile bases
                for base in self.missile_bases:
                    if not base.destroyed:
                        if (abs(missile.x - (base.x + base.width/2)) < base.width/2 and
                            abs(missile.y - (base.y + base.height/2)) < base.height/2):
                            base.destroyed = True

        # Check game over conditions
        if self.get_total_missiles_left() == 0:
            self.game_over = True

    def draw(self):
        self.screen.fill(BLACK)
        
        # Draw stars in background
        for _ in range(50):
            x = random.randint(0, WINDOW_WIDTH)
            y = random.randint(0, WINDOW_HEIGHT)
            pygame.draw.circle(self.screen, WHITE, (x, y), 1)
        
        # Draw cities
        for city in self.cities:
            city.draw(self.screen)
        
        # Draw missile bases
        for base in self.missile_bases:
            base.draw(self.screen)
        
        # Draw missiles
        for missile in self.player_missiles:
            missile.draw(self.screen)
        for missile in self.enemy_missiles:
            missile.draw(self.screen)
        
        # Draw score and missiles left
        score_text = self.font.render(f'Score: {self.score}', True, WHITE)
        self.screen.blit(score_text, (10, 10))
        
        missiles_left = self.get_total_missiles_left()
        missiles_text = self.small_font.render(f'Missiles: {missiles_left}', True, YELLOW)
        self.screen.blit(missiles_text, (10, 50))
        
        # Draw game over
        if self.game_over:
            game_over_text = self.font.render('GAME OVER', True, RED)
            text_rect = game_over_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
            self.screen.blit(game_over_text, text_rect)
            
            # Show reason for game over
            if missiles_left == 0:
                reason_text = self.small_font.render('Out of Missiles!', True, YELLOW)
                reason_rect = reason_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 40))
                self.screen.blit(reason_text, reason_rect)
        
        pygame.display.flip()

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)

if __name__ == "__main__":
    game = Game()
    game.run()
    pygame.quit() 