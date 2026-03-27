# dashboard.py
import pygame
from settings import *
from ui import Button

class DashboardScreen:
    def __init__(self):
        self.font_title = pygame.font.SysFont(None, 60)
        self.font_info = pygame.font.SysFont(None, 36)
        
        # Các nút bấm chính
        self.btn_play = Button(WINDOW_WIDTH//2 - 150, 250, 300, 60, "CHỌN MÀN CHƠI", PIPE_COLOR_ON, (0,0,0))
        self.btn_shop = Button(WINDOW_WIDTH//2 - 150, 340, 300, 60, "CỬA HÀNG", (50, 150, 200), (255,255,255))
        self.btn_quests = Button(WINDOW_WIDTH//2 - 150, 430, 300, 60, "NHIỆM VỤ", (150, 100, 200), (255,255,255))
        
        self.next_state = None

    def handle_event(self, event):
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()

        # Kiểm tra Hover
        self.btn_play.check_hover(mouse_pos)
        self.btn_shop.check_hover(mouse_pos)
        self.btn_quests.check_hover(mouse_pos)

        # Xử lý Click
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.btn_play.is_clicked(mouse_pos, mouse_pressed):
                self.next_state = STATE_LEVEL_SELECT # Chuyển sang chọn màn
            elif self.btn_shop.is_clicked(mouse_pos, mouse_pressed):
                self.next_state = STATE_SHOP
            elif self.btn_quests.is_clicked(mouse_pos, mouse_pressed):
                self.next_state = STATE_QUESTS

    def draw(self, screen, player_name, coins):
        screen.fill(BG_COLOR)
        
        # Header (Thông tin người chơi & Tiền)
        pygame.draw.rect(screen, INPUT_BOX_COLOR, (0, 0, WINDOW_WIDTH, 80))
        
        name_surf = self.font_info.render(f"PLAYER: {player_name.upper()}", True, TEXT_COLOR)
        screen.blit(name_surf, (30, 25))
        
        coin_surf = self.font_info.render(f"XU: {coins}", True, HIGHLIGHT_COLOR)
        screen.blit(coin_surf, (WINDOW_WIDTH - 150, 25))

        # Tiêu đề giữa
        title_surf = self.font_title.render("PIPEMASTER PRO", True, PIPE_COLOR_ON)
        title_rect = title_surf.get_rect(center=(WINDOW_WIDTH//2, 160))
        screen.blit(title_surf, title_rect)

        # Vẽ các nút
        self.btn_play.draw(screen)
        self.btn_shop.draw(screen)
        self.btn_quests.draw(screen)