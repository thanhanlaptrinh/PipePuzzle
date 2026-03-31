import json
import os
import pygame
import sys
import random
import io
from settings import *
from board import Board
from hill_climbing import get_best_single_rotation
from screens import StartScreen, DashboardScreen, LevelSelectScreen, ShopScreen, QuestsScreen, PauseMenu, TutorialPopup, WinPopup, Button, SkinScreen

# Cấu hình UTF-8 cho Terminal của bạn Sếp
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

SAVE_FILE = "save_data.json"

def load_progress():
    """Tải toàn bộ tiến độ: Level, Xu, Tên, và Danh sách Mã đã dùng"""
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('unlocked_levels', 1), data.get('coins', 100), data.get('player_name', ""), data.get('redeemed_codes', [])
        except:
            pass
    return 1, 100, "", []

def save_progress(level, coins, name, redeemed_codes):
    """Lưu toàn bộ dữ liệu vào két sắt"""
    data = {
        'unlocked_levels': level,
        'coins': coins,
        'player_name': name,
        'redeemed_codes': redeemed_codes
    }
    with open(SAVE_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False)

# --- Template dữ liệu nhiệm vụ (Của bạn Sếp) ---
quests_data_template = [
    {
        "id": "win_1_level",
        "title": "Thắng 1 màn",
        "description": "Hoàn thành 1 màn chơi",
        "goal": 1,
        "progress": 0,
        "reward": {"coins": 500},
        "completed": False
    },
    {
        "id": "collect_5000_coins",
        "title": "Thu thập 5000 xu",
        "description": "Tích lũy 5000 xu",
        "goal": 5000,
        "progress": 0,
        "reward": {"coins": 1000},
        "completed": False
    }
]

def load_quests():
    """Load tiến độ nhiệm vụ từ file save"""
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get("quests", [q.copy() for q in quests_data_template])
        except:
            pass
    return [q.copy() for q in quests_data_template]

def save_quests(quests):
    """Lưu tiến độ nhiệm vụ vào file save"""
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except:
            data = {}
    else:
        data = {}

    data["quests"] = quests
    with open(SAVE_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False)

# KHỞI TẠO BIẾN TOÀN CỤC CHO TIẾN ĐỘ
unlocked_levels, global_coins, global_name, redeemed_codes = load_progress()
quests = load_quests()
MAX_LEVELS = 60

def main():
    global unlocked_levels
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("PIPE PUZZLE")
    clock = pygame.time.Clock()

    start_screen = StartScreen()
    dashboard_screen = DashboardScreen()
    level_select_screen = LevelSelectScreen()
    shop_screen = ShopScreen()
    quests_screen = QuestsScreen(quests)
    pause_menu = PauseMenu()
    tutorial_popup = TutorialPopup()
    win_popup = WinPopup()
    skin_screen = SkinScreen()
    
    btn_options = Button(WINDOW_WIDTH - 120, 20, 100, 50, "MENU", (50, 50, 50), (255, 255, 255))
    
    game_board = None 
    
    player_coins = global_coins 
    player_name = "" 
    current_state = STATE_MENU_NAME
    
    try:
        raw_game_bg = pygame.image.load(BG_GAME_PATH).convert()
        game_bg = pygame.transform.smoothscale(raw_game_bg, (WINDOW_WIDTH, WINDOW_HEIGHT))
    except pygame.error as e:
        print(f"Không tải được ảnh nền game: {e}")
        game_bg = None
    
    is_paused = False 
    show_tutorial = False 
    show_win = False
    is_winning = False 
    win_timer = 0      
    ai_solving = False
    ai_timer = 0

    running = True
    while running:
        events = pygame.event.get()
        mouse_pos = pygame.mouse.get_pos()
        
        for event in events:
            if event.type == pygame.QUIT: running = False
            
            if current_state == STATE_MENU_NAME:                
                start_screen.handle_event(event)

            elif current_state == STATE_DASHBOARD: 
                action = dashboard_screen.handle_event(event, redeemed_codes)
                if action == "UNLOCK_ALL":
                    unlocked_levels = MAX_LEVELS
                    if "UNPIPE" not in redeemed_codes: 
                        redeemed_codes.append("UNPIPE")
                    save_progress(unlocked_levels, player_coins, player_name, redeemed_codes) 
                    
                elif action == "ADD_COINS":
                    player_coins += 10000 
                    if "PIPEGOLD" not in redeemed_codes:
                        redeemed_codes.append("PIPEGOLD")
                    save_progress(unlocked_levels, player_coins, player_name, redeemed_codes)
                    
            elif current_state == STATE_LEVEL_SELECT: 
                level_select_screen.handle_event(event, unlocked_levels)
            elif current_state == STATE_SHOP: 
                shop_screen.handle_event(event)
            elif current_state == STATE_QUESTS: 
                quests_screen.handle_event(event)
            elif current_state == STATE_SKIN: 
                skin_screen.handle_event(event)

            elif current_state == STATE_GAME_PLAY:
                if show_win:
                    win_popup.handle_event(event)
                elif show_tutorial:
                    tutorial_popup.handle_event(event)
                elif is_paused:
                    pause_menu.handle_event(event)
                elif is_winning:
                    pass
                else:
                    btn_options.check_hover(mouse_pos)
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        if btn_options.is_clicked(mouse_pos, pygame.mouse.get_pressed()):
                            is_paused = True
                        else:
                            game_board.handle_click(mouse_pos[0], mouse_pos[1])
                    
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                        is_paused = True

        if current_state == STATE_GAME_PLAY and game_board:
            if ai_solving and not show_win and not is_paused:
                current_time = pygame.time.get_ticks()
                if current_time - ai_timer >= 150: 
                    move = get_best_single_rotation(game_board)
                    if move:
                        row, col, rotations = move 
                        for _ in range(rotations):
                            game_board.grid[row][col].rotate()
                        game_board.update_connectivity()
                        ai_timer = current_time 
                    else:
                        ai_solving = False      

            if not show_win and not show_tutorial and not is_paused and not is_winning:
                if game_board.check_win():
                    is_winning = True 
                    win_timer = pygame.time.get_ticks() 
                    earned = random.randint(1000, 1500)
                    player_coins += earned
                    win_popup.earned_coins = earned 
                    
                    # --- LOGIC NHIỆM VỤ ĐÃ ĐƯỢC GỘP XỊN XÒ VÀO ĐÂY ---
                    for quest in quests:
                        if quest["id"] == "win_1_level" and not quest["completed"]:
                            quest["progress"] += 1
                            if quest["progress"] >= quest["goal"]:
                                quest["completed"] = True
                                player_coins += quest["reward"]["coins"]
                                print(f"Hoàn thành nhiệm vụ: {quest['title']} - Nhận {quest['reward']['coins']} xu!")

                    for quest in quests:
                        if quest["id"] == "collect_5000_coins" and not quest["completed"]:
                            if player_coins >= quest["goal"]:
                                quest["completed"] = True
                                player_coins += quest["reward"]["coins"]
                                print(f"Hoàn thành nhiệm vụ: {quest['title']} - Nhận {quest['reward']['coins']} xu!")
                    
                    save_quests(quests)
                    save_progress(unlocked_levels, player_coins, player_name, redeemed_codes)
                    
            # Hiệu ứng trễ 2 giây trước khi hiện bảng Win
            if is_winning:
                current_time = pygame.time.get_ticks()
                if current_time - win_timer >= 2000:
                    show_win = True    
                    is_winning = False 

        if current_state == STATE_MENU_NAME and start_screen.next_state == STATE_DASHBOARD:
            player_name = start_screen.player_name
            current_state = STATE_DASHBOARD
            start_screen.next_state = STATE_MENU_NAME 
            save_progress(unlocked_levels, player_coins, player_name, redeemed_codes)
            
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
                is_winning = False 
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
                    ai_solving = False 
                    win_popup.action = None

                elif win_popup.action == "NEXT":
                    if level_select_screen.selected_level == unlocked_levels and unlocked_levels < MAX_LEVELS:
                        unlocked_levels += 1
                        save_progress(unlocked_levels, player_coins, player_name, redeemed_codes)  

                    level_select_screen.selected_level = (level_select_screen.selected_level % MAX_LEVELS) + 1
                    game_board = Board(level_id=level_select_screen.selected_level)
                    show_win = False
                    is_winning = False
                    ai_solving = False 
                    show_tutorial = True
                    win_popup.action = None
                
                elif win_popup.action == "REPLAY":
                    game_board = Board(level_id=level_select_screen.selected_level)
                    show_win = False
                    is_winning = False
                    ai_solving = False 
                    win_popup.action = None
                    
            elif show_tutorial and tutorial_popup.action == "UNDERSTOOD":
                show_tutorial = False
                tutorial_popup.action = None
                
            elif is_paused:
                if pause_menu.action == "RESTART":
                    game_board = Board(level_id=level_select_screen.selected_level)
                    is_paused = False
                    is_winning = False
                    ai_solving = False 
                    pause_menu.action = None
                elif pause_menu.action == "AI_SOLVE":
                    # --- ĐÃ KHÔI PHỤC LOGIC TRỪ 100 COIN ---
                    if player_coins >= 100:
                        player_coins -= 100
                        save_progress(unlocked_levels, player_coins, player_name, redeemed_codes)
                        ai_solving = True                    
                        is_paused = False
                        pause_menu.action = None
                    else:
                        try:
                            pause_menu.error_msg = "KHÔNG ĐỦ 100 COIN!"
                            pause_menu.error_alpha = 255
                        except: pass
                        pause_menu.action = None
                elif pause_menu.action == "EXIT":
                    current_state = STATE_LEVEL_SELECT
                    is_paused = False
                    is_winning = False
                    ai_solving = False 
                    pause_menu.action = None

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