import pygame
import random
import math

pygame.init()

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 60

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)

PADDLE_WIDTH = 15
PADDLE_HEIGHT = 90
PADDLE_SPEED = 5
BALL_SIZE = 15
BALL_SPEED = 5
BALL_MAX_SPEED = 15
AI_SPEED_EASY = 3
AI_SPEED_MEDIUM = 4
AI_SPEED_HARD = 5
POINTS_TO_WIN = 5
COUNTDOWN_TIME = 3 

class Paddle:
    def __init__(self, x, y, is_ai=False, ai_difficulty="medium"):
        self.x = x
        self.y = y
        self.width = PADDLE_WIDTH
        self.height = PADDLE_HEIGHT
        self.speed = PADDLE_SPEED
        self.score = 0
        self.is_ai = is_ai
        self.ai_difficulty = ai_difficulty
        self.prediction_error = 0
        self.error_countdown = 0
    
    def move(self, up=True):
        if up and self.y > 0:
            self.y -= self.speed
        elif not up and self.y < WINDOW_HEIGHT - self.height:
            self.y += self.speed
    
    def ai_move(self, ball):
        if self.ai_difficulty == "easy":
            target_y = ball.y - self.height/2
            speed = AI_SPEED_EASY
        else:
            target_y = self.predict_ball_position(ball)
            if self.ai_difficulty == "medium":
                if self.error_countdown <= 0:
                    self.prediction_error = random.randint(-50, 50)
                    self.error_countdown = random.randint(30, 60)
                self.error_countdown -= 1
                target_y += self.prediction_error
                speed = AI_SPEED_MEDIUM
            else:
                speed = AI_SPEED_HARD
        
        if abs(self.y + self.height/2 - target_y) > speed:
            if self.y + self.height/2 > target_y:
                self.move(True)
            else:
                self.move(False)
    
    def predict_ball_position(self, ball):
        if ball.dx <= 0:
            return WINDOW_HEIGHT/2 - self.height/2
      
        time_to_paddle = (self.x - ball.x) / ball.dx
        
        future_y = ball.y + ball.dy * time_to_paddle
        
        while future_y < 0 or future_y > WINDOW_HEIGHT:
            if future_y < 0:
                future_y = -future_y
            elif future_y > WINDOW_HEIGHT:
                future_y = 2 * WINDOW_HEIGHT - future_y
        
        return future_y - self.height/2
    
    def draw(self, screen):
        pygame.draw.rect(screen, WHITE, 
                        (self.x, self.y, self.width, self.height))

class Ball:
    def __init__(self):
        self.reset()
        self.size = BALL_SIZE
    
    def reset(self):
        self.x = WINDOW_WIDTH/2
        self.y = WINDOW_HEIGHT/2
        angle = random.uniform(-math.pi/4, math.pi/4)
        if random.random() < 0.5: 
            angle += math.pi
        self.dx = BALL_SPEED * math.cos(angle)
        self.dy = BALL_SPEED * math.sin(angle)
    
    def update(self, left_paddle, right_paddle):
        self.x += self.dx
        self.y += self.dy
        
        if self.y < 0 or self.y > WINDOW_HEIGHT:
            self.dy = -self.dy
            self.y = max(0, min(self.y, WINDOW_HEIGHT))
        
        if self.x < 0:
            right_paddle.score += 1
            self.reset()
            return
        elif self.x > WINDOW_WIDTH:
            left_paddle.score += 1
            self.reset()
            return
        
        ball_rect = pygame.Rect(self.x - self.size/2, self.y - self.size/2,
                              self.size, self.size)
        
        for paddle in [left_paddle, right_paddle]:
            paddle_rect = pygame.Rect(paddle.x, paddle.y,
                                    paddle.width, paddle.height)
            
            if ball_rect.colliderect(paddle_rect):
                relative_intersect_y = (paddle.y + paddle.height/2) - self.y
                normalized_intersect = relative_intersect_y / (paddle.height/2)
                bounce_angle = normalized_intersect * math.pi/3 
                
                speed = min(math.sqrt(self.dx*self.dx + self.dy*self.dy) * 1.1,
                          BALL_MAX_SPEED)
                
                if paddle == right_paddle:
                    self.dx = -speed * math.cos(bounce_angle)
                    self.dy = speed * math.sin(bounce_angle)
                    self.x = paddle.x - self.size/2 
                else:
                    self.dx = speed * math.cos(bounce_angle)
                    self.dy = speed * math.sin(bounce_angle)
                    self.x = paddle.x + paddle.width + self.size/2 
                break
    
    def draw(self, screen):
        pygame.draw.rect(screen, WHITE,
                        (self.x - self.size/2, self.y - self.size/2,
                         self.size, self.size))

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Pong")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.title_font = pygame.font.Font(None, 72)
        self.countdown_font = pygame.font.Font(None, 150)
        self.ai_difficulty = "medium" 
        self.in_menu = True
        self.in_countdown = False
        self.countdown_start = 0
        self.selected_option = 1 
        self.reset()
    
    def reset(self):
        self.left_paddle = Paddle(50, WINDOW_HEIGHT/2 - PADDLE_HEIGHT/2)
        self.right_paddle = Paddle(WINDOW_WIDTH - 50 - PADDLE_WIDTH,
                                 WINDOW_HEIGHT/2 - PADDLE_HEIGHT/2,
                                 True, self.ai_difficulty)
        self.ball = Ball()
        self.game_over = False
    
    def start_countdown(self):
        self.in_countdown = True
        self.countdown_start = pygame.time.get_ticks()
        self.reset() 
    
    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if self.in_menu:
                    if event.key in [pygame.K_UP, pygame.K_w]:
                        self.selected_option = (self.selected_option - 1) % 3
                    elif event.key in [pygame.K_DOWN, pygame.K_s]:
                        self.selected_option = (self.selected_option + 1) % 3
                    elif event.key == pygame.K_RETURN:
                        new_difficulty = ["easy", "medium", "hard"][self.selected_option]
                        if new_difficulty != self.ai_difficulty:
                            self.ai_difficulty = new_difficulty
                            self.right_paddle.ai_difficulty = self.ai_difficulty
                        self.in_menu = False
                        self.start_countdown()
                elif not self.in_countdown:
                    if event.key == pygame.K_r:
                        self.reset()
                    elif event.key == pygame.K_ESCAPE:
                        self.in_menu = True
                        self.selected_option = ["easy", "medium", "hard"].index(self.ai_difficulty)
                    elif event.key == pygame.K_1:
                        self.ai_difficulty = "easy"
                        self.right_paddle.ai_difficulty = "easy"
                        self.start_countdown()
                    elif event.key == pygame.K_2:
                        self.ai_difficulty = "medium"
                        self.right_paddle.ai_difficulty = "medium"
                        self.start_countdown()
                    elif event.key == pygame.K_3:
                        self.ai_difficulty = "hard"
                        self.right_paddle.ai_difficulty = "hard"
                        self.start_countdown()
        
        if not self.in_menu and not self.in_countdown:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_w]:
                self.left_paddle.move(True)
            if keys[pygame.K_s]:
                self.left_paddle.move(False)
        
        return True
    
    def draw_menu(self):
        self.screen.fill(BLACK)
    
        title = self.title_font.render("PONG", True, WHITE)
        title_rect = title.get_rect(center=(WINDOW_WIDTH/2, 100))
        self.screen.blit(title, title_rect)
        
        difficulties = ["Easy", "Medium", "Hard"]
        for i, diff in enumerate(difficulties):
            color = WHITE if i == self.selected_option else GRAY
            text = self.font.render(diff, True, color)
            rect = text.get_rect(center=(WINDOW_WIDTH/2, 250 + i * 50))

            if i == self.selected_option:
                pygame.draw.rect(self.screen, WHITE, 
                               (rect.left - 20, rect.top, 10, rect.height))
            self.screen.blit(text, rect)
        
        controls = [
            "Controls:",
            "W/S - Move paddle up/down",
            "1/2/3 - Change AI difficulty",
            "R - Restart game",
            "ESC - Return to menu",
            "",
            "Press ENTER to start"
        ]
        
        for i, line in enumerate(controls):
            text = self.font.render(line, True, WHITE)
            rect = text.get_rect(center=(WINDOW_WIDTH/2, 400 + i * 30))
            self.screen.blit(text, rect)
    
    def draw_countdown(self):
        self.screen.fill(BLACK)
        self.left_paddle.draw(self.screen)
        self.right_paddle.draw(self.screen)

        for y in range(0, WINDOW_HEIGHT, 20):
            pygame.draw.rect(self.screen, GRAY,
                           (WINDOW_WIDTH/2 - 5, y, 10, 10))
        
        elapsed = (pygame.time.get_ticks() - self.countdown_start) / 1000
        count = max(1, int(COUNTDOWN_TIME - elapsed + 1))
        
        if count <= 3: 
            text = self.countdown_font.render(str(count), True, WHITE)
            text_rect = text.get_rect(center=(WINDOW_WIDTH/2, WINDOW_HEIGHT/2))
            self.screen.blit(text, text_rect)
    
    def draw(self):
        if self.in_menu:
            self.draw_menu()
        elif self.in_countdown:
            self.draw_countdown()
        else:
            self.screen.fill(BLACK)
            for y in range(0, WINDOW_HEIGHT, 20):
                pygame.draw.rect(self.screen, GRAY,
                               (WINDOW_WIDTH/2 - 5, y, 10, 10))
            
            self.left_paddle.draw(self.screen)
            self.right_paddle.draw(self.screen)
            self.ball.draw(self.screen)
            
            left_score = self.font.render(str(self.left_paddle.score), True, WHITE)
            right_score = self.font.render(str(self.right_paddle.score), True, WHITE)
            self.screen.blit(left_score, (WINDOW_WIDTH/4, 20))
            self.screen.blit(right_score, (3*WINDOW_WIDTH/4, 20))
            
            diff_text = self.font.render(f"AI: {self.ai_difficulty}", True, GRAY)
            self.screen.blit(diff_text, (10, WINDOW_HEIGHT - 30))
           
            if self.game_over:
                winner = "Player 1" if self.left_paddle.score > self.right_paddle.score else "AI"
                text = self.font.render(f"{winner} Wins! Press R to restart", True, WHITE)
                text_rect = text.get_rect(center=(WINDOW_WIDTH/2, WINDOW_HEIGHT/2))
                self.screen.blit(text, text_rect)
        
        pygame.display.flip()
    
    def update(self):
        if self.in_countdown:
            elapsed = (pygame.time.get_ticks() - self.countdown_start) / 1000
            if elapsed >= COUNTDOWN_TIME:
                self.in_countdown = False
        elif not self.in_menu and not self.game_over:
            self.ball.update(self.left_paddle, self.right_paddle)
            self.right_paddle.ai_move(self.ball)
            
            if (self.left_paddle.score >= POINTS_TO_WIN or 
                self.right_paddle.score >= POINTS_TO_WIN):
                self.game_over = True
    
    def run(self):
        running = True
        while running:
            running = self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(FPS)

def main():
    game = Game()
    game.run()

if __name__ == "__main__":
    main()

# find errors in my code? send a note to hello@shortfuse.games
