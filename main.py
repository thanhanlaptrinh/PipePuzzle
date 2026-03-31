import json
import os
import pygame
import sys
import random
import io
import heapq 

from settings import *
from board import Board
try:
    from hill_climbing import get_best_single_rotation
except ImportError:
    def get_best_single_rotation(board): return None 

from screens import StartScreen, DashboardScreen, LevelSelectScreen, ShopScreen, QuestsScreen, PauseMenu, TutorialPopup, WinPopup, Button, SkinScreen

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

SAVE_FILE = "save_data.json"

def find_optimal_rock_to_break(board):
    rows, cols = board.rows, board.cols
    distances = { (r, c): float('inf') for r in range(rows) for c in range(cols) }
    pq = []
    came_from = {}
    
    for r in range(rows):
        for c in range(cols):
            if getattr(board.grid[r][c], 'is_powered', False):
                distances[(r, c)] = 0
                heapq.heappush(pq, (0, r, c))
                
    if not pq:
        distances[(0, 0)] = 0
        heapq.heappush(pq, (0, 0, 0))
                
    while pq:
        cost, r, c = heapq.heappop(pq)
        if cost > distances[(r, c)]: continue
        if (r, c) == (rows-1, cols-1): break
        
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols:
                weight = 1 if getattr(board.grid[nr][nc], 'is_rock', False) else 0
                new_cost = cost + weight
                if new_cost < distances[(nr, nc)]:
                    distances[(nr, nc)] = new_cost
                    came_from[(nr, nc)] = (r, c)
                    heapq.heappush(pq, (new_cost, nr, nc))
                    
    if distances[(rows-1, cols-1)] == float('inf') or distances[(rows-1, cols-1)] == 0:
        return None 
        
    curr = (rows-1, cols-1)
    path = []
    while distances[curr] > 0:
        path.append(curr)
        if curr in came_from: curr = came_from[curr]
        else: break
            
    path.reverse()
    for r, c in path:
        if getattr(board.grid[r][c], 'is_rock', False):
            return board.grid[r][c]
    return None

def load_progress():
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('unlocked_levels', 1), data.get('coins', 100), data.get('player_name', ""), data.get('redeemed_codes', []), data.get('pickaxes', 3) 
        except: pass
    return 1, 100, "", [], 3

def save_progress(level, coins, name, redeemed_codes, pickaxes):
    data = {'unlocked_levels': level, 'coins': coins, 'player_name': name, 'redeemed_codes': redeemed_codes, 'pickaxes': pickaxes}
    with open(SAVE_FILE, 'w', encoding='utf-8') as f: json.dump(data, f, ensure_ascii=False)

quests_data_template = [
    {"id": "win_1_level", "title": "Thắng 1 màn", "description": "Hoàn thành 1 màn", "goal": 1, "progress": 0, "reward": {"coins": 500}, "completed": False},
    {"id": "collect_5000_coins", "title": "Thu thập 5000 xu", "description": "Tích lũy 5000 xu", "goal": 5000, "progress": 0, "reward": {"coins": 1000}, "completed": False}
]

def load_quests():
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE, 'r', encoding='utf-8') as f: data = json.load(f)
            return data.get("quests", [q.copy() for q in quests_data_template])
        except: pass
    return [q.copy() for q in quests_data_template]

def save_quests(quests):
    try:
        with open(SAVE_FILE, 'r', encoding='utf-8') as f: data = json.load(f)
    except: data = {}
    data["quests"] = quests
    with open(SAVE_FILE, 'w', encoding='utf-8') as f: json.dump(data, f, ensure_ascii=False)

unlocked_levels, global_coins, global_name, redeemed_codes, global_pickaxes = load_progress()
quests = load_quests()
MAX_LEVELS = 60

def main():
    global unlocked_levels
    pygame.init()
    
    pygame.mixer.init()
    try:
        pygame.mixer.music.load("assets/sounds/bgsound.mp3") 
        pygame.mixer.music.set_volume(1.0)
        pygame.mixer.music.play(-1) 
    except pygame.error as e:
        print(f"Không tải được nhạc nền: {e}")
        
    try: sound_coin = pygame.mixer.Sound("assets/sounds/coin.mp3")
    except pygame.error: sound_coin = None
        
    try: sound_win = pygame.mixer.Sound("assets/sounds/win.mp3")
    except pygame.error: sound_win = None
        
    try: sound_button = pygame.mixer.Sound("assets/sounds/button.mp3")
    except pygame.error: sound_button = None

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
    
    try:
        img_pickaxe = pygame.image.load("assets/images/pickaxe.png").convert_alpha()
        img_pickaxe.set_colorkey((255, 255, 255)) 
        img_pickaxe_ui = pygame.transform.smoothscale(img_pickaxe, (40, 40))
        img_pickaxe_cursor = pygame.transform.smoothscale(img_pickaxe, (30, 30))
    except pygame.error as e:
        img_pickaxe_ui = None; img_pickaxe_cursor = None

    btn_options = Button(WINDOW_WIDTH - 120, 20, 100, 50, "MENU", (50, 50, 50), (255, 255, 255))
    btn_buy_pickaxe = Button(75, WINDOW_HEIGHT - 90, 40, 40, "+", (46, 204, 113))
    
    game_board = None; player_coins = global_coins; player_pickaxes = global_pickaxes
    player_name = ""; current_state = STATE_MENU_NAME
    
    game_notif = ""; game_notif_alpha = 0
    
    try:
        raw_game_bg = pygame.image.load(BG_GAME_PATH).convert()
        game_bg = pygame.transform.smoothscale(raw_game_bg, (WINDOW_WIDTH, WINDOW_HEIGHT))
    except pygame.error as e: game_bg = None
    
    is_paused = False; show_tutorial = False; show_win = False; is_winning = False 
    win_timer = 0; ai_solving = False; ai_timer = 0; is_pickaxe_active = False 
    
    ai_paid_this_level = False       
    ai_paused_for_pickaxe = False    
    
    ai_animating_pickaxe = False
    ai_target_rock = None
    ai_pickaxe_start_pos = (0, 0)
    ai_pickaxe_target_pos = (0, 0)
    ai_pickaxe_current_pos = [0, 0]
    ai_pickaxe_progress = 0.0

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
                    if "UNPIPE" not in redeemed_codes: redeemed_codes.append("UNPIPE")
                    save_progress(unlocked_levels, player_coins, player_name, redeemed_codes, player_pickaxes) 
                elif action == "ADD_COINS":
                    player_coins += 10000 
                    if "PIPEGOLD" not in redeemed_codes: redeemed_codes.append("PIPEGOLD")
                    save_progress(unlocked_levels, player_coins, player_name, redeemed_codes, player_pickaxes)
                    if sound_coin:
                        try: sound_coin.set_volume(dashboard_screen.sfx_vol)
                        except: pass
                        sound_coin.play()
                    
            elif current_state == STATE_LEVEL_SELECT: level_select_screen.handle_event(event, unlocked_levels)
            elif current_state == STATE_SHOP: shop_screen.handle_event(event)
            elif current_state == STATE_QUESTS: quests_screen.handle_event(event)
            elif current_state == STATE_SKIN: skin_screen.handle_event(event)

            elif current_state == STATE_GAME_PLAY:
                if show_win: win_popup.handle_event(event)
                elif show_tutorial: tutorial_popup.handle_event(event)
                elif is_paused: pause_menu.handle_event(event)
                elif is_winning: pass
                else:
                    btn_options.check_hover(mouse_pos)
                    btn_buy_pickaxe.is_enabled = (player_pickaxes < 3) 
                    btn_buy_pickaxe.check_hover(mouse_pos)
                    
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        if btn_options.is_clicked(mouse_pos, pygame.mouse.get_pressed()):
                            is_paused = True; is_pickaxe_active = False; ai_paused_for_pickaxe = False
                        elif btn_buy_pickaxe.is_clicked(mouse_pos, pygame.mouse.get_pressed()):
                            if player_coins >= 100 and player_pickaxes < 3:
                                player_coins -= 100; player_pickaxes += 1
                                save_progress(unlocked_levels, player_coins, player_name, redeemed_codes, player_pickaxes)
                                if ai_paused_for_pickaxe:
                                    ai_solving = True; ai_paused_for_pickaxe = False
                            else:
                                game_notif = "KHÔNG ĐỦ XU ĐỂ MUA CUỐC!"; game_notif_alpha = 255
                        else:
                            pickaxe_area = pygame.Rect(20, WINDOW_HEIGHT - 200, 45, 155)
                            if pickaxe_area.collidepoint(mouse_pos):
                                if player_pickaxes > 0: is_pickaxe_active = not is_pickaxe_active 
                            else:
                                if is_pickaxe_active:
                                    if hasattr(game_board, 'break_rock'):
                                        if game_board.break_rock(mouse_pos[0], mouse_pos[1]):
                                            player_pickaxes -= 1 
                                            save_progress(unlocked_levels, player_coins, player_name, redeemed_codes, player_pickaxes)
                                    is_pickaxe_active = False 
                                    ai_solving = False; ai_paused_for_pickaxe = False
                                else:
                                    game_board.handle_click(mouse_pos[0], mouse_pos[1])
                                    if sound_button:
                                        try: sound_button.set_volume(dashboard_screen.sfx_vol)
                                        except: pass
                                        sound_button.play()
                                    ai_solving = False; ai_paused_for_pickaxe = False 
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                        is_paused = True; is_pickaxe_active = False; ai_paused_for_pickaxe = False

        if current_state == STATE_GAME_PLAY and game_board:
            if ai_animating_pickaxe and not is_paused:
                ai_pickaxe_progress += 0.05 
                
                if ai_pickaxe_progress >= 1.0:
                    ai_target_rock.is_rock = False 
                    player_pickaxes -= 1
                    game_board.update_connectivity()
                    save_progress(unlocked_levels, player_coins, player_name, redeemed_codes, player_pickaxes)
                    ai_timer = pygame.time.get_ticks() 
                    ai_animating_pickaxe = False 
                else:
                    p = 1 - (1 - ai_pickaxe_progress) * (1 - ai_pickaxe_progress)
                    sx, sy = ai_pickaxe_start_pos
                    tx, ty = ai_pickaxe_target_pos
                    ai_pickaxe_current_pos[0] = sx + (tx - sx) * p
                    ai_pickaxe_current_pos[1] = sy + (ty - sy) * p

            if ai_solving and not show_win and not is_paused and not ai_animating_pickaxe and not is_winning:
                if game_board.check_win():
                    ai_solving = False 
                else:
                    current_time = pygame.time.get_ticks()
                    if current_time - ai_timer >= 150: 
                        move = get_best_single_rotation(game_board)
                        
                        if move:
                            r_ai, c_ai, _ = move
                            node_ai = game_board.grid[r_ai][c_ai]
                            if getattr(node_ai, 'is_rock', False) or getattr(node_ai, 'is_fixed', False):
                                move = None 

                        if move:
                            row, col, rotations = move 
                            for _ in range(rotations): game_board.grid[row][col].rotate()
                            game_board.update_connectivity()
                            if sound_button:
                                try: sound_button.set_volume(dashboard_screen.sfx_vol)
                                except: pass
                                sound_button.play()
                            ai_timer = current_time 
                        else:
                            rocks_on_board = []
                            for r in range(game_board.rows):
                                for c in range(game_board.cols):
                                    if getattr(game_board.grid[r][c], 'is_rock', False):
                                        rocks_on_board.append(game_board.grid[r][c])
                            
                            if rocks_on_board:
                                target_rock = None
                                for r in range(game_board.rows):
                                    for c in range(game_board.cols):
                                        if game_board.grid[r][c].is_powered:
                                            for dr, dc in [(-1,0), (1,0), (0,-1), (0,1)]:
                                                nr, nc = r+dr, c+dc
                                                if 0 <= nr < game_board.rows and 0 <= nc < game_board.cols:
                                                    if getattr(game_board.grid[nr][nc], 'is_rock', False):
                                                        target_rock = game_board.grid[nr][nc]
                                                        break
                                        if target_rock: break
                                
                                if not target_rock:
                                    target_rock = random.choice(rocks_on_board)
                                
                                if player_pickaxes > 0:
                                    ai_target_rock = target_rock
                                    ai_pickaxe_start_pos = (40, WINDOW_HEIGHT - 100) 
                                    
                                    offset_x = (WINDOW_WIDTH - (game_board.cols * TILE_SIZE)) // 2
                                    offset_y = (WINDOW_HEIGHT - (game_board.rows * TILE_SIZE)) // 2
                                    tx = offset_x + target_rock.col * TILE_SIZE + TILE_SIZE // 2
                                    ty = offset_y + target_rock.row * TILE_SIZE + TILE_SIZE // 2
                                    ai_pickaxe_target_pos = (tx, ty)
                                    
                                    ai_pickaxe_current_pos = list(ai_pickaxe_start_pos)
                                    ai_pickaxe_progress = 0.0
                                    ai_animating_pickaxe = True 
                                else:
                                    ai_solving = False; ai_paused_for_pickaxe = True
                                    game_notif = "HẾT CUỐC! MUA THÊM CUỐC ĐỂ AI PHÁ ĐÁ!"; game_notif_alpha = 255
                            else:
                                ai_solving = False      

            if not show_win and not show_tutorial and not is_paused and not is_winning:
                if game_board.check_win():
                    is_winning = True; win_timer = pygame.time.get_ticks() 
                    earned = random.randint(1000, 1500); player_coins += earned
                    
                    if sound_coin:
                        try: sound_coin.set_volume(dashboard_screen.sfx_vol)
                        except: pass
                        sound_coin.play()
                    if sound_win:
                        try: sound_win.set_volume(dashboard_screen.sfx_vol)
                        except: pass
                        sound_win.play()
                        
                    win_popup.earned_coins = earned 
                    for quest in quests:
                        if quest["id"] == "win_1_level" and not quest["completed"]:
                            quest["progress"] += 1
                            if quest["progress"] >= quest["goal"]: quest["completed"] = True
                        if quest["id"] == "collect_5000_coins" and not quest["completed"]:
                            if player_coins >= quest["goal"]:
                                quest["completed"] = True; player_coins += quest["reward"]["coins"]
                    
                    # =================================================================
                    # FIX LOGIC: MỞ KHÓA MÀN MỚI NGAY KHI VỪA THẮNG GAME TẠI ĐÂY!
                    # =================================================================
                    if level_select_screen.selected_level == unlocked_levels and unlocked_levels < MAX_LEVELS:
                        unlocked_levels += 1
                    
                    save_quests(quests)
                    save_progress(unlocked_levels, player_coins, player_name, redeemed_codes, player_pickaxes)
                    
            if is_winning:
                current_time = pygame.time.get_ticks()
                if current_time - win_timer >= 2000: show_win = True; is_winning = False 

        if current_state == STATE_MENU_NAME and start_screen.next_state == STATE_DASHBOARD:
            player_name = start_screen.player_name; current_state = STATE_DASHBOARD
            start_screen.next_state = STATE_MENU_NAME 
            save_progress(unlocked_levels, player_coins, player_name, redeemed_codes, player_pickaxes)
        elif current_state == STATE_DASHBOARD and dashboard_screen.next_state is not None:
            current_state = dashboard_screen.next_state; dashboard_screen.next_state = None 
        elif current_state == STATE_LEVEL_SELECT:
            if level_select_screen.next_state == STATE_GAME_PLAY:
                game_board = Board(level_id=level_select_screen.selected_level) 
                current_state = STATE_GAME_PLAY; show_tutorial = True  
                is_paused = False; show_win = False; is_winning = False; is_pickaxe_active = False
                ai_paid_this_level = False; ai_paused_for_pickaxe = False; ai_animating_pickaxe = False
                level_select_screen.next_state = None
            elif level_select_screen.next_state == STATE_DASHBOARD: current_state = STATE_DASHBOARD; level_select_screen.next_state = None
        elif current_state == STATE_SKIN and skin_screen.next_state == STATE_DASHBOARD: current_state = STATE_DASHBOARD; skin_screen.next_state = None
        elif current_state == STATE_SHOP and shop_screen.next_state == STATE_DASHBOARD: current_state = STATE_DASHBOARD; shop_screen.next_state = None
        elif current_state == STATE_QUESTS and quests_screen.next_state == STATE_DASHBOARD: current_state = STATE_DASHBOARD; quests_screen.next_state = None
                
        elif current_state == STATE_GAME_PLAY:
            if show_win:
                if win_popup.action == "MENU": 
                    current_state = STATE_LEVEL_SELECT; show_win = False; is_winning = False; ai_solving = False; win_popup.action = None
                    ai_animating_pickaxe = False
                elif win_popup.action == "NEXT":
                    # MÀN ĐÃ MỞ TỪ TRƯỚC, BẤM NEXT CHỈ VIỆC CHUYỂN BẢN ĐỒ
                    level_select_screen.selected_level = (level_select_screen.selected_level % MAX_LEVELS) + 1
                    game_board = Board(level_id=level_select_screen.selected_level)
                    show_win = False; is_winning = False; ai_solving = False; is_pickaxe_active = False; show_tutorial = True; win_popup.action = None
                    ai_paid_this_level = False; ai_paused_for_pickaxe = False; ai_animating_pickaxe = False
                elif win_popup.action == "REPLAY": 
                    game_board = Board(level_id=level_select_screen.selected_level)
                    show_win = False; is_winning = False; ai_solving = False; is_pickaxe_active = False; win_popup.action = None
                    ai_paid_this_level = False; ai_paused_for_pickaxe = False; ai_animating_pickaxe = False
            elif show_tutorial and tutorial_popup.action == "UNDERSTOOD": show_tutorial = False; tutorial_popup.action = None
            elif is_paused:
                if pause_menu.action == "RESTART": 
                    game_board = Board(level_id=level_select_screen.selected_level); is_paused = False; is_winning = False; ai_solving = False; is_pickaxe_active = False; pause_menu.action = None
                    ai_paid_this_level = False; ai_paused_for_pickaxe = False; ai_animating_pickaxe = False
                elif pause_menu.action == "AI_SOLVE":
                    if ai_paid_this_level:
                        ai_solving = True; is_paused = False; ai_paused_for_pickaxe = False; pause_menu.action = None
                    else:
                        if player_coins >= 100: 
                            player_coins -= 100; ai_paid_this_level = True
                            save_progress(unlocked_levels, player_coins, player_name, redeemed_codes, player_pickaxes)
                            ai_solving = True; is_paused = False; ai_paused_for_pickaxe = False; pause_menu.action = None
                        else:
                            try: pause_menu.error_msg = "KHÔNG ĐỦ 100 COIN!"; pause_menu.error_alpha = 255
                            except: pass
                            pause_menu.action = None
                            
                elif pause_menu.action == "EXIT": 
                    current_state = STATE_LEVEL_SELECT; is_paused = False; is_winning = False; ai_solving = False; is_pickaxe_active = False; pause_menu.action = None
                    ai_animating_pickaxe = False

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
            game_board.draw(screen); btn_options.draw(screen)
            
            font_coin_game = pygame.font.SysFont("tahoma", 30, bold=True)
            coin_text = f"COIN: {player_coins}"
            start_screen.draw_text_outline(screen, coin_text, font_coin_game, (255, 215, 0), (0,0,0), (WINDOW_WIDTH - 230, 45))
            
            start_x = 22; start_y = WINDOW_HEIGHT - 200
            for i in range(3):
                slot_rect = pygame.Rect(start_x, start_y + i*55, 42, 42)
                has_pickaxe = (3 - i) <= player_pickaxes 
                pygame.draw.rect(screen, (80, 80, 80) if has_pickaxe else (40, 40, 40), slot_rect, border_radius=8)
                border_color = (200, 200, 200)
                if has_pickaxe: border_color = (46, 204, 113) if (is_pickaxe_active and (3-i) == player_pickaxes) else (241, 196, 15)
                pygame.draw.rect(screen, border_color, slot_rect, width=2 if has_pickaxe else 1, border_radius=8)
                if has_pickaxe and img_pickaxe_ui: screen.blit(img_pickaxe_ui, (slot_rect.x + 1, slot_rect.y + 1))
            btn_buy_pickaxe.draw(screen)
            
            if is_pickaxe_active and img_pickaxe_cursor:
                screen.blit(img_pickaxe_cursor, (mouse_pos[0] + 15, mouse_pos[1] - 15))
                
            if ai_animating_pickaxe and img_pickaxe_cursor:
                screen.blit(img_pickaxe_cursor, (ai_pickaxe_current_pos[0] - 15, ai_pickaxe_current_pos[1] - 15))
            
            if game_notif_alpha > 0:
                font_notif_game = pygame.font.SysFont("tahoma", 36, bold=True)
                txt_surf = font_notif_game.render(game_notif, True, (231, 76, 60))
                txt_surf.set_alpha(game_notif_alpha)
                outline_surf = font_notif_game.render(game_notif, True, (0, 0, 0))
                outline_surf.set_alpha(game_notif_alpha)
                for dx, dy in [(-2,0), (2,0), (0,-2), (0,2)]: screen.blit(outline_surf, outline_surf.get_rect(center=(WINDOW_WIDTH//2 + dx, 120 + dy)))
                screen.blit(txt_surf, txt_surf.get_rect(center=(WINDOW_WIDTH//2, 120)))
                game_notif_alpha -= 3
            
            if ai_paid_this_level: pause_menu.btn_ai.text = "TIẾP TỤC AI (FREE)"
            else: pause_menu.btn_ai.text = "AI GIẢI (-100)"
                
            if show_win: win_popup.draw(screen)
            elif show_tutorial: tutorial_popup.draw(screen)
            elif is_paused: pause_menu.draw(screen)

        pygame.display.flip()
        clock.tick(FPS)
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()