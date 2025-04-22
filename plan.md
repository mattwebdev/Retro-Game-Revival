# ZineGames Project Plan

A collection of type-in games inspired by 1980s computer magazines, implemented in PyGame while maintaining the spirit of simplicity and single-file implementations.

## Project Goals

1. Create authentic type-in game experiences
2. Everything must be written in code (no external assets)
3. Games must be complete and compile
4. Each game contained in a single, tidy file
5. Code must be readable and typo-resistant
6. Focus on geometric visuals with personality

## Technical Stack

### Why PyGame?
- More beginner-friendly, similar to BASIC's simplicity
- Clean, readable syntax for manual typing
- Built-in primitives for retro-style graphics
- Rich Python ecosystem for easy distribution
- Minimal dependencies

### Requirements
- Python 3.x
- PyGame
- No additional libraries

## Game Collection

### 1. Snake (Easy)
**Estimated Lines:** 100-150
- Grid-based movement
- Geometric shapes for snake segments
- Food collection mechanics
- Growing snake implementation
- Score tracking

### 2. Pong (Easy)
**Estimated Lines:** 120-170
- Simple paddle movement
- Ball physics (straight angles only)
- Basic collision detection
- Computer opponent with three difficulty levels:
  - Easy: Moves directly to ball with delay
  - Medium: Predicts ball position with small errors
  - Hard: Perfect prediction with speed limit
- Score tracking and victory conditions
- Optional two-player mode
- Teaching concepts:
  - Basic AI movement
  - Prediction algorithms
  - Difficulty scaling
  - Adding "personality" to computer players

### 3. Space Shooter (Medium)
**Estimated Lines:** 150-200
- Single screen shooter (Space Invaders style)
- Geometric shapes for graphics
  - Triangles for ships
  - Circles for bullets
- Basic collision detection
- Score tracking

### 4. Breakout Clone (Medium)
**Estimated Lines:** 200-250
- Paddle and ball mechanics
- Geometric brick layouts
- Simple physics
- Color-based power-ups
- Progressive difficulty

### 5. Frogger (Medium)
**Estimated Lines:** 300-350
- Classic arcade gameplay
- Animated water effects
- Vehicle and log mechanics
- Life system
- Scoring for successful crossings
- Enhanced geometric visuals

### 6. Lunar Lander (Hard)
**Estimated Lines:** 350-400
- Physics-based landing mechanics
- Particle effects for thrust
- Multiple landing zones
- Fuel management
- Score based on landing precision
- Geometric art style with shading

### 7. Asteroids (Hard)
**Estimated Lines:** 300-350
- Vector-style graphics
- Rotation and momentum physics
- Particle effects for explosions
- Progressive difficulty
- High score system

## Code Style Guidelines

### File Template
```python
# Game Name
# Author: [name]
# Original Publication Date: 2024
# Description: [brief description]

import pygame
import random
import math

# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
# ... additional colors ...

# Game settings
# ... game-specific constants ...

# Classes

# Main Game Loop

# Run Game
```

### Coding Standards
1. Clear, descriptive variable names
2. Comments for complex logic
3. Logical code sections
4. Configuration via constants
5. Minimal dependencies
6. Error handling included
7. Line numbers for easy reference
8. Consistent class structure
9. Separation of update and draw logic

## Graphics Guidelines

### Primitive Shapes Only
- `pygame.draw.rect()`
- `pygame.draw.circle()`
- `pygame.draw.polygon()`
- `pygame.draw.line()`
- `pygame.draw.ellipse()`
- `pygame.draw.arc()`

### Visual Enhancement Techniques
- Two-tone shading for depth
- Simple animation systems
- Particle effects
- Screen shake and juice effects
- Wave and fluid simulations
- Dynamic lighting (via shapes)
- Geometric patterns
- Color gradients (via multiple shapes)

## Implementation Phases

### Phase 1: Physics Games (Complete)
1. Create project structure
2. Implement Lunar Lander
3. Implement Frogger
4. Establish visual style
5. Test readability
6. Verify ease of typing

### Phase 2: Classic Arcade
1. Implement Space Shooter
2. Implement Snake
3. Refine coding standards
4. Add scoring systems
5. Test game balance

### Phase 3: Advanced Games
1. Implement Breakout
2. Implement Asteroids
3. Polish game mechanics
4. Add high score tracking
5. Final readability pass
6. Documentation

## Distribution Format

### Zine Style Presentation
Each game includes:
1. Title and description
2. Code listing with line numbers
3. Key concept explanations
4. Customization tips
5. ASCII art screenshots
6. Expected output
7. Debugging tips
8. Visual enhancement guide

### Modern Additions
While maintaining authenticity:
1. Basic error handling
2. Simple menu systems
3. Game state management
4. Basic sound effects
5. Optional challenges
6. Visual polish options

## Getting Started

### Basic Game Template
```python
import pygame
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
# ... additional colors ...

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Game Name")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.reset()
    
    def reset(self):
        # Initialize game state
        pass
    
    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
        return True
    
    def update(self):
        # Update game logic
        return True
    
    def draw(self):
        self.screen.fill(BLACK)
        # Draw game elements
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
```

## Testing Guidelines

### For Each Game
1. Test on multiple Python versions
2. Verify all features work
3. Check for typo resistance
4. Ensure clear error messages
5. Verify scoring systems
6. Test game balance
7. Validate readability
8. Check visual consistency

### User Testing
1. Have others type in the code
2. Gather feedback on clarity
3. Note common typing mistakes
4. Adjust formatting as needed
5. Verify completion time
6. Test visual appeal

## Future Considerations

### Potential Additions
1. More game variations
2. Community contributions
3. Online leaderboards
4. Code golfed versions
5. Extended challenges
6. Visual enhancement guides

### Documentation
1. Maintain changelog
2. Version compatibility notes
3. Troubleshooting guide
4. Best practices
5. Learning resources
6. Visual style guide 