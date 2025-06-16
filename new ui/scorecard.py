import pygame
import tkinter as tk
from tkinter import ttk
import threading
import time
import sys
from typing import List, Tuple

class GameApplication:
    def __init__(self):
        self.current_screen = "rumbleverse"  # "rumbleverse" or "volleyball"
        self.rumbleverse_app = None
        self.volleyball_app = None
        
    def start_rumbleverse(self):
        self.current_screen = "rumbleverse"
        self.rumbleverse_app = RumbleVerseUI(self)
        self.rumbleverse_app.run()
        
    def start_volleyball(self):
        self.current_screen = "volleyball"
        if self.rumbleverse_app:
            pygame.quit()
        self.volleyball_app = VolleyballScoreboard(self)
        self.volleyball_app.run()
        
    def back_to_rumbleverse(self):
        if self.volleyball_app:
            self.volleyball_app.root.destroy()
        pygame.init()
        self.start_rumbleverse()

# RumbleVerse Game Mode Selection (Modified)
pygame.init()

# Constants for RumbleVerse
SCREEN_WIDTH = 1400
SCREEN_HEIGHT = 800
FPS = 60

# Colors
PURPLE_DARK = (45, 25, 85)
PURPLE_MID = (85, 45, 125)
PURPLE_LIGHT = (125, 85, 165)
CYAN = (64, 224, 255)
ORANGE = (255, 165, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)

class GameModeCard:
    def __init__(self, x: int, y: int, width: int, height: int, title: str, subtitle: str, 
                 color: Tuple[int, int, int] = PURPLE_MID, border_color: Tuple[int, int, int] = WHITE,
                 is_selected: bool = False):
        self.rect = pygame.Rect(x, y, width, height)
        self.title = title
        self.subtitle = subtitle
        self.color = color
        self.border_color = border_color if not is_selected else ORANGE
        self.is_selected = is_selected
        self.border_width = 4 if is_selected else 2
        
    def draw(self, screen: pygame.Surface, font_large: pygame.font.Font, font_small: pygame.font.Font):
        # Draw card background
        pygame.draw.rect(screen, self.color, self.rect)
        pygame.draw.rect(screen, self.border_color, self.rect, self.border_width)
        
        # Draw title
        title_surface = font_large.render(self.title, True, WHITE)
        title_rect = title_surface.get_rect(center=(self.rect.centerx, self.rect.bottom - 80))
        screen.blit(title_surface, title_rect)
        
        # Draw subtitle
        subtitle_surface = font_small.render(self.subtitle, True, GRAY)
        subtitle_rect = subtitle_surface.get_rect(center=(self.rect.centerx, self.rect.bottom - 50))
        screen.blit(subtitle_surface, subtitle_rect)
        
        # Draw character placeholder (simplified representation)
        char_rect = pygame.Rect(self.rect.x + 20, self.rect.y + 20, self.rect.width - 40, self.rect.height - 120)
        pygame.draw.rect(screen, PURPLE_DARK, char_rect)
        
        # Add some visual elements to represent characters
        if self.title == "Solo":
            pygame.draw.circle(screen, WHITE, (char_rect.centerx, char_rect.centery - 20), 30)
            pygame.draw.circle(screen, BLACK, (char_rect.centerx - 10, char_rect.centery - 30), 5)
            pygame.draw.circle(screen, BLACK, (char_rect.centerx + 10, char_rect.centery - 30), 5)
            # Add volleyball indicator for Solo mode
            pygame.draw.circle(screen, (255, 215, 0), (char_rect.centerx, char_rect.centery + 20), 15)
            pygame.draw.arc(screen, WHITE, (char_rect.centerx - 15, char_rect.centery + 5, 30, 30), 0.5, 2.5, 3)
        elif self.title == "Duo":
            pygame.draw.circle(screen, WHITE, (char_rect.centerx - 25, char_rect.centery), 25)
            pygame.draw.circle(screen, CYAN, (char_rect.centerx + 25, char_rect.centery), 25)
        elif self.title == "Trio":
            pygame.draw.circle(screen, WHITE, (char_rect.centerx - 30, char_rect.centery - 10), 20)
            pygame.draw.circle(screen, CYAN, (char_rect.centerx, char_rect.centery + 10), 20)
            pygame.draw.circle(screen, ORANGE, (char_rect.centerx + 30, char_rect.centery - 10), 20)
        elif self.title == "Quad":
            pygame.draw.circle(screen, WHITE, (char_rect.centerx - 25, char_rect.centery - 15), 18)
            pygame.draw.circle(screen, CYAN, (char_rect.centerx + 25, char_rect.centery - 15), 18)
            pygame.draw.circle(screen, ORANGE, (char_rect.centerx - 25, char_rect.centery + 15), 18)
            pygame.draw.circle(screen, (255, 100, 255), (char_rect.centerx + 25, char_rect.centery + 15), 18)
        elif self.title == "Playground":
            # Draw city silhouette
            for i in range(5):
                building_height = 40 + (i * 15) % 60
                pygame.draw.rect(screen, CYAN, 
                               (char_rect.x + i * 30, char_rect.bottom - building_height, 25, building_height))

class RumbleVerseUI:
    def __init__(self, main_app):
        self.main_app = main_app
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("RumbleVerse - Game Mode Selection")
        self.clock = pygame.time.Clock()
        
        # Fonts
        self.font_title = pygame.font.Font(None, 72)
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 24)
        
        # Game mode cards
        card_width = 220
        card_height = 400
        start_x = 100
        spacing = 240
        card_y = 180
        
        self.game_modes = [
            GameModeCard(start_x, card_y, card_width, card_height, "Ranked", "", 
                        PURPLE_MID, ORANGE, True),
            GameModeCard(start_x + spacing, card_y, card_width, card_height, "Clash", "Office Battle"),
            GameModeCard(start_x + spacing * 2, card_y, card_width, card_height, "Time Trail", "Play Fast"),
            GameModeCard(start_x + spacing * 3, card_y, card_width, card_height, "Play Anon", "Battle Royale"),
            GameModeCard(start_x + spacing * 4, card_y, card_width, card_height, "Pay to Play", 
                        "ScanQR", PURPLE_LIGHT, CYAN)
        ]
        
        self.selected_mode = 0
        
    def draw_background(self):
        # Create gradient background
        for y in range(SCREEN_HEIGHT):
            color_ratio = y / SCREEN_HEIGHT
            r = int(PURPLE_DARK[0] + (PURPLE_LIGHT[0] - PURPLE_DARK[0]) * color_ratio)
            g = int(PURPLE_DARK[1] + (PURPLE_LIGHT[1] - PURPLE_DARK[1]) * color_ratio)
            b = int(PURPLE_DARK[2] + (PURPLE_LIGHT[2] - PURPLE_DARK[2]) * color_ratio)
            pygame.draw.line(self.screen, (r, g, b), (0, y), (SCREEN_WIDTH, y))
        
        # Draw some background elements (simplified city silhouette)
        for i in range(20):
            building_x = i * 70
            building_height = 100 + (i * 23) % 200
            building_width = 50 + (i * 17) % 30
            color_variation = 20 + (i * 13) % 40
            building_color = (PURPLE_DARK[0] + color_variation, 
                            PURPLE_DARK[1] + color_variation, 
                            PURPLE_DARK[2] + color_variation)
            pygame.draw.rect(self.screen, building_color, 
                           (building_x, SCREEN_HEIGHT - building_height, building_width, building_height))
    
    def draw_title(self):
        title_surface = self.font_title.render("Game Modes", True, CYAN)
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, 80))
        self.screen.blit(title_surface, title_rect)
        
        # Draw decorative lines
        line_y = 120
        pygame.draw.line(self.screen, CYAN, (50, line_y), (SCREEN_WIDTH - 50, line_y), 2)
        
        # Add instruction text
        instruction_surface = self.font_small.render("Click SOLO to open Foosball Scoreboard", True, WHITE)
        instruction_rect = instruction_surface.get_rect(center=(SCREEN_WIDTH // 2, 140))
        self.screen.blit(instruction_surface, instruction_rect)
    
    def draw_bottom_ui(self):
        # Bottom control hints
        controls = [
            ("Esc", "Back"),
            ("Enter", "Select Mode"),
            ("Click", "Ranked Mode")
        ]
        
        x_pos = 50
        for key, action in controls:
            # Draw key background
            key_rect = pygame.Rect(x_pos, SCREEN_HEIGHT - 60, 60, 30)
            pygame.draw.rect(self.screen, GRAY, key_rect)
            pygame.draw.rect(self.screen, WHITE, key_rect, 2)
            
            # Draw key text
            key_surface = self.font_small.render(key, True, BLACK)
            key_text_rect = key_surface.get_rect(center=key_rect.center)
            self.screen.blit(key_surface, key_text_rect)
            
            # Draw action text
            action_surface = self.font_small.render(action, True, WHITE)
            self.screen.blit(action_surface, (x_pos + 70, SCREEN_HEIGHT - 55))
            
            x_pos += 250
    
    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT and self.selected_mode > 0:
                self.game_modes[self.selected_mode].is_selected = False
                self.game_modes[self.selected_mode].border_color = WHITE
                self.game_modes[self.selected_mode].border_width = 2
                self.selected_mode -= 1
                self.game_modes[self.selected_mode].is_selected = True
                self.game_modes[self.selected_mode].border_color = ORANGE
                self.game_modes[self.selected_mode].border_width = 4
                
            elif event.key == pygame.K_RIGHT and self.selected_mode < len(self.game_modes) - 1:
                self.game_modes[self.selected_mode].is_selected = False
                self.game_modes[self.selected_mode].border_color = WHITE
                self.game_modes[self.selected_mode].border_width = 2
                self.selected_mode += 1
                self.game_modes[self.selected_mode].is_selected = True
                self.game_modes[self.selected_mode].border_color = ORANGE
                self.game_modes[self.selected_mode].border_width = 4
                
            elif event.key == pygame.K_RETURN:
                selected_mode = self.game_modes[self.selected_mode].title
                print(f"Selected: {selected_mode}")
                if selected_mode == "Ranked":
                    self.main_app.start_volleyball()
                    return False  # Exit pygame loop
                
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            for i, mode in enumerate(self.game_modes):
                if mode.rect.collidepoint(mouse_pos):
                    # Deselect current
                    self.game_modes[self.selected_mode].is_selected = False
                    self.game_modes[self.selected_mode].border_color = WHITE
                    self.game_modes[self.selected_mode].border_width = 2
                    
                    # Select new
                    self.selected_mode = i
                    mode.is_selected = True
                    mode.border_color = ORANGE
                    mode.border_width = 4
                    
                    # If Solo is clicked, open volleyball scoreboard
                    if mode.title == "Solo":
                        print("Opening Foosball Scoreboard...")
                        self.main_app.start_volleyball()
                        return False  # Exit pygame loop
                    break
        return True
    
    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    else:
                        if not self.handle_input(event):
                            return  # Exit to volleyball
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if not self.handle_input(event):
                        return  # Exit to volleyball
            
            # Draw everything
            self.draw_background()
            self.draw_title()
            
            # Draw game mode cards
            for mode in self.game_modes:
                mode.draw(self.screen, self.font_large, self.font_medium)
            
            self.draw_bottom_ui()
            
            pygame.display.flip()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

# Volleyball Scoreboard Application (Modified)
class VolleyballScoreboard:
    def __init__(self, main_app):
        self.main_app = main_app
        self.root = tk.Tk()
        self.root.title("Foosball Scoreboard")
        self.root.geometry("1200x800")
        self.root.configure(bg='#1e3a5f')
        
        # Game state variables
        self.home_score = tk.IntVar(value=0)
        self.away_score = tk.IntVar(value=0)
        self.home_sets = tk.IntVar(value=0)
        self.away_sets = tk.IntVar(value=0)
        self.home_timeouts = tk.IntVar(value=2)
        self.away_timeouts = tk.IntVar(value=2)
        self.current_set = tk.IntVar(value=1)
        self.serve_side = tk.StringVar(value="HOME")  # HOME or AWAY
        
        # Timer variables
        self.game_minutes = tk.IntVar(value=15)
        self.game_seconds = tk.IntVar(value=0)
        self.timer_running = False
        self.timer_thread = None
        
        self.setup_ui()
        
    def setup_ui(self):
        # Create main container
        main_frame = tk.Frame(self.root, bg='#1e3a5f')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Header section
        self.create_header(main_frame)
        
        # Volleyball section with scores
        self.create_volleyball_section(main_frame)
        
        # Control buttons section
        self.create_control_section(main_frame)
        
        # Sets and timeouts section
        self.create_sets_timeouts_section(main_frame)
        
        # Game clock section
        self.create_game_clock_section(main_frame)
        
    def create_header(self, parent):
        header_frame = tk.Frame(parent, bg='#1e3a5f')
        header_frame.pack(fill='x', pady=(0, 20))
        
        # Back to RumbleVerse button
        back_btn = tk.Button(header_frame, text="← Back to Game Modes", font=('Arial', 12, 'bold'), 
                           bg='#4a6fa5', fg='white', bd=0, padx=15, pady=5,
                           command=self.back_to_rumbleverse)
        back_btn.pack(side='left')
        
        # Team names
        tk.Label(header_frame, text="LEGENDS", font=('Arial', 18, 'bold'), 
                fg='white', bg='#1e3a5f').pack(side='left', padx=(20, 0))
        
        tk.Label(header_frame, text="FALCONS", font=('Arial', 18, 'bold'), 
                fg='white', bg='#1e3a5f').pack(side='right', padx=(0, 20))
        
        # Refresh button
        refresh_btn = tk.Button(header_frame, text="↻", font=('Arial', 16, 'bold'), 
                              bg='#4a6fa5', fg='white', bd=0, padx=10, pady=5,
                              command=self.reset_game)
        refresh_btn.pack(side='right')
        
    def create_volleyball_section(self, parent):
        # Main volleyball container with curved background
        volleyball_frame = tk.Frame(parent, bg='#4a6fa5', relief='raised', bd=2)
        volleyball_frame.pack(fill='x', pady=(0, 20))
        
        # Configure grid weights
        volleyball_frame.grid_columnconfigure(0, weight=1)
        volleyball_frame.grid_columnconfigure(1, weight=1)
        volleyball_frame.grid_columnconfigure(2, weight=1)
        
        # Home team score section
        home_frame = tk.Frame(volleyball_frame, bg='#4a6fa5')
        home_frame.grid(row=0, column=0, padx=20, pady=20, sticky='ew')
        
        tk.Label(home_frame, textvariable=self.home_score, font=('Arial', 72, 'bold'), 
                fg='white', bg='#4a6fa5').pack()
        tk.Label(home_frame, text="HOME TEAM", font=('Arial', 12), 
                fg='#cccccc', bg='#4a6fa5').pack()
        
        # Center volleyball section
        center_frame = tk.Frame(volleyball_frame, bg='#4a6fa5')
        center_frame.grid(row=0, column=1, padx=20, pady=20)
        
        # Volleyball image placeholder (circle with pattern)
        volleyball_canvas = tk.Canvas(center_frame, width=120, height=120, 
                                    bg='#4a6fa5', highlightthickness=0)
        volleyball_canvas.pack()
        
        # Draw volleyball
        volleyball_canvas.create_oval(10, 10, 110, 110, fill='#ffd700', outline='white', width=3)
        volleyball_canvas.create_arc(10, 10, 110, 110, start=45, extent=90, 
                                   outline='white', width=3, style='arc')
        volleyball_canvas.create_arc(10, 10, 110, 110, start=225, extent=90, 
                                   outline='white', width=3, style='arc')
        
        tk.Label(center_frame, text="FOOSBALL", font=('Arial', 10, 'bold'), 
                fg='white', bg='#4a6fa5').pack(pady=(5, 0))
        tk.Label(center_frame, text="V/S", font=('Arial', 16, 'bold'), 
                fg='white', bg='#4a6fa5').pack()
        
        # Serve indicator
        serve_frame = tk.Frame(center_frame, bg='#4a6fa5')
        serve_frame.pack(pady=(10, 0))
        
        tk.Button(serve_frame, text="◀", font=('Arial', 12), bg='#666666', fg='white', 
                 bd=0, padx=10, command=lambda: self.change_serve('HOME')).pack(side='left')
        tk.Label(serve_frame, text="SERVE", font=('Arial', 12, 'bold'), 
                fg='white', bg='#4a6fa5', padx=20).pack(side='left')
        tk.Button(serve_frame, text="▶", font=('Arial', 12), bg='#666666', fg='white', 
                 bd=0, padx=10, command=lambda: self.change_serve('AWAY')).pack(side='left')
        
        # Away team score section
        away_frame = tk.Frame(volleyball_frame, bg='#4a6fa5')
        away_frame.grid(row=0, column=2, padx=20, pady=20, sticky='ew')
        
        tk.Label(away_frame, textvariable=self.away_score, font=('Arial', 72, 'bold'), 
                fg='white', bg='#4a6fa5').pack()
        tk.Label(away_frame, text="AWAY TEAM", font=('Arial', 12), 
                fg='#cccccc', bg='#4a6fa5').pack()
        
    def create_control_section(self, parent):
        control_frame = tk.Frame(parent, bg='#1e3a5f')
        control_frame.pack(fill='x', pady=(0, 20))
        
        # Left side - Home team controls
        left_frame = tk.Frame(control_frame, bg='#1e3a5f')
        left_frame.pack(side='left', padx=(0, 20))
        
        tk.Label(left_frame, text="POINTS", font=('Arial', 10), 
                fg='#cccccc', bg='#1e3a5f').pack()
        
        home_points_frame = tk.Frame(left_frame, bg='#1e3a5f')
        home_points_frame.pack(pady=5)
        
        tk.Button(home_points_frame, text="+1", font=('Arial', 16, 'bold'), 
                 bg='#4a6fa5', fg='white', bd=0, padx=20, pady=10,
                 command=lambda: self.change_score('HOME', 1)).pack(side='left', padx=(0, 5))
        tk.Button(home_points_frame, text="-1", font=('Arial', 16, 'bold'), 
                 bg='#8b4a6b', fg='white', bd=0, padx=20, pady=10,
                 command=lambda: self.change_score('HOME', -1)).pack(side='left')
        
        # Center - Set indicator
        center_frame = tk.Frame(control_frame, bg='#1e3a5f')
        center_frame.pack(side='left', expand=True)
        
        set_frame = tk.Frame(center_frame, bg='#4a6fa5', relief='raised', bd=2)
        set_frame.pack(pady=10)
        
        set_control_frame = tk.Frame(set_frame, bg='#4a6fa5')
        set_control_frame.pack(padx=20, pady=15)
        
        tk.Button(set_control_frame, text="◀", font=('Arial', 12), bg='white', fg='#4a6fa5', 
                 bd=0, padx=10, command=self.prev_set).pack(side='left')
        self.set_label = tk.Label(set_control_frame, text="1st Set", font=('Arial', 16, 'bold'), 
                                 fg='white', bg='#4a6fa5', padx=20)
        self.set_label.pack(side='left')
        tk.Button(set_control_frame, text="▶", font=('Arial', 12), bg='white', fg='#4a6fa5', 
                 bd=0, padx=10, command=self.next_set).pack(side='left')
        
        # Right side - Away team controls
        right_frame = tk.Frame(control_frame, bg='#1e3a5f')
        right_frame.pack(side='right', padx=(20, 0))
        
        tk.Label(right_frame, text="POINTS", font=('Arial', 10), 
                fg='#cccccc', bg='#1e3a5f').pack()
        
        away_points_frame = tk.Frame(right_frame, bg='#1e3a5f')
        away_points_frame.pack(pady=5)
        
        tk.Button(away_points_frame, text="-1", font=('Arial', 16, 'bold'), 
                 bg='#8b4a6b', fg='white', bd=0, padx=20, pady=10,
                 command=lambda: self.change_score('AWAY', -1)).pack(side='left', padx=(0, 5))
        tk.Button(away_points_frame, text="+1", font=('Arial', 16, 'bold'), 
                 bg='#4a6fa5', fg='white', bd=0, padx=20, pady=10,
                 command=lambda: self.change_score('AWAY', 1)).pack(side='left')
        
    def create_sets_timeouts_section(self, parent):
        stats_frame = tk.Frame(parent, bg='#1e3a5f')
        stats_frame.pack(fill='x', pady=(0, 20))
        
        # Home team stats
        home_stats = tk.Frame(stats_frame, bg='#1e3a5f')
        home_stats.pack(side='left')
        
        # Sets won
        tk.Label(home_stats, text="SETS WON", font=('Arial', 10), 
                fg='#cccccc', bg='#1e3a5f').pack()
        home_sets_frame = tk.Frame(home_stats, bg='#4a6fa5', relief='raised', bd=2)
        home_sets_frame.pack(pady=5, padx=(0, 10))
        
        home_sets_control = tk.Frame(home_sets_frame, bg='#4a6fa5')
        home_sets_control.pack(padx=10, pady=10)
        
        tk.Button(home_sets_control, text="−", font=('Arial', 12, 'bold'), bg='white', fg='#4a6fa5', 
                 bd=0, padx=8, command=lambda: self.change_sets('HOME', -1)).pack(side='left')
        tk.Label(home_sets_control, textvariable=self.home_sets, font=('Arial', 24, 'bold'), 
                fg='white', bg='#4a6fa5', padx=15).pack(side='left')
        tk.Button(home_sets_control, text="+", font=('Arial', 12, 'bold'), bg='white', fg='#4a6fa5', 
                 bd=0, padx=8, command=lambda: self.change_sets('HOME', 1)).pack(side='left')
        
        # Time outs
        tk.Label(home_stats, text="TIME OUTS", font=('Arial', 10), 
                fg='#cccccc', bg='#1e3a5f').pack(pady=(10, 0))
        home_timeouts_frame = tk.Frame(home_stats, bg='#4a6fa5', relief='raised', bd=2)
        home_timeouts_frame.pack(pady=5)
        
        home_timeouts_control = tk.Frame(home_timeouts_frame, bg='#4a6fa5')
        home_timeouts_control.pack(padx=10, pady=10)
        
        tk.Button(home_timeouts_control, text="−", font=('Arial', 12, 'bold'), bg='white', fg='#4a6fa5', 
                 bd=0, padx=8, command=lambda: self.change_timeouts('HOME', -1)).pack(side='left')
        tk.Label(home_timeouts_control, textvariable=self.home_timeouts, font=('Arial', 24, 'bold'), 
                fg='white', bg='#4a6fa5', padx=15).pack(side='left')
        tk.Button(home_timeouts_control, text="+", font=('Arial', 12, 'bold'), bg='white', fg='#4a6fa5', 
                 bd=0, padx=8, command=lambda: self.change_timeouts('HOME', 1)).pack(side='left')
        
        # Center horn button
        center_stats = tk.Frame(stats_frame, bg='#1e3a5f')
        center_stats.pack(side='left', expand=True)
        
        horn_canvas = tk.Canvas(center_stats, width=80, height=80, bg='white', highlightthickness=0)
        horn_canvas.pack()
        horn_canvas.create_oval(10, 10, 70, 70, fill='white', outline='#4a6fa5', width=2)
        # Draw horn icon
        horn_canvas.create_polygon(25, 35, 35, 30, 45, 30, 55, 25, 55, 55, 45, 50, 35, 50, 25, 45, 
                                 fill='#4a6fa5')
        horn_canvas.bind("<Button-1>", self.sound_horn)
        
        # Away team stats
        away_stats = tk.Frame(stats_frame, bg='#1e3a5f')
        away_stats.pack(side='right')
        
        # Time outs
        tk.Label(away_stats, text="TIME OUTS", font=('Arial', 10), 
                fg='#cccccc', bg='#1e3a5f').pack()
        away_timeouts_frame = tk.Frame(away_stats, bg='#4a6fa5', relief='raised', bd=2)
        away_timeouts_frame.pack(pady=5, padx=(10, 0))
        
        away_timeouts_control = tk.Frame(away_timeouts_frame, bg='#4a6fa5')
        away_timeouts_control.pack(padx=10, pady=10)
        
        tk.Button(away_timeouts_control, text="−", font=('Arial', 12, 'bold'), bg='white', fg='#4a6fa5', 
                 bd=0, padx=8, command=lambda: self.change_timeouts('AWAY', -1)).pack(side='left')
        tk.Label(away_timeouts_control, textvariable=self.away_timeouts, font=('Arial', 24, 'bold'), 
                fg='white', bg='#4a6fa5', padx=15).pack(side='left')
        tk.Button(away_timeouts_control, text="+", font=('Arial', 12, 'bold'), bg='white', fg='#4a6fa5', 
                 bd=0, padx=8, command=lambda: self.change_timeouts('AWAY', 1)).pack(side='left')
        
        # Sets won
        tk.Label(away_stats, text="SETS WON", font=('Arial', 10), 
                fg='#cccccc', bg='#1e3a5f').pack(pady=(10, 0))
        away_sets_frame = tk.Frame(away_stats, bg='#4a6fa5', relief='raised', bd=2)
        away_sets_frame.pack(pady=5)
        
        away_sets_control = tk.Frame(away_sets_frame, bg='#4a6fa5')
        away_sets_control.pack(padx=10, pady=10)
        
        tk.Button(away_sets_control, text="−", font=('Arial', 12, 'bold'), bg='white', fg='#4a6fa5', 
                 bd=0, padx=8, command=lambda: self.change_sets('AWAY', -1)).pack(side='left')
        tk.Label(away_sets_control, textvariable=self.away_sets, font=('Arial', 24, 'bold'), 
                fg='white', bg='#4a6fa5', padx=15).pack(side='left')
        tk.Button(away_sets_control, text="+", font=('Arial', 12, 'bold'), bg='white', fg='#4a6fa5', 
                 bd=0, padx=8, command=lambda: self.change_sets('AWAY', 1)).pack(side='left')
        
    def create_game_clock_section(self, parent):
        clock_frame = tk.Frame(parent, bg='#4a6fa5', relief='raised', bd=2)
        clock_frame.pack(fill='x', pady=10)
        
        clock_container = tk.Frame(clock_frame, bg='#4a6fa5')
        clock_container.pack(pady=20)
        
        # Play button
        play_canvas = tk.Canvas(clock_container, width=60, height=60, bg='white', highlightthickness=0)
        play_canvas.pack(side='left', padx=(0, 20))
        play_canvas.create_oval(5, 5, 55, 55, fill='white', outline='#4a6fa5', width=2)
        play_canvas.create_polygon(22, 18, 22, 42, 42, 30, fill='#4a6fa5')
        play_canvas.bind("<Button-1>", self.toggle_timer)
        
        # Game clock label
        tk.Label(clock_container, text="GAME CLOCK", font=('Arial', 12, 'bold'), 
                fg='white', bg='#4a6fa5').pack(side='left', padx=(0, 20))
        
        # Time display
        time_frame = tk.Frame(clock_container, bg='#4a6fa5')
        time_frame.pack(side='left', padx=(0, 20))
        
        minutes_frame = tk.Frame(time_frame, bg='#666666', relief='raised', bd=2)
        minutes_frame.pack(side='left', padx=(0, 5))
        self.minutes_label = tk.Label(minutes_frame, textvariable=self.game_minutes, 
                                    font=('Arial', 24, 'bold'), fg='white', bg='#666666', 
                                    padx=15, pady=10)
        self.minutes_label.pack()
        
        tk.Label(time_frame, text=":", font=('Arial', 24, 'bold'), 
                fg='white', bg='#4a6fa5').pack(side='left')
        
        seconds_frame = tk.Frame(time_frame, bg='#666666', relief='raised', bd=2)
        seconds_frame.pack(side='left', padx=(5, 0))
        self.seconds_label = tk.Label(seconds_frame, text="00", 
                                    font=('Arial', 24, 'bold'), fg='white', bg='#666666', 
                                    padx=15, pady=10)
        self.seconds_label.pack()
        
        # Reset button
        reset_canvas = tk.Canvas(clock_container, width=60, height=60, bg='white', highlightthickness=0)
        reset_canvas.pack(side='left', padx=(20, 20))
        reset_canvas.create_oval(5, 5, 55, 55, fill='white', outline='#4a6fa5', width=2)
        reset_canvas.create_arc(15, 15, 45, 45, start=45, extent=270, outline='#4a6fa5', width=3)
        reset_canvas.create_polygon(42, 18, 48, 24, 42, 30, fill='#4a6fa5')
        reset_canvas.bind("<Button-1>", self.reset_timer)
        
        # Timer preset buttons
        preset_frame = tk.Frame(clock_container, bg='#4a6fa5')
        preset_frame.pack(side='left')
        
        btn1_frame = tk.Frame(preset_frame, bg='#666666', relief='raised', bd=2)
        btn1_frame.pack(side='left', padx=(0, 5))
        tk.Label(btn1_frame, text="1", font=('Arial', 16, 'bold'), 
                fg='white', bg='#666666', padx=15, pady=8).pack()
        tk.Label(btn1_frame, text="min", font=('Arial', 8), 
                fg='white', bg='#666666').pack()
        btn1_frame.bind("<Button-1>", lambda e: self.set_timer(1, 0))
        
        btn15_frame = tk.Frame(preset_frame, bg='#666666', relief='raised', bd=2)
        btn15_frame.pack(side='left')
        tk.Label(btn15_frame, text="15", font=('Arial', 16, 'bold'), 
                fg='white', bg='#666666', padx=12, pady=8).pack()
        tk.Label(btn15_frame, text="min", font=('Arial', 8), 
                fg='white', bg='#666666').pack()
        btn15_frame.bind("<Button-1>", lambda e: self.set_timer(15, 0))
        
    # Game logic methods
    def change_score(self, team, delta):
        if team == 'HOME':
            new_score = max(0, self.home_score.get() + delta)
            self.home_score.set(new_score)
        else:
            new_score = max(0, self.away_score.get() + delta)
            self.away_score.set(new_score)
            
    def change_sets(self, team, delta):
        if team == 'HOME':
            new_sets = max(0, self.home_sets.get() + delta)
            self.home_sets.set(new_sets)
        else:
            new_sets = max(0, self.away_sets.get() + delta)
            self.away_sets.set(new_sets)
            
    def change_timeouts(self, team, delta):
        if team == 'HOME':
            new_timeouts = max(0, min(3, self.home_timeouts.get() + delta))
            self.home_timeouts.set(new_timeouts)
        else:
            new_timeouts = max(0, min(3, self.away_timeouts.get() + delta))
            self.away_timeouts.set(new_timeouts)
            
    def change_serve(self, team):
        self.serve_side.set(team)
        print(f"Serve changed to {team}")
        
    def next_set(self):
        current = self.current_set.get()
        if current < 5:
            self.current_set.set(current + 1)
            self.update_set_label()
            
    def prev_set(self):
        current = self.current_set.get()
        if current > 1:
            self.current_set.set(current - 1)
            self.update_set_label()
            
    def update_set_label(self):
        set_num = self.current_set.get()
        ordinals = ["", "1st", "2nd", "3rd", "4th", "5th"]
        self.set_label.config(text=f"{ordinals[set_num]} Set")
        
    def sound_horn(self, event):
        print("Horn sounded!")
        # In a real app, you would play a sound file here
        
    def toggle_timer(self, event):
        if self.timer_running:
            self.stop_timer()
        else:
            self.start_timer()
            
    def start_timer(self):
        if not self.timer_running:
            self.timer_running = True
            self.timer_thread = threading.Thread(target=self.run_timer)
            self.timer_thread.daemon = True
            self.timer_thread.start()
            
    def stop_timer(self):
        self.timer_running = False
        
    def run_timer(self):
        while self.timer_running:
            time.sleep(1)
            if self.timer_running:
                current_seconds = self.game_seconds.get()
                current_minutes = self.game_minutes.get()
                
                if current_seconds > 0:
                    self.game_seconds.set(current_seconds - 1)
                elif current_minutes > 0:
                    self.game_minutes.set(current_minutes - 1)
                    self.game_seconds.set(59)
                else:
                    self.timer_running = False
                    
                # Update seconds display
                self.root.after(0, self.update_seconds_display)
                
    def update_seconds_display(self):
        seconds = self.game_seconds.get()
        self.seconds_label.config(text=f"{seconds:02d}")
        
    def reset_timer(self, event):
        self.stop_timer()
        self.set_timer(15, 0)
        
    def set_timer(self, minutes, seconds):
        self.stop_timer()
        self.game_minutes.set(minutes)
        self.game_seconds.set(seconds)
        self.update_seconds_display()
        
    def reset_game(self):
        self.stop_timer()
        self.home_score.set(0)
        self.away_score.set(0)
        self.home_sets.set(0)
        self.away_sets.set(0)
        self.home_timeouts.set(2)
        self.away_timeouts.set(2)
        self.current_set.set(1)
        self.update_set_label()
        self.set_timer(15, 0)
        
    def back_to_rumbleverse(self):
        self.stop_timer()
        self.root.destroy()
        self.main_app.back_to_rumbleverse()
        
    def run(self):
        # Handle window close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()
        
    def on_closing(self):
        self.stop_timer()
        self.root.destroy()
        sys.exit()

# Main Application Entry Point
if __name__ == "__main__":
    print("=== MERGED GAME APPLICATION ===")
    print("Starting with RumbleVerse Game Mode Selection...")
    print("Click or press Enter on SOLO mode to open Volleyball Scoreboard")
    print("Use arrow keys to navigate, Enter to select, Esc to quit")
    print("In Volleyball mode, use 'Back to Game Modes' button to return")
    print("=====================================")
    
    app = GameApplication()
    app.start_rumbleverse()
