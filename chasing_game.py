

import pygame
import random
import math
import sys
from enum import Enum
from dataclasses import dataclass
from typing import List, Tuple


pygame.init()


SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
FPS = 60
GAME_TITLE = "Chase Master - Avoid & Survive!"


class Colors(Enum):
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    RED = (255, 50, 50)
    BLUE = (50, 150, 255)
    GREEN = (50, 255, 100)
    YELLOW = (255, 255, 50)
    PURPLE = (200, 50, 255)
    ORANGE = (255, 165, 0)
    CYAN = (0, 255, 255)
    DARK_GRAY = (30, 30, 30)
    LIGHT_GRAY = (150, 150, 150)


class GameState(Enum):
    MENU = 1
    PLAYING = 2
    GAME_OVER = 3
    PAUSED = 4


@dataclass
class Vector2:

    x: float
    y: float
    
    def distance_to(self, other: 'Vector2') -> float:
        return math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)
    
    def normalize(self) -> 'Vector2':
        length = math.sqrt(self.x ** 2 + self.y ** 2)
        if length == 0:
            return Vector2(0, 0)
        return Vector2(self.x / length, self.y / length)
    
    def magnitude(self) -> float:
        return math.sqrt(self.x ** 2 + self.y ** 2)


class Player:
    def __init__(self, x: float, y: float):
        self.pos = Vector2(x, y)
        self.radius = 15
        self.speed = 5
        self.color = Colors.BLUE.value
        self.velocity = Vector2(0, 0)
        self.has_shield = False
        self.shield_time = 0
        self.shield_color = Colors.CYAN.value
        self.max_health = 1
        self.health = 1
    
    def handle_input(self, keys):
    
        self.velocity = Vector2(0, 0)
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.velocity.y = -self.speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.velocity.y = self.speed
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.velocity.x = -self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.velocity.x = self.speed
    
    def update(self):

        self.pos.x += self.velocity.x
        self.pos.y += self.velocity.y
        
        
        self.pos.x = max(self.radius, min(SCREEN_WIDTH - self.radius, self.pos.x))
        self.pos.y = max(self.radius, min(SCREEN_HEIGHT - self.radius, self.pos.y))
        
        
        if self.has_shield:
            self.shield_time -= 1
            if self.shield_time <= 0:
                self.has_shield = False
    
    def activate_shield(self, duration: int = 300):

        self.has_shield = True
        self.shield_time = duration
    
    def draw(self, surface: pygame.Surface):
         
        pygame.draw.circle(surface, self.color, (int(self.pos.x), int(self.pos.y)), self.radius)
        pygame.draw.circle(surface, Colors.LIGHT_GRAY.value, (int(self.pos.x), int(self.pos.y)), self.radius, 2)
        

        if self.has_shield:
            shield_radius = self.radius + 8
            pygame.draw.circle(surface, self.shield_color, (int(self.pos.x), int(self.pos.y)), shield_radius, 3)

class Enemy:

    def __init__(self, x: float, y: float):
        self.pos = Vector2(x, y)
        self.radius = 12
        self.speed = 1.5
        self.color = Colors.RED.value
        self.target_player = None
    
    def update(self, player: Player):

        self.target_player = player
        

        direction = Vector2(
            player.pos.x - self.pos.x,
            player.pos.y - self.pos.y
        )
        direction = direction.normalize()
        
    
        self.pos.x += direction.x * self.speed
        self.pos.y += direction.y * self.speed

        self.pos.x = max(self.radius, min(SCREEN_WIDTH - self.radius, self.pos.x))
        self.pos.y = max(self.radius, min(SCREEN_HEIGHT - self.radius, self.pos.y))
    
    def draw(self, surface: pygame.Surface):

        pygame.draw.circle(surface, self.color, (int(self.pos.x), int(self.pos.y)), self.radius)
        pygame.draw.circle(surface, Colors.YELLOW.value, (int(self.pos.x), int(self.pos.y)), self.radius, 2)
        

        eye_offset = 5
        pygame.draw.circle(surface, Colors.WHITE.value, (int(self.pos.x - eye_offset), int(self.pos.y - 3)), 2)
        pygame.draw.circle(surface, Colors.WHITE.value, (int(self.pos.x + eye_offset), int(self.pos.y - 3)), 2)

class Coin:

    def __init__(self, x: float, y: float):
        self.pos = Vector2(x, y)
        self.radius = 6
        self.color = Colors.YELLOW.value
        self.rotation = 0
        self.value = 10
    
    def update(self):

        self.rotation = (self.rotation + 5) % 360
    
    def draw(self, surface: pygame.Surface):

        pygame.draw.circle(surface, self.color, (int(self.pos.x), int(self.pos.y)), self.radius)
        pygame.draw.circle(surface, Colors.ORANGE.value, (int(self.pos.x), int(self.pos.y)), self.radius, 2)

class PowerUp:

    def __init__(self, x: float, y: float, power_type: str):
        self.pos = Vector2(x, y)
        self.radius = 8
        self.power_type = power_type 
        self.color_map = {
            'shield': Colors.CYAN.value,
            'speed': Colors.GREEN.value,
            'slow_enemy': Colors.PURPLE.value
        }
        self.color = self.color_map.get(power_type, Colors.ORANGE.value)
        self.pulse = 0
    
    def update(self):

        self.pulse = (self.pulse + 2) % 360
    
    def draw(self, surface: pygame.Surface):

        pulse_size = 2 + math.sin(self.pulse * 0.05) * 2
        pygame.draw.rect(
            surface,
            self.color,
            (int(self.pos.x - self.radius), int(self.pos.y - self.radius),
             int(self.radius * 2), int(self.radius * 2))
        )
        pygame.draw.rect(
            surface,
            Colors.WHITE.value,
            (int(self.pos.x - self.radius), int(self.pos.y - self.radius),
             int(self.radius * 2), int(self.radius * 2)),
            2
        )

class GameManager:

    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(GAME_TITLE)
        self.clock = pygame.time.Clock()
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 24)
        self.font_tiny = pygame.font.Font(None, 18)
        
        self.state = GameState.MENU
        self.reset_game()
    
    def reset_game(self):

        self.player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.enemies: List[Enemy] = [Enemy(random.randint(50, SCREEN_WIDTH - 50), 
                                           random.randint(50, SCREEN_HEIGHT - 50))]
        self.coins: List[Coin] = []
        self.power_ups: List[PowerUp] = []
        
        self.score = 0
        self.wave = 1
        self.time_alive = 0
        self.coins_collected = 0
        

        self.enemy_speed_multiplier = 1.0
        self.spawn_timer = 0
        self.spawn_interval = 300 
        self.enemy_spawn_chance = 0.1
        

        self.spawn_coins(5)
        
        self.state = GameState.PLAYING
    
    def spawn_coins(self, count: int = 1):

        for _ in range(count):
            x = random.randint(50, SCREEN_WIDTH - 50)
            y = random.randint(50, SCREEN_HEIGHT - 50)
            self.coins.append(Coin(x, y))
    
    def spawn_power_up(self):

        if random.random() < 0.3: 
            x = random.randint(50, SCREEN_WIDTH - 50)
            y = random.randint(50, SCREEN_HEIGHT - 50)
            power_type = random.choice(['shield', 'speed', 'slow_enemy'])
            self.power_ups.append(PowerUp(x, y, power_type))
    
    def check_collision(self, obj1_pos: Vector2, obj1_radius: float, 
                       obj2_pos: Vector2, obj2_radius: float) -> bool:

        distance = obj1_pos.distance_to(obj2_pos)
        return distance < (obj1_radius + obj2_radius)
    
    def handle_input(self):

        keys = pygame.key.get_pressed()
        self.player.handle_input(keys)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.state == GameState.PLAYING:
                        self.state = GameState.PAUSED
                    elif self.state == GameState.PAUSED:
                        self.state = GameState.PLAYING
                if event.key == pygame.K_SPACE and self.state == GameState.GAME_OVER:
                    self.reset_game()
                if event.key == pygame.K_SPACE and self.state == GameState.MENU:
                    self.reset_game()
        
        return True
    
    def update(self):

        if self.state != GameState.PLAYING:
            return
        

        self.player.update()
        
        for enemy in self.enemies:
            enemy.update(self.player)
        
        for coin in self.coins:
            coin.update()
        
        for power_up in self.power_ups:
            power_up.update()
        

        self.time_alive += 1
        self.score += 0.05  
        

        for coin in self.coins[:]:
            if self.check_collision(self.player.pos, self.player.radius, 
                                   coin.pos, coin.radius):
                self.score += coin.value
                self.coins.remove(coin)
                self.coins_collected += 1
                

                if random.random() < 0.7:
                    self.spawn_coins(1)
                
                if random.random() < 0.2:
                    self.spawn_power_up()
        

        for power_up in self.power_ups[:]:
            if self.check_collision(self.player.pos, self.player.radius,
                                   power_up.pos, power_up.radius):
                self.apply_power_up(power_up)
                self.power_ups.remove(power_up)
        

        for enemy in self.enemies:
            if self.check_collision(self.player.pos, self.player.radius,
                                   enemy.pos, enemy.radius):
                if self.player.has_shield:
                    self.player.has_shield = False
                else:
                    self.state = GameState.GAME_OVER
        
        # Increase difficulty over time
        self.update_difficulty()
        
        # Spawn more enemies as difficulty increases
        self.spawn_timer += 1
        if self.spawn_timer > self.spawn_interval:
            if random.random() < self.enemy_spawn_chance and len(self.enemies) < 1 + (self.wave // 2):
                x = random.randint(50, SCREEN_WIDTH - 50)
                y = random.randint(50, SCREEN_HEIGHT - 50)
                enemy = Enemy(x, y)
                enemy.speed *= self.enemy_speed_multiplier
                self.enemies.append(enemy)
            self.spawn_timer = 0
    
    def update_difficulty(self):
        """Increase difficulty as player survives"""
        self.wave = 1 + (self.time_alive // 300)  # New wave every 5 seconds
        self.enemy_speed_multiplier = 1.0 + (self.time_alive / 3000)  # Gradually increase
        self.spawn_interval = max(150, 300 - (self.time_alive // 30))  # Faster spawning
        self.enemy_spawn_chance = min(0.3, 0.1 + (self.time_alive / 6000))
        
        # Update enemy speeds
        for enemy in self.enemies:
            base_speed = 1.5 * self.enemy_speed_multiplier
            enemy.speed = base_speed
    
    def apply_power_up(self, power_up: PowerUp):
        """Apply power-up effects"""
        if power_up.power_type == 'shield':
            self.player.activate_shield(300)
            self.score += 25
        elif power_up.power_type == 'speed':
            self.player.speed = 7
            pygame.time.set_timer(pygame.USEREVENT + 1, 5000)
            self.score += 15
        elif power_up.power_type == 'slow_enemy':
            for enemy in self.enemies:
                enemy.speed *= 0.5
            pygame.time.set_timer(pygame.USEREVENT + 2, 5000)
            self.score += 20
    
    def draw(self):
        """Draw all game elements"""
        self.screen.fill(Colors.DARK_GRAY.value)
        
        # Draw UI background
        pygame.draw.rect(self.screen, Colors.BLACK.value, (0, 0, SCREEN_WIDTH, 60))
        
        # Draw game objects
        for coin in self.coins:
            coin.draw(self.screen)
        
        for power_up in self.power_ups:
            power_up.draw(self.screen)
        
        self.player.draw(self.screen)
        
        for enemy in self.enemies:
            enemy.draw(self.screen)
        
        # Draw HUD
        self.draw_hud()
        
        # Draw pause/game over screens
        if self.state == GameState.PAUSED:
            self.draw_paused_screen()
        elif self.state == GameState.GAME_OVER:
            self.draw_game_over_screen()
        elif self.state == GameState.MENU:
            self.draw_menu_screen()
        
        pygame.display.flip()
    
    def draw_hud(self):
        """Draw heads-up display"""
        # Score
        score_text = self.font_medium.render(f"Score: {int(self.score)}", True, Colors.GREEN.value)
        self.screen.blit(score_text, (10, 15))
        
        # Wave/Difficulty
        wave_text = self.font_small.render(f"Wave: {self.wave} | Speed: {self.enemy_speed_multiplier:.1f}x", 
                                          True, Colors.CYAN.value)
        self.screen.blit(wave_text, (SCREEN_WIDTH // 2 - 150, 15))
        
        # Coins collected
        coins_text = self.font_small.render(f"Coins: {self.coins_collected}", True, Colors.YELLOW.value)
        self.screen.blit(coins_text, (SCREEN_WIDTH - 200, 15))
        
        # Enemies
        enemies_text = self.font_small.render(f"Enemies: {len(self.enemies)}", True, Colors.RED.value)
        self.screen.blit(enemies_text, (SCREEN_WIDTH - 350, 15))
    
    def draw_paused_screen(self):
        """Draw pause overlay"""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(Colors.BLACK.value)
        self.screen.blit(overlay, (0, 0))
        
        pause_text = self.font_large.render("PAUSED", True, Colors.YELLOW.value)
        resume_text = self.font_small.render("Press ESC to Resume", True, Colors.WHITE.value)
        
        self.screen.blit(pause_text, (SCREEN_WIDTH // 2 - pause_text.get_width() // 2, 
                                     SCREEN_HEIGHT // 2 - 50))
        self.screen.blit(resume_text, (SCREEN_WIDTH // 2 - resume_text.get_width() // 2,
                                      SCREEN_HEIGHT // 2 + 20))
    
    def draw_game_over_screen(self):
        """Draw game over overlay"""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(220)
        overlay.fill(Colors.BLACK.value)
        self.screen.blit(overlay, (0, 0))
        
        game_over_text = self.font_large.render("GAME OVER!", True, Colors.RED.value)
        score_text = self.font_medium.render(f"Final Score: {int(self.score)}", True, Colors.YELLOW.value)
        wave_text = self.font_small.render(f"Wave Reached: {self.wave}", True, Colors.CYAN.value)
        coins_text = self.font_small.render(f"Coins Collected: {self.coins_collected}", True, Colors.GREEN.value)
        restart_text = self.font_small.render("Press SPACE to Restart", True, Colors.WHITE.value)
        
        y_offset = SCREEN_HEIGHT // 2 - 100
        self.screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, y_offset))
        self.screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, y_offset + 60))
        self.screen.blit(wave_text, (SCREEN_WIDTH // 2 - wave_text.get_width() // 2, y_offset + 110))
        self.screen.blit(coins_text, (SCREEN_WIDTH // 2 - coins_text.get_width() // 2, y_offset + 145))
        self.screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, y_offset + 200))
    
    def draw_menu_screen(self):
        """Draw main menu"""
        self.screen.fill(Colors.DARK_GRAY.value)
        
        title_text = self.font_large.render("CHASE MASTER", True, Colors.CYAN.value)
        subtitle_text = self.font_medium.render("Avoid Enemy • Collect Coins • Survive!", True, Colors.GREEN.value)
        
        controls_font = self.font_small
        controls = [
            "Controls:",
            "Arrow Keys / WASD - Move",
            "ESC - Pause/Resume",
            "",
            "Rules:",
            "• Avoid the RED enemy!",
            "• Collect YELLOW coins for points",
            "• Grab colored squares for power-ups",
            "• Difficulty increases over time",
            "",
            "Power-ups:",
            "🔵 Shield - Protect yourself once",
            "🟢 Speed - Move faster (5 sec)",
            "🟣 Slow - Slow all enemies (5 sec)"
        ]
        
        y_offset = 60
        self.screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, y_offset))
        self.screen.blit(subtitle_text, (SCREEN_WIDTH // 2 - subtitle_text.get_width() // 2, y_offset + 60))
        
        y_offset = 160
        for line in controls:
            color = Colors.YELLOW.value if line.endswith(":") else Colors.WHITE.value
            text = controls_font.render(line, True, color)
            self.screen.blit(text, (50, y_offset))
            y_offset += 25
        
        start_text = self.font_medium.render("Press SPACE to Start", True, Colors.GREEN.value)
        self.screen.blit(start_text, (SCREEN_WIDTH // 2 - start_text.get_width() // 2, SCREEN_HEIGHT - 80))
        
        pygame.display.flip()
    
    def run(self):
        """Main game loop"""
        running = True
        while running:
            running = self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

# ==================== MAIN ====================
if __name__ == "__main__":
    game = GameManager()
    game.run()
