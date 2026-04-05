import json
import os
import pygame
import sys
import random
import io
import heapq 
import math

from settings import *
from board import Board, Node
try:
    from hill_climbing import get_best_single_rotation
except ImportError:
    def get_best_single_rotation(board): return None 

from screens import StartScreen, DashboardScreen, LevelSelectScreen, ShopScreen, QuestsScreen, PauseMenu, TutorialPopup, WinPopup, Button, SkinScreen, CustomSetupScreen, STATE_CUSTOM_SETUP, get_en_font, TradePopup

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

SAVE_FILE = "save_data.json"


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
player_unlocked_bgs = ["DEFAULT"] 
custom_levels_data = {} # LƯU TRỮ MAP CUSTOM CỦA NGƯỜI CHƠI
player_unlocked_skins = ["DEFAULT"] # LƯU SKIN ĐÃ MUA
player_equipped_skin = "DEFAULT" # LƯU SKIN ĐANG DÙNG


def load_progress():
    global player_unlocked_bgs, custom_levels_data, player_unlocked_skins, player_equipped_skin
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                player_unlocked_bgs = data.get('unlocked_bgs', ["DEFAULT"])
                custom_levels_data = data.get('custom_levels', {})
                player_unlocked_skins = data.get('unlocked_skins', ["DEFAULT"])
                player_equipped_skin = data.get('equipped_skin', "DEFAULT")
                unlocked_levels = data.get('unlocked_levels', 1)
                coins = data.get('coins', 100)
                player_name = data.get('player_name', "")
                redeemed_codes = data.get('redeemed_codes', [])
                pickaxes = data.get('pickaxes', 3) 
                quest_data = normalize_quest_data(data.get('quest_data', {}), unlocked_levels) 
                return unlocked_levels, coins, player_name, redeemed_codes, pickaxes, quest_data
        except: pass
    return 1, 100, "", [], 3, build_default_quest_data(1)

def save_progress(level, coins, name, redeemed_codes, pickaxes, quest_data):
    global player_unlocked_bgs, custom_levels_data, player_unlocked_skins, player_equipped_skin
    data = {
        'unlocked_levels': level,
        'coins': coins,
        'player_name': name,
        'redeemed_codes': redeemed_codes,
        'pickaxes': pickaxes, 
        'quest_data': normalize_quest_data(quest_data, level), 
        'unlocked_bgs': player_unlocked_bgs,
        'custom_levels': custom_levels_data,
        'unlocked_skins': player_unlocked_skins,
        'equipped_skin': player_equipped_skin
    }
    with open(SAVE_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False)

unlocked_levels, global_coins, global_name, redeemed_codes, global_pickaxes, global_quest_data = load_progress()
MAX_LEVELS = 60

def main():
    global unlocked_levels, player_equipped_skin, player_unlocked_skins
    def reset_level_vars():
        nonlocal show_tutorial, is_paused, show_win, is_winning, is_pickaxe_active, ai_solving, game_bg
        nonlocal ai_paid_this_level, ai_paused_for_pickaxe, ai_animating_pickaxe
        nonlocal trades_remaining, trade_mode_active, show_trade_popup, trade_target_pos, hint_targets
        nonlocal moves_remaining, show_lose, is_losing # THÊM BIẾN LOSE
        
        show_tutorial = False; is_paused = False; show_win = False; is_winning = False; is_pickaxe_active = False
        show_lose = False; is_losing = False
        ai_paid_this_level = False; ai_paused_for_pickaxe = False; ai_animating_pickaxe = False; ai_solving = False
        trade_mode_active = False; show_trade_popup = False; trade_target_pos = None; hint_targets.clear()
        
        if level_select_screen.selected_act == 0:
            c_id = str(level_select_screen.selected_level - 1000)
            if c_id in custom_levels_data:
                trades_remaining = custom_levels_data[c_id].get("swaps", 0)
                moves_remaining = custom_levels_data[c_id].get("moves", -1)
                bg_name = custom_levels_data[c_id].get("bg", "DEFAULT")
                try: game_bg = pygame.transform.smoothscale(pygame.image.load(f"assets/images/bg_{bg_name.lower()}.jpg").convert(), (WINDOW_WIDTH, WINDOW_HEIGHT))
                except: 
                    try: game_bg = pygame.transform.smoothscale(pygame.image.load(f"assets/images/bg_{bg_name.lower()}.png").convert(), (WINDOW_WIDTH, WINDOW_HEIGHT))
                    except: game_bg = None
            else:
                trades_remaining = -1 if custom_setup_screen.swaps > 20 else custom_setup_screen.swaps 
                moves_remaining = -1 if custom_setup_screen.moves > 50 else custom_setup_screen.moves
        else:
            try: game_bg = pygame.transform.smoothscale(pygame.image.load(BG_GAME_PATH).convert(), (WINDOW_WIDTH, WINDOW_HEIGHT))
            except: game_bg = None
            diff = level_select_screen.selected_difficulty
            trades_remaining = -1 if diff == DIFF_EASY else (5 if diff == DIFF_NORMAL else 3)
            moves_remaining = -1 if diff == DIFF_EASY else (35 if diff == DIFF_NORMAL else 25) # Áp dụng luật Moves mới
            
    pygame.init()
    pygame.mixer.init()
    try:
        pygame.mixer.music.load("assets/sounds/bgsound.mp3") 
        pygame.mixer.music.set_volume(1.0)
        pygame.mixer.music.play(-1) 
    except pygame.error as e: pass
        
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
    quests_screen = QuestsScreen() 
    pause_menu = PauseMenu()
    tutorial_popup = TutorialPopup()
    win_popup = WinPopup()
    skin_screen = SkinScreen()
    
    try:
        img_pickaxe = pygame.image.load("assets/images/pickaxe.png").convert_alpha()
        img_pickaxe.set_colorkey((255, 255, 255)) 
        img_pickaxe_ui = pygame.transform.smoothscale(img_pickaxe, (40, 40))
        img_pickaxe_cursor = pygame.transform.smoothscale(img_pickaxe, (30, 30))
    except pygame.error as e: img_pickaxe_ui = None; img_pickaxe_cursor = None
    
    try: img_coin_ui = pygame.transform.smoothscale(pygame.image.load("assets/images/coin_icon.png").convert_alpha(), (30, 30))
    except: img_coin_ui = None

    btn_options = Button(WINDOW_WIDTH - 120, 20, 100, 50, "MENU", (50, 50, 50), (255, 255, 255))
    btn_buy_pickaxe = Button(75, WINDOW_HEIGHT - 120, 40, 40, "+", (46, 204, 113))
    btn_hint = Button(WINDOW_WIDTH - 200, WINDOW_HEIGHT - 80, 180, 50, "GOI Y", (230, 126, 34), font_size=24)
    btn_trade = Button(WINDOW_WIDTH - 200, WINDOW_HEIGHT - 140, 180, 50, "TRADE: OFF", (155, 89, 182), font_size=24)
    trade_popup = TradePopup()
    hint_targets = {} 
    
    trades_remaining = -1; moves_remaining = -1
    trade_mode_active = False; show_trade_popup = False; trade_target_pos = None 
    game_board = None; custom_setup_screen = CustomSetupScreen() 
    
    player_coins = global_coins; player_pickaxes = global_pickaxes
    import board
    board.CURRENT_SKIN_ID = player_equipped_skin
    player_name = ""; current_state = STATE_MENU_NAME
    quest_data = normalize_quest_data(global_quest_data, unlocked_levels)
    game_notif = ""; game_notif_alpha = 0; game_bg = None
    
    is_paused = False; show_tutorial = False; show_win = False; is_winning = False; win_timer = 0
    show_lose = False; is_losing = False
    ai_solving = False; ai_timer = 0; is_pickaxe_active = False 
    ai_paid_this_level = False; ai_paused_for_pickaxe = False; ai_animating_pickaxe = False
    ai_target_rock = None; ai_pickaxe_start_pos = (0, 0); ai_pickaxe_target_pos = (0, 0); ai_pickaxe_current_pos = [0, 0]; ai_pickaxe_progress = 0.0

    running = True
    while running:
        events = pygame.event.get()
        mouse_pos = pygame.mouse.get_pos()
        
        for event in events:
            if event.type == pygame.QUIT: running = False
            
            if current_state == STATE_MENU_NAME: start_screen.handle_event(event)
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
                        try: sound_coin.set_volume(dashboard_screen.sfx_vol); sound_coin.play()
                        except: pass
                    
            elif current_state == STATE_LEVEL_SELECT: 
                action = level_select_screen.handle_event(event, unlocked_levels, custom_levels_data)
                if action == "OPEN_CUSTOM_SETUP":
                    custom_id = level_select_screen.selected_level - 1000 
                    custom_setup_screen.load_level(custom_id)
                    current_state = STATE_CUSTOM_SETUP
                elif action == "PLAY_CUSTOM":
                    c_id = str(level_select_screen.selected_level - 1000)
                    game_board = Board(level_id=level_select_screen.selected_level, difficulty=DIFF_NORMAL, custom_data=custom_levels_data[c_id]) 
                    current_state = STATE_GAME_PLAY
                    reset_level_vars()
                    show_tutorial = True  
                    level_select_screen.next_state = None
                elif action and action.startswith("DELETE_CUSTOM_"):
                    idx = action.split("_")[-1]
                    if idx in custom_levels_data:
                        del custom_levels_data[idx]
                        save_progress(unlocked_levels, player_coins, player_name, redeemed_codes, player_pickaxes, quest_data)
                elif level_select_screen.next_state == STATE_GAME_PLAY:
                    game_board = Board(level_id=level_select_screen.selected_level, difficulty=level_select_screen.selected_difficulty) 
                    current_state = STATE_GAME_PLAY
                    reset_level_vars()
                    show_tutorial = True  
                    level_select_screen.next_state = None
                elif level_select_screen.next_state == STATE_DASHBOARD: 
                    current_state = STATE_DASHBOARD
                    level_select_screen.next_state = None

            elif current_state == STATE_SHOP: 
                action = shop_screen.handle_event(event, player_coins, player_pickaxes, unlocked_levels, player_unlocked_bgs)
                
                if action == "BUY_PICKAXE_1":
                    player_coins -= 100; player_pickaxes += 1
                    save_progress(unlocked_levels, player_coins, player_name, redeemed_codes, player_pickaxes, quest_data)
                    if sound_coin:
                        try: sound_coin.set_volume(dashboard_screen.sfx_vol); sound_coin.play()
                        except: pass
                elif action == "BUY_PICKAXE_3":
                    player_coins -= 250; player_pickaxes += 3 
                    save_progress(unlocked_levels, player_coins, player_name, redeemed_codes, player_pickaxes, quest_data)
                    if sound_coin:
                        try: sound_coin.set_volume(dashboard_screen.sfx_vol); sound_coin.play()
                        except: pass
                elif action and action.startswith("BUY_ACT_"):
                    act_num = int(action.split('_')[-1])
                    act_start_level = (act_num - 1) * 12 + 1
                    required_level = (act_num - 2) * 12 + 1 
                    if player_coins >= 1500 and unlocked_levels < act_start_level and unlocked_levels >= required_level:
                        player_coins -= 1500
                        unlocked_levels = act_start_level 
                        quest_data["stats"]["highest_unlocked_level"] = max(quest_data["stats"]["highest_unlocked_level"], unlocked_levels)
                        save_progress(unlocked_levels, player_coins, player_name, redeemed_codes, player_pickaxes, quest_data)
                        if sound_win:
                            try: sound_win.set_volume(dashboard_screen.sfx_vol); sound_win.play()
                            except: pass
                elif action and action.startswith("BUY_BG_"):
                    bg_name = action.split("BUY_BG_")[-1]
                    price = 500 if bg_name in ["FOREST", "DESERT"] else 800
                    if bg_name not in player_unlocked_bgs and player_coins >= price:
                        player_coins -= price
                        player_unlocked_bgs.append(bg_name)
                        save_progress(unlocked_levels, player_coins, player_name, redeemed_codes, player_pickaxes, quest_data)
                        if sound_coin:
                            try: sound_coin.set_volume(dashboard_screen.sfx_vol); sound_coin.play()
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
                            try: sound_coin.set_volume(dashboard_screen.sfx_vol); sound_coin.play()
                            except: pass

            elif current_state == STATE_SKIN: 
                # Truyền đủ dữ liệu để shop kiểm tra túi tiền và skin đã sở hữu
                skin_action = skin_screen.handle_event(event, player_coins, player_unlocked_skins, player_equipped_skin)
                if skin_action:
                    if skin_action.startswith("BUY_"):
                        s_id = skin_action.split("BUY_")[1]
                        # Mua skin đồng giá 1000 xu
                        if player_coins >= 1000:
                            player_coins -= 1000
                            player_unlocked_skins.append(s_id)
                            player_equipped_skin = s_id # Tự động trang bị sau khi mua
                            import board
                            board.CURRENT_SKIN_ID = player_equipped_skin
                            save_progress(unlocked_levels, player_coins, player_name, redeemed_codes, player_pickaxes, quest_data)
                            if sound_coin:
                                try: sound_coin.set_volume(dashboard_screen.sfx_vol); sound_coin.play()
                                except: pass
                        else:
                            # Không đủ tiền thì thông báo (tận dụng thông báo game có sẵn)
                            game_notif = "NOT ENOUGH COINS!"; game_notif_alpha = 255
                    
                    elif skin_action.startswith("EQUIP_"):
                        player_equipped_skin = skin_action.split("EQUIP_")[1]
                        import board
                        board.CURRENT_SKIN_ID = player_equipped_skin
                        save_progress(unlocked_levels, player_coins, player_name, redeemed_codes, player_pickaxes, quest_data)
                        if sound_button:
                            try: sound_button.set_volume(dashboard_screen.sfx_vol); sound_button.play()
                            except: pass
                
                if skin_screen.next_state == STATE_DASHBOARD:
                    current_state = STATE_DASHBOARD; skin_screen.next_state = None

            elif current_state == STATE_CUSTOM_SETUP: custom_setup_screen.handle_event(event, player_unlocked_bgs)

            elif current_state == STATE_GAME_PLAY:
                if show_win or show_lose: win_popup.handle_event(event)
                elif show_tutorial: tutorial_popup.handle_event(event)
                elif show_trade_popup:
                    t_action = trade_popup.handle_event(event)
                    if t_action == "CANCEL":
                        show_trade_popup = False; trade_mode_active = False
                    elif t_action: 
                        r, c = trade_target_pos
                        new_node = Node(r, c, t_action)
                        old_angle = game_board.grid[r][c].target_angle
                        new_node.angle = old_angle
                        new_node.target_angle = old_angle
                        rotations = (int(old_angle) // -90) % 4 
                        for _ in range(rotations): new_node.conns = [new_node.conns[-1]] + new_node.conns[:-1]
                        game_board.grid[r][c] = new_node
                        game_board.update_connectivity()
                        if trades_remaining > 0: trades_remaining -= 1
                        show_trade_popup = False; trade_mode_active = False
                        
                elif is_paused: pause_menu.handle_event(event)
                elif is_winning or is_losing: pass
                else:
                    btn_options.check_hover(mouse_pos)
                    btn_buy_pickaxe.is_enabled = (player_pickaxes < 9) 
                    btn_buy_pickaxe.check_hover(mouse_pos)
                    btn_hint.check_hover(mouse_pos)
                    
                    trade_txt = "INF" if trades_remaining == -1 else str(trades_remaining)
                    if trades_remaining == 0:
                        btn_trade.is_enabled = False; btn_trade.text = "TRADE: 0 (OFF)"; btn_trade.bg_color = (80, 80, 80)
                        trade_mode_active = False
                    else:
                        btn_trade.is_enabled = True
                        if trade_mode_active: btn_trade.text = f"TRADE: {trade_txt} (ON)"; btn_trade.bg_color = (46, 204, 113)
                        else: btn_trade.text = f"TRADE: {trade_txt} (OFF)"; btn_trade.bg_color = (155, 89, 182)
                    btn_trade.check_hover(mouse_pos)
                    
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button in [1, 3]:
                        is_left_click = (event.button == 1)
                        if is_left_click and btn_options.is_clicked(mouse_pos, pygame.mouse.get_pressed()):
                            is_paused = True; is_pickaxe_active = False; ai_paused_for_pickaxe = False; trade_mode_active = False
                        elif is_left_click and btn_buy_pickaxe.is_clicked(mouse_pos, pygame.mouse.get_pressed()):
                            if player_coins >= 100 and player_pickaxes < 9:
                                player_coins -= 100; player_pickaxes += 1
                                save_progress(unlocked_levels, player_coins, player_name, redeemed_codes, player_pickaxes, quest_data)
                                if ai_paused_for_pickaxe: ai_solving = True; ai_paused_for_pickaxe = False
                            else: game_notif = "NOT COINS OR BAG FULL!"; game_notif_alpha = 255
                        elif is_left_click and btn_hint.is_clicked(mouse_pos, pygame.mouse.get_pressed()):
                            moves_found = 0; temp_changes = {} 
                            for _ in range(3):
                                move = get_best_single_rotation(game_board)
                                if move:
                                    r, c, rotations = move
                                    if (r, c) not in temp_changes: temp_changes[(r, c)] = game_board.grid[r][c].conns.copy()
                                    for _ in range(rotations): game_board.grid[r][c].conns = [game_board.grid[r][c].conns[-1]] + game_board.grid[r][c].conns[:-1]
                                    hint_targets[(r, c)] = game_board.grid[r][c].conns.copy()
                                    game_board.update_connectivity()
                                    moves_found += 1
                                else: break
                            for (r, c), orig_conns in temp_changes.items(): game_board.grid[r][c].conns = orig_conns
                            game_board.update_connectivity()
                            if moves_found > 0: game_notif = f"HÃY XOAY {moves_found} Ô ĐANG NHẤP NHÁY!"; game_notif_alpha = 255
                            else: game_notif = "ĐÃ ĐI ĐÚNG ĐƯỜNG!"; game_notif_alpha = 255
                        elif is_left_click and btn_trade.is_clicked(mouse_pos, pygame.mouse.get_pressed()):
                            if trades_remaining != 0:
                                trade_mode_active = not trade_mode_active; is_pickaxe_active = False 
                        else:
                            pickaxe_area = pygame.Rect(18, WINDOW_HEIGHT - 500, 50, 430) 
                            if pickaxe_area.collidepoint(mouse_pos):
                                if player_pickaxes > 0 and is_left_click: 
                                    is_pickaxe_active = not is_pickaxe_active; trade_mode_active = False
                            else:
                                if is_pickaxe_active:
                                    if is_left_click and hasattr(game_board, 'break_rock') and game_board.break_rock(mouse_pos[0], mouse_pos[1]):
                                        player_pickaxes -= 1 
                                        save_progress(unlocked_levels, player_coins, player_name, redeemed_codes, player_pickaxes, quest_data)
                                    is_pickaxe_active = False; ai_solving = False; ai_paused_for_pickaxe = False
                                else:
                                    offset_x = (WINDOW_WIDTH - (game_board.cols * TILE_SIZE)) // 2
                                    offset_y = (WINDOW_HEIGHT - (game_board.rows * TILE_SIZE)) // 2
                                    c_col, c_row = (mouse_pos[0] - offset_x) // TILE_SIZE, (mouse_pos[1] - offset_y) // TILE_SIZE
                                    if trade_mode_active:
                                        if is_left_click and 0 <= c_row < game_board.rows and 0 <= c_col < game_board.cols:
                                            node = game_board.grid[c_row][c_col]
                                            if getattr(node, 'is_fixed', False) or getattr(node, 'is_rock', False) or node.pipe_type == 'P':
                                                game_notif = "CANNOT TRADE THIS PIPE!"; game_notif_alpha = 255
                                            else:
                                                trade_target_pos = (c_row, c_col); show_trade_popup = True
                                    else:
                                        if game_board.handle_click(mouse_pos[0], mouse_pos[1], is_left_click):
                                            if moves_remaining > 0: moves_remaining -= 1
                                        if (c_row, c_col) in hint_targets and game_board.grid[c_row][c_col].conns == hint_targets[(c_row, c_col)]:
                                            del hint_targets[(c_row, c_col)]
                                        if sound_button:
                                            try: sound_button.set_volume(dashboard_screen.sfx_vol); sound_button.play()
                                            except: pass
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                        is_paused = True; is_pickaxe_active = False; ai_paused_for_pickaxe = False; trade_mode_active = False

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
                                    game_notif = "NO PICKAXES! Buy More!"
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

            if not show_win and not show_lose and not show_tutorial and not is_paused and not is_winning and not is_losing:
                if game_board.check_win():
                    is_winning = True; win_timer = pygame.time.get_ticks(); win_popup.is_win = True
                    
                    # LOGIC THƯỞNG GIỜ ĐÃ NẰM ĐÚNG BÊN DƯỚI ĐIỀU KIỆN THẮNG
                    if level_select_screen.selected_act == 0:
                        # CHẾ ĐỘ CUSTOM: KHÔNG THƯỞNG COIN
                        earned = 0
                        win_popup.earned_coins = earned 
                        if sound_win:
                            try: sound_win.set_volume(dashboard_screen.sfx_vol)
                            except: pass
                            sound_win.play()
                    else:
                        # TĂNG TIẾN TIỀN THƯỞNG THEO ĐỘ KHÓ
                        if level_select_screen.selected_difficulty == DIFF_EASY:
                            earned = random.randint(500, 800)
                        elif level_select_screen.selected_difficulty == DIFF_NORMAL:
                            earned = random.randint(1000, 1500)
                        else: # DIFF_HARD
                            earned = random.randint(2000, 3000)
                            
                        player_coins += earned
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
                            
                        if level_select_screen.selected_level == unlocked_levels and unlocked_levels < MAX_LEVELS:
                            unlocked_levels += 1
                            quest_data["stats"]["highest_unlocked_level"] = max(quest_data["stats"]["highest_unlocked_level"], unlocked_levels)
                        
                        win_popup.earned_coins = earned 
                        save_progress(unlocked_levels, player_coins, player_name, redeemed_codes, player_pickaxes, quest_data)

                # NẾU MOVES VỀ 0 THÌ GAME OVER (Lệnh này phải nằm riêng biệt)
                elif moves_remaining == 0:
                    is_losing = True; win_timer = pygame.time.get_ticks(); win_popup.is_win = False
                    
            if is_winning or is_losing:
                current_time = pygame.time.get_ticks()
                if current_time - win_timer >= 1000: 
                    if is_winning: show_win = True; is_winning = False 
                    if is_losing: show_lose = True; is_losing = False 

        if current_state == STATE_MENU_NAME and start_screen.next_state == STATE_DASHBOARD:
            player_name = start_screen.player_name; current_state = STATE_DASHBOARD
            start_screen.next_state = STATE_MENU_NAME 
            save_progress(unlocked_levels, player_coins, player_name, redeemed_codes, player_pickaxes, quest_data)
        elif current_state == STATE_DASHBOARD and dashboard_screen.next_state is not None:
            current_state = dashboard_screen.next_state; dashboard_screen.next_state = None 
        elif current_state == STATE_LEVEL_SELECT:
            if level_select_screen.next_state == STATE_GAME_PLAY:
                game_board = Board(level_id=level_select_screen.selected_level, difficulty=level_select_screen.selected_difficulty) 
                current_state = STATE_GAME_PLAY
                reset_level_vars() # GỌI HÀM RESET Ở ĐÂY
                show_tutorial = True  
                level_select_screen.next_state = None
            elif level_select_screen.next_state == STATE_DASHBOARD: current_state = STATE_DASHBOARD; level_select_screen.next_state = None
        elif current_state == STATE_SKIN and skin_screen.next_state == STATE_DASHBOARD: current_state = STATE_DASHBOARD; skin_screen.next_state = None
        elif current_state == STATE_SHOP and shop_screen.next_state == STATE_DASHBOARD: current_state = STATE_DASHBOARD; shop_screen.next_state = None
        elif current_state == STATE_QUESTS and quests_screen.next_state == STATE_DASHBOARD: current_state = STATE_DASHBOARD; quests_screen.next_state = None
                
        elif current_state == STATE_GAME_PLAY:
            if show_win or show_lose:
                if win_popup.action == "MENU": 
                    current_state = STATE_LEVEL_SELECT
                    show_win = False; show_lose = False; is_winning = False; is_losing = False; ai_solving = False; win_popup.action = None
                    ai_animating_pickaxe = False
                elif win_popup.action == "NEXT":
                    level_select_screen.selected_level = (level_select_screen.selected_level % MAX_LEVELS) + 1
                    game_board = Board(level_id=level_select_screen.selected_level, difficulty=level_select_screen.selected_difficulty)
                    reset_level_vars()
                    show_tutorial = True
                    win_popup.action = None
                elif win_popup.action == "REPLAY": 
                    quest_data["stats"]["replays_used"] += 1
                    # Hỗ trợ reset cho cả map Custom
                    if level_select_screen.selected_act == 0:
                        c_id = str(custom_setup_screen.custom_id)
                        game_board = Board(level_id=1000 + custom_setup_screen.custom_id, difficulty=DIFF_NORMAL, custom_data=custom_levels_data.get(c_id))
                    else:
                        game_board = Board(level_id=level_select_screen.selected_level, difficulty=level_select_screen.selected_difficulty)
                    reset_level_vars()
                    win_popup.action = None
                elif win_popup.action == "BUY_MOVES":
                    if player_coins >= 100: # KIỂM TRA ĐỦ 100 COIN
                        player_coins -= 100
                        moves_remaining += 5 # Bơm thêm 5 lượt
                        show_lose = False; is_losing = False # Tắt bảng Game Over, hồi sinh game
                        win_popup.action = None
                        save_progress(unlocked_levels, player_coins, player_name, redeemed_codes, player_pickaxes, quest_data)
                        if sound_coin:
                            try: sound_coin.set_volume(dashboard_screen.sfx_vol); sound_coin.play()
                            except: pass
                    else:
                        game_notif = "NOT ENOUGH COINS!" # Không đủ tiền thì hiện thông báo
                        game_notif_alpha = 255
                        win_popup.action = None
            elif show_tutorial and tutorial_popup.action == "UNDERSTOOD": 
                show_tutorial = False; tutorial_popup.action = None
            elif is_paused:
                if pause_menu.action == "RESTART": 
                    game_board = Board(level_id=level_select_screen.selected_level, difficulty=level_select_screen.selected_difficulty)
                    reset_level_vars()
                    pause_menu.action = None
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
        elif current_state == STATE_CUSTOM_SETUP:
            custom_setup_screen.draw(screen, player_unlocked_bgs)
            if custom_setup_screen.next_state == STATE_LEVEL_SELECT:
                current_state = STATE_LEVEL_SELECT
                custom_setup_screen.next_state = None
            elif custom_setup_screen.next_state == STATE_GAME_PLAY:
                c_id = str(custom_setup_screen.custom_id) 
                swaps_val = -1 if custom_setup_screen.swaps > 20 else custom_setup_screen.swaps
                moves_val = -1 if custom_setup_screen.moves > 50 else custom_setup_screen.moves # ĐÃ FIX: LƯU MAX MOVES VÀO BỘ NHỚ
                
                custom_levels_data[c_id] = {
                    "rocks": custom_setup_screen.rocks,
                    "bg": custom_setup_screen.bgs[custom_setup_screen.bg_idx],
                    "swaps": swaps_val, 
                    "moves": moves_val, # GHI DỮ LIỆU MOVES XUỐNG FILE
                    "size": custom_setup_screen.sizes[custom_setup_screen.size_idx],
                    "pipes": [p for p, active in custom_setup_screen.pipe_active.items() if active]
                }
                save_progress(unlocked_levels, player_coins, player_name, redeemed_codes, player_pickaxes, quest_data)
                
                game_board = Board(level_id=1000 + custom_setup_screen.custom_id, difficulty=DIFF_NORMAL, custom_data=custom_levels_data[c_id]) 
                current_state = STATE_GAME_PLAY
                reset_level_vars() 
                show_tutorial = True
                custom_setup_screen.next_state = None


        elif current_state == STATE_CUSTOM_SETUP:
            custom_setup_screen.draw(screen, player_unlocked_bgs)
            if custom_setup_screen.next_state == STATE_LEVEL_SELECT:
                current_state = STATE_LEVEL_SELECT
                custom_setup_screen.next_state = None
            elif custom_setup_screen.next_state == STATE_GAME_PLAY:
                # 1. Lưu cấu hình sếp vừa tạo vào bộ nhớ
                swaps_val = -1 if custom_setup_screen.swaps > 20 else custom_setup_screen.swaps
                custom_levels_data[c_id] = {
                    "rocks": custom_setup_screen.rocks,
                    "bg": custom_setup_screen.bgs[custom_setup_screen.bg_idx],
                    "swaps": swaps_val, 
                    "size": custom_setup_screen.sizes[custom_setup_screen.size_idx], # LƯU KÍCH THƯỚC BÀN CỜ
                    "pipes": [p for p, active in custom_setup_screen.pipe_active.items() if active]
                }
                save_progress(unlocked_levels, player_coins, player_name, redeemed_codes, player_pickaxes, quest_data)
                
                # 2. Tạo màn chơi và đưa sếp vào game
                game_board = Board(level_id=1000 + custom_setup_screen.custom_id, difficulty=DIFF_NORMAL, custom_data=custom_levels_data[c_id]) 
                current_state = STATE_GAME_PLAY
                reset_level_vars() 
                show_tutorial = True
                custom_setup_screen.next_state = None

        elif current_state == STATE_SHOP: 
            shop_screen.draw(screen, player_coins, player_pickaxes, player_unlocked_bgs)
        elif current_state == STATE_QUESTS: quests_screen.draw(screen, quest_data)
        elif current_state == STATE_SKIN: skin_screen.draw(screen, player_coins, player_unlocked_skins, player_equipped_skin)
        elif current_state == STATE_GAME_PLAY and game_board:
            if game_bg: screen.blit(game_bg, (0, 0))
            else: screen.fill(BG_COLOR)
            
            # Phải có 4 dòng này thì bàn cờ và nút mới hiện lên
            game_board.draw(screen)
            btn_options.draw(screen)
            btn_hint.draw(screen)
            btn_trade.draw(screen)

            # HIỂN THỊ ĐẾM NGƯỢC SỐ LẦN XOAY SAI MÉP TRÊN
            if moves_remaining != -1: txt_m = f"MOVES LEFT: {moves_remaining}"; col_m = (231, 76, 60) if moves_remaining <= 3 else (255, 255, 255)
            else: txt_m = "MOVES LEFT: INF"; col_m = (0, 255, 255)
            start_screen.draw_text_outline(screen, txt_m, get_en_font(32), col_m, (0,0,0), (WINDOW_WIDTH//2, 25))

            if hint_targets:
                glow_alpha = int(100 + 155 * abs(math.sin(pygame.time.get_ticks() / 200)))
                holo_surf = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
                pygame.draw.rect(holo_surf, (255, 0, 255, glow_alpha), holo_surf.get_rect(), 4, border_radius=5)
                pygame.draw.rect(holo_surf, (255, 0, 255, glow_alpha//4), holo_surf.get_rect(), border_radius=5)
                
                offset_x = (WINDOW_WIDTH - (game_board.cols * TILE_SIZE)) // 2
                offset_y = (WINDOW_HEIGHT - (game_board.rows * TILE_SIZE)) // 2
                
                # Duyệt qua toàn bộ danh sách các ô gợi ý và vẽ
                for (r, c) in hint_targets.keys():
                    x = offset_x + c * TILE_SIZE
                    y = offset_y + r * TILE_SIZE
                    screen.blit(holo_surf, (x, y))
            
            # Hiển thị Tiền tối giản: Chỉ chữ + COINS, không nền, không logo
            font_coins_game = get_en_font(32) # Dùng font Pixel cho đồng bộ
            # Vẽ ở tọa độ (25, 25) để sát góc trái trên
            start_screen.draw_text_outline(screen, f"{player_coins} COINS", font_coins_game, (241, 196, 15), (0,0,0), (25, 25), align="topleft")
            
            # VẼ CỘT DỌC 9 Ô CUỐC HƯỚNG LÊN TRÊN
            start_x = 22
            start_y = WINDOW_HEIGHT - 120 # Tọa độ Y của ô cuốc dưới cùng
            max_pickaxes = 9
            
            for i in range(max_pickaxes):
                slot_rect = pygame.Rect(start_x, start_y - i * 45, 42, 42)
                has_pickaxe = i < player_pickaxes 
                
                # 1. Tạo và vẽ nền TRẮNG MỜ
                slot_bg = pygame.Surface((42, 42), pygame.SRCALPHA)
                pygame.draw.rect(slot_bg, (255, 255, 255, 60), slot_bg.get_rect(), border_radius=8)
                screen.blit(slot_bg, slot_rect.topleft)
                
                # 2. Xử lý màu viền
                border_color = (200, 200, 200) 
                if has_pickaxe: 
                    # Nếu đang chọn cúp (Active) thì viền Xanh lá, ngược lại viền Vàng
                    border_color = (46, 204, 113) if (is_pickaxe_active and i == player_pickaxes - 1) else (241, 196, 15)
                
                # 3. Vẽ viền ô cúp lên trên lớp nền mờ
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
            
            if ai_paid_this_level: pause_menu.btn_ai.text = "Resume AI"
            else: pause_menu.btn_ai.text = "AI Support"
                
            # Đoạn này dùng để vẽ các bảng thông báo đè lên trên bàn cờ
            if show_win or show_lose: win_popup.draw(screen)
            elif show_tutorial: tutorial_popup.draw(screen)
            elif show_trade_popup: trade_popup.draw(screen)
            elif is_paused: pause_menu.draw(screen)

        pygame.display.flip()
        clock.tick(FPS)
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()