import pygame
import math
import random
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional

pygame.init()

# Constants
WINDOW_WIDTH, WINDOW_HEIGHT = 800, 600
FPS = 60
BLACK, WHITE, YELLOW, RED, GREEN = (0, 0, 0), (255, 255, 255), (255, 255, 0), (255, 0, 0), (0, 255, 0)

# Game settings
SHIP_SPEED, ROTATION_SPEED, THRUST_POWER = 0.5, 3, 0.1
GRAVITY, TORPEDO_SPEED = 0.01, 5
TORPEDO_LIFETIME, HYPESPACE_COOLDOWN = 60, 180
VELOCITY_DAMPING, MAX_VELOCITY = 0.98, 5
SHIP_RADIUS, TORPEDO_RADIUS = 15, 3
HIT_FLASH_DURATION, POINTS_TO_WIN, COUNTDOWN_TIME = 10, 5, 3
STAR_RADIUS = 10
STAR_DANGER_RADIUS = 50  # Distance at which ships start getting warning
STAR_KILL_RADIUS = 25    # Distance at which ships are destroyed

AI_DIFFICULTY = {
    'easy': {'reaction_time': 30, 'accuracy': 0.7},
    'medium': {'reaction_time': 20, 'accuracy': 0.85},
    'hard': {'reaction_time': 10, 'accuracy': 0.95}
}

@dataclass
class Controls:
    rotate_left: int
    rotate_right: int
    thrust: int
    fire: int
    hyperspace: int

@dataclass
class Torpedo:
    x: float
    y: float
    dx: float
    dy: float
    lifetime: int

class Ship:
    def __init__(self, x: float, y: float, color: Tuple[int, int, int], 
                 controls: Controls, is_ai: bool = False, ai_difficulty: str = 'medium'):
        self.x, self.y = x, y
        self.dx = self.dy = 0
        self.angle = 0
        self.color, self.controls = color, controls
        self.score = 0
        self.hyperspace_cooldown = 0
        self.torpedoes: List[Torpedo] = []
        self.thrusting = False
        self.is_ai = is_ai
        self.ai_difficulty = ai_difficulty
        self.ai_decision_timer = 0
        self.ai_target_angle = 0
        self.ai_thrusting = False
        self.ai_firing = False
        self.hit_flash = 0
        self.star_warning = 0  # Counter for star warning flash
        self.dead = False      # Flag for ship destruction

    def rotate(self, clockwise: bool = True) -> None:
        self.angle += ROTATION_SPEED * (1 if clockwise else -1)

    def thrust(self) -> None:
        self.thrusting = True
        self.dx += math.cos(math.radians(self.angle)) * THRUST_POWER
        self.dy -= math.sin(math.radians(self.angle)) * THRUST_POWER

    def fire_torpedo(self) -> None:
        if len(self.torpedoes) < 4:
            self.torpedoes.append(Torpedo(
                self.x, self.y,
                self.dx + math.cos(math.radians(self.angle)) * TORPEDO_SPEED,
                self.dy - math.sin(math.radians(self.angle)) * TORPEDO_SPEED,
                TORPEDO_LIFETIME
            ))

    def hyperspace(self) -> None:
        if self.hyperspace_cooldown <= 0:
            self.x = random.randint(50, WINDOW_WIDTH - 50)
            self.y = random.randint(50, WINDOW_HEIGHT - 50)
            self.dx = self.dy = 0
            self.hyperspace_cooldown = HYPESPACE_COOLDOWN

    def ai_update(self, player_ship: 'Ship', star_x: float, star_y: float) -> None:
        if self.ai_decision_timer <= 0:
            dx, dy = player_ship.x - self.x, player_ship.y - self.y
            target_angle = math.degrees(math.atan2(-dy, dx))
            accuracy = AI_DIFFICULTY[self.ai_difficulty]['accuracy']
            
            self.ai_target_angle = target_angle + random.uniform(-30 * (1 - accuracy), 30 * (1 - accuracy))
            distance = math.sqrt(dx * dx + dy * dy)
            self.ai_thrusting = distance > 100 and random.random() < accuracy
            self.ai_firing = abs((self.angle - self.ai_target_angle) % 360) < 20 and distance < 300 and random.random() < accuracy
            
            if self.hyperspace_cooldown <= 0:
                star_dx, star_dy = star_x - self.x, star_y - self.y
                if math.sqrt(star_dx * star_dx + star_dy * star_dy) < 50 and random.random() < accuracy:
                    self.hyperspace()
            
            self.ai_decision_timer = AI_DIFFICULTY[self.ai_difficulty]['reaction_time']
        else:
            self.ai_decision_timer -= 1
        
        if self.ai_thrusting: self.thrust()
        if self.ai_firing: self.fire_torpedo()
        
        angle_diff = (self.ai_target_angle - self.angle) % 360
        self.rotate(angle_diff <= 180)

    def update(self, star_x: float, star_y: float, player_ship: Optional['Ship'] = None) -> None:
        if self.dead:
            return

        if self.is_ai and player_ship:
            self.ai_update(player_ship, star_x, star_y)
        
        dx, dy = star_x - self.x, star_y - self.y
        distance = math.sqrt(dx * dx + dy * dy)
        
        # Check for star collision
        if distance < STAR_KILL_RADIUS:
            self.dead = True
            return
        
        # Update star warning
        self.star_warning = max(0, self.star_warning - 1)
        if distance < STAR_DANGER_RADIUS:
            self.star_warning = 5  # Keep warning visible for 5 frames
        
        if distance > 0:
            self.dx += (dx / distance) * GRAVITY
            self.dy += (dy / distance) * GRAVITY
        
        self.dx *= VELOCITY_DAMPING
        self.dy *= VELOCITY_DAMPING
        
        current_speed = math.sqrt(self.dx * self.dx + self.dy * self.dy)
        if current_speed > MAX_VELOCITY:
            self.dx = (self.dx / current_speed) * MAX_VELOCITY
            self.dy = (self.dy / current_speed) * MAX_VELOCITY
        
        self.x = (self.x + self.dx) % WINDOW_WIDTH
        self.y = (self.y + self.dy) % WINDOW_HEIGHT
        
        self.torpedoes = [t for t in self.torpedoes if t.lifetime > 0]
        for t in self.torpedoes:
            t.x = (t.x + t.dx) % WINDOW_WIDTH
            t.y = (t.y + t.dy) % WINDOW_HEIGHT
            t.lifetime -= 1
        
        if self.hyperspace_cooldown > 0:
            self.hyperspace_cooldown -= 1
        if self.hit_flash > 0:
            self.hit_flash -= 1

    def draw(self, screen: pygame.Surface) -> None:
        if self.dead:
            return

        # Draw star warning if active
        if self.star_warning > 0:
            pygame.draw.circle(screen, YELLOW, (int(self.x), int(self.y)), SHIP_RADIUS + 5, 2)
        
        points = [
            (self.x + math.cos(math.radians(self.angle)) * 20,
             self.y - math.sin(math.radians(self.angle)) * 20),
            (self.x + math.cos(math.radians(self.angle + 150)) * 10,
             self.y - math.sin(math.radians(self.angle + 150)) * 10),
            (self.x + math.cos(math.radians(self.angle - 150)) * 10,
             self.y - math.sin(math.radians(self.angle - 150)) * 10)
        ]
        pygame.draw.polygon(screen, self.color, points)
        
        if self.thrusting:
            thrust_points = [
                (self.x + math.cos(math.radians(self.angle + 150)) * 10,
                 self.y - math.sin(math.radians(self.angle + 150)) * 10),
                (self.x + math.cos(math.radians(self.angle)) * -10,
                 self.y - math.sin(math.radians(self.angle)) * -10),
                (self.x + math.cos(math.radians(self.angle - 150)) * 10,
                 self.y - math.sin(math.radians(self.angle - 150)) * 10)
            ]
            pygame.draw.polygon(screen, YELLOW, thrust_points)
            self.thrusting = False
        
        for t in self.torpedoes:
            pygame.draw.circle(screen, self.color, (int(t.x), int(t.y)), TORPEDO_RADIUS)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Space War")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.title_font = pygame.font.Font(None, 72)
        self.countdown_font = pygame.font.Font(None, 150)
        
        self.in_menu = True
        self.game_mode = None
        self.ai_difficulty = 'medium'
        self.selected_option = 0
        self.game_over = False
        self.winner = None
        self.in_countdown = False
        self.countdown_start = 0
        
        self.reset_game()

    def reset_game(self) -> None:
        self.ship1 = Ship(WINDOW_WIDTH//4, WINDOW_HEIGHT//2, GREEN,
                         Controls(pygame.K_a, pygame.K_d, pygame.K_w, pygame.K_SPACE, pygame.K_h))
        
        self.ship2 = Ship(3*WINDOW_WIDTH//4, WINDOW_HEIGHT//2, RED,
                         Controls(pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_RETURN, pygame.K_RSHIFT),
                         is_ai=(self.game_mode == '1player'),
                         ai_difficulty=self.ai_difficulty)
        
        self.star_x, self.star_y = WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2
        self.game_over = False
        self.winner = None
        self.ship1.dead = False
        self.ship2.dead = False

    def start_countdown(self) -> None:
        self.in_countdown = True
        self.countdown_start = pygame.time.get_ticks()
        self.reset_game()

    def draw_menu(self) -> None:
        self.screen.fill(BLACK)
        title = self.title_font.render("SPACE WAR", True, WHITE)
        self.screen.blit(title, title.get_rect(center=(WINDOW_WIDTH//2, 100)))
        
        options = ["1 Player", "2 Players", f"AI Difficulty: {self.ai_difficulty.capitalize()}", "Start Game"]
        for i, option in enumerate(options):
            color = GREEN if i == self.selected_option else WHITE
            text = self.font.render(option, True, color)
            self.screen.blit(text, text.get_rect(center=(WINDOW_WIDTH//2, 250 + i * 50)))
        
        pygame.display.flip()

    def draw_countdown(self) -> None:
        self.screen.fill(BLACK)
        self.ship1.draw(self.screen)
        self.ship2.draw(self.screen)
        pygame.draw.circle(self.screen, YELLOW, (self.star_x, self.star_y), 10)
        
        elapsed = (pygame.time.get_ticks() - self.countdown_start) / 1000
        countdown_number = max(1, COUNTDOWN_TIME - int(elapsed))
        
        text = self.countdown_font.render(str(countdown_number) if countdown_number > 0 else "GO!", 
                                        True, GREEN if countdown_number == 0 else WHITE)
        self.screen.blit(text, text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2)))
        pygame.display.flip()

    def draw_victory_screen(self) -> None:
        self.screen.fill(BLACK)
        
        # Draw title with different message for star death
        if self.winner:
            if any(ship.dead for ship in [self.ship1, self.ship2]):
                title = self.title_font.render("STAR DESTRUCTION!", True, YELLOW)
            else:
                title = self.title_font.render("VICTORY!", True, self.winner.color)
        else:
            title = self.title_font.render("GAME OVER", True, WHITE)
        self.screen.blit(title, title.get_rect(center=(WINDOW_WIDTH//2, 200)))
        
        # Draw score
        score_text = self.font.render(f"Final Score - Green: {self.ship1.score}  Red: {self.ship2.score}", True, WHITE)
        self.screen.blit(score_text, score_text.get_rect(center=(WINDOW_WIDTH//2, 300)))
        
        # Draw instructions
        instructions = self.font.render("Press SPACE to play again or ESC for menu", True, WHITE)
        self.screen.blit(instructions, instructions.get_rect(center=(WINDOW_WIDTH//2, 400)))
        pygame.display.flip()

    def draw(self) -> None:
        self.screen.fill(BLACK)
        
        # Draw star with danger zone
        pygame.draw.circle(self.screen, YELLOW, (self.star_x, self.star_y), STAR_RADIUS)
        pygame.draw.circle(self.screen, (255, 165, 0), (self.star_x, self.star_y), STAR_DANGER_RADIUS, 1)
        
        # Draw ships
        self.ship1.draw(self.screen)
        self.ship2.draw(self.screen)
        
        # Draw scores
        score1 = self.font.render(f"Green: {self.ship1.score}", True, GREEN)
        score2 = self.font.render(f"Red: {self.ship2.score}", True, RED)
        self.screen.blit(score1, (10, 10))
        self.screen.blit(score2, (WINDOW_WIDTH - 100, 10))
        
        # Draw win condition
        win_text = self.font.render(f"First to {POINTS_TO_WIN} wins!", True, WHITE)
        self.screen.blit(win_text, win_text.get_rect(center=(WINDOW_WIDTH//2, 30)))
        
        pygame.display.flip()

    def handle_menu_input(self) -> bool:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.selected_option = (self.selected_option - 1) % 4
                elif event.key == pygame.K_DOWN:
                    self.selected_option = (self.selected_option + 1) % 4
                elif event.key == pygame.K_RETURN:
                    if self.selected_option == 0:
                        self.game_mode = '1player'
                        self.in_menu = False
                        self.start_countdown()
                    elif self.selected_option == 1:
                        self.game_mode = '2player'
                        self.in_menu = False
                        self.start_countdown()
                    elif self.selected_option == 2:
                        difficulties = ['easy', 'medium', 'hard']
                        self.ai_difficulty = difficulties[(difficulties.index(self.ai_difficulty) + 1) % 3]
                    elif self.selected_option == 3 and self.game_mode:
                        self.in_menu = False
                        self.start_countdown()
        return True

    def handle_victory_input(self) -> bool:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.start_countdown()
                    return True
                elif event.key == pygame.K_ESCAPE:
                    self.in_menu = True
                    return True
        return True

    def handle_game_input(self) -> bool:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.in_menu = True
                return True
        
        keys = pygame.key.get_pressed()
        for ship in [self.ship1, self.ship2]:
            if not ship.is_ai:
                if keys[ship.controls.rotate_left]: ship.rotate(False)
                if keys[ship.controls.rotate_right]: ship.rotate(True)
                if keys[ship.controls.thrust]: ship.thrust()
                if keys[ship.controls.hyperspace]: ship.hyperspace()
                if pygame.key.get_pressed()[ship.controls.fire]: ship.fire_torpedo()
        
        return True

    def check_collisions(self) -> None:
        # Check star collisions first
        for ship in [self.ship1, self.ship2]:
            if not ship.dead:
                dx, dy = self.star_x - ship.x, self.star_y - ship.y
                if math.sqrt(dx*dx + dy*dy) < STAR_KILL_RADIUS:
                    ship.dead = True
                    # Game over when ship is destroyed by star
                    self.game_over = True
                    self.winner = self.ship2 if ship == self.ship1 else self.ship1
                    return

        # Check torpedo hits
        for ship in [self.ship1, self.ship2]:
            if ship.dead:
                continue
            for torpedo in ship.torpedoes[:]:
                other_ship = self.ship2 if ship == self.ship1 else self.ship1
                if other_ship.dead:
                    continue
                dx, dy = torpedo.x - other_ship.x, torpedo.y - other_ship.y
                if math.sqrt(dx*dx + dy*dy) < (SHIP_RADIUS + TORPEDO_RADIUS):
                    ship.score += 1
                    ship.torpedoes.remove(torpedo)
                    other_ship.hit_flash = HIT_FLASH_DURATION
                    self.check_win_condition()  # Check if this hit won the game
                    break

    def check_win_condition(self) -> None:
        if self.ship1.score >= POINTS_TO_WIN:
            self.game_over = True
            self.winner = self.ship1
        elif self.ship2.score >= POINTS_TO_WIN:
            self.game_over = True
            self.winner = self.ship2
        # Star destruction is handled in check_collisions

    def update(self) -> None:
        self.ship1.update(self.star_x, self.star_y)
        self.ship2.update(self.star_x, self.star_y, self.ship1)
        self.check_collisions()

    def run(self) -> None:
        running = True
        while running:
            if self.in_menu:
                running = self.handle_menu_input()
                self.draw_menu()
            elif self.in_countdown:
                elapsed = (pygame.time.get_ticks() - self.countdown_start) / 1000
                if elapsed >= COUNTDOWN_TIME + 1:
                    self.in_countdown = False
                self.draw_countdown()
            elif self.game_over:
                running = self.handle_victory_input()
                self.draw_victory_screen()
            else:
                running = self.handle_game_input()
                self.update()
                self.draw()
            self.clock.tick(FPS)

def main():
    game = Game()
    game.run()
    pygame.quit()

if __name__ == "__main__":
    main() 