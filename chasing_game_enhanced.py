

import pygame
import random
import math
import sys
import json
import os
from enum import Enum
from dataclasses import dataclass, field
from typing import List, Tuple
from pathlib import Path


pygame.init()
pygame.mixer.init()


SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
FPS = 60
GAME_TITLE = "Chase Master - Enhanced Edition!"
SAVE_FILE = "chase_master_save.json"


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
    PINK = (255, 100, 200)
    DARK_RED = (139, 0, 0)


class GameState(Enum):
    MENU = 1
    MODE_SELECT = 2
    PLAYING = 3
    GAME_OVER = 4
    PAUSED = 5


class GameMode(Enum):
    SURVIVAL = "Survival"
    TIME_ATTACK = "Time Attack (60s)"
    ENDLESS_COINS = "Endless Coins"


class EnemyType(Enum):
    TRACKER = "Tracker"
    TANK = "Tank"
    GHOST = "Ghost"
    BOUNCER = "Bouncer"


class SoundManager:
    
    def __init__(self):
        self.sounds = {}
        self.create_sounds()
    
    def create_sounds(self):

        try:
        
            self.sounds['coin'] = self.generate_beep(800, 100)

            self.sounds['powerup'] = self.generate_beep(1000, 150)

            self.sounds['hit'] = self.generate_beep(300, 100)

            self.sounds['gameover'] = self.generate_beep(400, 300)

            self.sounds['shield'] = self.generate_beep(1200, 50)
        except:
            print("Sound initialization skipped (audio unavailable)")
    
    def generate_beep(self, frequency: int, duration: int) -> pygame.mixer.Sound:
        try:
            sample_rate = 22050
            frames = int(sample_rate * duration / 1000)
            arr = pygame.sndarray.make_sound(
                pygame.numpy.arange(frames).reshape(frames, 1) * frequency * 2 * 3.14159 / sample_rate
            )
            return arr
        except:
            return None
    
    def play(self, sound_name: str):

        try:
            if sound_name in self.sounds and self.sounds[sound_name]:
                self.sounds[sound_name].play()
        except:
            pass


try:
    sound_manager = SoundManager()
except:
    class DummySoundManager:
        def play(self, name): pass
    sound_manager = DummySoundManager()


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

@dataclass
class Achievement:

    id: str
    name: str
    description: str
    unlocked: bool = False

@dataclass
class PlayerStats:

    high_score: int = 0
    games_played: int = 0
    coins_collected: int = 0
    enemies_dodged: int = 0
    max_wave: int = 0
    achievements: List[Achievement] = field(default_factory=list)


class Player:
    
    def __init__(self, x: float, y: float):
        self.pos = Vector2(x, y)
        self.radius = 15
        self.speed = 5
        self.color = Colors.BLUE.value
        self.velocity = Vector2(0, 0)
        self.has_shield = False
        self.shield_time = 0
        self.invincible = False
        self.invincible_time = 0
        self.teleport_cooldown = 0
    
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
        self.pos.y = max(70 + self.radius, min(SCREEN_HEIGHT - self.radius, self.pos.y))
        

        if self.has_shield:
            self.shield_time -= 1
            if self.shield_time <= 0:
                self.has_shield = False
        

        if self.invincible:
            self.invincible_time -= 1
            if self.invincible_time <= 0:
                self.invincible = False
        

        if self.teleport_cooldown > 0:
            self.teleport_cooldown -= 1
    
    def activate_shield(self, duration: int = 300):
        self.has_shield = True
        self.shield_time = duration
        sound_manager.play('shield')
    
    def activate_invincibility(self, duration: int = 300):
        self.invincible = True
        self.invincible_time = duration
    
    def teleport(self):

        if self.teleport_cooldown > 0:
            return False
        
        self.pos.x = random.randint(50, SCREEN_WIDTH - 50)
        self.pos.y = random.randint(120, SCREEN_HEIGHT - 50)
        self.teleport_cooldown = 600  # 10 second cooldown
        sound_manager.play('powerup')
        return True
    
    def draw(self, surface: pygame.Surface):


        if self.invincible and int(self.invincible_time / 10) % 2 == 0:
            return
        
        pygame.draw.circle(surface, self.color, (int(self.pos.x), int(self.pos.y)), self.radius)
        pygame.draw.circle(surface, Colors.LIGHT_GRAY.value, (int(self.pos.x), int(self.pos.y)), self.radius, 2)
        

        if self.has_shield:
            pygame.draw.circle(surface, Colors.CYAN.value, (int(self.pos.x), int(self.pos.y)), self.radius + 8, 3)
        

        if self.invincible:
            pygame.draw.circle(surface, Colors.PINK.value, (int(self.pos.x), int(self.pos.y)), self.radius + 5, 2)

class Enemy:
    """Base enemy class"""
    def __init__(self, x: float, y: float, enemy_type: EnemyType):
        self.pos = Vector2(x, y)
        self.radius = 12
        self.speed = 1.5
        self.enemy_type = enemy_type
        self.target_player = None
        self.color_map = {
            EnemyType.TRACKER: Colors.RED.value,
            EnemyType.TANK: Colors.DARK_RED.value,
            EnemyType.GHOST: Colors.PURPLE.value,
            EnemyType.BOUNCER: Colors.ORANGE.value
        }
        self.color = self.color_map[enemy_type]
        self.behavior_timer = 0
        self.velocity = Vector2(0, 0)
        self.visible = True
    
    def update(self, player: Player):
    
        self.target_player = player
        
        if self.enemy_type == EnemyType.TRACKER:
            self.update_tracker(player)
        elif self.enemy_type == EnemyType.TANK:
            self.update_tank(player)
        elif self.enemy_type == EnemyType.GHOST:
            self.update_ghost(player)
        elif self.enemy_type == EnemyType.BOUNCER:
            self.update_bouncer(player)
        

        self.pos.x = max(self.radius, min(SCREEN_WIDTH - self.radius, self.pos.x))
        self.pos.y = max(70 + self.radius, min(SCREEN_HEIGHT - self.radius, self.pos.y))
    
    def update_tracker(self, player: Player):

        direction = Vector2(player.pos.x - self.pos.x, player.pos.y - self.pos.y).normalize()
        self.pos.x += direction.x * self.speed * 1.3
        self.pos.y += direction.y * self.speed * 1.3
    
    def update_tank(self, player: Player):

        direction = Vector2(player.pos.x - self.pos.x, player.pos.y - self.pos.y).normalize()
        self.pos.x += direction.x * self.speed * 0.6
        self.pos.y += direction.y * self.speed * 0.6
    
    def update_ghost(self, player: Player):


        self.behavior_timer += 1
        self.visible = (self.behavior_timer // 30) % 2 == 0
        
        direction = Vector2(player.pos.x - self.pos.x, player.pos.y - self.pos.y).normalize()
        self.pos.x += direction.x * self.speed * 0.9
        self.pos.y += direction.y * self.speed * 0.9
    
    def update_bouncer(self, player: Player):

        self.behavior_timer += 1
        

        if self.behavior_timer > 120:
            self.velocity = Vector2(
                random.uniform(-1, 1),
                random.uniform(-1, 1)
            ).normalize()
            self.behavior_timer = 0
        

        if random.random() < 0.1:
            direction = Vector2(player.pos.x - self.pos.x, player.pos.y - self.pos.y).normalize()
            self.velocity = direction
        
        self.pos.x += self.velocity.x * self.speed
        self.pos.y += self.velocity.y * self.speed
    
    def draw(self, surface: pygame.Surface):
        """Draw enemy uhhbjh ghvv kukunk; gugyu ugugu gjyyj ugyuu ububub buyuu fhdubvfvfbbv dbhd dvbbxhjvs hfbv fbj hvhjbvhj jhvbghg ghvn ygy giuhi yihi vygugyh """
        if not self.visible and self.enemy_type == EnemyType.GHOST:
            # Draw faint ghost
            pygame.draw.circle(surface, (*self.color, 100), (int(self.pos.x), int(self.pos.y)), self.radius)
        else:
            pygame.draw.circle(surface, self.color, (int(self.pos.x), int(self.pos.y)), self.radius)
        
        # Outline
        outline_color = Colors.YELLOW.value if self.visible else Colors.LIGHT_GRAY.value
        pygame.draw.circle(surface, outline_color, (int(self.pos.x), int(self.pos.y)), self.radius, 2)
        
        # Type indicator
        if self.enemy_type == EnemyType.TANK:
            pygame.draw.circle(surface, Colors.WHITE.value, (int(self.pos.x), int(self.pos.y)), self.radius - 3, 2)

class Coin:
    """Collectible coin"""
    def __init__(self, x: float, y: float, value: int = 10):
        self.pos = Vector2(x, y)
        self.radius = 6
        self.color = Colors.YELLOW.value
        self.rotation = 0
        self.value = value
    
    def update(self):
        self.rotation = (self.rotation + 5) % 360
    
    def draw(self, surface: pygame.Surface):
        pygame.draw.circle(surface, self.color, (int(self.pos.x), int(self.pos.y)), self.radius)
        pygame.draw.circle(surface, Colors.ORANGE.value, (int(self.pos.x), int(self.pos.y)), self.radius, 2)

class PowerUp:
    """Power-up item"""
    def __init__(self, x: float, y: float, power_type: str):
        self.pos = Vector2(x, y)
        self.radius = 8
        self.power_type = power_type
        self.color_map = {
            'shield': Colors.CYAN.value,
            'speed': Colors.GREEN.value,
            'slow_enemy': Colors.PURPLE.value,
            'invincibility': Colors.PINK.value,
            'shield_refresh': (100, 200, 255),
            'teleport': Colors.YELLOW.value,
            'multi_coin': Colors.ORANGE.value,
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
    """Main game manager"""
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(GAME_TITLE)
        self.clock = pygame.time.Clock()
        
        # Fonts
        self.font_large = pygame.font.Font(None, 56)
        self.font_medium = pygame.font.Font(None, 40)
        self.font_small = pygame.font.Font(None, 28)
        self.font_tiny = pygame.font.Font(None, 18)
        
        self.state = GameState.MENU
        self.game_mode = GameMode.SURVIVAL
        self.load_stats()
        self.reset_game()
    
    def load_stats(self):
        """Load player statistics from file"""
        if os.path.exists(SAVE_FILE):
            try:
                with open(SAVE_FILE, 'r') as f:
                    data = json.load(f)
                    # Create stats object
                    achs_data = data.pop('achievements', [])
                    self.stats = PlayerStats(**data)
                    # Reconstruct objects from dicts
                    self.stats.achievements = []
                    for a in achs_data:
                        if isinstance(a, dict):
                            self.stats.achievements.append(Achievement(**a))
                        else:
                            self.stats.achievements.append(a)
            except Exception as e:
                print(f"Error loading stats: {e}")
                self.stats = PlayerStats()
        else:
            self.stats = PlayerStats()
        
        self.init_achievements()
    
    def init_achievements(self):
        """Initialize achievement list"""
        achievements = [
            Achievement("first_coin", "First Collect", "Collect your first coin"),
            Achievement("coin_master", "Coin Master", "Collect 100 coins in one game"),
            Achievement("survivor_30", "30 Second Survivor", "Survive 30 seconds"),
            Achievement("survivor_60", "Minute Man", "Survive 60 seconds"),
            Achievement("dodger", "Perfect Dodger", "Play without using shield"),
            Achievement("powerup_hoarder", "Power-up Hoarder", "Collect 10 power-ups"),
        ]
        
        # Map existing achievements safely
        for ach in achievements:
            for existing in self.stats.achievements:
                # Handle both object and dict if something went wrong
                existing_id = existing.id if not isinstance(existing, dict) else existing.get('id')
                if existing_id == ach.id:
                    ach.unlocked = existing.unlocked if not isinstance(existing, dict) else existing.get('unlocked', False)
                    break
        
        self.stats.achievements = achievements
    
    def save_stats(self):
        """Save player statistics to file"""
        try:
            data = {
                'high_score': self.stats.high_score,
                'games_played': self.stats.games_played,
                'coins_collected': self.stats.coins_collected,
                'enemies_dodged': self.stats.enemies_dodged,
                'max_wave': self.stats.max_wave,
                'achievements': [{'id': a.id, 'name': a.name, 'description': a.description, 'unlocked': a.unlocked} 
                               for a in self.stats.achievements]
            }
            with open(SAVE_FILE, 'w') as f:
                json.dump(data, f, indent=2)
        except:
            pass
    
    def reset_game(self):
        """Reset game to initial state"""
        self.player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.enemies: List[Enemy] = [Enemy(100, 100, EnemyType.TRACKER)]
        self.coins: List[Coin] = []
        self.power_ups: List[PowerUp] = []
        
        self.score = 0
        self.wave = 1
        self.time_alive = 0
        self.coins_collected = 0
        self.enemy_speed_multiplier = 1.0
        self.multi_coin_multiplier = 1
        self.multi_coin_timer = 0
        
        # Game mode settings
        if self.game_mode == GameMode.TIME_ATTACK:
            self.time_limit = 60 * FPS  # 60 seconds
        else:
            self.time_limit = None
        
        self.spawn_coins(5)
        self.state = GameState.PLAYING
    
    def spawn_coins(self, count: int = 1):
        """Spawn coins"""
        for _ in range(count):
            x = random.randint(50, SCREEN_WIDTH - 50)
            y = random.randint(120, SCREEN_HEIGHT - 50)
            self.coins.append(Coin(x, y))
    
    def spawn_power_up(self):
        """Spawn random power-up"""
        if random.random() < 0.25:
            x = random.randint(50, SCREEN_WIDTH - 50)
            y = random.randint(120, SCREEN_HEIGHT - 50)
            power_type = random.choice([
                'shield', 'speed', 'slow_enemy', 'invincibility',
                'shield_refresh', 'teleport', 'multi_coin'
            ])
            self.power_ups.append(PowerUp(x, y, power_type))
    
    def check_collision(self, obj1_pos: Vector2, obj1_radius: float,
                       obj2_pos: Vector2, obj2_radius: float) -> bool:
        """Check collision between two objects"""
        distance = obj1_pos.distance_to(obj2_pos)
        return distance < (obj1_radius + obj2_radius)
    
    def handle_input(self):
        """Handle input"""
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
                if event.key == pygame.K_SPACE:
                    if self.state == GameState.GAME_OVER:
                        self.state = GameState.MODE_SELECT
                    if self.state == GameState.MENU:
                        self.state = GameState.MODE_SELECT
                if event.key == pygame.K_1 and self.state == GameState.MODE_SELECT:
                    self.game_mode = GameMode.SURVIVAL
                    self.reset_game()
                if event.key == pygame.K_2 and self.state == GameState.MODE_SELECT:
                    self.game_mode = GameMode.TIME_ATTACK
                    self.reset_game()
                if event.key == pygame.K_3 and self.state == GameState.MODE_SELECT:
                    self.game_mode = GameMode.ENDLESS_COINS
                    self.reset_game()
        
        return True
    
    def update(self):
        """Update game state"""
        if self.state != GameState.PLAYING:
            return
        
        # Update entities
        self.player.update()
        for enemy in self.enemies:
            enemy.update(self.player)
        for coin in self.coins:
            coin.update()
        for power_up in self.power_ups:
            power_up.update()
        
        # Game timer
        self.time_alive += 1
        
        # Time attack mode check
        if self.game_mode == GameMode.TIME_ATTACK:
            if self.time_alive >= self.time_limit:
                self.state = GameState.GAME_OVER
                return
        
        # Score from time
        if self.game_mode != GameMode.TIME_ATTACK:
            self.score += 0.05
        
        # Check coin collection
        for coin in self.coins[:]:
            if self.check_collision(self.player.pos, self.player.radius,
                                   coin.pos, coin.radius):
                value = coin.value * self.multi_coin_multiplier
                self.score += value
                self.coins_collected += 1
                self.coins.remove(coin)
                sound_manager.play('coin')
                
                # Check achievements
                if self.coins_collected == 1:
                    self.unlock_achievement("first_coin")
                if self.coins_collected >= 100:
                    self.unlock_achievement("coin_master")
                
                if random.random() < 0.6:
                    self.spawn_coins(1)
                if random.random() < 0.25:
                    self.spawn_power_up()
        
        # Check power-up collection
        for power_up in self.power_ups[:]:
            if self.check_collision(self.player.pos, self.player.radius,
                                   power_up.pos, power_up.radius):
                self.apply_power_up(power_up)
                self.power_ups.remove(power_up)
                sound_manager.play('powerup')
        
        # Check collision with enemies
        for enemy in self.enemies:
            if self.check_collision(self.player.pos, self.player.radius,
                                   enemy.pos, enemy.radius):
                if self.player.invincible:
                    continue
                if self.player.has_shield:
                    self.player.has_shield = False
                    sound_manager.play('hit')
                else:
                    sound_manager.play('gameover')
                    self.state = GameState.GAME_OVER
        
        # Update difficulty
        self.update_difficulty()
        
        # Reset multi-coin timer
        if self.multi_coin_timer > 0:
            self.multi_coin_timer -= 1
            if self.multi_coin_timer <= 0:
                self.multi_coin_multiplier = 1
        
        # Check achievements
        if self.time_alive == 30 * FPS:
            self.unlock_achievement("survivor_30")
        if self.time_alive == 60 * FPS:
            self.unlock_achievement("survivor_60")
    
    def update_difficulty(self):
        """Increase difficulty over time"""
        self.wave = 1 + (self.time_alive // 300)
        self.enemy_speed_multiplier = 1.0 + (self.time_alive / 3000)
        
        # Spawn enemies
        if len(self.enemies) < 1 + (self.wave // 3):
            if random.random() < 0.05:
                enemy_types = [EnemyType.TRACKER, EnemyType.TANK, EnemyType.GHOST, EnemyType.BOUNCER]
                enemy_type = random.choice(enemy_types)
                enemy = Enemy(random.randint(50, SCREEN_WIDTH - 50),
                            random.randint(120, SCREEN_HEIGHT - 50), enemy_type)
                enemy.speed *= self.enemy_speed_multiplier
                self.enemies.append(enemy)
        
        # Update existing enemy speeds
        for enemy in self.enemies:
            if enemy.enemy_type == EnemyType.TRACKER:
                enemy.speed = 1.5 * self.enemy_speed_multiplier * 1.3
            elif enemy.enemy_type == EnemyType.TANK:
                enemy.speed = 1.5 * self.enemy_speed_multiplier * 0.6
            else:
                enemy.speed = 1.5 * self.enemy_speed_multiplier
    
    def apply_power_up(self, power_up: PowerUp):
        """Apply power-up effects"""
        if power_up.power_type == 'shield':
            self.player.activate_shield(300)
            self.score += 25
        elif power_up.power_type == 'speed':
            old_speed = self.player.speed
            self.player.speed = 7
            pygame.time.set_timer(pygame.USEREVENT + 1, 5000)
            self.score += 15
        elif power_up.power_type == 'slow_enemy':
            for enemy in self.enemies:
                enemy.speed *= 0.5
            pygame.time.set_timer(pygame.USEREVENT + 2, 5000)
            self.score += 20
        elif power_up.power_type == 'invincibility':
            self.player.activate_invincibility(300)
            self.score += 50
        elif power_up.power_type == 'shield_refresh':
            self.player.activate_shield(300)
            self.score += 30
        elif power_up.power_type == 'teleport':
            self.player.teleport()
            self.score += 40
        elif power_up.power_type == 'multi_coin':
            self.multi_coin_multiplier = 2
            self.multi_coin_timer = 300
            self.score += 35
        
        self.unlock_achievement("powerup_hoarder")
    
    def unlock_achievement(self, achievement_id: str):
        """Unlock an achievement"""
        for ach in self.stats.achievements:
            if ach.id == achievement_id and not ach.unlocked:
                ach.unlocked = True
                self.save_stats()
    
    def draw(self):
        """Draw all game elements"""
        self.screen.fill(Colors.DARK_GRAY.value)
        
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
        
        # Draw UI screens
        if self.state == GameState.PAUSED:
            self.draw_paused_screen()
        elif self.state == GameState.GAME_OVER:
            self.draw_game_over_screen()
        elif self.state == GameState.MENU:
            self.draw_menu_screen()
        elif self.state == GameState.MODE_SELECT:
            self.draw_mode_select_screen()
        
        pygame.display.flip()
    
    def draw_hud(self):
        """Draw heads-up display"""
        pygame.draw.rect(self.screen, Colors.BLACK.value, (0, 0, SCREEN_WIDTH, 70))
        pygame.draw.line(self.screen, Colors.CYAN.value, (0, 70), (SCREEN_WIDTH, 70), 2)
        
        score_text = self.font_small.render(f"Score: {int(self.score)}", True, Colors.GREEN.value)
        self.screen.blit(score_text, (10, 15))
        
        mode_text = self.font_tiny.render(f"Mode: {self.game_mode.value}", True, Colors.CYAN.value)
        self.screen.blit(mode_text, (10, 45))
        
        wave_text = self.font_small.render(f"Wave: {self.wave}", True, Colors.YELLOW.value)
        self.screen.blit(wave_text, (SCREEN_WIDTH // 2 - 50, 15))
        
        coins_text = self.font_small.render(f"Coins: {self.coins_collected}", True, Colors.ORANGE.value)
        self.screen.blit(coins_text, (SCREEN_WIDTH - 250, 15))
        
        enemies_text = self.font_small.render(f"Enemies: {len(self.enemies)}", True, Colors.RED.value)
        self.screen.blit(enemies_text, (SCREEN_WIDTH - 450, 15))
        
        # Timer for time attack
        if self.game_mode == GameMode.TIME_ATTACK:
            time_left = max(0, (self.time_limit - self.time_alive) // FPS)
            time_text = self.font_small.render(f"Time: {time_left}s", True, Colors.PINK.value)
            self.screen.blit(time_text, (SCREEN_WIDTH // 2 + 200, 15))
        
        # Multi-coin indicator
        if self.multi_coin_multiplier > 1:
            multi_text = self.font_tiny.render(f"2x COINS! {self.multi_coin_timer // FPS}s", True, Colors.ORANGE.value)
            self.screen.blit(multi_text, (SCREEN_WIDTH - 250, 45))
    
    def draw_paused_screen(self):
        """Draw pause screen"""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(Colors.BLACK.value)
        self.screen.blit(overlay, (0, 0))
        
        pause_text = self.font_large.render("PAUSED", True, Colors.YELLOW.value)
        resume_text = self.font_small.render("Press ESC to Resume", True, Colors.WHITE.value)
        
        self.screen.blit(pause_text, (SCREEN_WIDTH // 2 - pause_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
        self.screen.blit(resume_text, (SCREEN_WIDTH // 2 - resume_text.get_width() // 2, SCREEN_HEIGHT // 2 + 20))
    
    def draw_game_over_screen(self):
        """Draw game over screen"""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(220)
        overlay.fill(Colors.BLACK.value)
        self.screen.blit(overlay, (0, 0))
        
        game_over_text = self.font_large.render("GAME OVER!", True, Colors.RED.value)
        score_text = self.font_medium.render(f"Final Score: {int(self.score)}", True, Colors.YELLOW.value)
        
        y_offset = SCREEN_HEIGHT // 2 - 80
        self.screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, y_offset))
        self.screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, y_offset + 60))
        
        restart_text = self.font_small.render("Press SPACE for Mode Select", True, Colors.WHITE.value)
        self.screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, y_offset + 130))
        
        # Update stats
        if int(self.score) > self.stats.high_score:
            self.stats.high_score = int(self.score)
        self.stats.games_played += 1
        self.stats.coins_collected += self.coins_collected
        self.stats.max_wave = max(self.stats.max_wave, self.wave)
        self.save_stats()
    
    def draw_menu_screen(self):
        """Draw main menu"""
        self.screen.fill(Colors.DARK_GRAY.value)
        
        title_text = self.font_large.render("CHASE MASTER", True, Colors.CYAN.value)
        subtitle_text = self.font_medium.render("ENHANCED EDITION", True, Colors.GREEN.value)
        
        y = 80
        self.screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, y))
        self.screen.blit(subtitle_text, (SCREEN_WIDTH // 2 - subtitle_text.get_width() // 2, y + 70))
        
        # Stats
        y = 200
        stats_lines = [
            f"High Score: {self.stats.high_score}",
            f"Games Played: {self.stats.games_played}",
            f"Max Wave: {self.stats.max_wave}",
            f"Total Coins: {self.stats.coins_collected}"
        ]
        for line in stats_lines:
            text = self.font_small.render(line, True, Colors.YELLOW.value)
            self.screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, y))
            y += 45
        
        start_text = self.font_medium.render("Press SPACE to Start", True, Colors.GREEN.value)
        self.screen.blit(start_text, (SCREEN_WIDTH // 2 - start_text.get_width() // 2, SCREEN_HEIGHT - 100))
        
        pygame.display.flip()
    
    def draw_mode_select_screen(self):
        """Draw game mode selection"""
        self.screen.fill(Colors.DARK_GRAY.value)
        
        title_text = self.font_large.render("SELECT GAME MODE", True, Colors.CYAN.value)
        self.screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 80))
        
        modes = [
            ("1", "SURVIVAL", "Survive as long as possible!"),
            ("2", "TIME ATTACK", "Survive 60 seconds!"),
            ("3", "ENDLESS COINS", "Collect coins for time!")
        ]
        
        y = 250
        for key, name, desc in modes:
            key_text = self.font_medium.render(f"[{key}] {name}", True, Colors.GREEN.value)
            desc_text = self.font_small.render(desc, True, Colors.LIGHT_GRAY.value)
            
            self.screen.blit(key_text, (SCREEN_WIDTH // 2 - key_text.get_width() // 2, y))
            self.screen.blit(desc_text, (SCREEN_WIDTH // 2 - desc_text.get_width() // 2, y + 50))
            y += 120
        
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
