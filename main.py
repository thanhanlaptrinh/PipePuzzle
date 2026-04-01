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

# =================================================================
# AI TÌM ĐÁ TỐI ƯU (Của Sếp)
# =================================================================
def find_optimal_rock_to_break(board):
    rows, cols = board.rows, board.cols
    distances = { (r, c): float('inf') for r in range(rows) for c in range(cols) }
    pq = []
    came_from = {}
    
    for r in range(rows):
        for c in range(cols):
            if board.grid[r][c].is_powered:
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
                weight = 1 if board.grid[nr][nc].is_rock else 0
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
        if board.grid[r][c].is_rock:
            return board.grid[r][c]
    return None

# =================================================================
# HỆ THỐNG NHIỆM VỤ MỚI (Của nhánh UI3)
# =================================================================
def build_default_quest_data(current_unlocked=1):
    quest_stats = QUEST_STAT_DEFAULTS.copy()
    quest_stats["highest_unlocked_level"] = max(1, int(current_unlocked))
    return {"stats": quest_stats, "claimed": []}

def normalize_quest_data(quest_data, current_unlocked=1):
    if not isinstance(quest_data, dict):
        return build_default_quest_data(current_unlocked)

    stats = quest_data.get("stats", {})
    if not isinstance(stats, dict):
        stats = {}

    fixed_stats = QUEST_STAT_DEFAULTS.copy()
    for key in fixed_stats:
        try:
            fixed_stats[key] = int(stats.get(key, fixed_stats[key]))
        except (TypeError, ValueError):
            pass

    fixed_stats["highest_unlocked_level"] = max(
        fixed_stats["highest_unlocked_level"], int(current_unlocked)
    )

    claimed = quest_data.get("claimed", [])
    if not isinstance(claimed, list):
        claimed = []

    valid_ids = {quest["id"] for quest in QUEST_DEFINITIONS}
    claimed = [qid for qid in claimed if qid in valid_ids]

    return {"stats": fixed_stats, "claimed": claimed}

def get_quest_by_id(quest_id):
    for quest in QUEST_DEFINITIONS:
        if quest["id"] == quest_id:
            return quest
    return None

def is_quest_completed(quest_data, quest):
    metric = quest["metric"]
    progress = int(quest_data["stats"].get(metric, 0))
    return progress >= int(quest["target"])

def claim_quest_reward(quest_data, quest_id):
    if quest_id in quest_data["claimed"]:
        return 0
    quest = get_quest_by_id(quest_id)
    if not quest:
        return 0
    if not is_quest_completed(quest_data, quest):
        return 0
    quest_data["claimed"].append(quest_id)
    return int(quest["reward"])

# =================================================================
# DUNG HỢP FILE LƯU TRỮ (Gộp Cuốc và Nhiệm vụ)
# =================================================================
def load_progress():
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                unlocked_levels = data.get('unlocked_levels', 1)
                coins = data.get('coins', 100)
                player_name = data.get('player_name', "")
                redeemed_codes = data.get('redeemed_codes', [])
                pickaxes = data.get('pickaxes', 3) # Của Sếp
                quest_data = normalize_quest_data(data.get('quest_data', {}), unlocked_levels) # Của UI3
                return unlocked_levels, coins, player_name, redeemed_codes, pickaxes, quest_data
        except: pass
    return 1, 100, "", [], 3, build_default_quest_data(1)

def save_progress(level, coins, name, redeemed_codes, pickaxes, quest_data):
    data = {
        'unlocked_levels': level,
        'coins': coins,
        'player_name': name,
        'redeemed_codes': redeemed_codes,
        'pickaxes': pickaxes, # Của Sếp
        'quest_data': normalize_quest_data(quest_data, level) # Của UI3
    }
    with open(SAVE_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False)

unlocked_levels, global_coins, global_name, redeemed_codes, global_pickaxes, global_quest_data = load_progress()
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
    quests_screen = QuestsScreen() # Đã gọi UI mới của bạn Sếp
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
        img_pickaxe_ui = None
        img_pickaxe_cursor = None
    try:
        img_coin_ui = pygame.image.load("assets/images/coin_icon.png").convert_alpha()
        img_coin_ui = pygame.transform.smoothscale(img_coin_ui, (30, 30))
    except: img_coin_ui = None

    btn_options = Button(WINDOW_WIDTH - 120, 20, 100, 50, "MENU", (50, 50, 50), (255, 255, 255))
    btn_buy_pickaxe = Button(75, WINDOW_HEIGHT - 120, 40, 40, "+", (46, 204, 113))
    
    game_board = None
    player_coins = global_coins; player_pickaxes = global_pickaxes
    player_name = ""
    current_state = STATE_MENU_NAME
    quest_data = normalize_quest_data(global_quest_data, unlocked_levels)
    
    game_notif = ""
    game_notif_alpha = 0
    
    try:
        raw_game_bg = pygame.image.load(BG_GAME_PATH).convert()
        game_bg = pygame.transform.smoothscale(raw_game_bg, (WINDOW_WIDTH, WINDOW_HEIGHT))
    except pygame.error as e: game_bg = None
    
    is_paused = False
    show_tutorial = False; show_win = False; is_winning = False 
    win_timer = 0; ai_solving = False
    ai_timer = 0; is_pickaxe_active = False 
    
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
                    quest_data["stats"]["highest_unlocked_level"] = max(quest_data["stats"]["highest_unlocked_level"], unlocked_levels)
                    save_progress(unlocked_levels, player_coins, player_name, redeemed_codes, player_pickaxes, quest_data)
                elif action == "ADD_COINS":
                    player_coins += 10000 
                    if "PIPEGOLD" not in redeemed_codes: redeemed_codes.append("PIPEGOLD")
                    save_progress(unlocked_levels, player_coins, player_name, redeemed_codes, player_pickaxes, quest_data)
                    if sound_coin:
                        try: sound_coin.set_volume(dashboard_screen.sfx_vol)
                        except: pass
                        sound_coin.play()
                    
            elif current_state == STATE_LEVEL_SELECT: level_select_screen.handle_event(event, unlocked_levels)
            elif current_state == STATE_SHOP: 
                action = shop_screen.handle_event(event, player_coins, player_pickaxes, unlocked_levels)
                if action == "BUY_PICKAXE_1":
                    player_coins -= 100; player_pickaxes += 1
                    save_progress(unlocked_levels, player_coins, player_name, redeemed_codes, player_pickaxes, quest_data)
                    if sound_coin:
                        try: sound_coin.set_volume(dashboard_screen.sfx_vol); sound_coin.play()
                        except: pass
                elif action == "BUY_PICKAXE_3":
                    player_coins -= 250; player_pickaxes += 3 # Sửa thành += 3 để cộng thêm vào số cuốc hiện có
                    save_progress(unlocked_levels, player_coins, player_name, redeemed_codes, player_pickaxes, quest_data)
                    if sound_coin:
                        try: sound_coin.set_volume(dashboard_screen.sfx_vol); sound_coin.play()
                        except: pass
                elif action and action.startswith("BUY_ACT_"):
                    act_num = int(action.split('_')[-1])
                    act_start_level = (act_num - 1) * 12 + 1
                    required_level = (act_num - 2) * 12 + 1 # Cấp độ yêu cầu của Act trước
                    
                    if player_coins >= 1500 and unlocked_levels < act_start_level and unlocked_levels >= required_level:
                        player_coins -= 1500
                        unlocked_levels = act_start_level 
                        
                        # Đồng bộ luôn nhiệm vụ "Phá đảo Act" cho chắc
                        quest_data["stats"]["highest_unlocked_level"] = max(quest_data["stats"]["highest_unlocked_level"], unlocked_levels)
                        
                        save_progress(unlocked_levels, player_coins, player_name, redeemed_codes, player_pickaxes, quest_data)
                        if sound_win:
                            try: sound_win.set_volume(dashboard_screen.sfx_vol); sound_win.play()
                            except: pass

            elif current_state == STATE_QUESTS:
                quests_action = quests_screen.handle_event(event, quest_data)
                if quests_action and quests_action[0] == "CLAIM_QUEST":
                    reward = claim_quest_reward(quest_data, quests_action[1])
                    if reward > 0:
                        player_coins += reward
                        try: quests_screen.add_notification(f"+{reward} COIN", (255, 215, 0))
                        except: pass
                        save_progress(unlocked_levels, player_coins, player_name, redeemed_codes, player_pickaxes, quest_data)
                        if sound_coin:
                            try: sound_coin.set_volume(dashboard_screen.sfx_vol)
                            except: pass
                            sound_coin.play()

            elif current_state == STATE_SKIN: skin_screen.handle_event(event)

            elif current_state == STATE_GAME_PLAY:
                if show_win: win_popup.handle_event(event)
                elif show_tutorial: tutorial_popup.handle_event(event)
                elif is_paused: pause_menu.handle_event(event)
                elif is_winning: pass
                else:
                    btn_options.check_hover(mouse_pos)
                    btn_buy_pickaxe.is_enabled = (player_pickaxes < 9) 
                    btn_buy_pickaxe.check_hover(mouse_pos)
                    
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        if btn_options.is_clicked(mouse_pos, pygame.mouse.get_pressed()):
                            is_paused = True; is_pickaxe_active = False; ai_paused_for_pickaxe = False
                        elif btn_buy_pickaxe.is_clicked(mouse_pos, pygame.mouse.get_pressed()):
                            if player_coins >= 100 and player_pickaxes < 9: # Sửa thành 9
                                player_coins -= 100; player_pickaxes += 1
                                save_progress(unlocked_levels, player_coins, player_name, redeemed_codes, player_pickaxes, quest_data)
                                if ai_paused_for_pickaxe:
                                    ai_solving = True; ai_paused_for_pickaxe = False
                            else:
                                game_notif = "KHÔNG ĐỦ XU HOẶC TÚI ĐÃ ĐẦY!"; game_notif_alpha = 255
                        else:
                            # Vùng click bao trọn cột dọc 9 ô cuốc (rộng 50px, kéo dài lên trên)
                            pickaxe_area = pygame.Rect(18, WINDOW_HEIGHT - 500, 50, 430) 
                            
                            if pickaxe_area.collidepoint(mouse_pos):
                                if player_pickaxes > 0: is_pickaxe_active = not is_pickaxe_active  
                            else:
                                if is_pickaxe_active:
                                    if hasattr(game_board, 'break_rock'):
                                        if game_board.break_rock(mouse_pos[0], mouse_pos[1]):
                                            player_pickaxes -= 1 
                                            save_progress(unlocked_levels, player_coins, player_name, redeemed_codes, player_pickaxes, quest_data)
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
                    ai_target_rock.break_rock() 
                    player_pickaxes -= 1
                    game_board.update_connectivity()
                    save_progress(unlocked_levels, player_coins, player_name, redeemed_codes, player_pickaxes, quest_data)
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
                            if node_ai.is_rock or node_ai.is_fixed:
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
                            # TÌM VIÊN ĐÁ TỐI ƯU TRÊN ĐƯỜNG NGẮN NHẤT
                            target_rock = None
                            best_rock_score = -9999
                            
                            # Lấy tọa độ tất cả các ô đang có nước
                            powered_nodes = [(r, c) for r in range(game_board.rows) for c in range(game_board.cols) if game_board.grid[r][c].is_powered]
                            
                            if powered_nodes:
                                for r in range(game_board.rows):
                                    for c in range(game_board.cols):
                                        if game_board.grid[r][c].is_rock:
                                            # Tính khoảng cách đến đích
                                            dist_to_end = abs(r - (game_board.rows - 1)) + abs(c - (game_board.cols - 1))
                                            # Tính khoảng cách đến dòng nước gần nhất
                                            min_dist_to_water = min([abs(r - pr) + abs(c - pc) for pr, pc in powered_nodes])
                                            
                                            # Chỉ nhắm vào đá nằm quanh khu vực nước (bán kính 3 ô)
                                            if min_dist_to_water <= 3:
                                                # Điểm = Trừ khoảng cách đến đích (ưu tiên gần đích) - Khoảng cách đến nước
                                                rock_score = -dist_to_end - (min_dist_to_water * 2)
                                                if rock_score > best_rock_score:
                                                    best_rock_score = rock_score
                                                    target_rock = game_board.grid[r][c]

                            if target_rock:
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
                                    ai_solving = False
                                    ai_paused_for_pickaxe = True
                                    game_notif = "HẾT CUỐC! MUA THÊM CUỐC ĐỂ AI PHÁ ĐÁ!"
                                    game_notif_alpha = 255
                            else:
                                # NẾU KHÔNG CÓ ĐÁ NÀO QUANH ĐÓ -> XOAY BỪA ĐỂ TÌM HƯỚNG MỚI
                                unfixed_nodes = [(r, c) for r in range(game_board.rows) for c in range(game_board.cols)
                                                 if not game_board.grid[r][c].is_fixed and not game_board.grid[r][c].is_rock]
                                if unfixed_nodes:
                                    rand_r, rand_c = random.choice(unfixed_nodes)
                                    game_board.grid[rand_r][rand_c].rotate()
                                    game_board.update_connectivity()
                                    ai_timer = current_time
                                else:
                                    ai_solving = False

            if not show_win and not show_tutorial and not is_paused and not is_winning:
                if game_board.check_win():
                    is_winning = True; win_timer = pygame.time.get_ticks() 
                    earned = random.randint(1000, 1500); player_coins += earned
                    
                    quest_data["stats"]["levels_completed"] += 1
                    quest_data["stats"]["total_coins_earned"] += earned

                    if sound_coin:
                        try: sound_coin.set_volume(dashboard_screen.sfx_vol)
                        except: pass
                        sound_coin.play()
                    if sound_win:
                        try: sound_win.set_volume(dashboard_screen.sfx_vol)
                        except: pass
                        sound_win.play()
                        
                    win_popup.earned_coins = earned 
                    
                    if level_select_screen.selected_level == unlocked_levels and unlocked_levels < MAX_LEVELS:
                        unlocked_levels += 1
                        quest_data["stats"]["highest_unlocked_level"] = max(quest_data["stats"]["highest_unlocked_level"], unlocked_levels)
                    
                    save_progress(unlocked_levels, player_coins, player_name, redeemed_codes, player_pickaxes, quest_data)
                    
            if is_winning:
                current_time = pygame.time.get_ticks()
                if current_time - win_timer >= 2000: show_win = True; is_winning = False 

        if current_state == STATE_MENU_NAME and start_screen.next_state == STATE_DASHBOARD:
            player_name = start_screen.player_name; current_state = STATE_DASHBOARD
            start_screen.next_state = STATE_MENU_NAME 
            save_progress(unlocked_levels, player_coins, player_name, redeemed_codes, player_pickaxes, quest_data)
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
                    level_select_screen.selected_level = (level_select_screen.selected_level % MAX_LEVELS) + 1
                    game_board = Board(level_id=level_select_screen.selected_level)
                    show_win = False; is_winning = False; ai_solving = False; is_pickaxe_active = False; show_tutorial = True; win_popup.action = None
                    ai_paid_this_level = False; ai_paused_for_pickaxe = False; ai_animating_pickaxe = False
                elif win_popup.action == "REPLAY": 
                    quest_data["stats"]["replays_used"] += 1
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
                            quest_data["stats"]["ai_solves_used"] += 1
                            save_progress(unlocked_levels, player_coins, player_name, redeemed_codes, player_pickaxes, quest_data)
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
        elif current_state == STATE_SHOP: shop_screen.draw(screen, player_coins, player_pickaxes)
        elif current_state == STATE_QUESTS: quests_screen.draw(screen, quest_data)
        elif current_state == STATE_SKIN: skin_screen.draw(screen)
        elif current_state == STATE_GAME_PLAY and game_board:
            if game_bg: screen.blit(game_bg, (0, 0))
            else: screen.fill(BG_COLOR)
            game_board.draw(screen); btn_options.draw(screen)
            
            box_xu_rect = pygame.Rect(20, 20, 180, 45)
            pygame.draw.rect(screen, (255, 255, 255), box_xu_rect, border_radius=10)
            pygame.draw.rect(screen, (200, 200, 200), box_xu_rect, 2, border_radius=10)
            
            if img_coin_ui: 
                screen.blit(img_coin_ui, (box_xu_rect.x + 10, box_xu_rect.y + 7))
                
            font_coin_game = pygame.font.SysFont("tahoma", 24, bold=True)
            start_screen.draw_text_outline(screen, f"{player_coins} XU", font_coin_game, (241, 196, 15), (0,0,0), (box_xu_rect.x + 105, box_xu_rect.centery))
            
            # VẼ CỘT DỌC 9 Ô CUỐC HƯỚNG LÊN TRÊN
            start_x = 22
            start_y = WINDOW_HEIGHT - 120 # Tọa độ Y của ô cuốc dưới cùng
            max_pickaxes = 9
            
            for i in range(max_pickaxes):
                slot_rect = pygame.Rect(start_x, start_y - i * 45, 42, 42)
                has_pickaxe = i < player_pickaxes 
                
                pygame.draw.rect(screen, (80, 80, 80) if has_pickaxe else (40, 40, 40), slot_rect, border_radius=8)
                
                border_color = (200, 200, 200)
                if has_pickaxe: 
                    border_color = (46, 204, 113) if (is_pickaxe_active and i == player_pickaxes - 1) else (241, 196, 15)
                
                pygame.draw.rect(screen, border_color, slot_rect, width=2 if has_pickaxe else 1, border_radius=8)
                if has_pickaxe and img_pickaxe_ui: 
                    screen.blit(img_pickaxe_ui, (slot_rect.x + 1, slot_rect.y + 1))
                    
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