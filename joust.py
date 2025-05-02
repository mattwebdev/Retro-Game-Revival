import pygame
import random
import math

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
FPS = 60
GRAVITY = 0.5
FLAP_STRENGTH = -8
HORIZONTAL_SPEED = 4
PLATFORM_HEIGHT = 20

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BROWN = (139, 69, 19)
LAVA = (255, 100, 0)
DARK_BROWN = (101, 67, 33)
LIGHT_BROWN = (205, 133, 63)
SKY_BLUE = (135, 206, 235)
CLOUD_WHITE = (240, 240, 240)
GOLD = (255, 215, 0)

# Set up the display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Joust")
clock = pygame.time.Clock()

class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.size = random.randint(2, 5)
        self.speed_x = random.uniform(-2, 2)
        self.speed_y = random.uniform(-2, 2)
        self.life = 30  # frames to live

    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y
        self.life -= 1
        self.size = max(0, self.size - 0.1)

    def draw(self, surface):
        if self.life > 0:
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), int(self.size))

class ScorePopup:
    def __init__(self, x, y, score):
        self.x = x
        self.y = y
        self.score = score
        self.life = 60  # frames to live
        self.font = pygame.font.Font(None, 36)

    def update(self):
        self.y -= 1  # Float upward
        self.life -= 1

    def draw(self, surface):
        if self.life > 0:
            text = self.font.render(f"+{self.score}", True, GOLD)
            surface.blit(text, (self.x, self.y))

def create_background():
    """Create a scrolling background with clouds."""
    background = pygame.Surface((WIDTH, HEIGHT))
    background.fill(SKY_BLUE)
    
    # Draw clouds
    for _ in range(10):
        x = random.randint(0, WIDTH)
        y = random.randint(0, HEIGHT // 2)
        size = random.randint(30, 60)
        pygame.draw.ellipse(background, CLOUD_WHITE, (x, y, size, size // 2))
    
    return background

def create_knight_sprite(color, direction=1, wing_angle=0):
    """Create a knight sprite with animated wings."""
    sprite = pygame.Surface((40, 40), pygame.SRCALPHA)
    
    # Body
    pygame.draw.ellipse(sprite, color, (10, 10, 20, 20))
    
    # Head
    pygame.draw.circle(sprite, color, (20, 8), 6)
    
    # Lance
    lance_length = 20
    lance_start = (20, 20)
    lance_end = (20 + direction * lance_length, 20)
    pygame.draw.line(sprite, WHITE, lance_start, lance_end, 3)
    
    # Wings (animated)
    wing_color = (200, 200, 200)
    wing_angle_rad = math.radians(wing_angle)
    
    # Left wing
    left_wing_base = (5, 20)
    left_wing_tip = (
        left_wing_base[0] - 10 * math.cos(wing_angle_rad),
        left_wing_base[1] - 10 * math.sin(wing_angle_rad)
    )
    left_wing = [left_wing_base, left_wing_tip, (5, 25)]
    pygame.draw.polygon(sprite, wing_color, left_wing)
    
    # Right wing
    right_wing_base = (35, 20)
    right_wing_tip = (
        right_wing_base[0] + 10 * math.cos(wing_angle_rad),
        right_wing_base[1] - 10 * math.sin(wing_angle_rad)
    )
    right_wing = [right_wing_base, right_wing_tip, (35, 25)]
    pygame.draw.polygon(sprite, wing_color, right_wing)
    
    return sprite

def create_platform_sprite(width):
    """Create a detailed platform sprite."""
    sprite = pygame.Surface((width, PLATFORM_HEIGHT), pygame.SRCALPHA)
    
    # Main platform with gradient
    for y in range(PLATFORM_HEIGHT):
        alpha = int(255 * (1 - y / PLATFORM_HEIGHT))
        color = (DARK_BROWN[0], DARK_BROWN[1], DARK_BROWN[2], alpha)
        pygame.draw.line(sprite, color, (0, y), (width, y))
    
    # Platform details
    for x in range(0, width, 20):
        # Vertical lines
        pygame.draw.line(sprite, LIGHT_BROWN, (x, 0), (x, PLATFORM_HEIGHT), 1)
        # Horizontal lines
        pygame.draw.line(sprite, LIGHT_BROWN, (x, PLATFORM_HEIGHT//2), (x + 20, PLATFORM_HEIGHT//2), 1)
    
    return sprite

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.direction = 1
        self.wing_angle = 0
        self.wing_direction = 1
        self.image = create_knight_sprite(WHITE, self.direction, self.wing_angle)
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH // 2, HEIGHT // 2)
        self.velocity_y = 0
        self.velocity_x = 0
        self.is_flapping = False
        self.particles = []

    def update(self):
        # Apply gravity
        self.velocity_y += GRAVITY
        
        # Update position
        self.rect.y += self.velocity_y
        self.rect.x += self.velocity_x
        
        # Keep player on screen
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.top < 0:
            self.rect.top = 0
            self.velocity_y = 0
        if self.rect.bottom > HEIGHT:
            self.rect.bottom = HEIGHT
            self.velocity_y = 0
            
        # Update sprite direction
        if self.velocity_x > 0:
            self.direction = 1
        elif self.velocity_x < 0:
            self.direction = -1
            
        # Animate wings
        if self.is_flapping:
            self.wing_angle += 10 * self.wing_direction
            if self.wing_angle > 45 or self.wing_angle < -45:
                self.wing_direction *= -1
        else:
            self.wing_angle = 0
            
        self.image = create_knight_sprite(WHITE, self.direction, self.wing_angle)
        
        # Update particles
        for particle in self.particles[:]:
            particle.update()
            if particle.life <= 0:
                self.particles.remove(particle)

    def flap(self):
        self.velocity_y = FLAP_STRENGTH
        self.is_flapping = True
        # Add flap particles
        for _ in range(5):
            self.particles.append(Particle(
                self.rect.centerx,
                self.rect.centery,
                WHITE
            ))

    def move_left(self):
        self.velocity_x = -HORIZONTAL_SPEED
        self.direction = -1

    def move_right(self):
        self.velocity_x = HORIZONTAL_SPEED
        self.direction = 1

    def stop_horizontal(self):
        self.velocity_x = 0
        self.is_flapping = False

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width):
        super().__init__()
        self.image = create_platform_sprite(width)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.direction = random.choice([-1, 1])
        self.wing_angle = 0
        self.wing_direction = 1
        self.image = create_knight_sprite(RED, self.direction, self.wing_angle)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.velocity_y = 0
        self.velocity_x = random.choice([-2, 2])
        self.particles = []
        self.state = "patrol"  # patrol, attack, or flee
        self.target_platform = None
        self.flap_cooldown = 0
        self.change_direction_cooldown = 0
        self.attack_cooldown = 0

    def update(self):
        # Update cooldowns
        if self.flap_cooldown > 0:
            self.flap_cooldown -= 1
        if self.change_direction_cooldown > 0:
            self.change_direction_cooldown -= 1
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

        # Apply gravity
        self.velocity_y += GRAVITY
        
        # Update position
        self.rect.y += self.velocity_y
        self.rect.x += self.velocity_x
        
        # Bounce off walls
        if self.rect.left < 0 or self.rect.right > WIDTH:
            self.velocity_x *= -1
            self.direction *= -1
            self.change_direction_cooldown = 30  # Prevent rapid direction changes
        
        # Keep enemy on platforms
        platform_hits = pygame.sprite.spritecollide(self, platforms, False)
        if platform_hits:
            self.rect.bottom = platform_hits[0].rect.top
            self.velocity_y = 0
            
            # Decide next action when on platform
            if self.attack_cooldown <= 0:
                if random.random() < 0.3:  # 30% chance to attack
                    self.state = "attack"
                    self.attack_cooldown = 120
                else:
                    self.state = "patrol"
                    self.target_platform = random.choice(platforms.sprites())
            
            # Flap when ready to take off
            if self.flap_cooldown <= 0 and self.velocity_y >= 0:
                self.flap()
                self.flap_cooldown = 30
        else:
            # In air behavior
            if self.state == "attack" and self.attack_cooldown > 0:
                # Try to position above player
                if player.rect.centerx < self.rect.centerx:
                    self.velocity_x = -HORIZONTAL_SPEED
                    self.direction = -1
                else:
                    self.velocity_x = HORIZONTAL_SPEED
                    self.direction = 1
                
                # Flap to gain height
                if self.flap_cooldown <= 0 and self.velocity_y > -2:
                    self.flap()
                    self.flap_cooldown = 30
            elif self.state == "patrol" and self.target_platform:
                # Move towards target platform
                if self.target_platform.rect.centerx < self.rect.centerx:
                    self.velocity_x = -HORIZONTAL_SPEED
                    self.direction = -1
                else:
                    self.velocity_x = HORIZONTAL_SPEED
                    self.direction = 1
                
                # Flap occasionally while patrolling
                if self.flap_cooldown <= 0 and random.random() < 0.1:
                    self.flap()
                    self.flap_cooldown = 30
        
        # Animate wings
        self.wing_angle += 5 * self.wing_direction
        if self.wing_angle > 45 or self.wing_angle < -45:
            self.wing_direction *= -1
            
        self.image = create_knight_sprite(RED, self.direction, self.wing_angle)
        
        # Update particles
        for particle in self.particles[:]:
            particle.update()
            if particle.life <= 0:
                self.particles.remove(particle)

    def flap(self):
        self.velocity_y = FLAP_STRENGTH
        # Add flap particles
        for _ in range(5):
            self.particles.append(Particle(
                self.rect.centerx,
                self.rect.centery,
                RED
            ))

class Lava(pygame.sprite.Sprite):
    def __init__(self, x, y, width):
        super().__init__()
        self.image = pygame.Surface((width, 20), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.animation_frame = 0
        self.update_animation()

    def update_animation(self):
        self.image.fill((0, 0, 0, 0))
        self.animation_frame = (self.animation_frame + 1) % 10
        for i in range(0, self.rect.width, 10):
            height = random.randint(5, 15)
            color = (
                LAVA[0],
                LAVA[1],
                LAVA[2],
                int(255 * (0.5 + 0.5 * math.sin(self.animation_frame + i/10)))
            )
            pygame.draw.rect(self.image, color, (i, 20-height, 10, height))

# Create sprite groups
all_sprites = pygame.sprite.Group()
platforms = pygame.sprite.Group()
enemies = pygame.sprite.Group()
lava_pits = pygame.sprite.Group()

# Create background
background = create_background()

# Create player
player = Player()
all_sprites.add(player)

# Create platforms
platform_positions = [
    (100, 400, 200),
    (400, 300, 200),
    (600, 500, 200),
    (200, 200, 200),
]

for x, y, width in platform_positions:
    platform = Platform(x, y, width)
    platforms.add(platform)
    all_sprites.add(platform)

# Create lava pits
lava_positions = [
    (0, HEIGHT - 20, WIDTH),
]

for x, y, width in lava_positions:
    lava = Lava(x, y, width)
    lava_pits.add(lava)
    all_sprites.add(lava)

# Create enemies
for _ in range(3):
    x = random.randint(0, WIDTH - 40)
    y = random.randint(0, HEIGHT // 2)
    enemy = Enemy(x, y)
    enemies.add(enemy)
    all_sprites.add(enemy)

# Game loop
running = True
score = 0
font = pygame.font.Font(None, 36)
score_popups = []

while running:
    # Keep loop running at the right speed
    clock.tick(FPS)
    
    # Process input/events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                player.flap()
            elif event.key == pygame.K_LEFT:
                player.move_left()
            elif event.key == pygame.K_RIGHT:
                player.move_right()
        elif event.type == pygame.KEYUP:
            if event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                player.stop_horizontal()
    
    # Update
    all_sprites.update()
    
    # Update lava animation
    for lava in lava_pits:
        lava.update_animation()
    
    # Check for platform collisions
    platform_hits = pygame.sprite.spritecollide(player, platforms, False)
    if platform_hits:
        player.rect.bottom = platform_hits[0].rect.top
        player.velocity_y = 0
    
    # Check for enemy collisions
    enemy_hits = pygame.sprite.spritecollide(player, enemies, False)
    for enemy in enemy_hits:
        if player.velocity_y < enemy.velocity_y and player.rect.bottom < enemy.rect.centery:
            # Player wins the joust
            score += 100
            score_popups.append(ScorePopup(enemy.rect.centerx, enemy.rect.centery, 100))
            # Add explosion particles
            for _ in range(20):
                player.particles.append(Particle(
                    enemy.rect.centerx,
                    enemy.rect.centery,
                    RED
                ))
            enemy.kill()
        else:
            # Player loses
            running = False
    
    # Check for lava collisions
    if pygame.sprite.spritecollide(player, lava_pits, False):
        running = False
    
    # Update score popups
    for popup in score_popups[:]:
        popup.update()
        if popup.life <= 0:
            score_popups.remove(popup)
    
    # Draw / render
    screen.blit(background, (0, 0))
    all_sprites.draw(screen)
    
    # Draw particles
    for particle in player.particles:
        particle.draw(screen)
    for enemy in enemies:
        for particle in enemy.particles:
            particle.draw(screen)
    
    # Draw score popups
    for popup in score_popups:
        popup.draw(screen)
    
    # Draw score
    score_text = font.render(f'Score: {score}', True, WHITE)
    screen.blit(score_text, (10, 10))
    
    # Flip the display
    pygame.display.flip()

pygame.quit() 