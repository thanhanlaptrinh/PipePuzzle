# main.py
import pygame
import sys
from settings import *
from board import Board
# Import tất cả các màn hình quản lý
from start_screen import StartScreen
from dashboard import DashboardScreen
# Tạm thời import class rỗng để không bị lỗi, team sẽ code sau
try:
    from level_select import LevelSelectScreen
    from shop import ShopScreen
    from quests import QuestsScreen
except ImportError:
    # Nếu team chưa tạo file, tạo class giả lập để test luồng
    class LevelSelectScreen: 
        def __init__(self): self.next_state = None
        def handle_event(self, e): 
            if e.type == pygame.KEYDOWN and e.key == pygame.K_1: self.next_state = STATE_GAME_PLAY
        def draw(self, s): s.fill((50,50,50)); pygame.font.SysFont(None, 40).render("LEVEL SELECT (Press 1 to Play)", True, (255,255,255))
    class ShopScreen: 
        def __init__(self): self.next_state = None
        def handle_event(self, e): pass
        def draw(self, s): pass
    class QuestsScreen: 
        def __init__(self): self.next_state = None
        def handle_event(self, e): pass
        def draw(self, s): pass

def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("PIPEMASTER PRO - System Integrated")
    clock = pygame.time.Clock()

    # --- 1. KHỞI TẠO CÁC ĐỐI TƯỢNG MÀN HÌNH ---
    start_screen = StartScreen()
    dashboard_screen = DashboardScreen()
    level_select_screen = LevelSelectScreen()
    shop_screen = ShopScreen()
    quests_screen = QuestsScreen()
    
    # Board game sẽ được khởi tạo lại khi chọn màn cụ thể
    game_board = None 
    
    # --- 2. BIẾN LƯU TRỮ THÔNG TIN NGƯỜI CHƠI ---
    player_name = ""
    player_coins = 100 # Cho sẵn 100 xu để test cửa hàng
    current_level = 0

    # --- 3. BIẾN QUẢN LÝ TRẠNG THÁI GAME CHÍNH ---
    # Bắt đầu ở màn hình nhập tên
    current_state = STATE_MENU_NAME

    running = True
    while running:
        # A. LẤY SỰ KIỆN CHUNG
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False
            
            # B. PHÂN PHỐI SỰ KIỆN THEO TRẠNG THÁI HIỆN TẠI
            if current_state == STATE_MENU_NAME:
                start_screen.handle_event(event)
            elif current_state == STATE_DASHBOARD:
                dashboard_screen.handle_event(event)
            elif current_state == STATE_LEVEL_SELECT:
                level_select_screen.handle_event(event)
            elif current_state == STATE_SHOP:
                shop_screen.handle_event(event)
            elif current_state == STATE_QUESTS:
                quests_screen.handle_event(event)
            elif current_state == STATE_GAME_PLAY:
                # Xử lý click chuột xoay ống
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    game_board.handle_click(mouse_x, mouse_y)
                # Bấm Esc để quay lại Chọn màn
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    current_state = STATE_LEVEL_SELECT

        # C. CẬP NHẬT LOGIC CHUYỂN CẢNH (KEY FIX ĐÂY NÈ LEADER)
        
        # 1. Từ Nhập tên -> Dashboard
        if current_state == STATE_MENU_NAME:
            # Kiểm tra xem start_screen đã ra lệnh qua Dashboard chưa
            if start_screen.next_state == STATE_DASHBOARD: 
                player_name = start_screen.player_name
                current_state = STATE_DASHBOARD
                start_screen.next_state = STATE_MENU_NAME # Reset lại
        
        # 2. Từ Dashboard đi các ngả
        elif current_state == STATE_DASHBOARD:
            if dashboard_screen.next_state is not None:
                current_state = dashboard_screen.next_state
                dashboard_screen.next_state = None # Reset
                
        # 3. Từ Chọn màn -> Vào Game
        elif current_state == STATE_LEVEL_SELECT:
            if level_select_screen.next_state == STATE_GAME_PLAY:
                # Lấy level được chọn (team sẽ code logic lấy level sau)
                current_level = 1 
                # Khởi tạo board mới cho level này
                game_board = Board() 
                current_state = STATE_GAME_PLAY
                level_select_screen.next_state = None # Reset

        # D. VẼ GIAO DIỆN TƯƠNG ỨNG
        screen.fill(BG_COLOR)
        
        if current_state == STATE_MENU_NAME:
            start_screen.draw(screen)
        elif current_state == STATE_DASHBOARD:
            # Truyền tên và tiền vào để vẽ header
            dashboard_screen.draw(screen, player_name, player_coins)
        elif current_state == STATE_LEVEL_SELECT:
            level_select_screen.draw(screen)
        elif current_state == STATE_SHOP:
            shop_screen.draw(screen)
        elif current_state == STATE_QUESTS:
            quests_screen.draw(screen)
        elif current_state == STATE_GAME_PLAY:
            if game_board:
                game_board.draw(screen)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()