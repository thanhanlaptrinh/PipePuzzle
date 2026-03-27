# screens.py (Đã sửa lỗi font Tiếng Việt Unicode)
import pygame
# Import thêm settings để lấy FONT_PATH
from settings import *

class Button:
    def __init__(self, x, y, width, height, text, color, text_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.text_color = text_color
        
        # Hạ cỡ chữ của tất cả các nút xuống 30 cho thanh lịch
        self.font = pygame.font.SysFont('tahoma', 30, bold=True)
        self.is_hovered = False

    def draw(self, screen):
        draw_color = (min(self.color[0]+30, 255), min(self.color[1]+30, 255), min(self.color[2]+30, 255)) if self.is_hovered else self.color
        pygame.draw.rect(screen, draw_color, self.rect, border_radius=12)
        text_surf = self.font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

    def check_hover(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)

    def is_clicked(self, mouse_pos, mouse_pressed):
        return self.is_hovered and mouse_pressed[0]

class StartScreen:
    def __init__(self):
        self.player_name = ""
        
        # --- CẬP NHẬT Ở ĐÂY ---
        self.font_main = pygame.font.SysFont('tahoma', 60)
        self.font_sub = pygame.font.SysFont('tahoma', 32)
        
        self.input_rect = pygame.Rect(WINDOW_WIDTH//2 - 150, WINDOW_HEIGHT//2 - 30, 300, 60)
        self.cursor_visible = True
        self.cursor_timer = 0
        self.next_state = STATE_MENU_NAME 

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                self.player_name = self.player_name[:-1]
            elif event.key == pygame.K_RETURN:
                if len(self.player_name) > 0:
                    self.next_state = STATE_DASHBOARD
            else:
                if event.unicode.isalpha() or event.unicode.isdigit():
                    if len(self.player_name) < 12:
                        self.player_name += event.unicode

    def draw(self, screen):
        screen.fill(BG_COLOR)
        title_surf = self.font_main.render("PIPE PUZZLE CYBER", True, PIPE_COLOR_ON)
        screen.blit(title_surf, title_surf.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 - 120)))
        
        instr_surf = self.font_sub.render("Enter your name (Max 12 char):", True, TEXT_COLOR)
        screen.blit(instr_surf, instr_surf.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 - 60)))
        
        pygame.draw.rect(screen, INPUT_BOX_COLOR, self.input_rect, 0, 10)
        pygame.draw.rect(screen, GRID_COLOR, self.input_rect, 2, 10)
        
        # --- VẼ TÊN ---
        name_surf = self.font_sub.render(self.player_name, True, TEXT_COLOR)
        # Sửa lại center để tên căn giữa ô
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
            # --- VẼ CHỮ TIẾNG VIỆT ---
            hint_surf = self.font_sub.render("Nhấn ENTER để bắt đầu", True, HIGHLIGHT_COLOR)
            screen.blit(hint_surf, hint_surf.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + 80)))

class DashboardScreen:
    def __init__(self):
        self.font_title = pygame.font.SysFont('tahoma', 60, bold=True)
        self.font_info = pygame.font.SysFont('tahoma', 36)
        
        # --- DỜI NÚT SKIN XUỐNG GÓC DƯỚI BÊN PHẢI ---
        # WINDOW_HEIGHT - 80 sẽ đẩy nó xuống sát đáy màn hình
        self.btn_skin = Button(WINDOW_WIDTH - 140, WINDOW_HEIGHT - 80, 120, 50, "SKIN", (200, 160, 50), (0,0,0))
        
        self.btn_play = Button(WINDOW_WIDTH//2 - 150, 250, 300, 60, "CHỌN MÀN CHƠI", PIPE_COLOR_ON, (0,0,0))
        self.btn_shop = Button(WINDOW_WIDTH//2 - 150, 340, 300, 60, "CỬA HÀNG", (50, 150, 200), (255,255,255))
        self.btn_quests = Button(WINDOW_WIDTH//2 - 150, 430, 300, 60, "NHIỆM VỤ", (150, 100, 200), (255,255,255))
        self.next_state = None

    def handle_event(self, event):
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()
        
        self.btn_play.check_hover(mouse_pos)
        self.btn_shop.check_hover(mouse_pos)
        self.btn_quests.check_hover(mouse_pos)
        self.btn_skin.check_hover(mouse_pos) # (QUAN TRỌNG) Để nút sáng lên khi trỏ chuột

        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.btn_play.is_clicked(mouse_pos, mouse_pressed): self.next_state = STATE_LEVEL_SELECT
            elif self.btn_shop.is_clicked(mouse_pos, mouse_pressed): self.next_state = STATE_SHOP
            elif self.btn_quests.is_clicked(mouse_pos, mouse_pressed): self.next_state = STATE_QUESTS
            # (QUAN TRỌNG) Để bấm được nút SKIN
            elif self.btn_skin.is_clicked(mouse_pos, mouse_pressed): self.next_state = STATE_SKIN 

    def draw(self, screen, player_name, coins):
        screen.fill(BG_COLOR)
        pygame.draw.rect(screen, INPUT_BOX_COLOR, (0, 0, WINDOW_WIDTH, 80))
        screen.blit(self.font_info.render(f"PLAYER: {player_name.upper()}", True, TEXT_COLOR), (30, 25))
        screen.blit(self.font_info.render(f"XU: {coins}", True, HIGHLIGHT_COLOR), (WINDOW_WIDTH - 150, 25))

        title_surf = self.font_title.render("PIPE PUZZLE", True, PIPE_COLOR_ON)
        screen.blit(title_surf, title_surf.get_rect(center=(WINDOW_WIDTH//2, 160)))

        self.btn_play.draw(screen)
        self.btn_shop.draw(screen)
        self.btn_quests.draw(screen)
        self.btn_skin.draw(screen)

class LevelSelectScreen:
    def __init__(self):
        # --- CẬP NHẬT Ở ĐÂY ---
        self.font_title = pygame.font.SysFont('tahoma', 60)
        self.buttons = []
        self.next_state = None
        self.selected_level = 1

        for i in range(10):
            row = i // 5
            col = i % 5
            btn = Button(100 + col * 130, 200 + row * 150, 100, 100, f"{i+1}", PIPE_COLOR_ON, (0, 0, 0))
            self.buttons.append((i+1, btn))
        
        self.btn_back = Button(20, 20, 150, 50, "QUAY LẠI", INPUT_BOX_COLOR, TEXT_COLOR)

    def handle_event(self, event):
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()
        self.btn_back.check_hover(mouse_pos)
        for _, btn in self.buttons: btn.check_hover(mouse_pos)

        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.btn_back.is_clicked(mouse_pos, mouse_pressed):
                self.next_state = STATE_DASHBOARD
                return
            for level_id, btn in self.buttons:
                if btn.is_clicked(mouse_pos, mouse_pressed):
                    self.selected_level = level_id
                    self.next_state = STATE_GAME_PLAY

    def draw(self, screen):
        screen.fill(BG_COLOR)
        # --- VẼ CHỮ TIẾNG VIỆT ---
        title_surf = self.font_title.render("CHỌN MÀN CHƠI", True, TEXT_COLOR)
        screen.blit(title_surf, title_surf.get_rect(center=(WINDOW_WIDTH//2, 100)))
        self.btn_back.draw(screen)
        for _, btn in self.buttons: btn.draw(screen)

class PauseMenu:
    def __init__(self):
        self.overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.overlay.set_alpha(200)
        self.overlay.fill((0, 0, 0))
        center_x, center_y = WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2
        
        # --- VẼ NÚT TIẾNG VIỆT ---
        self.btn_restart = Button(center_x - 100, center_y - 100, 200, 50, "CHƠI LẠI", PIPE_COLOR_ON, (0, 0, 0))
        self.btn_ai = Button(center_x - 100, center_y - 30, 200, 50, "AI GIẢI", (150, 100, 200), (255, 255, 255))
        self.btn_exit = Button(center_x - 100, center_y + 40, 200, 50, "THOÁT MÀN", (200, 50, 50), (255, 255, 255))
        self.action = None 
        
    def handle_event(self, event):
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()
        self.btn_restart.check_hover(mouse_pos); self.btn_ai.check_hover(mouse_pos); self.btn_exit.check_hover(mouse_pos)
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.btn_restart.is_clicked(mouse_pos, mouse_pressed): self.action = "RESTART"
            elif self.btn_ai.is_clicked(mouse_pos, mouse_pressed): self.action = "AI_SOLVE"
            elif self.btn_exit.is_clicked(mouse_pos, mouse_pressed): self.action = "EXIT"

    def draw(self, screen):
        screen.blit(self.overlay, (0, 0))
        self.btn_restart.draw(screen); self.btn_ai.draw(screen); self.btn_exit.draw(screen)

class TutorialPopup:
    def __init__(self):
        self.overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.overlay.set_alpha(200)
        self.overlay.fill((0, 0, 0))
        
        # Hạ cỡ chữ Tiêu đề xuống 36, chữ nội dung xuống 22
        self.font_title = pygame.font.SysFont('tahoma', 36, bold=True)
        self.font_text = pygame.font.SysFont('tahoma', 22)
        
        # NỚI RỘNG KHUNG BẢNG: Từ 500 lên 640 pixel để chữ thở
        self.popup_rect = pygame.Rect(WINDOW_WIDTH//2 - 320, WINDOW_HEIGHT//2 - 200, 640, 400)
        
        # Nút bấm căn giữa lại
        self.btn_understand = Button(WINDOW_WIDTH//2 - 120, WINDOW_HEIGHT//2 + 100, 240, 50, "TÔI ĐÃ HIỂU!", PIPE_COLOR_ON, (0, 0, 0))
        self.action = None

    def handle_event(self, event):
        mouse_pos = pygame.mouse.get_pos()
        self.btn_understand.check_hover(mouse_pos)
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.btn_understand.is_clicked(mouse_pos, pygame.mouse.get_pressed()): 
                self.action = "UNDERSTOOD"

    def draw(self, screen):
        screen.blit(self.overlay, (0, 0))
        pygame.draw.rect(screen, INPUT_BOX_COLOR, self.popup_rect, border_radius=15)
        pygame.draw.rect(screen, PIPE_COLOR_ON, self.popup_rect, 2, border_radius=15)
        
        title_surf = self.font_title.render("HƯỚNG DẪN CƠ BẢN", True, PIPE_COLOR_ON)
        screen.blit(title_surf, title_surf.get_rect(center=(WINDOW_WIDTH//2, self.popup_rect.top + 40)))
        
        instructions = [
            "1. Click chuột TRÁI vào ống nước để xoay 90 độ.",
            "2. Nối thông dòng nước (màu neon) từ góc TRÁI-TRÊN.",
            "3. Dùng nút 'AI GIẢI' trên MENU nếu bạn bị kẹt.",
            "MỤC TIÊU: Dẫn nước chạm tới góc PHẢI-DƯỚI!"
        ]
        
        # Thụt lề vào 40px cho đẹp
        for i, text in enumerate(instructions):
            color = HIGHLIGHT_COLOR if i == 3 else TEXT_COLOR
            text_surf = self.font_text.render(text, True, color)
            screen.blit(text_surf, (self.popup_rect.left + 40, self.popup_rect.top + 110 + i*45))
            
        self.btn_understand.draw(screen)

# Placeholder cho Shop và Quests (Team se code sau)
class ShopScreen:
    def __init__(self):
        self.next_state = None
        self.font = pygame.font.SysFont('tahoma', 40)
    def handle_event(self, e): pass
    def draw(self, s): s.fill(BG_COLOR); s.blit(self.font.render("CỬA HÀNG (Team se code sau)", True, TEXT_COLOR), (200, 300))

class QuestsScreen:
    def __init__(self):
        self.next_state = None
        self.font = pygame.font.SysFont('tahoma', 40)
    def handle_event(self, e): pass
    def draw(self, s): s.fill(BG_COLOR); s.blit(self.font.render("NHIỆM VỤ (Team se code sau)", True, TEXT_COLOR), (200, 300))

class WinPopup:
    def __init__(self):
        self.overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.overlay.set_alpha(220)
        self.overlay.fill((0, 0, 0))
        
        self.font_title = pygame.font.SysFont('tahoma', 40, bold=True)
        self.popup_rect = pygame.Rect(WINDOW_WIDTH//2 - 250, WINDOW_HEIGHT//2 - 150, 500, 300)
        
        # 2 nút MENU và CHƠI TIẾP
        self.btn_menu = Button(WINDOW_WIDTH//2 - 200, WINDOW_HEIGHT//2 + 50, 180, 50, "MENU", INPUT_BOX_COLOR, TEXT_COLOR)
        self.btn_next = Button(WINDOW_WIDTH//2 + 20, WINDOW_HEIGHT//2 + 50, 180, 50, "CHƠI TIẾP", PIPE_COLOR_ON, (0, 0, 0))
        self.action = None

    def handle_event(self, event):
        mouse_pos = pygame.mouse.get_pos()
        self.btn_menu.check_hover(mouse_pos)
        self.btn_next.check_hover(mouse_pos)
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.btn_menu.is_clicked(mouse_pos, pygame.mouse.get_pressed()):
                self.action = "MENU"
            elif self.btn_next.is_clicked(mouse_pos, pygame.mouse.get_pressed()):
                self.action = "NEXT"

    def draw(self, screen):
        screen.blit(self.overlay, (0, 0))
        pygame.draw.rect(screen, INPUT_BOX_COLOR, self.popup_rect, border_radius=15)
        pygame.draw.rect(screen, HIGHLIGHT_COLOR, self.popup_rect, 3, border_radius=15) # Viền vàng rực rỡ
        
        title_surf = self.font_title.render("HỆ THỐNG ĐÃ KẾT NỐI!", True, HIGHLIGHT_COLOR)
        screen.blit(title_surf, title_surf.get_rect(center=(WINDOW_WIDTH//2, self.popup_rect.top + 60)))
        
        self.btn_menu.draw(screen)
        self.btn_next.draw(screen)

class SkinScreen:
    def __init__(self):
        self.next_state = None
        self.font = pygame.font.SysFont('tahoma', 40)
        self.btn_back = Button(20, 20, 150, 50, "QUAY LẠI", INPUT_BOX_COLOR, TEXT_COLOR)
    def handle_event(self, event):
        mouse_pos = pygame.mouse.get_pos()
        self.btn_back.check_hover(mouse_pos)
        if event.type == pygame.MOUSEBUTTONDOWN and self.btn_back.is_clicked(mouse_pos, pygame.mouse.get_pressed()):
            self.next_state = STATE_DASHBOARD
    def draw(self, screen): 
        screen.fill(BG_COLOR)
        screen.blit(self.font.render("CHỌN SKIN (Tính năng đang phát triển)", True, HIGHLIGHT_COLOR), (WINDOW_WIDTH//2 - 300, 300))
        self.btn_back.draw(screen)