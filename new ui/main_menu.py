import pygame
import sys
from typing import List, Tuple

# Initialize Pygame
pygame.init()

# Constants
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
        
        # Draw character placeholder
        char_rect = pygame.Rect(self.rect.x + 20, self.rect.y + 20, self.rect.width - 40, self.rect.height - 120)
        pygame.draw.rect(screen, PURPLE_DARK, char_rect)
        
        if self.title == "Solo":
            pygame.draw.circle(screen, WHITE, (char_rect.centerx, char_rect.centery - 20), 30)
            pygame.draw.circle(screen, BLACK, (char_rect.centerx - 10, char_rect.centery - 30), 5)
            pygame.draw.circle(screen, BLACK, (char_rect.centerx + 10, char_rect.centery - 30), 5)
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
            for i in range(5):
                building_height = 40 + (i * 15) % 60
                pygame.draw.rect(screen, CYAN, 
                                 (char_rect.x + i * 30, char_rect.bottom - building_height, 25, building_height))

class RumbleVerseUI:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Foosball - Game Mode Selection")
        self.clock = pygame.time.Clock()
        
        self.font_title = pygame.font.Font(None, 72)
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 24)
        
        card_width = 220
        card_height = 400
        start_x = 100
        spacing = 240
        card_y = 180
        
        self.game_modes = [
            GameModeCard(start_x, card_y, card_width, card_height, "RANKED", "Battle Royale", 
                         PURPLE_MID, ORANGE, True),
            GameModeCard(start_x + spacing, card_y, card_width, card_height, "Time Trial", "Battle Royale"),
            GameModeCard(start_x + spacing * 2, card_y, card_width, card_height, "Duo Clash", "Offic Clash"),
            GameModeCard(start_x + spacing * 3, card_y, card_width, card_height, "Practice", "Playground"),
            GameModeCard(start_x + spacing * 4, card_y, card_width, card_height, "Pay to Play", 
                         "Pay and play", PURPLE_LIGHT, CYAN)
        ]
        
        self.selected_mode = 0
        
    def draw_background(self):
        for y in range(SCREEN_HEIGHT):
            color_ratio = y / SCREEN_HEIGHT
            r = int(PURPLE_DARK[0] + (PURPLE_LIGHT[0] - PURPLE_DARK[0]) * color_ratio)
            g = int(PURPLE_DARK[1] + (PURPLE_LIGHT[1] - PURPLE_DARK[1]) * color_ratio)
            b = int(PURPLE_DARK[2] + (PURPLE_LIGHT[2] - PURPLE_DARK[2]) * color_ratio)
            pygame.draw.line(self.screen, (r, g, b), (0, y), (SCREEN_WIDTH, y))
        
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
        
        pygame.draw.line(self.screen, CYAN, (50, 120), (SCREEN_WIDTH - 50, 120), 2)
    
    def draw_bottom_ui(self):
        controls = [("<", "Back"), (">", "Fill Teammates: ON")]
        x_pos = 50
        for key, action in controls:
            key_rect = pygame.Rect(x_pos, SCREEN_HEIGHT - 60, 40, 30)
            pygame.draw.rect(self.screen, GRAY, key_rect)
            pygame.draw.rect(self.screen, WHITE, key_rect, 2)
            
            key_surface = self.font_small.render(key, True, BLACK)
            self.screen.blit(key_surface, key_surface.get_rect(center=key_rect.center))
            
            action_surface = self.font_small.render(action, True, WHITE)
            self.screen.blit(action_surface, (x_pos + 50, SCREEN_HEIGHT - 55))
            
            x_pos += 200
    
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
                selected_title = self.game_modes[self.selected_mode].title
                print(f"Selected: {selected_title}")

                if selected_title == "RANKED":
                    pygame.quit()
                    import soccercard
                    soccercard.foosballScoreboard().root.mainloop()

                elif selected_title == "Time Trial":
                    print("You selected Time Trial - add your custom logic here")

                elif selected_title == "Duo Clash":
                    print("You selected Duo Clash - add your custom logic here")

                elif selected_title == "Practice":
                    print("Launching practice mode...")

                elif selected_title == "Pay to Play":
                    print("Handle payment logic or redirect...")

        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            for i, mode in enumerate(self.game_modes):
                if mode.rect.collidepoint(mouse_pos):
                    self.game_modes[self.selected_mode].is_selected = False
                    self.game_modes[self.selected_mode].border_color = WHITE
                    self.game_modes[self.selected_mode].border_width = 2

                    self.selected_mode = i
                    mode.is_selected = True
                    mode.border_color = ORANGE
                    mode.border_width = 4
                    break
    
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
                        self.handle_input(event)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_input(event)
            
            self.draw_background()
            self.draw_title()
            for mode in self.game_modes:
                mode.draw(self.screen, self.font_large, self.font_medium)
            self.draw_bottom_ui()
            pygame.display.flip()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

# Run the application
if __name__ == "__main__":
    game = RumbleVerseUI()
    print("RumbleVerse Game Mode Selection - Use arrow keys to navigate, Enter to select, Esc to quit")
    game.run()
