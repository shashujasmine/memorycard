"""
GAME PLATFORM HUB - Multi-Game Gaming Dashboard
Combines Memory Card Game + Chasing Game with unified stats & achievements
"""

import pygame
import random
import math
import sys
import json
import os
from enum import Enum
from dataclasses import dataclass, field
from typing import List, Tuple, Optional
from datetime import datetime

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# ==================== CONSTANTS ====================
SCREEN_WIDTH = 1400
SCREEN_HEIGHT = 900
FPS = 60
GAME_TITLE = "🎮 GAME PLATFORM HUB"
SAVE_FILE = "game_platform_data.json"


class PlatformState(Enum):
    MAIN_MENU = 1
    GAME_SELECTION = 2
    MEMORY_GAME = 3
    CHASING_GAME = 4
    STATS_DASHBOARD = 5
    ACHIEVEMENTS = 6
    LEADERBOARD = 7


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
    DARK_BLUE = (20, 50, 100)


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

@dataclass
class GameStats:
    game_name: str
    high_score: int = 0
    games_played: int = 0
    total_time: int = 0 
    best_time: int = 999999
    achievements_unlocked: int = 0

@dataclass
class PlatformAchievement:
    id: str
    name: str
    description: str
    game: str 
    icon: str
    unlocked: bool = False
    unlock_date: str = ""

@dataclass
class PlatformStats:
    player_name: str = "Player"
    total_score: int = 0
    games_completed: int = 0
    total_playtime: int = 0
    platform_level: int = 1
    memory_stats: GameStats = field(default_factory=lambda: GameStats("Memory Card"))
    chasing_stats: GameStats = field(default_factory=lambda: GameStats("Chasing"))
    achievements: List[PlatformAchievement] = field(default_factory=list)


class MemoryCard:
    def __init__(self, x: float, y: float, size: int, emoji: str):
        self.x = x
        self.y = y
        self.size = size
        self.emoji = emoji
        self.flipped = False
        self.matched = False
        self.rotation = 0
    
    def contains_point(self, px: float, py: float) -> bool:
        return (self.x <= px <= self.x + self.size and 
                self.y <= py <= self.y + self.size)
    
    def draw(self, surface: pygame.Surface, font_small):
        color = Colors.GREEN.value if self.matched else Colors.BLUE.value
        pygame.draw.rect(surface, color, (self.x, self.y, self.size, self.size))
        pygame.draw.rect(surface, Colors.YELLOW.value if not self.matched else Colors.LIGHT_GRAY.value,
                        (self.x, self.y, self.size, self.size), 3)
        
        if self.flipped or self.matched:
            text = font_small.render(self.emoji, True, Colors.WHITE.value)
            text_rect = text.get_rect(center=(self.x + self.size // 2, self.y + self.size // 2))
            surface.blit(text, text_rect)
        else:
            text = font_small.render("?", True, Colors.WHITE.value)
            text_rect = text.get_rect(center=(self.x + self.size // 2, self.y + self.size // 2))
            surface.blit(text, text_rect)

class MemoryCardGame:
    def __init__(self):
        self.grid_size = 4
        self.cards: List[MemoryCard] = []
        self.flipped_cards = []
        self.matched_count = 0
        self.moves = 0
        self.score = 0
        self.time_start = 0
        self.time_elapsed = 0
        self.emojis = ['🍕', '🎮', '🚀', '🎨', '🎭', '🎸', '🌟', '⚽', 
                       '🦄', '🐢', '🎯', '🎲', '🌈', '🎊', '🎈', '🎉']
        self.game_active = False
        self.game_over = False
        self.check_timer = 0
        self.card_size = 70
    
    def init_game(self):

        self.cards = []
        self.flipped_cards = []
        self.matched_count = 0
        self.moves = 0
        self.score = 0
        self.game_active = False
        self.game_over = False
        

        total_cards = self.grid_size * self.grid_size
        pairs = total_cards // 2
        emojis_selected = self.emojis[:pairs]
        emojis_shuffled = (emojis_selected + emojis_selected)
        random.shuffle(emojis_shuffled)
        
        start_x = 150
        start_y = 150
        spacing = 90
        
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                x = start_x + j * spacing
                y = start_y + i * spacing
                self.cards.append(MemoryCard(x, y, self.card_size, emojis_shuffled[i * self.grid_size + j]))
    
    def handle_click(self, x: float, y: float):

        if not self.game_active:
            self.game_active = True
            self.time_start = pygame.time.get_ticks()
        
        if self.game_over or len(self.flipped_cards) >= 2:
            return
        
        for card in self.cards:
            if card.contains_point(x, y) and not card.flipped and not card.matched:
                card.flipped = True
                self.flipped_cards.append(card)
                
                if len(self.flipped_cards) == 2:
                    self.moves += 1
                    if self.flipped_cards[0].emoji == self.flipped_cards[1].emoji:
                        self.flipped_cards[0].matched = True
                        self.flipped_cards[1].matched = True
                        self.matched_count += 2
                        self.score += 100 - (self.moves * 2)
                        self.flipped_cards = []
                        
                        if self.matched_count == len(self.cards):
                            self.game_over = True
                    else:
                        self.check_timer = 60 
    
    def update(self):

        if self.game_active and not self.game_over:
            self.time_elapsed = (pygame.time.get_ticks() - self.time_start) // 1000
        
        if self.check_timer > 0:
            self.check_timer -= 1
            if self.check_timer == 0 and len(self.flipped_cards) == 2:
                self.flipped_cards[0].flipped = False
                self.flipped_cards[1].flipped = False
                self.flipped_cards = []
    
    def draw(self, surface: pygame.Surface, font_small, font_medium):

        for card in self.cards:
            card.draw(surface, font_small)
        

        score_text = font_medium.render(f"Score: {self.score}", True, Colors.GREEN.value)
        moves_text = font_medium.render(f"Moves: {self.moves}", True, Colors.YELLOW.value)
        time_text = font_medium.render(f"Time: {self.time_elapsed}s", True, Colors.CYAN.value)
        
        surface.blit(score_text, (1050, 150))
        surface.blit(moves_text, (1050, 220))
        surface.blit(time_text, (1050, 290))
        
        if self.game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(200)
            overlay.fill(Colors.BLACK.value)
            surface.blit(overlay, (0, 0))
            
            win_text = font_medium.render("YOU WON!", True, Colors.GREEN.value)
            final_score_text = font_small.render(f"Final Score: {self.score}", True, Colors.YELLOW.value)
            
            surface.blit(win_text, (SCREEN_WIDTH // 2 - win_text.get_width() // 2, 300))
            surface.blit(final_score_text, (SCREEN_WIDTH // 2 - final_score_text.get_width() // 2, 400))


class ChasingGameInstance:
    def __init__(self):
        self.player_pos = Vector2(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.enemy_pos = Vector2(200, 200)
        self.coins: List[Tuple[float, float]] = []
        self.player_radius = 12
        self.enemy_radius = 10
        self.player_speed = 4
        self.enemy_speed = 1.8
        self.score = 0
        self.coins_collected = 0
        self.time_alive = 0
        self.game_over = False
        

        for _ in range(5):
            self.coins.append((
                random.randint(100, SCREEN_WIDTH - 100),
                random.randint(150, SCREEN_HEIGHT - 100)
            ))
    
    def handle_input(self, keys):
        """Handle player movement"""
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.player_pos.y -= self.player_speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.player_pos.y += self.player_speed
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.player_pos.x -= self.player_speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.player_pos.x += self.player_speed
        
        self.player_pos.x = max(self.player_radius, min(SCREEN_WIDTH - self.player_radius, self.player_pos.x))
        self.player_pos.y = max(100, min(SCREEN_HEIGHT - self.player_radius, self.player_pos.y))
    
    def update(self):

        if self.game_over:
            return
        
        self.time_alive += 1
        self.score += 0.1
        

        direction = Vector2(
            self.player_pos.x - self.enemy_pos.x,
            self.player_pos.y - self.enemy_pos.y
        ).normalize()
        
        self.enemy_pos.x += direction.x * self.enemy_speed
        self.enemy_pos.y += direction.y * self.enemy_speed
        
        self.enemy_pos.x = max(self.enemy_radius, min(SCREEN_WIDTH - self.enemy_radius, self.enemy_pos.x))
        self.enemy_pos.y = max(100, min(SCREEN_HEIGHT - self.enemy_radius, self.enemy_pos.y))
        

        for coin in self.coins[:]:
            dx = self.player_pos.x - coin[0]
            dy = self.player_pos.y - coin[1]
            dist = math.sqrt(dx ** 2 + dy ** 2)
            
            if dist < self.player_radius + 6:
                self.coins.remove(coin)
                self.coins_collected += 1
                self.score += 50
                
                if random.random() < 0.7:
                    self.coins.append((
                        random.randint(100, SCREEN_WIDTH - 100),
                        random.randint(150, SCREEN_HEIGHT - 100)
                    ))
        

        dx = self.player_pos.x - self.enemy_pos.x
        dy = self.player_pos.y - self.enemy_pos.y
        dist = math.sqrt(dx ** 2 + dy ** 2)
        
        if dist < (self.player_radius + self.enemy_radius):
            self.game_over = True
    
    def draw(self, surface: pygame.Surface, font_small):


        for coin in self.coins:
            pygame.draw.circle(surface, Colors.YELLOW.value, (int(coin[0]), int(coin[1])), 6)
            pygame.draw.circle(surface, Colors.ORANGE.value, (int(coin[0]), int(coin[1])), 6, 2)
        

        pygame.draw.circle(surface, Colors.BLUE.value, (int(self.player_pos.x), int(self.player_pos.y)), self.player_radius)
        pygame.draw.circle(surface, Colors.LIGHT_GRAY.value, (int(self.player_pos.x), int(self.player_pos.y)), self.player_radius, 2)
        

        pygame.draw.circle(surface, Colors.RED.value, (int(self.enemy_pos.x), int(self.enemy_pos.y)), self.enemy_radius)
        pygame.draw.circle(surface, Colors.YELLOW.value, (int(self.enemy_pos.x), int(self.enemy_pos.y)), self.enemy_radius, 2)
        
     
        score_text = font_small.render(f"Score: {int(self.score)}", True, Colors.GREEN.value)
        coins_text = font_small.render(f"Coins: {self.coins_collected}", True, Colors.YELLOW.value)
        time_text = font_small.render(f"Time: {self.time_alive // 60}s", True, Colors.CYAN.value)
        
        surface.blit(score_text, (20, 20))
        surface.blit(coins_text, (20, 55))
        surface.blit(time_text, (20, 90))
        
        if self.game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(200)
            overlay.fill(Colors.BLACK.value)
            surface.blit(overlay, (0, 0))
            
            game_over_text = font_small.render("GAME OVER!", True, Colors.RED.value)
            score_text = font_small.render(f"Final Score: {int(self.score)}", True, Colors.YELLOW.value)
            
            surface.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, 300))
            surface.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 380))


class GamePlatformHub:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(GAME_TITLE)
        self.clock = pygame.time.Clock()
        

        self.font_large = pygame.font.Font(None, 64)
        self.font_medium = pygame.font.Font(None, 40)
        self.font_small = pygame.font.Font(None, 28)
        self.font_tiny = pygame.font.Font(None, 18)
        
        self.state = PlatformState.MAIN_MENU
        self.load_stats()
        

        self.memory_game = MemoryCardGame()
        self.chasing_game = ChasingGameInstance()
        

        self.selected_game = 0
        self.scroll_offset = 0
    
    def load_stats(self):

        if os.path.exists(SAVE_FILE):
            try:
                with open(SAVE_FILE, 'r') as f:
                    data = json.load(f)
                    self.stats = PlatformStats(**data)
            except:
                self.stats = PlatformStats()
        else:
            self.stats = PlatformStats()
        
        self.init_achievements()
    
    def init_achievements(self):

        achievement_list = [
            PlatformAchievement("memory_master", "Memory Master", "Score 500+ in Memory Game", "Memory", "🧠"),
            PlatformAchievement("chasing_survivor", "Survivor", "Survive 30 seconds in Chasing", "Chasing", "🏃"),
            PlatformAchievement("speedster", "Speedster", "Complete Memory in under 30 seconds", "Memory", "⚡"),
            PlatformAchievement("coin_collector", "Coin Collector", "Collect 50 coins in one Chasing session", "Chasing", "💰"),
            PlatformAchievement("gaming_legend", "Gaming Legend", "Unlock 5 achievements", "Platform", "👑"),
        ]
        
        for ach in achievement_list:
            existing = next((a for a in self.stats.achievements if a.id == ach.id), None)
            if existing:
                ach.unlocked = existing.unlocked
                ach.unlock_date = existing.unlock_date
        
        self.stats.achievements = achievement_list
    
    def save_stats(self):

        try:
            data = {
                'player_name': self.stats.player_name,
                'total_score': self.stats.total_score,
                'games_completed': self.stats.games_completed,
                'total_playtime': self.stats.total_playtime,
                'platform_level': self.stats.platform_level,
                'memory_stats': {
                    'game_name': self.stats.memory_stats.game_name,
                    'high_score': self.stats.memory_stats.high_score,
                    'games_played': self.stats.memory_stats.games_played,
                },
                'chasing_stats': {
                    'game_name': self.stats.chasing_stats.game_name,
                    'high_score': self.stats.chasing_stats.high_score,
                    'games_played': self.stats.chasing_stats.games_played,
                },
                'achievements': [
                    {
                        'id': a.id, 'name': a.name, 'description': a.description,
                        'game': a.game, 'icon': a.icon, 'unlocked': a.unlocked,
                        'unlock_date': a.unlock_date
                    }
                    for a in self.stats.achievements
                ]
            }
            with open(SAVE_FILE, 'w') as f:
                json.dump(data, f, indent=2)
        except:
            pass
    
    def handle_input(self):

        keys = pygame.key.get_pressed()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.state in [PlatformState.MEMORY_GAME, PlatformState.CHASING_GAME]:
                        self.state = PlatformState.GAME_SELECTION
                    elif self.state != PlatformState.MAIN_MENU:
                        self.state = PlatformState.MAIN_MENU
                
                elif self.state == PlatformState.MAIN_MENU:
                    if event.key == pygame.K_SPACE:
                        self.state = PlatformState.GAME_SELECTION
                    elif event.key == pygame.K_s:
                        self.state = PlatformState.STATS_DASHBOARD
                    elif event.key == pygame.K_a:
                        self.state = PlatformState.ACHIEVEMENTS
                
                elif self.state == PlatformState.GAME_SELECTION:
                    if event.key == pygame.K_UP:
                        self.selected_game = (self.selected_game - 1) % 2
                    elif event.key == pygame.K_DOWN:
                        self.selected_game = (self.selected_game + 1) % 2
                    elif event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                        if self.selected_game == 0:
                            self.state = PlatformState.MEMORY_GAME
                            self.memory_game.init_game()
                        else:
                            self.state = PlatformState.CHASING_GAME
                            self.chasing_game = ChasingGameInstance()
                
                elif self.state == PlatformState.MEMORY_GAME:
                    pass
                
                elif self.state == PlatformState.CHASING_GAME:
                    if self.chasing_game.game_over:
                        if event.key == pygame.K_SPACE:
                            self.state = PlatformState.GAME_SELECTION
        

        if self.state == PlatformState.MEMORY_GAME:
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.memory_game.handle_click(event.pos[0], event.pos[1])
        
        elif self.state == PlatformState.CHASING_GAME:
            self.chasing_game.handle_input(keys)
        
        return True
    
    def update(self):
        """Update game state"""
        if self.state == PlatformState.MEMORY_GAME:
            self.memory_game.update()
        
        elif self.state == PlatformState.CHASING_GAME:
            self.chasing_game.update()
    
    def draw(self):
        """Draw everything"""
        self.screen.fill(Colors.DARK_GRAY.value)
        
        if self.state == PlatformState.MAIN_MENU:
            self.draw_main_menu()
        elif self.state == PlatformState.GAME_SELECTION:
            self.draw_game_selection()
        elif self.state == PlatformState.MEMORY_GAME:
            self.draw_game_hud("Memory Card Game")
            self.memory_game.draw(self.screen, self.font_small, self.font_medium)
        elif self.state == PlatformState.CHASING_GAME:
            self.draw_game_hud("Chasing Game")
            self.chasing_game.draw(self.screen, self.font_small)
        elif self.state == PlatformState.STATS_DASHBOARD:
            self.draw_stats_dashboard()
        elif self.state == PlatformState.ACHIEVEMENTS:
            self.draw_achievements()
        
        pygame.display.flip()
    
    def draw_main_menu(self):
        """Draw main menu"""
        # Title
        title = self.font_large.render("GAME PLATFORM HUB", True, Colors.CYAN.value)
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 100))
        
        # Subtitle
        subtitle = self.font_medium.render(f"Welcome, {self.stats.player_name}!", True, Colors.GREEN.value)
        self.screen.blit(subtitle, (SCREEN_WIDTH // 2 - subtitle.get_width() // 2, 200))
        
        # Menu options
        y = 350
        options = [
            ("SPACE", "Play Games"),
            ("S", "Statistics"),
            ("A", "Achievements"),
            ("Q", "Quit")
        ]
        
        for key, option in options:
            key_text = self.font_small.render(f"[{key}]", True, Colors.YELLOW.value)
            option_text = self.font_small.render(option, True, Colors.WHITE.value)
            
            self.screen.blit(key_text, (SCREEN_WIDTH // 2 - 200, y))
            self.screen.blit(option_text, (SCREEN_WIDTH // 2 - 100, y))
            y += 80
        
        # Stats preview
        y = 350
        stats_lines = [
            f"Level: {self.stats.platform_level}",
            f"Games: {self.stats.games_completed}",
            f"Total Score: {self.stats.total_score}"
        ]
        
        for line in stats_lines:
            text = self.font_tiny.render(line, True, Colors.CYAN.value)
            self.screen.blit(text, (SCREEN_WIDTH - 350, y))
            y += 35
    
    def draw_game_selection(self):
        """Draw game selection menu"""
        title = self.font_large.render("SELECT A GAME", True, Colors.CYAN.value)
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 100))
        
        games = [
            ("🧠 MEMORY CARD GAME", "Match pairs and test your memory"),
            ("🏃 CHASING GAME", "Avoid enemy and collect coins")
        ]
        
        y = 300
        for i, (name, desc) in enumerate(games):
            color = Colors.GREEN.value if i == self.selected_game else Colors.WHITE.value
            
            name_text = self.font_medium.render(name, True, color)
            desc_text = self.font_small.render(desc, True, Colors.LIGHT_GRAY.value)
            
            if i == self.selected_game:
                pygame.draw.rect(self.screen, Colors.BLUE.value, 
                               (SCREEN_WIDTH // 2 - 300, y - 20, 600, 100))
            
            self.screen.blit(name_text, (SCREEN_WIDTH // 2 - name_text.get_width() // 2, y))
            self.screen.blit(desc_text, (SCREEN_WIDTH // 2 - desc_text.get_width() // 2, y + 50))
            y += 200
        
        # Instructions
        inst_text = self.font_small.render("↑ ↓ Navigate | SPACE Select | ESC Back", True, Colors.YELLOW.value)
        self.screen.blit(inst_text, (SCREEN_WIDTH // 2 - inst_text.get_width() // 2, SCREEN_HEIGHT - 100))
    
    def draw_game_hud(self, game_name: str):
        """Draw game header HUD"""
        pygame.draw.rect(self.screen, Colors.BLACK.value, (0, 0, SCREEN_WIDTH, 70))
        pygame.draw.line(self.screen, Colors.CYAN.value, (0, 70), (SCREEN_WIDTH, 70), 2)
        
        title = self.font_medium.render(game_name, True, Colors.CYAN.value)
        esc_text = self.font_tiny.render("ESC to Back | SPACE to Restart", True, Colors.YELLOW.value)
        
        self.screen.blit(title, (20, 15))
        self.screen.blit(esc_text, (SCREEN_WIDTH - 350, 20))
    
    def draw_stats_dashboard(self):
        """Draw statistics dashboard"""
        title = self.font_large.render("📊 STATISTICS DASHBOARD", True, Colors.CYAN.value)
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 50))
        
        y = 150
        
        # Overall stats
        overall_stats = [
            f"Player Level: {self.stats.platform_level}",
            f"Total Games Played: {self.stats.games_completed}",
            f"Total Score: {self.stats.total_score}",
            f"Achievements Unlocked: {sum(1 for a in self.stats.achievements if a.unlocked)}/{len(self.stats.achievements)}"
        ]
        
        for stat in overall_stats:
            text = self.font_small.render(stat, True, Colors.GREEN.value)
            self.screen.blit(text, (100, y))
            y += 50
        
        # Game-specific stats
        y += 30
        games_header = self.font_medium.render("GAME STATISTICS", True, Colors.YELLOW.value)
        self.screen.blit(games_header, (100, y))
        y += 60
        
        # Memory game stats
        memory_text = self.font_small.render(f"🧠 Memory Card: High Score {self.stats.memory_stats.high_score} | {self.stats.memory_stats.games_played} plays", True, Colors.BLUE.value)
        self.screen.blit(memory_text, (120, y))
        y += 45
        
        # Chasing game stats
        chasing_text = self.font_small.render(f"🏃 Chasing: High Score {self.stats.chasing_stats.high_score} | {self.stats.chasing_stats.games_played} plays", True, Colors.RED.value)
        self.screen.blit(chasing_text, (120, y))
        
        # Back instruction
        back_text = self.font_small.render("Press ESC to go back", True, Colors.YELLOW.value)
        self.screen.blit(back_text, (SCREEN_WIDTH // 2 - back_text.get_width() // 2, SCREEN_HEIGHT - 80))
    
    def draw_achievements(self):
        """Draw achievements page"""
        title = self.font_large.render("🏆 ACHIEVEMENTS", True, Colors.CYAN.value)
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 50))
        
        y = 150
        unlocked_count = sum(1 for a in self.stats.achievements if a.unlocked)
        counter_text = self.font_small.render(f"Unlocked: {unlocked_count}/{len(self.stats.achievements)}", True, Colors.GREEN.value)
        self.screen.blit(counter_text, (100, y))
        y += 50
        
        for achievement in self.stats.achievements:
            if achievement.unlocked:
                color = Colors.YELLOW.value
                text = f"✓ {achievement.icon} {achievement.name}"
            else:
                color = Colors.LIGHT_GRAY.value
                text = f"✗ {achievement.name}"
            
            ach_text = self.font_small.render(text, True, color)
            desc_text = self.font_tiny.render(achievement.description, True, Colors.LIGHT_GRAY.value)
            
            self.screen.blit(ach_text, (120, y))
            self.screen.blit(desc_text, (140, y + 30))
            y += 70
        
        # Back instruction
        back_text = self.font_small.render("Press ESC to go back", True, Colors.YELLOW.value)
        self.screen.blit(back_text, (SCREEN_WIDTH // 2 - back_text.get_width() // 2, SCREEN_HEIGHT - 80))
    
    def run(self):
        """Main loop"""
        running = True
        while running:
            running = self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        self.save_stats()
        pygame.quit()
        sys.exit()

# ==================== MAIN ====================
if __name__ == "__main__":
    platform = GamePlatformHub()
    platform.run()
