import pygame
import tkinter as tk
from tkinter import ttk
import threading
import time
import sys
import random
from typing import List, Tuple
from PIL import Image, ImageDraw  # For creating QR code image

class GameApplication:
    def __init__(self):
        self.current_screen = "rumbleverse"  # "rumbleverse", "tablesoccer", or "qrcode"
        self.rumbleverse_app = None
        self.tablesoccer_app = None
        self.qrcode_window = None
        self.running = True
        
    def start_rumbleverse(self):
        self.current_screen = "rumbleverse"
        # Initialize pygame if not already initialized
        if not pygame.get_init():
            pygame.init()
        self.rumbleverse_app = RumbleVerseUI(self)
        self.rumbleverse_app.run()
        
    def start_tablesoccer(self):
        self.current_screen = "tablesoccer"
        # Properly quit pygame before starting tkinter
        if pygame.get_init():
            pygame.quit()
        self.tablesoccer_app = TableSoccerScoreboard(self)
        self.tablesoccer_app.run()
        
    def show_qr_code(self):
        self.current_screen = "qrcode"
        # Properly quit pygame before starting tkinter
        if pygame.get_init():
            pygame.quit()
        self.qrcode_window = QRCodeWindow(self)
        self.qrcode_window.run()
        
    def back_to_rumbleverse(self):
        print("Returning to Game Mode Selection...")
        if self.tablesoccer_app and hasattr(self.tablesoccer_app, 'root') and self.tablesoccer_app.root.winfo_exists():
            self.tablesoccer_app.stop_timer()
            self.tablesoccer_app.root.quit()  # Use quit() instead of destroy()
            self.tablesoccer_app.root.destroy()
        
        if self.qrcode_window and hasattr(self.qrcode_window, 'root') and self.qrcode_window.root.winfo_exists():
            self.qrcode_window.root.quit()
            self.qrcode_window.root.destroy()
        
        # Small delay to ensure clean transition
        time.sleep(0.1)
        
        # Restart pygame and rumbleverse
        try:
            self.start_rumbleverse()
        except Exception as e:
            print(f"Error returning to game modes: {e}")
            # Fallback: restart the entire application
            self.restart_application()
    
    def restart_application(self):
        """Fallback method to restart the entire application"""
        print("Restarting application...")
        if self.tablesoccer_app:
            try:
                self.tablesoccer_app.root.destroy()
            except:
                pass
        if self.qrcode_window:
            try:
                self.qrcode_window.root.destroy()
            except:
                pass
        if pygame.get_init():
            pygame.quit()
        
        # Create new application instance
        new_app = GameApplication()
        new_app.start_rumbleverse()

# QR Code Window
class QRCodeWindow:
    def __init__(self, main_app):
        self.main_app = main_app
        self.root = tk.Tk()
        self.root.title("PaytoPlay - QR Code")
        self.root.geometry("600x700")
        self.root.configure(bg='#1e3a5f')
        
        self.setup_ui()
        
    def setup_ui(self):
        # Create main container
        main_frame = tk.Frame(self.root, bg='#1e3a5f')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Header section
        header_frame = tk.Frame(main_frame, bg='#1e3a5f')
        header_frame.pack(fill='x', pady=(0, 20))
        
        # Back to RumbleVerse button
        back_btn = tk.Button(header_frame, text="← Back to Game Modes", font=('Arial', 12, 'bold'), 
                           bg='#4a6fa5', fg='white', bd=0, padx=15, pady=5,
                           command=self.back_to_rumbleverse)
        back_btn.pack(side='left')
        
        # Title
        tk.Label(main_frame, text="SCAN TO PAY", font=('Arial', 24, 'bold'), 
                fg='white', bg='#1e3a5f').pack(pady=(0, 20))
        
        # QR Code frame
        qr_frame = tk.Frame(main_frame, bg='white', bd=10, relief='raised')
        qr_frame.pack(pady=20)
        
        # Create QR code image
        qr_size = 400
        qr_image = self.create_qr_code(qr_size)
        
        # Display QR code
        self.qr_canvas = tk.Canvas(qr_frame, width=qr_size, height=qr_size, 
                                 bg='white', highlightthickness=0)
        self.qr_canvas.pack()
        
        # Draw QR code on canvas
        for y in range(qr_size):
            for x in range(qr_size):
                if qr_image.getpixel((x, y)) == 0:  # Black pixel
                    self.qr_canvas.create_rectangle(x, y, x+1, y+1, fill='black', outline='black')
        
        # Instructions
        instructions_frame = tk.Frame(main_frame, bg='#4a6fa5', bd=2, relief='raised')
        instructions_frame.pack(fill='x', pady=20, padx=50)
        
        tk.Label(instructions_frame, text="1. Scan the QR code with your payment app", 
                font=('Arial', 12), fg='white', bg='#4a6fa5', anchor='w').pack(fill='x', padx=20, pady=(20, 10))
        tk.Label(instructions_frame, text="2. Complete the payment process", 
                font=('Arial', 12), fg='white', bg='#4a6fa5', anchor='w').pack(fill='x', padx=20, pady=10)
        tk.Label(instructions_frame, text="3. Wait for confirmation to access premium content", 
                font=('Arial', 12), fg='white', bg='#4a6fa5', anchor='w').pack(fill='x', padx=20, pady=(10, 20))
        
        # Replace QR code button (for demonstration)
        replace_btn = tk.Button(main_frame, text="Replace with Your QR Code", font=('Arial', 12), 
                              bg='#4a6fa5', fg='white', bd=0, padx=15, pady=10,
                              command=self.show_replace_instructions)
        replace_btn.pack(pady=20)
    
    def create_qr_code(self, size):
        """Create a QR code image with finder patterns and random data"""
        # Create a blank image
        image = Image.new('1', (size, size), 1)  # '1' mode is 1-bit pixels, black and white
        draw = ImageDraw.Draw(image)
        
        # Calculate module size (we'll use a 29x29 QR code pattern)
        module_size = size // 29
        
        # Generate QR code pattern
        pattern = []
        random.seed(42)  # Fixed seed for consistent pattern
        for i in range(29):
            row = []
            for j in range(29):
                # Create finder patterns (the three large squares in corners)
                if (i < 7 and j < 7) or (i < 7 and j > 21) or (i > 21 and j < 7):
                    # Outer border of finder pattern
                    if i == 0 or i == 6 or j == 0 or j == 6 or i == 22 or i == 28 or j == 22 or j == 28:
                        row.append(0)  # Black
                    # Inner square of finder pattern
                    elif i >= 2 and i <= 4 and j >= 2 and j <= 4:
                        row.append(0)  # Black
                    elif i >= 2 and i <= 4 and j >= 24 and j <= 26:
                        row.append(0)  # Black
                    elif i >= 24 and i <= 26 and j >= 2 and j <= 4:
                        row.append(0)  # Black
                    else:
                        row.append(1)  # White
                # Timing patterns (the lines connecting finder patterns)
                elif i == 6 and j % 2 == 0:
                    row.append(0)  # Black
                elif j == 6 and i % 2 == 0:
                    row.append(0)  # Black
                # Alignment pattern (the smaller square not in a corner)
                elif 22 <= i <= 26 and 22 <= j <= 26:
                    if i == 22 or i == 26 or j == 22 or j == 26 or (i == 24 and j == 24):
                        row.append(0)  # Black
                    else:
                        row.append(1)  # White
                # Format information
                elif (i < 9 and j == 8) or (i == 8 and j < 9):
                    row.append(random.choice([0, 1]))
                # Random data for the rest
                else:
                    row.append(random.choice([0, 1]))
            pattern.append(row)
        
        # Draw the QR code pattern
        for i in range(29):
            for j in range(29):
                if pattern[i][j] == 0:  # Black module
                    draw.rectangle(
                        [j * module_size, i * module_size, 
                         (j + 1) * module_size - 1, (i + 1) * module_size - 1], 
                        fill=0
                    )
        
        return image
    
    def show_replace_instructions(self):
        """Show instructions for replacing the QR code"""
        instruction_window = tk.Toplevel(self.root)
        instruction_window.title("Replace QR Code Instructions")
        instruction_window.geometry("500x300")
        instruction_window.configure(bg='#1e3a5f')
        
        frame = tk.Frame(instruction_window, bg='#1e3a5f', padx=20, pady=20)
        frame.pack(fill='both', expand=True)
        
        tk.Label(frame, text="How to Replace the QR Code", font=('Arial', 16, 'bold'), 
                fg='white', bg='#1e3a5f').pack(pady=(0, 20))
        
        instructions = [
            "1. Create your own QR code image file",
            "2. Save it as 'custom_qr.png' in the same folder as this script",
            "3. Modify the create_qr_code method to load your image:",
            "   - Replace the current code with:",
            "   - try:",
            "       return Image.open('custom_qr.png').convert('1')",
            "     except:",
            "       # Fallback to generated QR code"
        ]
        
        for line in instructions:
            tk.Label(frame, text=line, font=('Arial', 11), 
                    fg='white', bg='#1e3a5f', anchor='w').pack(fill='x', pady=2)
        
        tk.Button(frame, text="Close", font=('Arial', 12), 
                bg='#4a6fa5', fg='white', bd=0, padx=15, pady=5,
                command=instruction_window.destroy).pack(pady=20)
    
    def back_to_rumbleverse(self):
        print("Back button clicked - returning to game modes...")
        self.main_app.back_to_rumbleverse()
        
    def run(self):
        # Handle window close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()
        
    def on_closing(self):
        self.root.destroy()
        sys.exit()

# RumbleVerse Game Mode Selection (Modified)
# Initialize pygame at module level
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
        # Generate QR code pattern for PaytoPlay card
        if title == "PaytoPlay":
            self.qr_pattern = self.generate_qr_pattern()
        
    def generate_qr_pattern(self):
        """Generate a random QR code-like pattern"""
        # Create a 15x15 grid for QR code pattern
        pattern = []
        random.seed(42)  # Fixed seed for consistent pattern
        for i in range(15):
            row = []
            for j in range(15):
                # Create QR code-like pattern with finder patterns in corners
                if (i < 3 and j < 3) or (i < 3 and j > 11) or (i > 11 and j < 3):
                    # Finder patterns (corner squares)
                    if (i == 0 or i == 2 or j == 0 or j == 2):
                        row.append(1)
                    else:
                        row.append(0)
                elif i == 1 and j == 1:
                    row.append(1)
                elif i == 1 and j == 13:
                    row.append(1)
                elif i == 13 and j == 1:
                    row.append(1)
                else:
                    # Random pattern for data area
                    row.append(random.choice([0, 1]))
            pattern.append(row)
        return pattern
        
    def draw_qr_code(self, screen, char_rect):
        """Draw QR code pattern"""
        if not hasattr(self, 'qr_pattern'):
            return
            
        # Calculate cell size
        qr_size = min(char_rect.width - 40, char_rect.height - 40)
        cell_size = qr_size // 15
        start_x = char_rect.centerx - (15 * cell_size) // 2
        start_y = char_rect.centery - (15 * cell_size) // 2
        
        # Draw white background
        qr_bg_rect = pygame.Rect(start_x - 5, start_y - 5, 15 * cell_size + 10, 15 * cell_size + 10)
        pygame.draw.rect(screen, WHITE, qr_bg_rect)
        
        # Draw QR pattern
        for i, row in enumerate(self.qr_pattern):
            for j, cell in enumerate(row):
                if cell == 1:
                    cell_rect = pygame.Rect(
                        start_x + j * cell_size,
                        start_y + i * cell_size,
                        cell_size,
                        cell_size
                    )
                    pygame.draw.rect(screen, BLACK, cell_rect)
        
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
        if self.title == "Ranked":
            pygame.draw.circle(screen, WHITE, (char_rect.centerx, char_rect.centery - 20), 30)
            pygame.draw.circle(screen, BLACK, (char_rect.centerx - 10, char_rect.centery - 30), 5)
            pygame.draw.circle(screen, BLACK, (char_rect.centerx + 10, char_rect.centery - 30), 5)
            # Add table soccer indicator for Ranked mode
            pygame.draw.rect(screen, (34, 139, 34), (char_rect.centerx - 25, char_rect.centery + 10, 50, 20))
            pygame.draw.circle(screen, WHITE, (char_rect.centerx, char_rect.centery + 20), 8)
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
        elif self.title == "PaytoPlay":
            # Draw QR code
            self.draw_qr_code(screen, char_rect)

class RumbleVerseUI:
    def __init__(self, main_app):
        self.main_app = main_app
        # Create new display surface
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
            GameModeCard(start_x, card_y, card_width, card_height, "Ranked", "Tablesoccer Scoreboard", 
                        PURPLE_MID, ORANGE, True),
            GameModeCard(start_x + spacing, card_y, card_width, card_height, "Duo", "Battle Royale"),
            GameModeCard(start_x + spacing * 2, card_y, card_width, card_height, "Trio", "Battle Royale"),
            GameModeCard(start_x + spacing * 3, card_y, card_width, card_height, "Quad", "Battle Royale"),
            GameModeCard(start_x + spacing * 4, card_y, card_width, card_height, "PaytoPlay", 
                        "Scan QR to Pay", PURPLE_LIGHT, CYAN)
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
        instruction_surface = self.font_small.render("Click RANKED for Tablesoccer | Click PAYTOPAY to see QR Code", True, WHITE)
        instruction_rect = instruction_surface.get_rect(center=(SCREEN_WIDTH // 2, 140))
        self.screen.blit(instruction_surface, instruction_rect)
    
    def draw_bottom_ui(self):
        # Bottom control hints
        controls = [
            ("Esc", "Back"),
            ("Enter", "Select Mode"),
            ("Click", "Select Game Mode")
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
                    self.main_app.start_tablesoccer()
                    return False  # Exit pygame loop
                elif selected_mode == "PaytoPlay":
                    print("PaytoPlay selected - Opening QR Code window")
                    self.main_app.show_qr_code()
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
                    
                    # Handle specific mode actions
                    if mode.title == "Ranked":
                        print("Opening Tablesoccer Scoreboard...")
                        self.main_app.start_tablesoccer()
                        return False  # Exit pygame loop
                    elif mode.title == "PaytoPlay":
                        print("PaytoPlay clicked - Opening QR Code window")
                        self.main_app.show_qr_code()
                        return False  # Exit pygame loop
                    break
        return True
    
    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                        pygame.quit()
                        sys.exit()
                    else:
                        if not self.handle_input(event):
                            return  # Exit to tablesoccer or QR code
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if not self.handle_input(event):
                        return  # Exit to tablesoccer or QR code
            
            # Draw everything
            self.draw_background()
            self.draw_title()
            
            # Draw game mode cards
            for mode in self.game_modes:
                mode.draw(self.screen, self.font_large, self.font_medium)
            
            self.draw_bottom_ui()
            
            pygame.display.flip()
            self.clock.tick(FPS)

# Tablesoccer Scoreboard Application (Modified)
class TableSoccerScoreboard:
    def __init__(self, main_app):
        self.main_app = main_app
        self.root = tk.Tk()
        self.root.title("Tablesoccer Scoreboard")
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
        
        # Tablesoccer section with scores
        self.create_tablesoccer_section(main_frame)
        
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
        tk.Label(header_frame, text="BULLDOGS", font=('Arial', 18, 'bold'), 
                fg='white', bg='#1e3a5f').pack(side='left', padx=(20, 0))
        
        tk.Label(header_frame, text="FALCONS", font=('Arial', 18, 'bold'), 
                fg='white', bg='#1e3a5f').pack(side='right', padx=(0, 20))
        
        # Refresh button
        refresh_btn = tk.Button(header_frame, text="↻", font=('Arial', 16, 'bold'), 
                              bg='#4a6fa5', fg='white', bd=0, padx=10, pady=5,
                              command=self.reset_game)
        refresh_btn.pack(side='right')
        
    def create_tablesoccer_section(self, parent):
        # Main tablesoccer container with curved background
        tablesoccer_frame = tk.Frame(parent, bg='#4a6fa5', relief='raised', bd=2)
        tablesoccer_frame.pack(fill='x', pady=(0, 20))
        
        # Configure grid weights
        tablesoccer_frame.grid_columnconfigure(0, weight=1)
        tablesoccer_frame.grid_columnconfigure(1, weight=1)
        tablesoccer_frame.grid_columnconfigure(2, weight=1)
        
        # Home team score section
        home_frame = tk.Frame(tablesoccer_frame, bg='#4a6fa5')
        home_frame.grid(row=0, column=0, padx=20, pady=20, sticky='ew')
        
        tk.Label(home_frame, textvariable=self.home_score, font=('Arial', 72, 'bold'), 
                fg='white', bg='#4a6fa5').pack()
        tk.Label(home_frame, text="HOME TEAM", font=('Arial', 12), 
                fg='#cccccc', bg='#4a6fa5').pack()
        
        # Center tablesoccer section
        center_frame = tk.Frame(tablesoccer_frame, bg='#4a6fa5')
        center_frame.grid(row=0, column=1, padx=20, pady=20)
        
        # Tablesoccer table placeholder
        tablesoccer_canvas = tk.Canvas(center_frame, width=120, height=120, 
                                    bg='#4a6fa5', highlightthickness=0)
        tablesoccer_canvas.pack()
        
        # Draw tablesoccer table
        tablesoccer_canvas.create_rectangle(20, 30, 100, 90, fill='#228B22', outline='white', width=3)
        # Draw center line
        tablesoccer_canvas.create_line(60, 30, 60, 90, fill='white', width=2)
        # Draw goals
        tablesoccer_canvas.create_rectangle(15, 50, 20, 70, fill='white', outline='white')
        tablesoccer_canvas.create_rectangle(100, 50, 105, 70, fill='white', outline='white')
        # Draw ball
        tablesoccer_canvas.create_oval(55, 55, 65, 65, fill='white', outline='black', width=1)
        
        tk.Label(center_frame, text="TABLESOCCER", font=('Arial', 10, 'bold'), 
                fg='white', bg='#4a6fa5').pack(pady=(5, 0))
        tk.Label(center_frame, text="V/S", font=('Arial', 16, 'bold'), 
                fg='white', bg='#4a6fa5').pack()
        
        # Serve indicator (now "POSSESSION")
        serve_frame = tk.Frame(center_frame, bg='#4a6fa5')
        serve_frame.pack(pady=(10, 0))
        
        tk.Button(serve_frame, text="◀", font=('Arial', 12), bg='#666666', fg='white', 
                 bd=0, padx=10, command=lambda: self.change_serve('HOME')).pack(side='left')
        tk.Label(serve_frame, text="POSSESSION", font=('Arial', 10, 'bold'), 
                fg='white', bg='#4a6fa5', padx=15).pack(side='left')
        tk.Button(serve_frame, text="▶", font=('Arial', 12), bg='#666666', fg='white', 
                 bd=0, padx=10, command=lambda: self.change_serve('AWAY')).pack(side='left')
        
        # Away team score section
        away_frame = tk.Frame(tablesoccer_frame, bg='#4a6fa5')
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
        
        tk.Label(left_frame, text="GOALS", font=('Arial', 10), 
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
        self.set_label = tk.Label(set_control_frame, text="1st Game", font=('Arial', 16, 'bold'), 
                                 fg='white', bg='#4a6fa5', padx=20)
        self.set_label.pack(side='left')
        tk.Button(set_control_frame, text="▶", font=('Arial', 12), bg='white', fg='#4a6fa5', 
                 bd=0, padx=10, command=self.next_set).pack(side='left')
        
        # Right side - Away team controls
        right_frame = tk.Frame(control_frame, bg='#1e3a5f')
        right_frame.pack(side='right', padx=(20, 0))
        
        tk.Label(right_frame, text="GOALS", font=('Arial', 10), 
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
        
        # Games won
        tk.Label(home_stats, text="GAMES WON", font=('Arial', 10), 
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
        
        # Center whistle button
        center_stats = tk.Frame(stats_frame, bg='#1e3a5f')
        center_stats.pack(side='left', expand=True)
        
        whistle_canvas = tk.Canvas(center_stats, width=80, height=80, bg='white', highlightthickness=0)
        whistle_canvas.pack()
        whistle_canvas.create_oval(10, 10, 70, 70, fill='white', outline='#4a6fa5', width=2)
        # Draw whistle icon
        whistle_canvas.create_oval(25, 25, 55, 55, fill='#4a6fa5')
        whistle_canvas.create_oval(30, 30, 50, 50, fill='white')
        whistle_canvas.create_line(40, 25, 40, 15, fill='#4a6fa5', width=3)
        whistle_canvas.bind("<Button-1>", self.sound_whistle)
        
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
        
        # Games won
        tk.Label(away_stats, text="GAMES WON", font=('Arial', 10), 
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
        print(f"Ball possession changed to {team}")
        
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
        self.set_label.config(text=f"{ordinals[set_num]} Game")
        
    def sound_whistle(self, event):
        print("Whistle blown!")
        # In a real app, you would play a whistle sound file here
        
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
        print("Back button clicked - returning to game modes...")
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
    print("Click or press Enter on RANKED mode to open Tablesoccer Scoreboard")
    print("Click PAYTOPAY to see QR Code payment window")
    print("Use arrow keys to navigate, Enter to select, Esc to quit")
    print("In Tablesoccer mode, use 'Back to Game Modes' button to return")
    print("=====================================")
    
    app = GameApplication()
    app.start_rumbleverse()
