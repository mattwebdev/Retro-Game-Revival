import pygame
import numpy as np
import math
import os
import time
import random
import json
import os.path

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FOV = 60  # Field of view
HALF_FOV = FOV / 2
CASTED_RAYS = 120
STEP_ANGLE = FOV / CASTED_RAYS
MAX_DEPTH = 800
TILE_SIZE = 64
PLAYER_SIZE = 10
TEXTURE_SIZE = 64

# Player stats
MAX_HEALTH = 100
MAX_AMMO = 50
STARTING_AMMO = 25

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)
YELLOW = (255, 255, 0)
HEALTH_RED = (220, 40, 40)
AMMO_BLUE = (40, 40, 220)
TRANSPARENT_BLACK = (0, 0, 0, 180)

# Create the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Wolfenstein 3D Clone")

# Weapon states
WEAPON_IDLE = 0
WEAPON_FIRING = 1
WEAPON_COOLDOWN = 2

# Add game state constants
GAME_STATE_PLAYING = 'playing'
GAME_STATE_GAME_OVER = 'game_over'
GAME_STATE_MAIN_MENU = 'main_menu'
GAME_STATE_PAUSED = 'paused'
GAME_STATE_HIGH_SCORES = 'high_scores'

# Add weapon type constants
WEAPON_PISTOL = 'pistol'
WEAPON_SHOTGUN = 'shotgun'
WEAPON_RIFLE = 'rifle'

# Weapon configurations
WEAPON_CONFIGS = {
    WEAPON_PISTOL: {
        'damage': 50,
        'cooldown': 20,
        'max_range': 500,
        'starting_ammo': 25,
        'max_ammo': 50,
        'spread': 0,  # No spread
        'color': GRAY,
        'barrel_color': DARK_GRAY,
        'shots_per_fire': 1
    },
    WEAPON_SHOTGUN: {
        'damage': 20,  # Per pellet
        'cooldown': 45,
        'max_range': 300,
        'starting_ammo': 15,
        'max_ammo': 30,
        'spread': 10,  # Degrees
        'color': (139, 69, 19),  # Brown
        'barrel_color': (101, 67, 33),  # Dark brown
        'shots_per_fire': 8  # Number of pellets
    },
    WEAPON_RIFLE: {
        'damage': 100,
        'cooldown': 60,
        'max_range': 800,
        'starting_ammo': 10,
        'max_ammo': 20,
        'spread': 0,
        'color': (169, 169, 169),  # Silver
        'barrel_color': (105, 105, 105),  # Dark silver
        'shots_per_fire': 1
    }
}

# Add power-up constants
POWERUP_HEALTH = 'health'
POWERUP_AMMO = 'ammo'
POWERUP_DAMAGE = 'damage'

# Power-up configurations
POWERUP_CONFIGS = {
    POWERUP_HEALTH: {
        'color': (0, 255, 0),  # Green
        'heal_amount': 25,
        'size': 15,
        'bob_height': 10,
        'bob_speed': 0.05
    },
    POWERUP_AMMO: {
        'color': (0, 0, 255),  # Blue
        'ammo_amount': 15,
        'size': 15,
        'bob_height': 10,
        'bob_speed': 0.05
    },
    POWERUP_DAMAGE: {
        'color': (255, 215, 0),  # Gold
        'multiplier': 2.0,
        'duration': 600,  # 10 seconds at 60 FPS
        'size': 20,
        'bob_height': 15,
        'bob_speed': 0.08
    }
}

# Add high score constants
HIGH_SCORES_FILE = 'high_scores.json'
MAX_HIGH_SCORES = 5

# Enemy type constants
ENEMY_GUARD = 'guard'
ENEMY_HEAVY = 'heavy'
ENEMY_SCOUT = 'scout'
ENEMY_COMMANDER = 'commander'

# Enemy configurations
ENEMY_CONFIGS = {
    ENEMY_GUARD: {
        'health': 100,
        'damage': 5,
        'speed': 1.0,
        'size': TILE_SIZE // 2,
        'attack_range': TILE_SIZE,
        'chase_range': TILE_SIZE * 4,
        'color': RED,
        'score': 100,
        'powerup_chance': 0.3
    },
    ENEMY_HEAVY: {
        'health': 200,
        'damage': 10,
        'speed': 0.7,
        'size': TILE_SIZE * 0.7,
        'attack_range': TILE_SIZE * 1.5,
        'chase_range': TILE_SIZE * 5,
        'color': (139, 69, 19),  # Brown
        'score': 200,
        'powerup_chance': 0.6
    },
    ENEMY_SCOUT: {
        'health': 50,
        'damage': 3,
        'speed': 1.8,
        'size': TILE_SIZE // 2.5,
        'attack_range': TILE_SIZE * 0.7,
        'chase_range': TILE_SIZE * 6,
        'color': (0, 191, 255),  # Deep Sky Blue
        'score': 150,
        'powerup_chance': 0.4,
        'dodge_chance': 0.4
    },
    ENEMY_COMMANDER: {
        'health': 150,
        'damage': 7,
        'speed': 1.0,
        'size': TILE_SIZE * 0.6,
        'attack_range': TILE_SIZE * 1.2,
        'chase_range': TILE_SIZE * 5,
        'color': (148, 0, 211),  # Purple
        'score': 300,
        'powerup_chance': 0.8,
        'buff_range': TILE_SIZE * 3,
        'buff_multiplier': 1.5
    }
}

# Level constants
LEVEL_STATE_EXPLORING = 'exploring'
LEVEL_STATE_COMPLETE = 'complete'
LEVEL_STATE_TRANSITION = 'transition'

# Level configurations
LEVEL_CONFIGS = {
    1: {
        'name': 'Training Ground',
        'objective': 'Eliminate all enemies',
        'min_enemies': 4,
        'enemy_types': [ENEMY_GUARD, ENEMY_SCOUT],
        'powerup_count': 3,
        'secret_count': 1,
        'par_time': 120,  # seconds
        'completion_bonus': 1000,
        'secret_bonus': 500
    },
    2: {
        'name': 'Command Center',
        'objective': 'Find the exit and eliminate the commander',
        'min_enemies': 6,
        'enemy_types': [ENEMY_GUARD, ENEMY_SCOUT, ENEMY_COMMANDER],
        'powerup_count': 4,
        'secret_count': 2,
        'par_time': 180,
        'completion_bonus': 2000,
        'secret_bonus': 750
    },
    3: {
        'name': 'Fortress',
        'objective': 'Survive the heavy trooper ambush',
        'min_enemies': 8,
        'enemy_types': [ENEMY_GUARD, ENEMY_HEAVY, ENEMY_COMMANDER],
        'powerup_count': 5,
        'secret_count': 2,
        'par_time': 240,
        'completion_bonus': 3000,
        'secret_bonus': 1000
    }
}

# Level maps (0 = empty, 1-4 = walls, 5 = door, 6 = exit, 7 = secret wall)
LEVEL_MAPS = {
    1: [  # Training Ground - Simple layout with open areas
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 3, 0, 0, 0, 5, 0, 0, 0, 0, 0, 3, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 2, 2, 2, 2, 0, 0, 0, 0, 0, 1],
        [1, 0, 3, 0, 0, 0, 0, 0, 0, 5, 0, 0, 3, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 7, 0, 2, 0, 0, 0, 0, 0, 1],
        [1, 0, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 0, 0, 1],
        [1, 0, 5, 0, 0, 0, 4, 4, 4, 4, 0, 0, 0, 0, 6, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    ],
    2: [  # Command Center - More complex layout with multiple paths
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1],
        [1, 0, 2, 0, 5, 0, 2, 2, 0, 5, 0, 2, 0, 7, 0, 1],
        [1, 0, 2, 0, 1, 0, 2, 2, 0, 1, 0, 2, 0, 0, 0, 1],
        [1, 0, 5, 0, 1, 0, 5, 5, 0, 1, 0, 2, 2, 2, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 5, 0, 1],
        [1, 0, 2, 2, 1, 2, 2, 2, 2, 1, 0, 2, 2, 2, 0, 1],
        [1, 0, 0, 0, 5, 0, 0, 7, 0, 5, 0, 0, 6, 0, 0, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    ],
    3: [  # Fortress - Complex layout with multiple rooms and ambush points
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1],
        [1, 0, 2, 5, 1, 0, 2, 0, 5, 0, 2, 0, 5, 0, 0, 1],
        [1, 0, 0, 0, 1, 0, 2, 0, 1, 0, 2, 0, 1, 0, 0, 1],
        [1, 1, 5, 1, 1, 0, 5, 0, 1, 0, 5, 0, 1, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 2, 0, 1, 2, 2, 2, 1, 0, 2, 0, 1, 2, 0, 1],
        [1, 0, 2, 0, 5, 7, 0, 0, 5, 0, 2, 0, 5, 0, 0, 1],
        [1, 0, 2, 0, 1, 0, 0, 0, 1, 0, 2, 0, 1, 0, 0, 1],
        [1, 0, 5, 0, 1, 0, 2, 0, 1, 0, 5, 0, 1, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 2, 7, 0, 0, 0, 0, 0, 0, 6, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    ]
}

# Add after the other constants
# Visual effect constants
BLOOD_PARTICLES = []
SCREEN_SHAKE = {'duration': 0, 'intensity': 0}
DAMAGE_FLASH = {'duration': 0, 'intensity': 0}

class BloodParticle:
    def __init__(self, x, y, angle):
        self.x = x
        self.y = y
        self.dx = random.uniform(-2, 2) + math.cos(math.radians(angle)) * 3
        self.dy = random.uniform(-2, 2) + math.sin(math.radians(angle)) * 3
        self.lifetime = random.randint(20, 40)
        self.size = random.randint(2, 4)
        self.color = (random.randint(180, 255), 0, 0, 255)  # Red with random intensity
    
    def update(self):
        self.x += self.dx
        self.y += self.dy
        self.lifetime -= 1
        if self.lifetime < 10:  # Fade out
            self.color = (*self.color[:3], int(255 * (self.lifetime / 10)))
        return self.lifetime > 0
    
    def draw(self, surface, player_x, player_y, player_angle):
        # Calculate relative position to player
        dx = self.x - player_x
        dy = self.y - player_y
        
        # Calculate angle to particle relative to player's view
        particle_angle = math.degrees(math.atan2(dy, dx))
        relative_angle = (particle_angle - player_angle) % 360
        if relative_angle > 180:
            relative_angle = relative_angle - 360
        
        if abs(relative_angle) < FOV / 2:
            # Calculate screen position
            screen_x = SCREEN_WIDTH / 2 + (relative_angle / (FOV / 2)) * (SCREEN_WIDTH / 2)
            distance = math.sqrt(dx * dx + dy * dy)
            size = max(1, self.size * SCREEN_HEIGHT / (distance * 2))
            
            # Draw particle
            particle_surface = pygame.Surface((int(size * 2), int(size * 2)), pygame.SRCALPHA)
            pygame.draw.circle(particle_surface, self.color, (int(size), int(size)), int(size))
            surface.blit(particle_surface, (int(screen_x - size), int(SCREEN_HEIGHT/2 - size)))

def apply_screen_shake(surface):
    if SCREEN_SHAKE['duration'] > 0:
        offset_x = random.randint(-SCREEN_SHAKE['intensity'], SCREEN_SHAKE['intensity'])
        offset_y = random.randint(-SCREEN_SHAKE['intensity'], SCREEN_SHAKE['intensity'])
        SCREEN_SHAKE['duration'] -= 1
        
        # Create a slightly larger surface to handle the shake
        shake_surface = pygame.Surface((SCREEN_WIDTH + 20, SCREEN_HEIGHT + 20))
        shake_surface.fill(BLACK)
        shake_surface.blit(surface, (10 + offset_x, 10 + offset_y))
        surface.blit(shake_surface, (-10, -10))

def apply_damage_flash(surface):
    if DAMAGE_FLASH['duration'] > 0:
        flash_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        alpha = int(DAMAGE_FLASH['intensity'] * (DAMAGE_FLASH['duration'] / 10))
        flash_surface.fill((255, 0, 0, alpha))
        surface.blit(flash_surface, (0, 0))
        DAMAGE_FLASH['duration'] -= 1

class Weapon:
    def __init__(self, weapon_type=WEAPON_PISTOL):
        self.weapon_type = weapon_type
        self.config = WEAPON_CONFIGS[weapon_type]
        self.state = WEAPON_IDLE
        self.animation_frame = 0
        self.fire_cooldown = 0
        self.max_cooldown = self.config['cooldown']
        self.recoil_offset = 0
        self.bullet_damage = self.config['damage']
        self.max_range = self.config['max_range']
        self.ammo = self.config['starting_ammo']
        self.max_ammo = self.config['max_ammo']
        self.spread = self.config['spread']
        self.shots_per_fire = self.config['shots_per_fire']

    def update(self):
        # Update recoil
        if self.recoil_offset > 0:
            self.recoil_offset = max(0, self.recoil_offset - 1)
        
        # Update firing animation
        if self.state == WEAPON_FIRING:
            self.animation_frame += 1
            if self.animation_frame >= 5:  # Reset after 5 frames
                self.animation_frame = 0
                self.state = WEAPON_COOLDOWN
                self.fire_cooldown = self.max_cooldown
        
        # Update cooldown
        if self.state == WEAPON_COOLDOWN:
            self.fire_cooldown -= 1
            if self.fire_cooldown <= 0:
                self.state = WEAPON_IDLE
                self.fire_cooldown = 0

    def fire(self):
        if self.state == WEAPON_IDLE and self.ammo > 0:
            self.state = WEAPON_FIRING
            self.animation_frame = 0
            self.recoil_offset = 10
            self.ammo -= 1
            
            # Add screen shake based on weapon type
            if self.weapon_type == WEAPON_SHOTGUN:
                SCREEN_SHAKE['duration'] = 10
                SCREEN_SHAKE['intensity'] = 8
            elif self.weapon_type == WEAPON_RIFLE:
                SCREEN_SHAKE['duration'] = 15
                SCREEN_SHAKE['intensity'] = 6
            else:  # Pistol
                SCREEN_SHAKE['duration'] = 5
                SCREEN_SHAKE['intensity'] = 3
            
            return True
        return False

    def get_spread_angles(self):
        if self.spread == 0:
            return [0]  # No spread, just return center angle
        
        angles = []
        for _ in range(self.shots_per_fire):
            spread_angle = random.uniform(-self.spread, self.spread)
            angles.append(spread_angle)
        return angles

    def add_ammo(self, amount):
        self.ammo = min(self.max_ammo, self.ammo + amount)

    def draw(self, surface):
        # Draw weapon model
        weapon_height = 100
        weapon_width = 60
        base_y = SCREEN_HEIGHT - weapon_height + self.recoil_offset
        
        # Draw gun body with weapon-specific color
        pygame.draw.rect(surface, self.config['color'], 
                        (SCREEN_WIDTH//2 - weapon_width//2, 
                         base_y,
                         weapon_width, weapon_height))
        
        # Draw barrel with weapon-specific color
        barrel_width = 20
        if self.weapon_type == WEAPON_SHOTGUN:
            barrel_width = 30  # Wider barrel for shotgun
        elif self.weapon_type == WEAPON_RIFLE:
            barrel_height = 50  # Longer barrel for rifle
            pygame.draw.rect(surface, self.config['barrel_color'],
                           (SCREEN_WIDTH//2 - 10,
                            base_y - barrel_height,
                            20, barrel_height))
        else:  # Default pistol barrel
            pygame.draw.rect(surface, self.config['barrel_color'],
                           (SCREEN_WIDTH//2 - barrel_width//2,
                            base_y - 20,
                            barrel_width, 40))
        
        # Draw muzzle flash when firing
        if self.state == WEAPON_FIRING and self.animation_frame < 3:
            flash_points = [
                (SCREEN_WIDTH//2, base_y - 30),
                (SCREEN_WIDTH//2 - 20, base_y - 40),
                (SCREEN_WIDTH//2 + 20, base_y - 40)
            ]
            pygame.draw.polygon(surface, YELLOW, flash_points)

class PowerUp:
    def __init__(self, x, y, powerup_type):
        self.x = x * TILE_SIZE + TILE_SIZE // 2
        self.y = y * TILE_SIZE + TILE_SIZE // 2
        self.type = powerup_type
        self.config = POWERUP_CONFIGS[powerup_type]
        self.active = True
        self.start_y = self.y
        self.time = 0
        
        # For damage powerup effect
        self.effect_active = False
        self.effect_start_time = 0
        self.effect_duration = self.config.get('duration', 0)
    
    def update(self):
        if not self.active:
            return
        
        # Bobbing animation
        self.time += self.config['bob_speed']
        self.y = self.start_y + math.sin(self.time) * self.config['bob_height']
    
    def collect(self, player_health, weapons, current_weapon_type, current_time):
        if not self.active:
            return player_health, False
        
        if self.type == POWERUP_HEALTH:
            player_health = min(MAX_HEALTH, player_health + self.config['heal_amount'])
            self.active = False
            return player_health, True
            
        elif self.type == POWERUP_AMMO:
            weapon = weapons[current_weapon_type]
            weapon.add_ammo(self.config['ammo_amount'])
            self.active = False
            return player_health, True
            
        elif self.type == POWERUP_DAMAGE:
            self.effect_active = True
            self.effect_start_time = current_time
            self.active = False
            return player_health, True
        
        return player_health, False
    
    def is_effect_active(self, current_time):
        if not self.effect_active:
            return False
        
        if current_time - self.effect_start_time >= self.effect_duration:
            self.effect_active = False
            return False
            
        return True
    
    def draw(self, surface, player_x, player_y, player_angle):
        if not self.active:
            return
            
        # Calculate relative position to player
        dx = self.x - player_x
        dy = self.y - player_y
        
        # Calculate angle to powerup relative to player's view
        powerup_angle = math.degrees(math.atan2(dy, dx))
        relative_angle = (powerup_angle - player_angle) % 360
        
        # Calculate distance
        distance = math.sqrt(dx * dx + dy * dy)
        
        # Check if powerup is hidden behind a wall
        wall_distance = cast_ray_to_enemy(player_x, player_y, self.x, self.y)
        if wall_distance is not None and wall_distance < distance:
            return
        
        # Only draw if in field of view
        relative_angle = relative_angle % 360
        if relative_angle > 180:
            relative_angle = relative_angle - 360
            
        if abs(relative_angle) < FOV / 2:
            # Calculate screen position based on angle
            screen_x = SCREEN_WIDTH / 2 + (relative_angle / (FOV / 2)) * (SCREEN_WIDTH / 2)
            
            # Calculate size based on distance with perspective correction and capped size
            base_size = self.config['size'] * 0.6  # Reduced base size by 40%
            min_size = base_size * 0.3  # Smaller minimum size
            max_size = base_size * 1.5  # Smaller maximum size
            
            # Calculate perspective size with smooth falloff
            perspective_factor = SCREEN_HEIGHT / (distance * math.cos(math.radians(relative_angle)))
            size = base_size * perspective_factor * 0.3  # Further reduced scale
            
            # Clamp size between min and max
            size = max(min_size, min(size, max_size))
            
            # Only draw if in front of player and not too close
            if distance > TILE_SIZE / 4:
                # Draw powerup with minimal glow effect
                glow_size = size * 1.1  # Reduced glow size
                glow_surface = pygame.Surface((int(glow_size * 2), int(glow_size * 2)), pygame.SRCALPHA)
                
                # Reduce the number of glow layers and alpha
                for radius in range(int(size), int(glow_size), 4):  # Fewer glow layers
                    alpha = int(40 * (1 - (radius - size) / (glow_size - size)))  # Lower alpha
                    pygame.draw.circle(glow_surface, (*self.config['color'], alpha),
                                    (int(glow_size), int(glow_size)), radius)
                
                # Draw main powerup circle with reduced opacity
                pygame.draw.circle(surface, (*self.config['color'], 160),  # More transparent
                                 (int(screen_x), int(self.y)),
                                 int(size * 0.7))  # Smaller core
                
                # Position glow effect
                surface.blit(glow_surface,
                           (int(screen_x - glow_size), int(self.y - glow_size)))

class HighScores:
    def __init__(self):
        self.scores = []
        self.load_scores()
    
    def load_scores(self):
        try:
            if os.path.exists(HIGH_SCORES_FILE):
                with open(HIGH_SCORES_FILE, 'r') as f:
                    self.scores = json.load(f)
        except:
            self.scores = []
    
    def save_scores(self):
        with open(HIGH_SCORES_FILE, 'w') as f:
            json.dump(self.scores, f)
    
    def add_score(self, score, stats):
        # Create score entry
        score_entry = {
            'score': score,
            'kills': stats.kills,
            'accuracy': round(stats.accuracy, 1),
            'survival_time': stats.survival_time,
            'date': time.strftime('%Y-%m-%d %H:%M')
        }
        
        # Insert score in sorted position
        insert_pos = 0
        for i, entry in enumerate(self.scores):
            if score <= entry['score']:
                insert_pos = i + 1
        
        # Insert the new score
        self.scores.insert(insert_pos, score_entry)
        
        # Keep only top scores
        self.scores = self.scores[:MAX_HIGH_SCORES]
        
        # Save to file
        self.save_scores()
        
        # Return position (0 = new high score)
        return insert_pos

def load_texture(filename):
    try:
        texture = pygame.image.load(os.path.join('textures', filename))
        return pygame.transform.scale(texture, (TEXTURE_SIZE, TEXTURE_SIZE))
    except:
        # Create a default checkerboard texture if file not found
        texture = pygame.Surface((TEXTURE_SIZE, TEXTURE_SIZE))
        for y in range(TEXTURE_SIZE):
            for x in range(TEXTURE_SIZE):
                if (x // 8 + y // 8) % 2 == 0:
                    texture.set_at((x, y), WHITE)
                else:
                    texture.set_at((x, y), GRAY)
        return texture

# Create textures directory if it doesn't exist
os.makedirs('textures', exist_ok=True)

# Texture cache dictionary
texture_arrays = {}

# Wall types: 0 = empty, 1-4 = different wall textures, 5 = door
WALL_TEXTURES = {
    1: load_texture('wall1.png'),  # Stone wall
    2: load_texture('wall2.png'),  # Brick wall
    3: load_texture('wall3.png'),  # Wood wall
    4: load_texture('wall4.png'),  # Metal wall
    5: load_texture('door.png'),   # Door
}

class LevelState:
    def __init__(self, level_number=1):
        self.level_number = level_number
        self.config = LEVEL_CONFIGS[level_number]
        self.map = LEVEL_MAPS[level_number]
        self.state = LEVEL_STATE_EXPLORING
        self.secrets_found = 0
        self.enemies_killed = 0
        self.start_time = time.time()
        self.completion_time = 0
        self.transition_alpha = 0
        self.transition_text = ""
    
    def is_complete(self, enemies, player_x, player_y):
        if self.state != LEVEL_STATE_EXPLORING:
            return False
            
        # Check level-specific completion conditions
        if self.config['objective'] == 'Eliminate all enemies':
            return self.enemies_killed >= self.config['min_enemies']
        elif self.config['objective'] == 'Find the exit and eliminate the commander':
            commander_dead = any(not e.is_alive for e in enemies if e.type == ENEMY_COMMANDER)
            at_exit = self.is_at_exit(player_x, player_y)
            return commander_dead and at_exit
        elif self.config['objective'] == 'Survive the heavy trooper ambush':
            return self.enemies_killed >= self.config['min_enemies']
        return False
    
    def is_at_exit(self, player_x, player_y):
        # Convert player position to map coordinates
        map_x = int(player_x / TILE_SIZE)
        map_y = int(player_y / TILE_SIZE)
        
        # Check if player is at exit tile (6)
        if 0 <= map_y < len(self.map) and 0 <= map_x < len(self.map[0]):
            return self.map[map_y][map_x] == 6
        return False
    
    def check_secret_wall(self, x, y):
        # Convert position to map coordinates
        map_x = int(x / TILE_SIZE)
        map_y = int(y / TILE_SIZE)
        
        # Check if position is a secret wall
        if 0 <= map_y < len(self.map) and 0 <= map_x < len(self.map[0]):
            if self.map[map_y][map_x] == 7:  # Secret wall
                self.map[map_y][map_x] = 0  # Remove wall
                self.secrets_found += 1
                return True
        return False
    
    def calculate_bonus(self):
        bonus = 0
        # Completion bonus
        bonus += self.config['completion_bonus']
        
        # Secret bonus
        bonus += self.secrets_found * self.config['secret_bonus']
        
        # Time bonus (if completed under par time)
        if self.completion_time < self.config['par_time']:
            time_bonus = int((self.config['par_time'] - self.completion_time) * 10)
            bonus += time_bonus
        
        return bonus
    
    def start_transition(self):
        self.state = LEVEL_STATE_TRANSITION
        self.completion_time = time.time() - self.start_time
        bonus = self.calculate_bonus()
        
        if self.level_number < len(LEVEL_CONFIGS):
            self.transition_text = f"Level {self.level_number} Complete!\n"
        else:
            self.transition_text = "Congratulations! Game Complete!\n"
        
        self.transition_text += f"""
Bonus: {bonus} points
Secrets: {self.secrets_found}/{self.config['secret_count']}
Time: {int(self.completion_time)}s (Par: {self.config['par_time']}s)
"""

def draw_level_transition(surface, level_state):
    if level_state.state != LEVEL_STATE_TRANSITION:
        return
    
    # Create overlay with fade effect
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.fill(BLACK)
    overlay.set_alpha(level_state.transition_alpha)
    surface.blit(overlay, (0, 0))
    
    # Increase fade
    level_state.transition_alpha = min(255, level_state.transition_alpha + 5)
    
    # Only draw text when fade is complete
    if level_state.transition_alpha >= 255:
        font = pygame.font.Font(None, 48)
        y_offset = SCREEN_HEIGHT // 4
        
        # Draw each line of text
        for line in level_state.transition_text.split('\n'):
            if line.strip():
                text = font.render(line, True, WHITE)
                text_rect = text.get_rect(center=(SCREEN_WIDTH//2, y_offset))
                surface.blit(text, text_rect)
                y_offset += 50
        
        # Draw continue prompt
        if pygame.time.get_ticks() % 1000 < 500:  # Blinking effect
            prompt = font.render("Press SPACE to continue", True, YELLOW)
            prompt_rect = prompt.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT * 3//4))
            surface.blit(prompt, prompt_rect)

def spawn_enemies_for_level(level_state):
    enemies = []
    config = level_state.config
    map_data = level_state.map
    
    # Find valid spawn positions (empty spaces away from player start)
    valid_positions = []
    for y in range(len(map_data)):
        for x in range(len(map_data[0])):
            if map_data[y][x] == 0:  # Empty space
                # Check if far enough from player start
                if math.sqrt((x - 1.5)**2 + (y - 1.5)**2) > 5:
                    valid_positions.append((x, y))
    
    # Spawn minimum required enemies
    for _ in range(config['min_enemies']):
        if valid_positions:
            x, y = random.choice(valid_positions)
            valid_positions.remove((x, y))
            enemy_type = random.choice(config['enemy_types'])
            enemies.append(Enemy(x, y, enemy_type))
    
    return enemies

def spawn_powerups_for_level(level_state):
    powerups = []
    config = level_state.config
    map_data = level_state.map
    
    # Find valid spawn positions
    valid_positions = []
    for y in range(len(map_data)):
        for x in range(len(map_data[0])):
            if map_data[y][x] == 0:  # Empty space
                valid_positions.append((x, y))
    
    # Spawn powerups
    powerup_types = [POWERUP_HEALTH, POWERUP_AMMO, POWERUP_DAMAGE]
    for _ in range(config['powerup_count']):
        if valid_positions:
            x, y = random.choice(valid_positions)
            valid_positions.remove((x, y))
            powerup_type = random.choice(powerup_types)
            powerups.append(PowerUp(x, y, powerup_type))
    
    return powerups

# Player variables
player_x = TILE_SIZE * 1.5
player_y = TILE_SIZE * 1.5
player_angle = 0
player_speed = 2
player_rotation_speed = 3

# Door states (door_y, door_x): animation_state (0 = closed, 1 = open)
door_states = {}

def init_door_states():
    # Initialize all doors to closed state
    global door_states
    door_states = {}  # Reset door states
    current_map = level_state.map if level_state else LEVEL_MAPS[1]  # Default to first level if none set
    
    for y in range(len(current_map)):
        for x in range(len(current_map[y])):
            if current_map[y][x] == 5:  # Door
                door_states[(y, x)] = {'state': 0, 'animation': 0.0}  # state: 0=closed, 1=opening, 2=open, 3=closing

def find_doors_in_range():
    # Check for doors within interaction range
    doors = []
    player_map_x = player_x / TILE_SIZE
    player_map_y = player_y / TILE_SIZE
    current_map = level_state.map
    
    # Check nearby tiles for doors (within 2 tile radius)
    for y in range(max(0, int(player_map_y - 2)), min(len(current_map), int(player_map_y + 3))):
        for x in range(max(0, int(player_map_x - 2)), min(len(current_map[0]), int(player_map_x + 3))):
            if current_map[y][x] == 5:  # Door
                # Calculate distance to door
                door_center_x = x * TILE_SIZE + TILE_SIZE / 2
                door_center_y = y * TILE_SIZE + TILE_SIZE / 2
                distance = math.sqrt((player_x - door_center_x)**2 + (player_y - door_center_y)**2)
                
                # Check if player is facing the door
                dx = door_center_x - player_x
                dy = door_center_y - player_y
                angle_to_door = math.degrees(math.atan2(dy, dx))
                angle_diff = (angle_to_door - player_angle) % 360
                if angle_diff > 180:
                    angle_diff = 360 - angle_diff
                
                # Add door if it's close enough and player is roughly facing it
                if distance < TILE_SIZE * 2 and angle_diff < 60:
                    doors.append((y, x))  # Keep y,x order to match door_states dictionary
                    print(f"Found door at ({x}, {y}), distance: {distance/TILE_SIZE:.1f} tiles, angle: {angle_diff:.1f} degrees")  # Debug print
    
    return doors

def update_doors():
    for pos, state in door_states.items():
        if state['state'] == 1:  # Opening
            state['animation'] = min(1.0, state['animation'] + 0.1)
            if state['animation'] >= 1.0:
                state['state'] = 2  # Fully open
        elif state['state'] == 3:  # Closing
            state['animation'] = max(0.0, state['animation'] - 0.1)
            if state['animation'] <= 0.0:
                state['state'] = 0  # Fully closed

def is_door_blocking(x, y):
    map_x = int(x / TILE_SIZE)
    map_y = int(y / TILE_SIZE)
    current_map = level_state.map
    
    if 0 <= map_y < len(current_map) and 0 <= map_x < len(current_map[0]):
        if current_map[map_y][map_x] == 5:  # Door
            door_state = door_states.get((map_y, map_x))
            if door_state and door_state['animation'] < 0.8:  # Door is not open enough
                return True
    return False

def check_collision(x, y):
    # Convert position to map coordinates
    map_x = int(x / TILE_SIZE)
    map_y = int(y / TILE_SIZE)
    current_map = level_state.map
    
    # Check if position is out of bounds or in a wall
    if map_x < 0 or map_x >= len(current_map[0]) or map_y < 0 or map_y >= len(current_map):
        return True
    
    # Check for walls and doors
    if current_map[map_y][map_x] in [1, 2, 3, 4]:
        return True
    elif current_map[map_y][map_x] == 5:
        return is_door_blocking(x, y)
    
    return False

def get_wall_texture_column(texture, x):
    # Cache texture arrays for better performance
    texture_id = id(texture)
    if texture_id not in texture_arrays:
        texture_arrays[texture_id] = pygame.surfarray.array3d(texture)
    return texture_arrays[texture_id][:, int(x) % TEXTURE_SIZE]

def cast_rays():
    start_angle = player_angle - HALF_FOV
    current_map = level_state.map
    
    # Pre-calculate values
    angles = [math.radians(start_angle + STEP_ANGLE * ray) for ray in range(CASTED_RAYS)]
    cos_angles = [math.cos(angle) for angle in angles]
    sin_angles = [math.sin(angle) for angle in angles]
    
    # Create surface for walls
    wall_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    wall_surface.fill(BLACK)
    
    for ray in range(CASTED_RAYS):
        # Ray casting
        ray_x = player_x
        ray_y = player_y
        sin_a = sin_angles[ray]
        cos_a = cos_angles[ray]
        
        # Cast ray until we hit a wall
        for depth in range(0, MAX_DEPTH, 2):
            point_x = ray_x + depth * cos_a
            point_y = ray_y + depth * sin_a
            
            # Convert point to map position
            map_x = int(point_x / TILE_SIZE)
            map_y = int(point_y / TILE_SIZE)
            
            # Check if ray is out of bounds
            if map_x < 0 or map_x >= len(current_map[0]) or map_y < 0 or map_y >= len(current_map):
                break
            
            # Check if ray hit a wall or door
            wall_type = current_map[map_y][map_x]
            if wall_type > 0:
                # For doors, check animation state
                if wall_type == 5:  # Door
                    door_state = door_states.get((map_y, map_x))
                    if door_state:
                        # Skip if door is fully open
                        if door_state['animation'] >= 1.0:
                            continue
                        # Adjust wall height based on door animation
                        wall_height_factor = 1.0 - door_state['animation']
                    else:
                        wall_height_factor = 1.0
                else:
                    wall_height_factor = 1.0
                
                # Calculate distance and wall height
                distance = depth * math.cos(math.radians(start_angle + ray * STEP_ANGLE - player_angle))
                wall_height = min((TILE_SIZE * SCREEN_HEIGHT) / (distance + 0.0001), SCREEN_HEIGHT)
                wall_height *= wall_height_factor  # Apply door animation
                
                # Draw wall slice
                wall_top = int((SCREEN_HEIGHT - wall_height) / 2)
                
                # Calculate color based on distance and wall type
                shade = max(0.2, 1 - (distance / MAX_DEPTH))
                if wall_type == 5:  # Door
                    color = (int(255 * shade), int(50 * shade), int(50 * shade))  # Red for doors
                elif wall_type == 1:  # Stone walls
                    color = (int(200 * shade), int(200 * shade), int(200 * shade))  # Gray
                elif wall_type == 2:  # Brick walls
                    color = (int(180 * shade), int(100 * shade), int(100 * shade))  # Brownish
                elif wall_type == 3:  # Wood walls
                    color = (int(150 * shade), int(120 * shade), int(80 * shade))  # Brown
                else:  # Metal walls
                    color = (int(120 * shade), int(120 * shade), int(140 * shade))  # Bluish gray
                
                # Draw the wall slice
                pygame.draw.rect(
                    wall_surface,
                    color,
                    (ray * (SCREEN_WIDTH // CASTED_RAYS), wall_top, 
                     SCREEN_WIDTH // CASTED_RAYS + 1, wall_height)
                )
                break
    
    # Draw the wall surface to the screen
    screen.blit(wall_surface, (0, 0))

def slide_along_wall(new_x, new_y, old_x, old_y):
    # Try to slide along the wall by preserving one coordinate
    if not check_collision(new_x, old_y):
        return new_x, old_y
    if not check_collision(old_x, new_y):
        return old_x, new_y
    return old_x, old_y

def cast_ray_for_shooting(start_x, start_y, angle, max_range):
    # Returns hit position and type of wall hit (if any)
    sin_a = math.sin(math.radians(angle))
    cos_a = math.cos(math.radians(angle))
    
    for depth in range(0, int(max_range), 2):
        point_x = start_x + depth * cos_a
        point_y = start_y + depth * sin_a
        
        # Convert point to map position
        map_x = int(point_x / TILE_SIZE)
        map_y = int(point_y / TILE_SIZE)
        
        # Check if ray is out of bounds
        if map_x < 0 or map_x >= len(MAP[0]) or map_y < 0 or map_y >= len(MAP):
            return None, None
        
        # Check if ray hit a wall
        if MAP[map_y][map_x] > 0:
            return (point_x, point_y), MAP[map_y][map_x]
    
    return None, None

def draw_bullet_impact(surface, pos, wall_type):
    if pos:
        # Project the impact position to screen space
        # This is a simplified version - you might need to adjust based on your projection math
        rel_x = pos[0] - player_x
        rel_y = pos[1] - player_y
        
        # Calculate angle relative to player view
        angle = math.degrees(math.atan2(rel_y, rel_x)) - player_angle
        
        # Calculate screen position
        screen_x = (angle / FOV + 0.5) * SCREEN_WIDTH
        
        # Draw impact mark
        pygame.draw.circle(surface, YELLOW, (int(screen_x), SCREEN_HEIGHT//2), 3)

def cast_ray_to_enemy(start_x, start_y, end_x, end_y):
    # Returns the distance to the first wall hit, if any
    dx = end_x - start_x
    dy = end_y - start_y
    distance = math.sqrt(dx * dx + dy * dy)
    current_map = level_state.map
    
    if distance == 0:
        return None
    
    # Normalize direction
    dx = dx / distance
    dy = dy / distance
    
    # Step along the line in small increments
    step_size = TILE_SIZE / 4  # Small steps for accuracy
    steps = int(distance / step_size)
    
    for i in range(steps):
        # Calculate current position
        current_x = start_x + dx * i * step_size
        current_y = start_y + dy * i * step_size
        
        # Convert to map coordinates
        map_x = int(current_x / TILE_SIZE)
        map_y = int(current_y / TILE_SIZE)
        
        # Check if we hit a wall
        if map_x < 0 or map_x >= len(current_map[0]) or map_y < 0 or map_y >= len(current_map):
            return 0  # Hit map boundary
        
        if current_map[map_y][map_x] > 0 and current_map[map_y][map_x] != 5:  # Ignore doors for now
            return math.sqrt((current_x - start_x)**2 + (current_y - start_y)**2)
    
    return None  # No wall between points

def check_enemy_hit(start_x, start_y, base_angle, max_range, enemies, spread_angles=[0]):
    hits = []
    current_map = level_state.map
    for spread in spread_angles:
        angle = base_angle + spread
        sin_a = math.sin(math.radians(angle))
        cos_a = math.cos(math.radians(angle))
        
        # Cast ray in small steps
        step_size = TILE_SIZE / 8
        hit_wall = False
        
        for depth in range(0, int(max_range), int(step_size)):
            ray_x = start_x + depth * cos_a
            ray_y = start_y + depth * sin_a
            
            # Check for wall hits first
            map_x = int(ray_x / TILE_SIZE)
            map_y = int(ray_y / TILE_SIZE)
            
            if map_x < 0 or map_x >= len(current_map[0]) or map_y < 0 or map_y >= len(current_map):
                hits.append((None, (ray_x, ray_y), None))
                hit_wall = True
                break
            
            # Check for walls and doors
            tile_type = current_map[map_y][map_x]
            if tile_type > 0:  # Any non-empty tile
                if tile_type == 5:  # Door
                    # Check door state
                    door_state = door_states.get((map_y, map_x))
                    if door_state and door_state['animation'] < 0.8:  # Door is not open enough
                        hits.append((None, (ray_x, ray_y), tile_type))
                        hit_wall = True
                        break
                elif tile_type != 6:  # Not an exit
                    hits.append((None, (ray_x, ray_y), tile_type))
                    hit_wall = True
                    break
            
            # Only check for enemy hits if we haven't hit a wall
            if not hit_wall:
                for enemy in enemies:
                    if enemy.is_alive:
                        dx = enemy.x - ray_x
                        dy = enemy.y - ray_y
                        distance = math.sqrt(dx * dx + dy * dy)
                        
                        if distance < enemy.size * 0.8:
                            hits.append((enemy, (ray_x, ray_y), None))
                            break
                
                if len(hits) > 0 and hits[-1][0] is not None:  # If we hit an enemy
                    break
    
    # Return the first enemy hit, or the closest wall hit if no enemies were hit
    enemy_hits = [hit for hit in hits if hit[0] is not None]
    if enemy_hits:
        return enemy_hits[0]
    
    wall_hits = [hit for hit in hits if hit[1] is not None]
    return wall_hits[0] if wall_hits else (None, None, None)

class Enemy:
    def __init__(self, x, y, enemy_type=ENEMY_GUARD):
        self.x = x * TILE_SIZE + TILE_SIZE // 2
        self.y = y * TILE_SIZE + TILE_SIZE // 2
        self.type = enemy_type
        self.config = ENEMY_CONFIGS[enemy_type]
        self.health = self.config['health']
        self.speed = self.config['speed']
        self.size = self.config['size']
        self.damage = self.config['damage']
        self.attack_range = self.config['attack_range']
        self.chase_range = self.config['chase_range']
        self.attack_cooldown = 0
        self.max_attack_cooldown = 90
        self.state = 'patrol'
        self.patrol_point = 0
        self.is_alive = True
        self.hit_cooldown = 0
        self.hit_pos = None
        self.hit_flash = 0
        self.buffed = False
        self.dodge_direction = 1
        self.dodge_timer = 0
        self.alerted = False
        
        # For commander's buff tracking
        self.buff_targets = set()
    
    def update(self, player_x, player_y, enemies=None):
        if not self.is_alive:
            return 0
            
        # Update hit visual feedback
        if self.hit_cooldown > 0:
            self.hit_cooldown -= 1
            
        # Update attack cooldown
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        
        # Calculate distance to player
        dx = player_x - self.x
        dy = player_y - self.y
        distance = math.sqrt(dx * dx + dy * dy)
        
        # Commander buff ability
        if self.type == ENEMY_COMMANDER and enemies:
            self.buff_targets.clear()
            for enemy in enemies:
                if enemy != self and enemy.is_alive:
                    buff_dx = enemy.x - self.x
                    buff_dy = enemy.y - self.y
                    buff_distance = math.sqrt(buff_dx * buff_dx + buff_dy * buff_dy)
                    if buff_distance <= self.config['buff_range']:
                        enemy.buffed = True
                        self.buff_targets.add(enemy)
                    elif enemy in self.buff_targets:
                        enemy.buffed = False
        
        # Scout alerting behavior
        if self.type == ENEMY_SCOUT and distance < self.chase_range and enemies:
            for enemy in enemies:
                if enemy != self and enemy.is_alive and not enemy.alerted:
                    enemy.alerted = True
                    enemy.state = 'chase'
        
        # State machine
        if distance < self.attack_range:
            self.state = 'attack'
        elif distance < self.chase_range or self.alerted:
            self.state = 'chase'
        else:
            self.state = 'patrol'
        
        # Handle states
        if self.state == 'attack':
            if self.attack_cooldown <= 0:
                self.attack_cooldown = self.max_attack_cooldown
                # Only deal damage if there's line of sight
                wall_distance = cast_ray_to_enemy(player_x, player_y, self.x, self.y)
                if wall_distance is None or wall_distance > distance:
                    return self.get_damage()
        elif self.state == 'chase':
            # Scout dodging behavior
            if self.type == ENEMY_SCOUT:
                self.dodge_timer += 1
                if self.dodge_timer > 30:  # Change direction every half second
                    self.dodge_timer = 0
                    self.dodge_direction = -self.dodge_direction
                
                # Add perpendicular movement for dodging
                dodge_dx = -dy * self.dodge_direction * 0.5
                dodge_dy = dx * self.dodge_direction * 0.5
                
                # Combine chase and dodge movements
                move_dx = (dx + dodge_dx) * self.speed / distance
                move_dy = (dy + dodge_dy) * self.speed / distance
            else:
                # Normal chase movement
                move_dx = dx * self.speed / distance
                move_dy = dy * self.speed / distance
            
            # Move towards player but maintain minimum distance
            if distance > self.attack_range * 0.75:
                if not check_collision(self.x + move_dx, self.y + move_dy):
                    self.x += move_dx
                    self.y += move_dy
        elif self.state == 'patrol':
            # Different patrol patterns based on enemy type
            if self.type == ENEMY_SCOUT:
                # Wider, faster patrol
                patrol_points = [
                    (self.x + TILE_SIZE * 3, self.y),
                    (self.x - TILE_SIZE * 3, self.y),
                    (self.x, self.y + TILE_SIZE * 3),
                    (self.x, self.y - TILE_SIZE * 3)
                ]
            elif self.type == ENEMY_HEAVY:
                # Smaller patrol area
                patrol_points = [
                    (self.x + TILE_SIZE, self.y),
                    (self.x - TILE_SIZE, self.y)
                ]
            else:
                # Standard patrol
                patrol_points = [
                    (self.x + TILE_SIZE * 2, self.y),
                    (self.x - TILE_SIZE * 2, self.y)
                ]
            
            target = patrol_points[self.patrol_point]
            dx = target[0] - self.x
            dy = target[1] - self.y
            
            if abs(dx) < self.speed and abs(dy) < self.speed:
                self.patrol_point = (self.patrol_point + 1) % len(patrol_points)
            else:
                if not check_collision(self.x + math.copysign(self.speed, dx),
                                     self.y + math.copysign(self.speed, dy)):
                    self.x += math.copysign(self.speed, dx)
                    self.y += math.copysign(self.speed, dy)
        
        return 0
    
    def get_damage(self):
        # Apply commander buff if active
        damage = self.damage
        if self.buffed:
            damage = int(damage * ENEMY_CONFIGS[ENEMY_COMMANDER]['buff_multiplier'])
        return damage
    
    def take_damage(self, damage, hit_pos):
        # Scout dodge chance
        if self.type == ENEMY_SCOUT and random.random() < self.config['dodge_chance']:
            return False  # Dodged the hit
            
        self.health -= damage
        self.hit_cooldown = 10
        self.hit_pos = hit_pos
        self.hit_flash = 5
        
        # Create blood particles
        angle = random.uniform(0, 360)  # Random spray direction
        for _ in range(10):  # Create 10 particles per hit
            BLOOD_PARTICLES.append(BloodParticle(hit_pos[0], hit_pos[1], angle))
        
        if self.health <= 0:
            self.is_alive = False
            # Create more particles for death
            for _ in range(20):
                BLOOD_PARTICLES.append(BloodParticle(self.x, self.y, random.uniform(0, 360)))
            # Clear commander buffs if this was a commander
            if self.type == ENEMY_COMMANDER:
                for enemy in self.buff_targets:
                    enemy.buffed = False
            return True
        return False
    
    def draw(self, surface, player_x, player_y, player_angle):
        if not self.is_alive:
            return
            
        # Calculate relative position to player
        dx = self.x - player_x
        dy = self.y - player_y
        
        # Calculate angle to enemy relative to player's view
        enemy_angle = math.degrees(math.atan2(dy, dx))
        relative_angle = (enemy_angle - player_angle) % 360
        
        # Calculate distance
        distance = math.sqrt(dx * dx + dy * dy)
        
        # Check if enemy is hidden behind a wall using ray casting
        current_map = level_state.map
        step_size = TILE_SIZE / 4  # Smaller steps for more accurate collision
        steps = int(distance / step_size)
        
        # Normalize direction vector
        if distance > 0:
            ray_dx = dx / distance
            ray_dy = dy / distance
            
            # Step along the line from player to enemy
            for i in range(steps):
                check_x = player_x + ray_dx * i * step_size
                check_y = player_y + ray_dy * i * step_size
                
                # Convert to map coordinates
                map_x = int(check_x / TILE_SIZE)
                map_y = int(check_y / TILE_SIZE)
                
                # Check if we hit a wall
                if (map_x < 0 or map_x >= len(current_map[0]) or 
                    map_y < 0 or map_y >= len(current_map)):
                    return  # Out of bounds
                
                tile = current_map[map_y][map_x]
                if tile > 0:  # Wall or door
                    if tile == 5:  # Door
                        door_state = door_states.get((map_y, map_x))
                        if not door_state or door_state['animation'] < 0.8:
                            return  # Door is blocking view
                    elif tile != 6:  # Not an exit
                        return  # Wall is blocking view
        
        # Only draw if in field of view
        relative_angle = relative_angle % 360
        if relative_angle > 180:
            relative_angle = relative_angle - 360
            
        if abs(relative_angle) < FOV / 2:
            # Calculate screen position based on angle
            screen_x = SCREEN_WIDTH / 2 + (relative_angle / (FOV / 2)) * (SCREEN_WIDTH / 2)
            
            # Calculate size based on distance with perspective correction
            size = (self.size * SCREEN_HEIGHT) / (distance * math.cos(math.radians(relative_angle)))
            
            # Only draw if in front of player and not too close
            if distance > TILE_SIZE / 2:
                # Get base color
                color = self.config['color']
                
                # Modify color based on state
                if self.buffed:
                    # Add golden tint for buffed enemies
                    color = tuple(min(255, c + 50) for c in color)
                elif self.hit_cooldown > 0:
                    # Flash white when hit
                    color = HEALTH_RED
                
                # Draw enemy
                pygame.draw.rect(surface, color,
                               (screen_x - size/4,
                                (SCREEN_HEIGHT - size) / 2,
                                size/2,
                                size))
                
                # Draw commander aura
                if self.type == ENEMY_COMMANDER:
                    aura_surface = pygame.Surface((int(size), int(size)), pygame.SRCALPHA)
                    pygame.draw.circle(aura_surface, (*self.config['color'], 100),
                                    (int(size/2), int(size/2)), int(size/2))
                    surface.blit(aura_surface,
                               (screen_x - size/2, (SCREEN_HEIGHT - size) / 2))
                
                # Draw hit effect
                if self.hit_flash > 0:
                    self.hit_flash -= 1
                    if self.hit_pos:
                        # Project hit position to screen space
                        hit_dx = self.hit_pos[0] - player_x
                        hit_dy = self.hit_pos[1] - player_y
                        hit_angle = math.degrees(math.atan2(hit_dy, hit_dx))
                        hit_relative_angle = (hit_angle - player_angle) % 360
                        if hit_relative_angle > 180:
                            hit_relative_angle -= 360
                        
                        if abs(hit_relative_angle) < FOV / 2:
                            hit_screen_x = SCREEN_WIDTH / 2 + (hit_relative_angle / (FOV / 2)) * (SCREEN_WIDTH / 2)
                            pygame.draw.circle(surface, YELLOW,
                                            (int(hit_screen_x),
                                             int((SCREEN_HEIGHT - size) / 2 + size/2)), 5)

class GameStats:
    def __init__(self):
        self.score = 0
        self.kills = 0
        self.shots_fired = 0
        self.shots_hit = 0
        self.time_started = time.time()
        self.accuracy = 0
        self.survival_time = 0
    
    def update(self):
        self.survival_time = int(time.time() - self.time_started)
        self.accuracy = (self.shots_hit / self.shots_fired * 100) if self.shots_fired > 0 else 0
    
    def add_score(self, points):
        self.score += points
    
    def enemy_killed(self):
        self.kills += 1
        self.add_score(100)  # 100 points per kill
    
    def shot_fired(self, hit=False):
        self.shots_fired += 1
        if hit:
            self.shots_hit += 1
            self.add_score(10)  # 10 points per hit

def draw_high_scores(surface):
    # Create a semi-transparent overlay
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.fill(BLACK)
    surface.blit(overlay, (0, 0))
    
    # Create font objects
    title_font = pygame.font.Font(None, 74)
    score_font = pygame.font.Font(None, 48)
    detail_font = pygame.font.Font(None, 36)
    
    # Draw title
    title_text = title_font.render("HIGH SCORES", True, YELLOW)
    title_rect = title_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/6))
    surface.blit(title_text, title_rect)
    
    # Load high scores
    high_scores = HighScores()
    
    if not high_scores.scores:
        # No scores yet
        no_scores_text = score_font.render("No scores yet!", True, WHITE)
        text_rect = no_scores_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2))
        surface.blit(no_scores_text, text_rect)
    else:
        # Draw scores
        for i, score in enumerate(high_scores.scores):
            # Position for this score entry
            base_y = SCREEN_HEIGHT/3 + i * 100
            
            # Draw rank
            rank_text = score_font.render(f"#{i+1}", True, WHITE)
            surface.blit(rank_text, (SCREEN_WIDTH/4, base_y))
            
            # Draw score
            score_text = score_font.render(str(score['score']), True, YELLOW)
            surface.blit(score_text, (SCREEN_WIDTH/2 - score_text.get_width()/2, base_y))
            
            # Draw details
            details_text = detail_font.render(
                f"Kills: {score['kills']} | Accuracy: {score['accuracy']}% | Time: {score['survival_time']}s",
                True, WHITE
            )
            surface.blit(details_text, (SCREEN_WIDTH/2 - details_text.get_width()/2, base_y + 40))
            
            # Draw date
            date_text = detail_font.render(score['date'], True, GRAY)
            surface.blit(date_text, (SCREEN_WIDTH*3/4 - date_text.get_width()/2, base_y))
    
    # Draw instructions
    back_text = detail_font.render("Press SPACE to continue", True, WHITE)
    text_rect = back_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT*7/8))
    surface.blit(back_text, text_rect)

def draw_game_over_screen(surface, stats, high_scores):
    # Create a semi-transparent overlay
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    pygame.draw.rect(overlay, TRANSPARENT_BLACK, (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
    surface.blit(overlay, (0, 0))
    
    # Create font objects
    big_font = pygame.font.Font(None, 74)
    medium_font = pygame.font.Font(None, 48)
    small_font = pygame.font.Font(None, 36)
    
    # Game Over text
    game_over_text = big_font.render("GAME OVER", True, RED)
    text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/6))
    surface.blit(game_over_text, text_rect)
    
    # Check if it's a high score
    score_position = high_scores.add_score(stats.score, stats)
    if score_position < MAX_HIGH_SCORES:
        if score_position == 0:
            new_record_text = medium_font.render("NEW HIGH SCORE!", True, YELLOW)
        else:
            new_record_text = medium_font.render(f"TOP {score_position + 1} SCORE!", True, YELLOW)
        text_rect = new_record_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/4))
        surface.blit(new_record_text, text_rect)
    
    # Stats
    stats_texts = [
        f"Score: {stats.score}",
        f"Enemies Defeated: {stats.kills}",
        f"Accuracy: {stats.accuracy:.1f}%",
        f"Survival Time: {stats.survival_time}s"
    ]
    
    # Increased vertical spacing between stats
    vertical_spacing = 60
    start_y = SCREEN_HEIGHT/2 - (len(stats_texts) * vertical_spacing) / 2
    
    for i, text in enumerate(stats_texts):
        stat_surface = medium_font.render(text, True, WHITE)
        text_rect = stat_surface.get_rect(
            center=(SCREEN_WIDTH/2, start_y + i * vertical_spacing)
        )
        surface.blit(stat_surface, text_rect)
    
    # Instructions
    instructions = [
        ("Press SPACE to view high scores", WHITE),
        ("Press ESC to return to main menu", YELLOW)
    ]
    
    for i, (text, color) in enumerate(instructions):
        instruction_text = small_font.render(text, True, color)
        text_rect = instruction_text.get_rect(
            center=(SCREEN_WIDTH/2, SCREEN_HEIGHT * (6+i)/8)
        )
        surface.blit(instruction_text, text_rect)

def reset_game(level_number=1):
    global player_x, player_y, player_angle
    # Reset player position
    player_x = TILE_SIZE * 1.5
    player_y = TILE_SIZE * 1.5
    player_angle = 0
    
    # Create new instances
    weapons = {
        WEAPON_PISTOL: Weapon(WEAPON_PISTOL),
        WEAPON_SHOTGUN: Weapon(WEAPON_SHOTGUN),
        WEAPON_RIFLE: Weapon(WEAPON_RIFLE)
    }
    current_weapon_type = WEAPON_PISTOL
    weapon = weapons[current_weapon_type]
    stats = GameStats()
    
    # Initialize level
    level_state = LevelState(level_number)
    
    # Spawn enemies and powerups for the level
    enemies = spawn_enemies_for_level(level_state)
    powerups = spawn_powerups_for_level(level_state)
    
    return weapons, current_weapon_type, weapon, stats, enemies, powerups, level_state

def draw_main_menu(surface):
    # Create a semi-transparent overlay
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.fill(BLACK)
    surface.blit(overlay, (0, 0))
    
    # Title
    title_font = pygame.font.Font(None, 100)
    title_text = title_font.render("WOLFENSTEIN 3D", True, RED)
    title_rect = title_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/4))
    surface.blit(title_text, title_rect)
    
    # Create menu buttons
    buttons = {
        'start': Button(SCREEN_WIDTH/2 - 100, SCREEN_HEIGHT/2 - 60, 200, 60, "Start Game"),
        'high_scores': Button(SCREEN_WIDTH/2 - 100, SCREEN_HEIGHT/2 + 20, 200, 60, "High Scores"),
        'quit': Button(SCREEN_WIDTH/2 - 100, SCREEN_HEIGHT/2 + 100, 200, 60, "Quit")
    }
    
    for button in buttons.values():
        button.draw(surface)
    
    return buttons

def draw_pause_menu(surface):
    # Create a semi-transparent overlay
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))  # Semi-transparent black
    surface.blit(overlay, (0, 0))
    
    # Title
    title_font = pygame.font.Font(None, 74)
    title_text = title_font.render("PAUSED", True, WHITE)
    title_rect = title_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/4))
    surface.blit(title_text, title_rect)
    
    # Create menu buttons
    buttons = {
        'resume': Button(SCREEN_WIDTH/2 - 100, SCREEN_HEIGHT/2 - 30, 200, 60, "Resume"),
        'main_menu': Button(SCREEN_WIDTH/2 - 100, SCREEN_HEIGHT/2 + 50, 200, 60, "Main Menu")
    }
    
    for button in buttons.values():
        button.draw(surface)
    
    return buttons

def draw_minimap(surface, player_x, player_y, player_angle, enemies, scale=0.2):
    current_map = level_state.map
    # Calculate minimap dimensions
    map_width = len(current_map[0]) * TILE_SIZE * scale
    map_height = len(current_map) * TILE_SIZE * scale
    
    # Create minimap surface with transparency
    minimap = pygame.Surface((map_width, map_height), pygame.SRCALPHA)
    
    # Draw walls and doors
    for y in range(len(current_map)):
        for x in range(len(current_map[y])):
            if current_map[y][x] > 0:  # Wall or door
                color = (200, 200, 200, 160)  # Default wall color
                if current_map[y][x] == 5:  # Door
                    door_state = door_states.get((y, x))
                    if door_state and door_state['state'] in [1, 2]:  # Opening or open
                        color = (0, 255, 0, 160)  # Green for open doors
                    else:
                        color = (255, 0, 0, 160)  # Red for closed doors
                elif current_map[y][x] == 6:  # Exit
                    color = (255, 215, 0, 160)  # Gold for exit
                elif current_map[y][x] == 7:  # Secret wall
                    color = (128, 0, 128, 160)  # Purple for secret walls
                
                pygame.draw.rect(minimap, color,
                               (x * TILE_SIZE * scale,
                                y * TILE_SIZE * scale,
                                TILE_SIZE * scale,
                                TILE_SIZE * scale))
    
    # Draw enemies
    for enemy in enemies:
        if enemy.is_alive:
            # Calculate enemy position on minimap
            enemy_x = (enemy.x / TILE_SIZE) * (TILE_SIZE * scale)
            enemy_y = (enemy.y / TILE_SIZE) * (TILE_SIZE * scale)
            # Draw enemy as a red dot
            pygame.draw.circle(minimap, (255, 0, 0, 200),
                             (int(enemy_x), int(enemy_y)),
                             int(3))
    
    # Draw player
    player_map_x = (player_x / TILE_SIZE) * (TILE_SIZE * scale)
    player_map_y = (player_y / TILE_SIZE) * (TILE_SIZE * scale)
    
    # Draw player direction line
    line_length = 10
    end_x = player_map_x + math.cos(math.radians(player_angle)) * line_length
    end_y = player_map_y + math.sin(math.radians(player_angle)) * line_length
    pygame.draw.line(minimap, (0, 255, 0, 200),
                    (player_map_x, player_map_y),
                    (end_x, end_y), 2)
    
    # Draw player position
    pygame.draw.circle(minimap, (0, 255, 0, 200),
                      (int(player_map_x), int(player_map_y)),
                      int(4))
    
    # Draw minimap background and border
    margin = 10
    background = pygame.Surface((map_width + margin * 2, map_height + margin * 2), pygame.SRCALPHA)
    pygame.draw.rect(background, (0, 0, 0, 128), background.get_rect())
    pygame.draw.rect(background, (255, 255, 255, 200), background.get_rect(), 2)
    
    # Blit minimap onto background
    background.blit(minimap, (margin, margin))
    
    # Position minimap in top-right corner with margin
    minimap_x = SCREEN_WIDTH - background.get_width() - margin
    minimap_y = margin
    surface.blit(background, (minimap_x, minimap_y))

def game_loop():
    global player_x, player_y, player_angle, level_state
    clock = pygame.time.Clock()
    running = True
    fps_font = pygame.font.Font(None, 36)
    hud_font = pygame.font.Font(None, 48)
    
    # Initialize game state
    game_state = GAME_STATE_MAIN_MENU
    weapons, current_weapon_type, weapon, stats, enemies, powerups, level_state = reset_game()
    
    # Initialize player stats
    player_health = MAX_HEALTH
    last_damage_time = 0
    DAMAGE_COOLDOWN = 30
    
    # Mouse settings for game
    MOUSE_SENSITIVITY = 0.2
    
    # Initialize door states
    init_door_states()
    
    # Impact marks list
    impact_marks = []
    
    # Menu buttons
    main_menu_buttons = None
    pause_menu_buttons = None
    
    # Initialize high scores
    high_scores = HighScores()
    
    while running:
        current_time = pygame.time.get_ticks()
        
        # Handle mouse visibility and grab
        pygame.mouse.set_visible(game_state in [GAME_STATE_MAIN_MENU, GAME_STATE_PAUSED, GAME_STATE_GAME_OVER])
        if game_state == GAME_STATE_PLAYING:
            pygame.event.set_grab(True)
        else:
            pygame.event.set_grab(False)
        
        # Update game elements if playing
        if game_state == GAME_STATE_PLAYING:
            weapon.update()
            update_doors()
            
            # Update power-ups
            for powerup in powerups:
                powerup.update()
                
                # Check for power-up collection
                if powerup.active:
                    dx = player_x - powerup.x
                    dy = player_y - powerup.y
                    distance = math.sqrt(dx * dx + dy * dy)
                    if distance < TILE_SIZE / 2:
                        player_health, collected = powerup.collect(
                            player_health, weapons, current_weapon_type, current_time
                        )
                        if collected:
                            stats.add_score(50)  # 50 points for collecting power-up
            
            # Check for level completion
            if level_state.is_complete(enemies, player_x, player_y):
                level_state.start_transition()
                stats.add_score(level_state.calculate_bonus())
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if game_state == GAME_STATE_PLAYING:
                        game_state = GAME_STATE_PAUSED
                        pause_menu_buttons = None
                    elif game_state == GAME_STATE_PAUSED:
                        game_state = GAME_STATE_PLAYING
                    elif game_state == GAME_STATE_GAME_OVER:
                        game_state = GAME_STATE_MAIN_MENU
                        main_menu_buttons = None
                    elif game_state == GAME_STATE_HIGH_SCORES:
                        game_state = GAME_STATE_MAIN_MENU
                        main_menu_buttons = None
                elif event.key == pygame.K_SPACE:
                    if game_state == GAME_STATE_GAME_OVER:
                        game_state = GAME_STATE_HIGH_SCORES
                    elif game_state == GAME_STATE_HIGH_SCORES:
                        game_state = GAME_STATE_MAIN_MENU
                        main_menu_buttons = None
                    elif level_state.state == LEVEL_STATE_TRANSITION:
                        if level_state.level_number < len(LEVEL_CONFIGS):
                            # Start next level
                            weapons, current_weapon_type, weapon, stats, enemies, powerups, level_state = reset_game(level_state.level_number + 1)
                            player_health = MAX_HEALTH
                        else:
                            # Game complete, show high scores
                            game_state = GAME_STATE_HIGH_SCORES
                # Weapon switching
                elif game_state == GAME_STATE_PLAYING:
                    if event.key in [pygame.K_1, pygame.K_2, pygame.K_3]:
                        # Map number keys to weapons
                        weapon_map = {
                            pygame.K_1: WEAPON_PISTOL,
                            pygame.K_2: WEAPON_SHOTGUN,
                            pygame.K_3: WEAPON_RIFLE
                        }
                        new_weapon_type = weapon_map[event.key]
                        if new_weapon_type != current_weapon_type:
                            current_weapon_type = new_weapon_type
                            weapon = weapons[current_weapon_type]
            
            # Handle menu interactions
            if game_state == GAME_STATE_MAIN_MENU:
                if main_menu_buttons is None:
                    main_menu_buttons = draw_main_menu(screen)
                for name, button in main_menu_buttons.items():
                    if button.handle_event(event):
                        if name == 'start':
                            game_state = GAME_STATE_PLAYING
                            weapons, current_weapon_type, weapon, stats, enemies, powerups, level_state = reset_game()
                            player_health = MAX_HEALTH
                            impact_marks = []
                        elif name == 'high_scores':
                            game_state = GAME_STATE_HIGH_SCORES
                        elif name == 'quit':
                            running = False
            
            elif game_state == GAME_STATE_PAUSED:
                if pause_menu_buttons is None:
                    pause_menu_buttons = draw_pause_menu(screen)
                for name, button in pause_menu_buttons.items():
                    if button.handle_event(event):
                        if name == 'resume':
                            game_state = GAME_STATE_PLAYING
                        elif name == 'main_menu':
                            game_state = GAME_STATE_MAIN_MENU
                            main_menu_buttons = None
            
            # Handle game inputs
            elif game_state == GAME_STATE_PLAYING:
                if event.type == pygame.MOUSEMOTION:
                    mouse_rel_x = event.rel[0]
                    player_angle += mouse_rel_x * MOUSE_SENSITIVITY
                    player_angle = player_angle % 360
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left click
                        if weapon.fire():
                            stats.shot_fired()
                            # Check for damage powerup effect
                            damage_multiplier = 1.0
                            for powerup in powerups:
                                if powerup.type == POWERUP_DAMAGE and powerup.is_effect_active(current_time):
                                    damage_multiplier = powerup.config['multiplier']
                                    break
                            
                            hit_enemy, hit_pos, wall_type = check_enemy_hit(
                                player_x, player_y, player_angle, weapon.max_range,
                                enemies, weapon.get_spread_angles()
                            )
                            
                            if hit_enemy:
                                stats.shot_fired(hit=True)
                                # Apply damage multiplier
                                damage = int(weapon.bullet_damage * damage_multiplier)
                                if hit_enemy.take_damage(damage, hit_pos):
                                    stats.enemy_killed()
                                    level_state.enemies_killed += 1
                                    # Add score based on enemy type
                                    stats.add_score(ENEMY_CONFIGS[hit_enemy.type]['score'])
                                    
                                    # Check for powerup spawn
                                    if random.random() < ENEMY_CONFIGS[hit_enemy.type]['powerup_chance']:
                                        powerup_type = random.choice([POWERUP_HEALTH, POWERUP_AMMO, POWERUP_DAMAGE])
                                        powerups.append(PowerUp(
                                            hit_enemy.x // TILE_SIZE,
                                            hit_enemy.y // TILE_SIZE,
                                            powerup_type
                                        ))
                            
                            impact_marks.append((hit_pos, None, 30))
                            break
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_e:
                    # Check for doors
                    nearby_doors = find_doors_in_range()
                    for door_pos in nearby_doors:
                        door_state = door_states.get(door_pos)
                        if door_state:
                            if door_state['state'] in [0, 3]:  # Closed or closing
                                print(f"Opening door at {door_pos}")  # Debug print
                                door_state['state'] = 1  # Start opening
                            elif door_state['state'] in [1, 2]:  # Opening or open
                                print(f"Closing door at {door_pos}")  # Debug print
                                door_state['state'] = 3  # Start closing
                    
                    # Check for secret walls
                    if level_state.check_secret_wall(player_x, player_y):
                        stats.add_score(100)  # Bonus for finding secret
        
        # Clear screen
        screen.fill(BLACK)
        
        # Draw game state
        if game_state == GAME_STATE_PLAYING or game_state == GAME_STATE_PAUSED:
            # Draw game world
            pygame.draw.rect(screen, (50, 50, 50), (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT // 2))
            pygame.draw.rect(screen, (80, 80, 80), (0, SCREEN_HEIGHT // 2, SCREEN_WIDTH, SCREEN_HEIGHT // 2))
            
            # Use current level's map for ray casting
            MAP = level_state.map
            cast_rays()
            
            # Update and draw game elements
            if game_state == GAME_STATE_PLAYING:
                if current_time - last_damage_time >= DAMAGE_COOLDOWN:
                    for enemy in enemies:
                        damage = enemy.update(player_x, player_y)
                        if damage > 0:
                            player_health = max(0, player_health - damage)
                            last_damage_time = current_time
                            if player_health <= 0:
                                game_state = GAME_STATE_GAME_OVER
                            break
            
            # Draw impact marks
            for i in range(len(impact_marks)-1, -1, -1):
                pos, wall_type, time = impact_marks[i]
                draw_bullet_impact(screen, pos, wall_type)
                impact_marks[i] = (pos, wall_type, time - 1)
                if time <= 0:
                    impact_marks.pop(i)
            
            # Draw enemies
            for enemy in enemies:
                enemy.draw(screen, player_x, player_y, player_angle)
            
            # Draw weapon
            weapon.draw(screen)
            
            # Draw minimap
            draw_minimap(screen, player_x, player_y, player_angle, enemies)
            
            # Draw HUD if not paused
            if game_state == GAME_STATE_PLAYING:
                # Health bar
                health_width = 200
                health_height = 20
                health_x = SCREEN_WIDTH - health_width - 20
                health_y = SCREEN_HEIGHT - 40
                
                pygame.draw.rect(screen, DARK_GRAY, 
                               (health_x, health_y, health_width, health_height))
                health_fill = (health_width * player_health) // MAX_HEALTH
                pygame.draw.rect(screen, HEALTH_RED,
                               (health_x, health_y, health_fill, health_height))
                pygame.draw.rect(screen, WHITE,
                               (health_x, health_y, health_width, health_height), 2)
                
                # Health text
                health_text = hud_font.render(f'{player_health}', True, WHITE)
                screen.blit(health_text, (health_x - 50, health_y - 5))
                
                # Weapon info
                weapon_text = hud_font.render(f'{current_weapon_type.upper()}', True, WHITE)
                screen.blit(weapon_text, (20, SCREEN_HEIGHT - 80))
                
                # Ammo counter
                ammo_text = hud_font.render(f'AMMO: {weapon.ammo}', True, AMMO_BLUE)
                screen.blit(ammo_text, (20, SCREEN_HEIGHT - 40))
                
                # Score and level info
                score_text = hud_font.render(f'Score: {stats.score}', True, YELLOW)
                screen.blit(score_text, (20, 20))
                level_text = hud_font.render(f'Level {level_state.level_number}: {level_state.config["name"]}', True, WHITE)
                screen.blit(level_text, (20, 60))
                objective_text = hud_font.render(f'Objective: {level_state.config["objective"]}', True, GREEN)
                screen.blit(objective_text, (20, 100))
                
                # Secrets counter
                secrets_text = hud_font.render(f'Secrets: {level_state.secrets_found}/{level_state.config["secret_count"]}', True, YELLOW)
                screen.blit(secrets_text, (20, 140))
                
                # FPS counter
                fps = clock.get_fps()
                fps_text = fps_font.render(f'FPS: {int(fps)}', True, GREEN)
                screen.blit(fps_text, (SCREEN_WIDTH - 100, 20))
                
                # Draw power-ups
                for powerup in powerups:
                    powerup.draw(screen, player_x, player_y, player_angle)
                
                # Draw damage multiplier if active
                for powerup in powerups:
                    if powerup.type == POWERUP_DAMAGE and powerup.is_effect_active(current_time):
                        time_left = (powerup.effect_start_time + powerup.effect_duration - current_time) / 1000
                        multiplier_text = hud_font.render(f'DAMAGE x{powerup.config["multiplier"]:.1f} ({time_left:.1f}s)', True, powerup.config['color'])
                        screen.blit(multiplier_text, (20, 180))
                        break
            
            # Handle player movement if playing
            if game_state == GAME_STATE_PLAYING and level_state.state == LEVEL_STATE_EXPLORING:
                keys = pygame.key.get_pressed()
                old_x, old_y = player_x, player_y
                cos_a = math.cos(math.radians(player_angle))
                sin_a = math.sin(math.radians(player_angle))
                
                new_x, new_y = player_x, player_y
                
                if keys[pygame.K_w]:
                    new_x += player_speed * cos_a
                    new_y += player_speed * sin_a
                if keys[pygame.K_s]:
                    new_x -= player_speed * cos_a
                    new_y -= player_speed * sin_a
                if keys[pygame.K_a]:
                    new_x += player_speed * sin_a
                    new_y -= player_speed * cos_a
                if keys[pygame.K_d]:
                    new_x -= player_speed * sin_a
                    new_y += player_speed * cos_a
                    
                if check_collision(new_x, new_y):
                    new_x, new_y = slide_along_wall(new_x, new_y, old_x, old_y)
                
                player_x, player_y = new_x, new_y
        
        # Draw menus
        if game_state == GAME_STATE_MAIN_MENU:
            main_menu_buttons = draw_main_menu(screen)
        elif game_state == GAME_STATE_PAUSED:
            pause_menu_buttons = draw_pause_menu(screen)
        elif game_state == GAME_STATE_GAME_OVER:
            draw_game_over_screen(screen, stats, high_scores)
        elif game_state == GAME_STATE_HIGH_SCORES:
            draw_high_scores(screen)
        
        # Draw level transition if active
        if level_state.state == LEVEL_STATE_TRANSITION:
            draw_level_transition(screen, level_state)
        
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

class Button:
    def __init__(self, x, y, width, height, text, font_size=48):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = pygame.font.Font(None, font_size)
        self.normal_color = GRAY
        self.hover_color = WHITE
        self.text_color = BLACK
        self.is_hovered = False

    def draw(self, surface):
        color = self.hover_color if self.is_hovered else self.normal_color
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, WHITE, self.rect, 2)  # Border
        
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.rect.collidepoint(event.pos):
                return True
        return False

if __name__ == "__main__":
    game_loop() 