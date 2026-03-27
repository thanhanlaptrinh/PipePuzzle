# main.py
import pygame
import sys
from settings import *
from board import Board
from screens import StartScreen, DashboardScreen, LevelSelectScreen, ShopScreen, QuestsScreen, PauseMenu, TutorialPopup, WinPopup, Button, SkinScreen

def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("PIPEMASTER PRO - Chờ 3s Win Game")
    clock = pygame.time.Clock()

    start_screen = StartScreen()
    dashboard_screen = DashboardScreen()
    level_select_screen = LevelSelectScreen()
    shop_screen = ShopScreen()
    quests_screen = QuestsScreen()
    pause_menu = PauseMenu()
    tutorial_popup = TutorialPopup()
    win_popup = WinPopup()
    skin_screen = SkinScreen()
    
    btn_options = Button(WINDOW_WIDTH - 120, 20, 100, 50, "MENU", INPUT_BOX_COLOR, TEXT_COLOR)
    
    game_board = None 
    player_name = ""
    player_coins = 100
    current_state = STATE_MENU_NAME
    
    # Nạp hình nền cho lúc chơi
    try:
        raw_game_bg = pygame.image.load(BG_GAME_PATH).convert()
        game_bg = pygame.transform.scale(raw_game_bg, (WINDOW_WIDTH, WINDOW_HEIGHT))
    except pygame.error as e:
        print(f"Không tải được ảnh nền game: {e}")
        game_bg = None
    
    # --- CÁC BIẾN QUẢN LÝ POPUP & THỜI GIAN CHỜ ---
    is_paused = False 
    show_tutorial = False 
    show_win = False
    is_winning = False # Cờ báo hiệu: "Đã thắng rồi, đang trong thời gian chờ hiện bảng"
    win_timer = 0      # Lưu lại thời điểm bắt đầu đếm ngược

    running = True
    while running:
        events = pygame.event.get()
        mouse_pos = pygame.mouse.get_pos()
        
        # ==========================================
        # 1. BẮT SỰ KIỆN
        # ==========================================
        for event in events:
            if event.type == pygame.QUIT: running = False
            
            if current_state == STATE_MENU_NAME: start_screen.handle_event(event)
            elif current_state == STATE_DASHBOARD: dashboard_screen.handle_event(event)
            elif current_state == STATE_LEVEL_SELECT: level_select_screen.handle_event(event)
            elif current_state == STATE_SHOP: shop_screen.handle_event(event)
            elif current_state == STATE_QUESTS: quests_screen.handle_event(event)
            elif current_state == STATE_SKIN: skin_screen.handle_event(event)


            
            elif current_state == STATE_GAME_PLAY:
                if show_win:
                    win_popup.handle_event(event)
                elif show_tutorial:
                    tutorial_popup.handle_event(event)
                elif is_paused:
                    pause_menu.handle_event(event)
                elif is_winning:
                    # NẾU ĐANG CHỜ 3 GIÂY -> KHÔNG CHO CLICK CHUỘT LÀM RỐI ỐNG NƯỚC NỮA
                    pass 
                else:
                    # Chơi bình thường
                    btn_options.check_hover(mouse_pos)
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        if btn_options.is_clicked(mouse_pos, pygame.mouse.get_pressed()):
                            is_paused = True
                        else:
                            game_board.handle_click(mouse_pos[0], mouse_pos[1])
                    
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                        is_paused = True

        # ==========================================
        # 2. KIỂM TRA ĐIỀU KIỆN THẮNG & ĐẾM NGƯỢC 3 GIÂY
        # ==========================================
        if current_state == STATE_GAME_PLAY and game_board:
            # Nếu chưa thắng và cũng chưa kích hoạt trạng thái đếm ngược
            if not show_win and not show_tutorial and not is_paused and not is_winning:
                if game_board.check_win():
                    is_winning = True # Kích hoạt thời gian chờ
                    win_timer = pygame.time.get_ticks() # Bấm giờ ngay lúc này!
                    
            # Nếu đang trong trạng thái chờ 3s (is_winning đang True)
            if is_winning:
                current_time = pygame.time.get_ticks()
                # Nếu thời gian hiện tại - thời gian lúc bắt đầu chờ >= 3000 mili-giây (3 giây)
                if current_time - win_timer >= 3000:
                    show_win = True    # Hiện bảng lên
                    is_winning = False # Tắt trạng thái đếm ngược

        # ==========================================
        # 3. XỬ LÝ LOGIC CHUYỂN CẢNH
        # ==========================================
        if current_state == STATE_MENU_NAME and start_screen.next_state == STATE_DASHBOARD:
            player_name = start_screen.player_name
            current_state = STATE_DASHBOARD
            start_screen.next_state = STATE_MENU_NAME 
            
        elif current_state == STATE_DASHBOARD and dashboard_screen.next_state is not None:
            current_state = dashboard_screen.next_state
            dashboard_screen.next_state = None 
                
        elif current_state == STATE_LEVEL_SELECT:
            if level_select_screen.next_state == STATE_GAME_PLAY:
                game_board = Board(level_id=level_select_screen.selected_level) 
                current_state = STATE_GAME_PLAY
                show_tutorial = True  
                is_paused = False 
                show_win = False
                is_winning = False # Reset cờ đếm giờ
                level_select_screen.next_state = None
            elif level_select_screen.next_state == STATE_DASHBOARD:
                current_state = STATE_DASHBOARD
                level_select_screen.next_state = None
                
        elif current_state == STATE_SKIN and skin_screen.next_state == STATE_DASHBOARD:
            current_state = STATE_DASHBOARD
            skin_screen.next_state = None
        
        elif current_state == STATE_SHOP and shop_screen.next_state == STATE_DASHBOARD:
            current_state = STATE_DASHBOARD
            shop_screen.next_state = None
            
        elif current_state == STATE_QUESTS and quests_screen.next_state == STATE_DASHBOARD:
            current_state = STATE_DASHBOARD
            quests_screen.next_state = None
                
        elif current_state == STATE_GAME_PLAY:
            if show_win:
                if win_popup.action == "MENU":
                    current_state = STATE_LEVEL_SELECT
                    show_win = False
                    is_winning = False
                    win_popup.action = None
                elif win_popup.action == "NEXT":
                    level_select_screen.selected_level = (level_select_screen.selected_level % 12) + 1
                    game_board = Board(level_id=level_select_screen.selected_level)
                    show_win = False
                    is_winning = False
                    show_tutorial = True
                    win_popup.action = None
                    
            elif show_tutorial and tutorial_popup.action == "UNDERSTOOD":
                show_tutorial = False
                tutorial_popup.action = None
                
            elif is_paused:
                if pause_menu.action == "RESTART":
                    game_board = Board(level_id=level_select_screen.selected_level)
                    is_paused = False
                    is_winning = False
                    pause_menu.action = None
                elif pause_menu.action == "AI_SOLVE":
                    print(">>> Gọi Thuật toán AI Hill Climbing...")
                    is_paused = False
                    pause_menu.action = None
                elif pause_menu.action == "EXIT":
                    current_state = STATE_LEVEL_SELECT
                    is_paused = False
                    is_winning = False
                    pause_menu.action = None

        # ==========================================
        # 4. VẼ TẤT CẢ LÊN MÀN HÌNH
        # ==========================================
        if current_state == STATE_MENU_NAME: start_screen.draw(screen)
        elif current_state == STATE_DASHBOARD: dashboard_screen.draw(screen, player_name, player_coins)
        elif current_state == STATE_LEVEL_SELECT:
            if game_bg: screen.blit(game_bg, (0, 0))
            else: screen.fill(BG_COLOR)
            level_select_screen.draw(screen)
        elif current_state == STATE_SHOP: shop_screen.draw(screen)
        elif current_state == STATE_QUESTS: quests_screen.draw(screen)
        elif current_state == STATE_SKIN: skin_screen.draw(screen)
        
        elif current_state == STATE_GAME_PLAY and game_board:
            if game_bg: screen.blit(game_bg, (0, 0))
            else: screen.fill(BG_COLOR)
            
            game_board.draw(screen)
            btn_options.draw(screen)
            
            if show_win: win_popup.draw(screen)
            elif show_tutorial: tutorial_popup.draw(screen)
            elif is_paused: pause_menu.draw(screen)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()