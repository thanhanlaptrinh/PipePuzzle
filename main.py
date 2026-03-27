# main.py
import pygame
import sys
from settings import *
from board import Board
from screens import StartScreen, DashboardScreen, LevelSelectScreen, ShopScreen, QuestsScreen, PauseMenu, TutorialPopup, WinPopup, Button, SkinScreen

def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("PIPEMASTER PRO - Hoàn Thiện UI 100%")
    clock = pygame.time.Clock()

    # Khởi tạo toàn bộ các màn hình
    start_screen = StartScreen()
    dashboard_screen = DashboardScreen()
    level_select_screen = LevelSelectScreen()
    shop_screen = ShopScreen()
    quests_screen = QuestsScreen()
    pause_menu = PauseMenu()
    tutorial_popup = TutorialPopup()
    win_popup = WinPopup()
    skin_screen = SkinScreen()
    
    # Nút MENU trong game
    btn_options = Button(WINDOW_WIDTH - 120, 20, 100, 50, "MENU", INPUT_BOX_COLOR, TEXT_COLOR)
    
    # Các biến hệ thống
    game_board = None 
    player_name = ""
    player_coins = 100
    current_state = STATE_MENU_NAME
    
    # Các cờ (flag) kiểm soát Popup
    is_paused = False 
    show_tutorial = False 
    show_win = False

    running = True
    while running:
        events = pygame.event.get()
        mouse_pos = pygame.mouse.get_pos()
        
        # ==========================================
        # 1. BẮT SỰ KIỆN (CHUỘT, BÀN PHÍM)
        # ==========================================
        for event in events:
            if event.type == pygame.QUIT: running = False
            
            # Nếu ở ngoài Menu
            if current_state == STATE_MENU_NAME: start_screen.handle_event(event)
            elif current_state == STATE_DASHBOARD: dashboard_screen.handle_event(event)
            elif current_state == STATE_LEVEL_SELECT: level_select_screen.handle_event(event)
            elif current_state == STATE_SHOP: shop_screen.handle_event(event)
            elif current_state == STATE_QUESTS: quests_screen.handle_event(event)
            
            # Nếu đang ở trong Màn Chơi
            elif current_state == STATE_GAME_PLAY:
                if show_win:
                    win_popup.handle_event(event)
                elif show_tutorial:
                    tutorial_popup.handle_event(event)
                elif is_paused:
                    pause_menu.handle_event(event)
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
        # 2. KIỂM TRA ĐIỀU KIỆN THẮNG LIÊN TỤC
        # ==========================================
        if current_state == STATE_GAME_PLAY and game_board:
            if not show_win and not show_tutorial and not is_paused:
                if game_board.check_win():
                    show_win = True

        # ==========================================
        # 3. XỬ LÝ LOGIC CHUYỂN CẢNH & NÚT BẤM
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
                show_tutorial = True  # Bật Hướng dẫn
                is_paused = False 
                show_win = False
                level_select_screen.next_state = None
            elif level_select_screen.next_state == STATE_DASHBOARD:
                current_state = STATE_DASHBOARD
                level_select_screen.next_state = None
                
        elif current_state == STATE_GAME_PLAY:
            # Xử lý nút khi Thắng
            if show_win:
                if win_popup.action == "MENU":
                    current_state = STATE_LEVEL_SELECT
                    show_win = False
                    win_popup.action = None
                elif win_popup.action == "NEXT":
                    # Tự động nhảy sang level tiếp theo
                    level_select_screen.selected_level = (level_select_screen.selected_level % 10) + 1
                    game_board = Board(level_id=level_select_screen.selected_level)
                    show_win = False
                    show_tutorial = True # Vẫn hiện hướng dẫn ở màn mới (bạn có thể đổi thành False nếu muốn)
                    win_popup.action = None
                    
            # Xử lý nút khi Hướng dẫn
            elif show_tutorial and tutorial_popup.action == "UNDERSTOOD":
                show_tutorial = False
                tutorial_popup.action = None
                
            # Xử lý nút khi Tạm dừng
            elif is_paused:
                if pause_menu.action == "RESTART":
                    game_board = Board(level_id=level_select_screen.selected_level)
                    is_paused = False
                    pause_menu.action = None
                elif pause_menu.action == "AI_SOLVE":
                    print(">>> Gọi Thuật toán AI Hill Climbing...")
                    is_paused = False
                    pause_menu.action = None
                elif pause_menu.action == "EXIT":
                    current_state = STATE_LEVEL_SELECT
                    is_paused = False
                    pause_menu.action = None

        # ==========================================
        # 4. VẼ TẤT CẢ LÊN MÀN HÌNH
        # ==========================================
        screen.fill(BG_COLOR)
        if current_state == STATE_MENU_NAME: start_screen.draw(screen)
        elif current_state == STATE_DASHBOARD: dashboard_screen.draw(screen, player_name, player_coins)
        elif current_state == STATE_LEVEL_SELECT: level_select_screen.draw(screen)
        elif current_state == STATE_SHOP: shop_screen.draw(screen)
        elif current_state == STATE_QUESTS: quests_screen.draw(screen)
        
        elif current_state == STATE_GAME_PLAY and game_board:
            game_board.draw(screen)
            btn_options.draw(screen)
            
            # Ưu tiên vẽ màng đè theo thứ tự: Thắng -> Hướng Dẫn -> Tạm dừng
            if show_win:
                win_popup.draw(screen)
            elif show_tutorial:
                tutorial_popup.draw(screen)
            elif is_paused:
                pause_menu.draw(screen)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()