# start_screen.py
import pygame
from settings import *

class StartScreen:
    def __init__(self):
        self.player_name = ""
        self.font_main = pygame.font.SysFont(None, 60)
        self.font_sub = pygame.font.SysFont(None, 32)
        
        self.input_rect = pygame.Rect(WINDOW_WIDTH//2 - 150, WINDOW_HEIGHT//2 - 30, 300, 60)
        self.cursor_visible = True
        self.cursor_timer = 0
        
        # SỬA LỖI Ở ĐÂY: Dùng tên trạng thái mới
        self.next_state = STATE_MENU_NAME 

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                self.player_name = self.player_name[:-1]
            elif event.key == pygame.K_RETURN:
                if len(self.player_name) > 0:
                    # SỬA LỖI Ở ĐÂY: Bấm Enter xong thì chuyển thẳng sang Dashboard
                    self.next_state = STATE_DASHBOARD
            else:
                if event.unicode.isalpha() or event.unicode.isdigit():
                    if len(self.player_name) < 12:
                        self.player_name += event.unicode

    def draw(self, screen):
        screen.fill(BG_COLOR)
        
        title_surf = self.font_main.render("PIPE PUZZLE CYBER", True, PIPE_COLOR_ON)
        title_rect = title_surf.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 - 120))
        screen.blit(title_surf, title_rect)
        
        instr_surf = self.font_sub.render("Enter your name (Max 12 char):", True, TEXT_COLOR)
        instr_rect = instr_surf.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 - 60))
        screen.blit(instr_surf, instr_rect)
        
        pygame.draw.rect(screen, INPUT_BOX_COLOR, self.input_rect, 0, 10)
        pygame.draw.rect(screen, GRID_COLOR, self.input_rect, 2, 10)
        
        name_surf = self.font_sub.render(self.player_name, True, TEXT_COLOR)
        name_rect = name_surf.get_rect(center=self.input_rect.center)
        screen.blit(name_surf, name_rect)
        
        self.cursor_timer += 1
        if self.cursor_timer >= 30:
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = 0
            
        if self.cursor_visible:
            cursor_x = name_rect.right + 2 if len(self.player_name) > 0 else self.input_rect.centerx
            pygame.draw.line(screen, TEXT_COLOR, (cursor_x, self.input_rect.centery - 15), (cursor_x, self.input_rect.centery + 15), 2)
            
        if len(self.player_name) > 0:
            hint_surf = self.font_sub.render("Press ENTER to start", True, HIGHLIGHT_COLOR)
            hint_rect = hint_surf.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + 80))
            screen.blit(hint_surf, hint_rect)