import pygame
import random
from settings import *

pygame.mixer.init()
try: sound_button = pygame.mixer.Sound("assets/sounds/button.mp3")
except: sound_button = None

# --- MÀU SẮC CYBERPUNK ---
COLOR_BG_DARK = (15, 10, 25)
COLOR_PANEL = (25, 20, 40)
COLOR_GLOW_BLUE = (0, 255, 255)
COLOR_GLOW_YELLOW = (255, 255, 0)
COLOR_PURCHASE = (231, 76, 60) 
COLOR_TEXT_MAIN = (255, 255, 255)
COLOR_TEXT_DESC = (180, 180, 200)

# KHAI BÁO TOÀN CỤC ĐỂ KHÔNG BỊ LỖI NAMEERROR
C_BRIGHT_CYAN = (0, 190, 255)
C_BRIGHT_GOLD = (255, 180, 0)
C_BRIGHT_GREEN = (50, 220, 110)
C_BRIGHT_SLATE = (160, 180, 200)
COLOR_GLOW_BLUE = (0, 255, 255)
COLOR_GLOW_YELLOW = (255, 255, 0)
COLOR_SHOP_PANEL = (20, 15, 30)
COLOR_GLOW_GOLD = (212, 175, 55)

# ==========================================
# HÀM TẢI FONT ĐỘNG (PIXEL & TIMES NEW ROMAN)
# ==========================================
def get_en_font(size):
    try:
        return pygame.font.Font("assets/fonts/pixel.ttf", size)
    except:
        return pygame.font.SysFont('impact', size)

def get_vn_font(size, bold=False):
    return pygame.font.SysFont('timesnewroman', size, bold=bold)


class Button:
    def __init__(self, x, y, w, h, text, bg_color, text_color=(255, 255, 255), disable_hover_effect=False, font_size=30, is_vn=False):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.bg_color = bg_color
        self.text_color = text_color
        self.is_hovered = False
        self.is_enabled = True
        self.disable_hover_effect = disable_hover_effect 
        self.is_vn = is_vn 
        
        if is_vn: self.font = get_vn_font(font_size, bold=True)
        else: self.font = get_en_font(font_size)

    def check_hover(self, mouse_pos):
        if self.is_enabled: self.is_hovered = self.rect.collidepoint(mouse_pos)
        else: self.is_hovered = False

    def is_clicked(self, mouse_pos, mouse_pressed):
        clicked = self.is_enabled and self.rect.collidepoint(mouse_pos) and mouse_pressed[0]
        if clicked and sound_button: sound_button.play()
        return clicked

    def draw(self, screen):
        if not self.is_enabled:
            current_bg = (60, 60, 70)
            current_text = (120, 120, 130)
            border_color = (60, 60, 70)
            border_width = 2
        elif self.is_hovered and self.bg_color != (0, 0, 0, 0) and not self.disable_hover_effect:
            current_bg = (min(255, self.bg_color[0] + 30), min(255, self.bg_color[1] + 30), min(255, self.bg_color[2] + 30))
            current_text = COLOR_GLOW_YELLOW
            border_color = COLOR_GLOW_BLUE
            border_width = 3
        else:
            current_bg = self.bg_color
            current_text = self.text_color
            border_color = (100, 100, 120) 
            border_width = 2

        if current_bg != (0, 0, 0, 0):
            pygame.draw.rect(screen, current_bg, self.rect, border_radius=10)
            pygame.draw.rect(screen, border_color, self.rect, width=border_width, border_radius=10)

        offset_y = 0 if self.is_vn else 4
        center_pos = (self.rect.centerx, self.rect.centery + offset_y)
        self.draw_text_outline(screen, self.text, self.font, current_text, (0, 0, 0), center_pos)

    def draw_text_outline(self, screen, text, font, text_color, outline_color, center_pos):
        outline_width = 2 
        for dx in [-outline_width, 0, outline_width]:
            for dy in [-outline_width, 0, outline_width]:
                if (dx != 0 or dy != 0):
                    txt_surface = font.render(text, True, outline_color)
                    screen.blit(txt_surface, txt_surface.get_rect(center=(center_pos[0]+dx, center_pos[1]+dy)))
        txt_surface = font.render(text, True, text_color)
        screen.blit(txt_surface, txt_surface.get_rect(center=center_pos))


class ShopItemCard:
    def __init__(self, x, y, w, h, title, desc, price, img_path, action_id, font_size_title=36):
        self.rect = pygame.Rect(x, y, w, h)
        self.title = title
        self.desc = desc
        self.price = price
        self.action_id = action_id
        
        try:
            raw_img = pygame.image.load(img_path).convert_alpha()
            img_size = min(140, w - 40, h - 140)
            self.img = pygame.transform.smoothscale(raw_img, (img_size, img_size))
        except: self.img = None

        self.font_title = get_en_font(36)
        self.font_desc = get_en_font(20)
        
        btn_w, btn_h = 200, 60
        self.btn_buy = Button(x + (w - btn_w)//2, y + h - 80, btn_w, btn_h, f"{price} COINS", COLOR_PURCHASE, font_size=26, is_vn=False)

    def check_hover(self, mouse_pos, scroll_y=0):
        adjusted_mouse_pos = (mouse_pos[0], mouse_pos[1] + scroll_y)
        self.btn_buy.check_hover(adjusted_mouse_pos)

    def is_clicked(self, mouse_pos, mouse_pressed, scroll_y=0):
        adjusted_mouse_pos = (mouse_pos[0], mouse_pos[1] + scroll_y)
        return self.btn_buy.is_clicked(adjusted_mouse_pos, mouse_pressed)

    def draw(self, surface):
        pygame.draw.rect(surface, COLOR_PANEL, self.rect, border_radius=15)
        pygame.draw.rect(surface, (60, 50, 80), self.rect, width=3, border_radius=15)
        
        txt_title = self.font_title.render(self.title, True, COLOR_GLOW_BLUE)
        surface.blit(txt_title, (self.rect.x + 20, self.rect.y + 20))
        
        txt_desc = self.font_desc.render(self.desc, True, COLOR_TEXT_DESC)
        surface.blit(txt_desc, (self.rect.x + 20, self.rect.y + 65))
        
        if self.img:
            img_rect = self.img.get_rect(center=(self.rect.centerx, self.rect.y + 155))
            surface.blit(self.img, img_rect)
            
        self.btn_buy.draw(surface)


class ShopScreen:
    def __init__(self):
        self.next_state = None
        self.font_title = get_en_font(90)
        self.font_menu = get_en_font(40)

        try:
            raw_bg = pygame.image.load("assets/images/shop_bg.png").convert()
            self.bg = pygame.transform.smoothscale(raw_bg, (WINDOW_WIDTH, WINDOW_HEIGHT))
        except: self.bg = None

        self.btn_back = Button(WINDOW_WIDTH - 80, 20, 60, 60, "X", COLOR_PURCHASE, font_size=36, is_vn=False)

        self.menu_width = 280
        self.menu_rect = pygame.Rect(0, 120, self.menu_width, WINDOW_HEIGHT - 120)
        self.content_rect = pygame.Rect(self.menu_width, 120, WINDOW_WIDTH - self.menu_width - 25, WINDOW_HEIGHT - 120)
        
        self.scroll_y = 0
        self.is_dragging_scroll = False
        self.scrollbar_rect = pygame.Rect(WINDOW_WIDTH - 20, 130, 15, WINDOW_HEIGHT - 140)
        self.thumb_height = 100 
        self.thumb_rect = pygame.Rect(WINDOW_WIDTH - 20, 130, 15, self.thumb_height)

        self.shop_items = []
        card_w, card_h = 310, 340
        start_x = 40
        
        self.y_items = 20
        self.shop_items.append(ShopItemCard(start_x, self.y_items + 70, card_w, card_h, 
                                           "1 x PICKAXE", "Break 1 rock", 100, 
                                           "assets/images/pickaxe.png", "BUY_PICKAXE_1"))
        self.shop_items.append(ShopItemCard(start_x + card_w + 40, self.y_items + 70, card_w, card_h, 
                                           "3 x BUNDLE", "Save 50 coins", 250, 
                                           "assets/images/shop_pickaxe_3.png", "BUY_PICKAXE_3"))

        # Bỏ dòng Skins, đôn Acts lên
        self.y_acts = self.y_items + card_h + 140 
        
        for i in range(2, 6): 
            row = (i-2) // 2
            col = (i-2) % 2
            ax = start_x + col * (card_w + 40)
            ay = self.y_acts + 70 + row * (card_h + 40)
            self.shop_items.append(ShopItemCard(ax, ay, card_w, card_h, f"CHAP {i}", f"Unlock Chap {i}", 1500, "assets/images/shop_act_icon.png", f"BUY_CHAP_{i}"))

        self.y_bgs = ay + card_h + 140
        bg_data = [("FOREST", 500), ("DESERT", 500), ("CITY", 800)]
        for i, (bg_name, price) in enumerate(bg_data):
            ax = start_x + (i % 2) * (card_w + 40)
            ay = self.y_bgs + 70 + (i // 2) * (card_h + 40)
            self.shop_items.append(ShopItemCard(ax, ay, card_w, card_h, f"BG: {bg_name}", "Custom Map BG", price, f"assets/images/bg_{bg_name.lower()}.jpg", f"BUY_BG_{bg_name}"))

        self.total_content_height = ay + card_h + 70 
        
        if self.total_content_height > self.content_rect.h:
            ratio = self.content_rect.h / self.total_content_height
            self.thumb_height = max(40, int(self.scrollbar_rect.h * ratio))
            self.thumb_rect.h = self.thumb_height
        else: 
            self.thumb_height = self.scrollbar_rect.h
            self.thumb_rect.h = self.thumb_height

        self.notif_msg = ""; self.notif_alpha = 0; self.notif_color = (255, 255, 255)

    def show_notif(self, msg, color):
        self.notif_msg = msg; self.notif_color = color; self.notif_alpha = 255

    def handle_event(self, event, coins, pickaxes, unlocked_levels, unlocked_bgs):
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()
        self.btn_back.check_hover(mouse_pos)

        max_scroll = max(0, self.total_content_height - self.content_rect.h)
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.thumb_rect.collidepoint(mouse_pos): self.is_dragging_scroll = True
            elif self.scrollbar_rect.collidepoint(mouse_pos):
                if mouse_pos[1] < self.thumb_rect.top: self.scroll_y = max(0, self.scroll_y - self.content_rect.h)
                else: self.scroll_y = min(max_scroll, self.scroll_y + self.content_rect.h)
        elif event.type == pygame.MOUSEBUTTONUP: self.is_dragging_scroll = False
        elif event.type == pygame.MOUSEMOTION:
            if self.is_dragging_scroll:
                rel_y = mouse_pos[1] - self.scrollbar_rect.y - self.thumb_height//2
                scroll_ratio = rel_y / (self.scrollbar_rect.h - self.thumb_height)
                self.scroll_y = max(0, min(max_scroll, int(scroll_ratio * max_scroll)))
        elif event.type == pygame.MOUSEWHEEL:
            self.scroll_y = max(0, min(max_scroll, self.scroll_y - event.y * 50))

        if max_scroll > 0:
            thumb_ratio = self.scroll_y / max_scroll
            self.thumb_rect.y = self.scrollbar_rect.y + int(thumb_ratio * (self.scrollbar_rect.h - self.thumb_height))

        if self.content_rect.collidepoint(mouse_pos):
            content_mouse_pos = (mouse_pos[0] - self.content_rect.x, mouse_pos[1] - self.content_rect.y + self.scroll_y)
        else:
            content_mouse_pos = (-200, -200) 

        for item in self.shop_items:
            item.check_hover(content_mouse_pos) 
            
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if item.is_clicked(content_mouse_pos, mouse_pressed):
                    act_num_str = item.action_id.split('_')[-1]
                    if item.action_id == "BUY_PICKAXE_1":
                        if pickaxes >= 9: self.show_notif("BAG FULL (MAX 9)!", (231, 76, 60))
                        elif coins >= 100: self.show_notif("SUCCESS!", (46, 204, 113)); return "BUY_PICKAXE_1"
                        else: self.show_notif("NOT ENOUGH COINS!", (231, 76, 60))
                    elif item.action_id == "BUY_PICKAXE_3":
                        if pickaxes > 6: self.show_notif("NOT ENOUGH SPACE!", COLOR_GLOW_YELLOW)
                        elif coins >= 250: self.show_notif("SUCCESS!", (46, 204, 113)); return "BUY_PICKAXE_3"
                        else: self.show_notif("NOT ENOUGH COINS!", (231, 76, 60))
                    elif item.action_id.startswith("BUY_CHAP_") and act_num_str.isdigit():
                        act_num = int(act_num_str)
                        act_start_lvl = (act_num - 1) * 12 + 1
                        required_lvl = (act_num - 2) * 12 + 1 
                        
                        if unlocked_levels >= act_start_lvl: 
                            self.show_notif(f"CHAP {act_num} ALREADY OWNED!", COLOR_GLOW_YELLOW)
                        elif unlocked_levels < required_lvl:
                            self.show_notif(f"UNLOCK CHAP {act_num - 1} FIRST!", (231, 76, 60))
                        elif coins >= 1500: 
                            self.show_notif(f"CHAP {act_num} UNLOCKED!", COLOR_GLOW_BLUE)
                            return item.action_id
                        else: 
                            self.show_notif("NOT ENOUGH COINS!", (231, 76, 60))
                    elif item.action_id.startswith("BUY_BG_"):
                        bg_n = item.action_id.split("BUY_BG_")[-1]
                        price = 500 if bg_n in ["FOREST", "DESERT"] else 800
                        if bg_n in unlocked_bgs:
                            self.show_notif("ALREADY OWNED!", COLOR_GLOW_YELLOW)
                        elif coins >= price:
                            self.show_notif(f"{bg_n} BG UNLOCKED!", C_BRIGHT_GREEN)
                            return item.action_id
                        else:
                            self.show_notif("NOT ENOUGH COINS!", (231, 76, 60))
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.btn_back.is_clicked(mouse_pos, mouse_pressed): self.next_state = STATE_DASHBOARD

        return None

    def draw_text_outline(self, screen, text, font, text_color, outline_color, center_pos, align="center"):
        outline_width = 3
        for dx in [-outline_width, 0, outline_width]:
            for dy in [-outline_width, 0, outline_width]:
                if dx != 0 or dy != 0:
                    txt_surface = font.render(text, True, outline_color)
                    if align == "center": 
                        rect = txt_surface.get_rect(center=(center_pos[0] + dx, center_pos[1] + dy))
                    else: 
                        rect = txt_surface.get_rect(topleft=(center_pos[0] + dx, center_pos[1] + dy))
                    screen.blit(txt_surface, rect)
                    
        txt_surface = font.render(text, True, text_color)
        if align == "center": 
            rect = txt_surface.get_rect(center=center_pos)
        else: 
            rect = txt_surface.get_rect(topleft=center_pos)
        screen.blit(txt_surface, rect)

    def draw(self, screen, coins, pickaxes, unlocked_bgs): 
        if self.bg: screen.blit(self.bg, (0, 0))
        else: screen.fill(COLOR_BG_DARK)
        
        self.draw_text_outline(screen, "SHOP", self.font_title, (255, 255, 255), (0, 0, 0), (WINDOW_WIDTH//2, 55))
        
        font_coins_shop = get_en_font(32)
        self.draw_text_outline(screen, f"{coins} COINS", font_coins_shop, (241, 196, 15), (0, 0, 0), (WINDOW_WIDTH // 2, 110))
        
        self.btn_back.draw(screen)

        pygame.draw.rect(screen, COLOR_PANEL, self.menu_rect)
        pygame.draw.line(screen, COLOR_GLOW_BLUE, (self.menu_width, 120), (self.menu_width, WINDOW_HEIGHT), 3) 
        
        menu_scroll_surf = pygame.Surface((self.menu_width, self.total_content_height), pygame.SRCALPHA)
        
        # Đã cập nhật lại nhãn menu (Bỏ SKINS)
        for i, label in enumerate(["ITEMS", "CHAPS", "BGS"]):
            if i == 0: active = self.scroll_y < self.y_acts - 100
            elif i == 1: active = self.y_acts - 100 <= self.scroll_y < self.y_bgs - 100
            else: active = self.scroll_y >= self.y_bgs - 100
            c = C_BRIGHT_GOLD if active else (150, 150, 150)
            t = get_en_font(40).render(label, True, c)
            screen.blit(t, (40, 160 + i*80))

        screen.blit(menu_scroll_surf, self.menu_rect.topleft, (0, self.scroll_y, self.menu_width, self.menu_rect.h))

        self.content_surface = pygame.Surface((self.content_rect.w, self.total_content_height), pygame.SRCALPHA)
        font_header = get_en_font(36) 

        txt_h_items = font_header.render("MINING ITEMS", True, COLOR_GLOW_YELLOW)
        self.content_surface.blit(txt_h_items, (40, self.y_items))
        pygame.draw.line(self.content_surface, COLOR_GLOW_BLUE, (30, self.y_items + 50), (self.content_rect.w - 50, self.y_items + 50), 3)

        txt_h_acts = font_header.render("UNLOCK CHAPTERS", True, (155, 89, 182))
        self.content_surface.blit(txt_h_acts, (40, self.y_acts))
        pygame.draw.line(self.content_surface, (155, 89, 182), (30, self.y_acts + 50), (self.content_rect.w - 50, self.y_acts + 50), 3)

        txt_h_bgs = font_header.render("BACKGROUNDS", True, C_BRIGHT_GREEN)
        self.content_surface.blit(txt_h_bgs, (40, self.y_bgs))
        pygame.draw.line(self.content_surface, C_BRIGHT_GREEN, (30, self.y_bgs + 50), (self.content_rect.w - 50, self.y_bgs + 50), 3)

        for item in self.shop_items: 
            if item.action_id.startswith("BUY_BG_"):
                bg_n = item.action_id.split("BUY_BG_")[-1]
                if bg_n in unlocked_bgs:
                    item.btn_buy.text = "OWNED"
                    item.btn_buy.bg_color = (80, 80, 80)
            item.draw(self.content_surface)
        
        screen.blit(self.content_surface, self.content_rect.topleft, (0, self.scroll_y, self.content_rect.w, self.content_rect.h))

        if self.thumb_height < self.scrollbar_rect.h: 
            pygame.draw.rect(screen, COLOR_BG_DARK, self.scrollbar_rect, border_radius=5) 
            pygame.draw.rect(screen,COLOR_GLOW_BLUE, self.thumb_rect, border_radius=5) 

        if self.notif_alpha > 0:
            font_notif = get_en_font(36)
            txt_surf = font_notif.render(self.notif_msg, True, self.notif_color)
            txt_surf.set_alpha(self.notif_alpha)
            outline_surf = font_notif.render(self.notif_msg, True, (0,0,0))
            outline_surf.set_alpha(self.notif_alpha)
            cx, cy = WINDOW_WIDTH//2 + 80, WINDOW_HEIGHT - 60
            for dx, dy in [(-2,0), (2,0), (0,-2), (0,2)]: screen.blit(outline_surf, outline_surf.get_rect(center=(cx+dx, cy+dy)))
            screen.blit(txt_surf, txt_surf.get_rect(center=(cx, cy)))
            self.notif_alpha -= 3


class StartScreen:
    def __init__(self):
        self.font_title = get_en_font(110)
        self.font_prompt = get_en_font(32) 
        self.font_input = get_en_font(40) 
        self.font_error = get_en_font(24) 
        self.player_name = ""; self.next_state = None; self.error_msg = ""
        
        box_w, box_h = 500, 75
        self.input_rect = pygame.Rect((WINDOW_WIDTH - box_w) // 2, 250, box_w, box_h)
        self.btn_start = Button((WINDOW_WIDTH - 220) // 2, self.input_rect.bottom + 35, 220, 65, "START", COLOR_GLOW_BLUE, font_size=36, is_vn=False)
        
        self.cursor_visible = True; self.last_blink = pygame.time.get_ticks()
        try:
            raw_bg = pygame.image.load(BG_START_PATH).convert()
            self.bg = pygame.transform.smoothscale(raw_bg, (WINDOW_WIDTH, WINDOW_HEIGHT))
        except:
            self.bg = None

    def draw_text_outline(self, screen, text, font, text_color, outline_color, center_pos, align="center"):
        outline_width = 3
        for dx in [-outline_width, 0, outline_width]:
            for dy in [-outline_width, 0, outline_width]:
                if dx != 0 or dy != 0:
                    txt_surface = font.render(text, True, outline_color)
                    if align == "center": 
                        rect = txt_surface.get_rect(center=(center_pos[0] + dx, center_pos[1] + dy))
                    else: 
                        rect = txt_surface.get_rect(topleft=(center_pos[0] + dx, center_pos[1] + dy))
                    screen.blit(txt_surface, rect)
                    
        txt_surface = font.render(text, True, text_color)
        if align == "center": 
            rect = txt_surface.get_rect(center=center_pos)
        else: 
            rect = txt_surface.get_rect(topleft=center_pos)
        screen.blit(txt_surface, rect)

    def handle_event(self, event):
        mouse_pos = pygame.mouse.get_pos(); self.btn_start.check_hover(mouse_pos)
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.btn_start.is_clicked(mouse_pos, pygame.mouse.get_pressed()):
                if len(self.player_name.strip()) > 0: self.next_state = STATE_DASHBOARD
                else: self.error_msg = "PLEASE ENTER NAME!"
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                if len(self.player_name.strip()) > 0: self.next_state = STATE_DASHBOARD
                else: self.error_msg = "PLEASE ENTER NAME!"
            elif event.key == pygame.K_BACKSPACE: 
                self.player_name = self.player_name[:-1]
                self.error_msg = ""
            else:
                if len(self.player_name) < 12: 
                    self.player_name += event.unicode
                    self.error_msg = ""
        return None

    def draw(self, screen):
        if hasattr(self, 'bg') and self.bg: screen.blit(self.bg, (0, 0))
        else: screen.fill(COLOR_BG_DARK)
        
        self.draw_text_outline(screen, "PIPE PUZZLE", self.font_title, COLOR_TEXT_MAIN, (0, 0, 0), (WINDOW_WIDTH // 2, 135))
        
        prompt_y = self.input_rect.top - 40
        self.draw_text_outline(screen, "ENTER YOUR NAME:", self.font_prompt, COLOR_TEXT_DESC, (0, 0, 0), (WINDOW_WIDTH // 2, prompt_y + 4))
        
        pygame.draw.rect(screen, (25, 25, 30), self.input_rect, border_radius=12)
        pygame.draw.rect(screen, COLOR_GLOW_BLUE, self.input_rect, width=4, border_radius=12)
        
        txt_surface = self.font_input.render(self.player_name, True, (255, 255, 255))
        txt_rect = txt_surface.get_rect(center=(self.input_rect.centerx, self.input_rect.centery + 6))
        screen.blit(txt_surface, txt_rect)
        
        current_time = pygame.time.get_ticks()
        if current_time - self.last_blink > 500: 
            self.cursor_visible = not self.cursor_visible
            self.last_blink = current_time
        if self.cursor_visible:
            cursor_x = txt_rect.right + 7 if len(self.player_name) > 0 else self.input_rect.centerx
            cursor_y_start = self.input_rect.centery - 20 + 4
            cursor_y_end = self.input_rect.centery + 20 + 4
            pygame.draw.line(screen, COLOR_GLOW_BLUE, (cursor_x, cursor_y_start), (cursor_x, cursor_y_end), 5)
            
        self.btn_start.draw(screen)
        if self.error_msg: 
            self.draw_text_outline(screen, self.error_msg, self.font_error, (231, 76, 60), (0, 0, 0), (WINDOW_WIDTH // 2, self.btn_start.rect.bottom + 35))


class DashboardScreen:
    def __init__(self):
        self.font_title = get_en_font(100)
        self.font_small = get_en_font(24)
        self.next_state = None
        
        btn_w, btn_h = 360, 75
        start_x = WINDOW_WIDTH//2 - 180
        btn_font = 40
        
        
        
        # Cập nhật màu sắc cho các nút
        self.btn_play = Button(start_x, 240, btn_w, btn_h, "LEVEL SELECT", C_BRIGHT_CYAN, font_size=btn_font, is_vn=False)
        self.btn_quests = Button(start_x, 430, btn_w, btn_h, "MISSION", C_BRIGHT_GREEN, font_size=btn_font, is_vn=False)
        
        # Nút Shop giờ đây có nền Vàng sáng
        self.btn_shop = Button(start_x, 335, btn_w, btn_h, "", C_BRIGHT_GOLD, font_size=btn_font, is_vn=False)
        
        self.btn_skin = Button(WINDOW_WIDTH - 180, WINDOW_HEIGHT - 90, 150, 60, "SKIN", C_BRIGHT_CYAN, font_size=28, is_vn=False)
        self.btn_options = Button(30, WINDOW_HEIGHT - 90, 180, 60, "OPTIONS", C_BRIGHT_SLATE, font_size=28, is_vn=False)
        
        self.show_options_popup = False
        self.show_giftcode_popup = False
        self.giftcode_input = ""
        self.notifications = [] 
        
        box_w, box_h = 650, 500
        box_x, box_y = (WINDOW_WIDTH - box_w)//2, (WINDOW_HEIGHT - box_h)//2
        sub_btn_w, sub_btn_h = 170, 60
        sub_font = 28
        
        self.btn_opt_exit = Button(box_x + 40, box_y + 400, sub_btn_w, sub_btn_h, "LEAVE", COLOR_PURCHASE, font_size=sub_font, is_vn=False)
        self.btn_opt_rename = Button(box_x + 240, box_y + 400, sub_btn_w, sub_btn_h, "RENAME", C_BRIGHT_CYAN, font_size=sub_font, is_vn=False)
        self.btn_opt_giftcode = Button(box_x + 440, box_y + 400, sub_btn_w, sub_btn_h, "GIFTCODE", C_BRIGHT_GOLD, disable_hover_effect=True, font_size=sub_font, is_vn=False)
        self.btn_opt_close = Button(box_x + box_w - 55, box_y + 10, 45, 45, "X", COLOR_PURCHASE, font_size=sub_font, is_vn=False)
        
        self.music_vol = 1.0; self.sfx_vol = 1.0
        self.rect_music_slider = pygame.Rect(box_x + 220, box_y + 175, 350, 30)
        self.rect_sfx_slider = pygame.Rect(box_x + 220, box_y + 295, 350, 30)
        self.is_dragging_music = False; self.is_dragging_sfx = False
        
        try:
            self.bg_sky = pygame.image.load("assets/images/sky.png").convert()
            self.bg_sky = pygame.transform.smoothscale(self.bg_sky, (WINDOW_WIDTH, WINDOW_HEIGHT))
        except: self.bg_sky = None
        try:
            self.img_coin = pygame.image.load("assets/images/coin_icon.png").convert_alpha()
            self.img_coin = pygame.transform.smoothscale(self.img_coin, (40, 40)) 
        except: self.img_coin = None

    def handle_event(self, event, redeemed_codes):
        mouse_pos = pygame.mouse.get_pos(); mouse_pressed = pygame.mouse.get_pressed()
        if self.show_giftcode_popup:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    code = self.giftcode_input.upper()
                    if code in redeemed_codes: 
                        self.notifications.append({'text': "ALREADY USED!", 'x': WINDOW_WIDTH//2, 'y': WINDOW_HEIGHT//2, 'alpha': 255, 'color': COLOR_PURCHASE})
                        self.show_giftcode_popup = False; self.show_options_popup = True; self.giftcode_input = ""
                        return None
                    elif code == "UNPIPE": 
                        self.notifications.append({'text': "UNLOCK ALL LVL!", 'x': WINDOW_WIDTH//2, 'y': WINDOW_HEIGHT//2, 'alpha': 255, 'color': (0,255,255)})
                        self.show_giftcode_popup = False; self.show_options_popup = True; self.giftcode_input = ""; return "UNLOCK_ALL"
                    elif code == "PIPEGOLD": 
                        self.notifications.append({'text': "+10.000 COINS", 'x': WINDOW_WIDTH//2, 'y': WINDOW_HEIGHT//2, 'alpha': 255, 'color': (255,215,0)})
                        self.show_giftcode_popup = False; self.show_options_popup = True; self.giftcode_input = ""; return "ADD_COINS"
                    else: 
                        self.notifications.append({'text': "INVALID CODE!", 'x': WINDOW_WIDTH//2, 'y': WINDOW_HEIGHT//2, 'alpha': 255, 'color': COLOR_PURCHASE})
                        self.show_giftcode_popup = False; self.show_options_popup = True; self.giftcode_input = ""; return None
                elif event.key == pygame.K_BACKSPACE: self.giftcode_input = self.giftcode_input[:-1]
                elif event.key == pygame.K_ESCAPE: self.show_giftcode_popup = False; self.show_options_popup = True 
                else:
                    if len(self.giftcode_input) < 15: self.giftcode_input += event.unicode
            return None
            
        if self.show_options_popup:
            for btn in [self.btn_opt_exit, self.btn_opt_rename, self.btn_opt_giftcode, self.btn_opt_close]: btn.check_hover(mouse_pos)
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.btn_opt_close.is_clicked(mouse_pos, mouse_pressed): self.show_options_popup = False
                elif self.btn_opt_exit.is_clicked(mouse_pos, mouse_pressed): import sys; pygame.quit(); sys.exit()
                elif self.btn_opt_rename.is_clicked(mouse_pos, mouse_pressed): self.next_state = STATE_MENU_NAME; self.show_options_popup = False
                elif self.btn_opt_giftcode.is_clicked(mouse_pos, mouse_pressed): self.show_options_popup = False; self.show_giftcode_popup = True; self.giftcode_input = ""
                if mouse_pressed[0]:
                    if self.rect_music_slider.collidepoint(mouse_pos): self.is_dragging_music = True
                    if self.rect_sfx_slider.collidepoint(mouse_pos): self.is_dragging_sfx = True
            elif event.type == pygame.MOUSEBUTTONUP: self.is_dragging_music = False; self.is_dragging_sfx = False
            if self.is_dragging_music or (mouse_pressed[0] and self.rect_music_slider.collidepoint(mouse_pos)): 
                self.music_vol = max(0.0, min(1.0, (mouse_pos[0] - self.rect_music_slider.x) / self.rect_music_slider.width))
                pygame.mixer.music.set_volume(self.music_vol)
            if self.is_dragging_sfx or (mouse_pressed[0] and self.rect_sfx_slider.collidepoint(mouse_pos)): 
                self.sfx_vol = max(0.0, min(1.0, (mouse_pos[0] - self.rect_sfx_slider.x) / self.rect_sfx_slider.width))
            return None
            
        for btn in [self.btn_play, self.btn_shop, self.btn_quests, self.btn_skin, self.btn_options]: btn.check_hover(mouse_pos)
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.btn_play.is_clicked(mouse_pos, mouse_pressed): self.next_state = STATE_LEVEL_SELECT
            elif self.btn_shop.is_clicked(mouse_pos, mouse_pressed): self.next_state = STATE_SHOP
            elif self.btn_quests.is_clicked(mouse_pos, mouse_pressed): self.next_state = STATE_QUESTS
            elif self.btn_skin.is_clicked(mouse_pos, mouse_pressed): self.next_state = STATE_SKIN
            elif self.btn_options.is_clicked(mouse_pos, mouse_pressed): self.show_options_popup = True
        return None

    def draw_text_outline(self, screen, text, font, text_color, outline_color, center_pos):
        outline_width = 3
        for dx in [-outline_width, 0, outline_width]:
            for dy in [-outline_width, 0, outline_width]:
                if dx != 0 or dy != 0:
                    txt_surface = font.render(text, True, outline_color)
                    screen.blit(txt_surface, txt_surface.get_rect(center=(center_pos[0]+dx, center_pos[1]+dy)))
        txt_surface = font.render(text, True, text_color)
        screen.blit(txt_surface, txt_surface.get_rect(center=center_pos))

    def draw(self, screen, player_name, coins):
        if self.bg_sky: screen.blit(self.bg_sky, (0, 0))
        else: screen.fill(COLOR_BG_DARK)
        
        self.draw_text_outline(screen, "PIPE PUZZLE", self.font_title, COLOR_TEXT_MAIN, (0, 0, 0), (WINDOW_WIDTH//2, 115))
        font_player = get_en_font(36)
        self.draw_text_outline(screen, f"PLAYER: {player_name}", font_player, COLOR_TEXT_MAIN, (0, 0, 0), (WINDOW_WIDTH//2, 185))
        
        # Vẽ nút Play và Mission
        for btn in [self.btn_play, self.btn_quests]:
            btn.draw(screen)
            current_glow = (255, 255, 255) if not btn.is_hovered else COLOR_GLOW_YELLOW
            pygame.draw.rect(screen, current_glow, btn.rect, 3, border_radius=10)
        
        # Vẽ các nút nhỏ
        for btn in [self.btn_skin, self.btn_options]:
            btn.draw(screen)
            pygame.draw.rect(screen, (255, 255, 255), btn.rect, 2, border_radius=10)
        
        # Vẽ nút SHOP SÁNG SỦA
        self.btn_shop.draw(screen) 
        current_shop_glow = (255, 255, 255) if not self.btn_shop.is_hovered else (255, 255, 100)
        pygame.draw.rect(screen, current_shop_glow, self.btn_shop.rect, 4, border_radius=10)

        shop_rect = self.btn_shop.rect
        font_shop_big = get_en_font(40)
        # Chữ SHOP dùng màu Đen hoặc Xanh đậm cho nổi trên nền Vàng
        self.draw_text_outline(screen, "SHOP", font_shop_big, (50, 40, 0), (255,255,255), (shop_rect.centerx, shop_rect.top + 25))
        
        font_shop_coins = get_en_font(22)
        self.draw_text_outline(screen, f"{coins} COINS", font_shop_coins, (100, 80, 0), (255,255,255), (shop_rect.centerx, shop_rect.bottom - 22))

        # Hiển thị Options Popup (nếu có)
        if self.show_options_popup:
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA); overlay.fill((0, 0, 0, 210)); screen.blit(overlay, (0, 0))
            box_w, box_h = 650, 500; box_x, box_y = (WINDOW_WIDTH - box_w)//2, (WINDOW_HEIGHT - box_h)//2
            pygame.draw.rect(screen, COLOR_PANEL, (box_x, box_y, box_w, box_h), border_radius=15)
            pygame.draw.rect(screen, COLOR_GLOW_BLUE, (box_x, box_y, box_w, box_h), 5, border_radius=15)
            self.draw_text_outline(screen, "OPTIONS", get_en_font(80), COLOR_GLOW_BLUE, (0,0,0), (WINDOW_WIDTH//2, box_y + 80))
            self.draw_text_outline(screen, "BGM", get_en_font(32), COLOR_TEXT_MAIN, (0,0,0), (box_x + 120, box_y + 190 + 4))
            pygame.draw.rect(screen, COLOR_BG_DARK, self.rect_music_slider, border_radius=10)
            fill_music_w = int(self.rect_music_slider.width * self.music_vol)
            if fill_music_w > 0: pygame.draw.rect(screen, COLOR_GLOW_BLUE, pygame.Rect(self.rect_music_slider.x, self.rect_music_slider.y, fill_music_w, self.rect_music_slider.height), border_radius=10)
            pygame.draw.rect(screen, (255, 255, 255), self.rect_music_slider, 3, border_radius=10)
            pygame.draw.circle(screen, (255, 255, 255), (self.rect_music_slider.x + fill_music_w, self.rect_music_slider.centery), 20); pygame.draw.circle(screen, (0, 0, 0), (self.rect_music_slider.x + fill_music_w, self.rect_music_slider.centery), 20, 3) 
            self.draw_text_outline(screen, "SFX", get_en_font(32), COLOR_TEXT_MAIN, (0,0,0), (box_x + 120, box_y + 310 + 4))
            pygame.draw.rect(screen, COLOR_BG_DARK, self.rect_sfx_slider, border_radius=10)
            fill_sfx_w = int(self.rect_sfx_slider.width * self.sfx_vol)
            if fill_sfx_w > 0: pygame.draw.rect(screen, COLOR_GLOW_BLUE, pygame.Rect(self.rect_sfx_slider.x, self.rect_sfx_slider.y, fill_sfx_w, self.rect_sfx_slider.height), border_radius=10)
            pygame.draw.rect(screen, (255, 255, 255), self.rect_sfx_slider, 3, border_radius=10)
            pygame.draw.circle(screen, (255, 255, 255), (self.rect_sfx_slider.x + fill_sfx_w, self.rect_sfx_slider.centery), 20); pygame.draw.circle(screen, (0, 0, 0), (self.rect_sfx_slider.x + fill_sfx_w, self.rect_sfx_slider.centery), 20, 3)
            for btn in [self.btn_opt_exit, self.btn_opt_rename, self.btn_opt_giftcode, self.btn_opt_close]: btn.draw(screen)
        elif self.show_giftcode_popup:
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA); overlay.fill((0, 0, 0, 210)); screen.blit(overlay, (0, 0))
            box_w, box_h = 550, 300; box_x, box_y = (WINDOW_WIDTH - box_w)//2, (WINDOW_HEIGHT - box_h)//2
            pygame.draw.rect(screen, COLOR_PANEL, (box_x, box_y, box_w, box_h), border_radius=15); pygame.draw.rect(screen, (255,180,0), (box_x, box_y, box_w, box_h), 5, border_radius=15)
            self.draw_text_outline(screen, "SECRET CODE:", get_en_font(40), COLOR_TEXT_MAIN, (0,0,0), (WINDOW_WIDTH//2, box_y + 60))
            pygame.draw.rect(screen, COLOR_BG_DARK, (box_x + 25, box_y + 110, box_w - 50, 80), border_radius=10); pygame.draw.rect(screen, (0,255,255), (box_x + 25, box_y + 110, box_w - 50, 80), 3, border_radius=10)
            txt_input = get_en_font(45).render(self.giftcode_input + "_", True, (255,255,0)); screen.blit(txt_input, (box_x + 50, box_y + 125))
            self.draw_text_outline(screen, "ENTER to Confirm - ESC to Cancel", get_en_font(22), (150, 150, 150), (0,0,0), (WINDOW_WIDTH//2, box_y + 240))
            
        for notif in self.notifications[:]: 
            self.draw_text_outline(screen, notif['text'], get_en_font(35), notif['color'], (0,0,0), (notif['x'], notif['y']))
            notif['y'] -= 2; notif['alpha'] -= 4
            if notif['alpha'] <= 0: 
                self.notifications.remove(notif)


class LevelSelectScreen:
    def __init__(self):
        self.font_title = get_en_font(80)
        self.font_act = get_en_font(50)
        self.next_state, self.selected_level = None, 1
        self.selected_act, self.selected_difficulty = 1, DIFF_NORMAL
        
        self.btn_back = Button(WINDOW_WIDTH - 80, 20, 60, 60, "X", COLOR_PURCHASE, font_size=36)
        
        self.btn_diff_easy = Button(WINDOW_WIDTH//2 - 215, 170, 130, 50, "EASY", (60, 60, 60), COLOR_EASY, font_size=20)
        self.btn_diff_normal = Button(WINDOW_WIDTH//2 - 65, 170, 130, 50, "NORMAL", COLOR_NORMAL, (0, 0, 0), font_size=20)
        self.btn_diff_hard = Button(WINDOW_WIDTH//2 + 85, 170, 130, 50, "HARD", (60, 60, 60), COLOR_HARD, font_size=20)
        
        self.btn_delete_mode = Button(WINDOW_WIDTH//2 - 150, 450, 300, 60, "DELETE MODE: OFF", COLOR_PANEL, font_size=24)
        self.delete_mode = False
        self.notif_msg = ""
        self.notif_alpha = 0
        
        btn_size = 100; padding = 15; cols = 4
        grid_w = cols * btn_size + (cols - 1) * padding
        start_x = (WINDOW_WIDTH - grid_w) // 2
        mid_y = 250 + (3 * btn_size + 2 * padding) // 2
        
        self.btn_act_prev = Button(start_x - 100, mid_y - 45, 70, 90, "<", (50, 50, 60), (255, 255, 255), font_size=60)
        self.btn_next = Button(start_x + grid_w + 30, mid_y - 45, 70, 90, ">", (50, 50, 60), (255, 255, 255), font_size=60)
        
        self.level_buttons = [Button(0, 0, 100, 100, "", C_BRIGHT_CYAN, font_size=32) for _ in range(12)]
            
        self.act_backgrounds = {}
        bg_files = {
            0: "assets/images/bg_act1_2.jpg", 1: "assets/images/bg_act1_2.jpg", 2: "assets/images/bg_act1_2.jpg",
            3: "assets/images/bg_act3_4.jpg", 4: "assets/images/bg_act3_4.jpg", 5: "assets/images/bg_act5.jpg"
        }
        for act_num, file_path in bg_files.items():
            try: self.act_backgrounds[act_num] = pygame.transform.smoothscale(pygame.image.load(file_path).convert(), (WINDOW_WIDTH, WINDOW_HEIGHT))
            except: self.act_backgrounds[act_num] = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT)); self.act_backgrounds[act_num].fill(COLOR_BG_DARK)

    def update_ui(self, unlocked_levels, custom_levels_data):
        btn_size, padding = 100, 15
        start_x = (WINDOW_WIDTH - (4 * btn_size + 3 * padding)) // 2
        
        if self.selected_act == 0:
            start_y = 300
            for i in range(4):
                btn = self.level_buttons[i]
                btn.rect.topleft = (start_x + i * (btn_size + padding), start_y)
                
                # C1 mặc định mở, C2 mở nếu C1 đã tạo
                if i == 0 or str(i-1) in custom_levels_data:
                    btn.is_enabled = True
                    if str(i) in custom_levels_data:
                        btn.bg_color = COLOR_PURCHASE if self.delete_mode else (46, 204, 113) # Xanh lá
                        btn.text = f"C{i+1} PLAY"
                    else:
                        btn.bg_color = COLOR_PURCHASE if self.delete_mode else C_BRIGHT_CYAN # Xanh dương
                        btn.text = f"C{i+1} NEW"
                else:
                    btn.is_enabled = False
                    btn.bg_color = (80, 80, 80)
                    btn.text = f"C{i+1}"
        else:
            start_y = 250
            for i in range(12):
                btn = self.level_buttons[i]
                btn.rect.topleft = (start_x + (i % 4) * (btn_size + padding), start_y + (i // 4) * (btn_size + padding))
                lvl = (self.selected_act-1)*12+i+1
                btn.text, btn.is_enabled = str(lvl), lvl <= unlocked_levels
                
            self.btn_diff_easy.bg_color = COLOR_EASY if self.selected_difficulty == DIFF_EASY else (60, 60, 60)
            self.btn_diff_easy.text_color = (255, 255, 255) if self.selected_difficulty == DIFF_EASY else COLOR_EASY
            self.btn_diff_normal.bg_color = COLOR_NORMAL if self.selected_difficulty == DIFF_NORMAL else (60, 60, 60)
            self.btn_diff_normal.text_color = (255, 255, 255) if self.selected_difficulty == DIFF_NORMAL else COLOR_NORMAL
            self.btn_diff_hard.bg_color = COLOR_HARD if self.selected_difficulty == DIFF_HARD else (60, 60, 60)
            self.btn_diff_hard.text_color = (255, 255, 255) if self.selected_difficulty == DIFF_HARD else COLOR_HARD
            
            c_color = COLOR_NORMAL
            if self.selected_difficulty == DIFF_EASY: c_color = COLOR_EASY
            elif self.selected_difficulty == DIFF_HARD: c_color = COLOR_HARD
            for btn in self.level_buttons: 
                if btn.is_enabled: btn.bg_color = c_color
                else: btn.bg_color = (80, 80, 80)

    def handle_event(self, event, unlocked_levels, custom_levels_data):
        m_pos = pygame.mouse.get_pos(); m_pre = pygame.mouse.get_pressed()
        self.btn_back.check_hover(m_pos); self.btn_act_prev.check_hover(m_pos); self.btn_next.check_hover(m_pos)
        
        if self.selected_act > 0:
            self.btn_diff_easy.check_hover(m_pos); self.btn_diff_normal.check_hover(m_pos); self.btn_diff_hard.check_hover(m_pos)
            
        if self.selected_act == 0:
            self.btn_delete_mode.check_hover(m_pos)
            if event.type == pygame.MOUSEBUTTONDOWN and self.btn_delete_mode.is_clicked(m_pos, m_pre):
                self.delete_mode = not self.delete_mode
                self.btn_delete_mode.text = "DELETE MODE: ON" if self.delete_mode else "DELETE MODE: OFF"
                self.btn_delete_mode.bg_color = COLOR_PURCHASE if self.delete_mode else COLOR_PANEL

        self.update_ui(unlocked_levels, custom_levels_data)
        
        num_btns = 4 if self.selected_act == 0 else 12
        for i in range(num_btns):
            btn = self.level_buttons[i]
            btn.check_hover(m_pos)
            if event.type == pygame.MOUSEBUTTONDOWN and btn.is_clicked(m_pos, m_pre) and btn.is_enabled:
                if self.selected_act == 0:
                    if self.delete_mode:
                        if str(i) in custom_levels_data:
                            self.notif_msg = f"DELETED C{i+1}"
                            self.notif_alpha = 255
                            self.delete_mode = False; self.btn_delete_mode.text = "DELETE MODE: OFF"; self.btn_delete_mode.bg_color = COLOR_PANEL
                            return f"DELETE_CUSTOM_{i}" 
                        else:
                            self.notif_msg = "NOTHING TO DELETE"
                            self.notif_alpha = 255
                    else:
                        self.selected_level = 1000 + i
                        if str(i) in custom_levels_data: return "PLAY_CUSTOM"
                        return "OPEN_CUSTOM_SETUP" 
                else:
                    self.selected_level = (self.selected_act-1)*12+i+1
                    self.next_state = STATE_GAME_PLAY
                
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.btn_back.is_clicked(m_pos, m_pre): self.next_state = STATE_DASHBOARD
            elif self.selected_act > 0: 
                if self.btn_diff_easy.is_clicked(m_pos, m_pre): self.selected_difficulty = DIFF_EASY
                elif self.btn_diff_normal.is_clicked(m_pos, m_pre): self.selected_difficulty = DIFF_NORMAL
                elif self.btn_diff_hard.is_clicked(m_pos, m_pre): self.selected_difficulty = DIFF_HARD
                
            if self.btn_act_prev.is_clicked(m_pos, m_pre):
                if self.selected_act > 0: self.selected_act -= 1
                self.delete_mode = False; self.btn_delete_mode.text = "DELETE MODE: OFF"; self.btn_delete_mode.bg_color = COLOR_PANEL
            elif self.btn_next.is_clicked(m_pos, m_pre):
                if self.selected_act < 5: self.selected_act += 1
                self.delete_mode = False
        return None

    def draw_text_outline(self, screen, text, font, text_color, outline_color, center_pos):
        for dx, dy in [(-3,-3), (3,3), (-3,3), (3,-3)]:
            txt = font.render(text, True, outline_color)
            screen.blit(txt, txt.get_rect(center=(center_pos[0]+dx, center_pos[1]+dy)))
        txt = font.render(text, True, text_color)
        screen.blit(txt, txt.get_rect(center=center_pos))

    def draw(self, screen):
        screen.fill(COLOR_BG_DARK)
        if self.selected_act in self.act_backgrounds: screen.blit(self.act_backgrounds[self.selected_act], (0, 0))

        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        if self.selected_difficulty == DIFF_EASY and self.selected_act > 0:
            overlay.fill((255, 182, 193, 70)); screen.blit(overlay, (0, 0))
        elif self.selected_difficulty == DIFF_HARD and self.selected_act > 0:
            overlay.fill((255, 0, 0, 60)); screen.blit(overlay, (0, 0))

        txt = self.font_title.render("LEVEL SELECT", True, (255, 255, 255))
        screen.blit(txt, txt.get_rect(center=(WINDOW_WIDTH//2, 50)))
        self.draw_text_outline(screen, f"CHAP {self.selected_act}", self.font_act, COLOR_GLOW_BLUE, (0, 0, 0), (WINDOW_WIDTH // 2, 120))
        
        self.btn_back.draw(screen)
        if self.selected_act > 0:
            self.btn_diff_easy.draw(screen); self.btn_diff_normal.draw(screen); self.btn_diff_hard.draw(screen)
            
        if self.selected_act > 0: self.btn_act_prev.draw(screen)
        if self.selected_act < 5: self.btn_next.draw(screen)
        
        num_buttons = 4 if self.selected_act == 0 else 12
        for i in range(num_buttons): self.level_buttons[i].draw(screen)
            
        if self.selected_act == 0: self.btn_delete_mode.draw(screen)
            
        if self.notif_alpha > 0:
            n_txt = get_en_font(36).render(self.notif_msg, True, COLOR_GLOW_YELLOW)
            n_txt.set_alpha(self.notif_alpha)
            screen.blit(n_txt, n_txt.get_rect(center=(WINDOW_WIDTH//2, 220)))
            self.notif_alpha -= 5


# ==========================================
# MÀN HÌNH TÙY CHỈNH CUSTOM LEVEL (CHAP 0)
# ==========================================
class CustomSetupScreen:
    def __init__(self):
        self.font_title = get_en_font(60); self.font_label = get_en_font(24); self.font_val = get_en_font(32)
        self.next_state = None; self.custom_id = 0 
        self.pipe_types = ['I', 'L', 'T', '+', 'C', 'P', 'O', 'X']; self.pipe_imgs = {}
        for ptype in self.pipe_types: self.pipe_imgs[ptype] = generate_pipe_icon(ptype)
        
        self.btn_back = Button(20, 20, 60, 60, "X", COLOR_PURCHASE, font_size=36)
        self.btn_play = Button(WINDOW_WIDTH//2 - 125, WINDOW_HEIGHT - 90, 250, 60, "CREATE & PLAY", C_BRIGHT_GREEN, font_size=28)
        
        # Bố cục 5 mục cân đối
        st_y = 120; gp_y = 65; cx = WINDOW_WIDTH//2
        self.rocks = 5
        self.btn_rock_sub = Button(cx - 100, st_y, 45, 45, "<", COLOR_PANEL, font_size=30)
        self.btn_rock_add = Button(cx + 50, st_y, 45, 45, ">", COLOR_PANEL, font_size=30)
        
        self.bgs = ["DEFAULT", "FOREST", "DESERT", "CITY"]; self.bg_idx = 0
        self.btn_bg_sub = Button(cx - 150, st_y+gp_y, 45, 45, "<", COLOR_PANEL, font_size=30)
        self.btn_bg_add = Button(cx + 100, st_y+gp_y, 45, 45, ">", COLOR_PANEL, font_size=30)
        self.bg_images = {}
        for bg in self.bgs:
            try: self.bg_images[bg] = pygame.transform.smoothscale(pygame.image.load(f"assets/images/bg_{bg.lower()}.jpg").convert(), (WINDOW_WIDTH, WINDOW_HEIGHT))
            except:
                try: self.bg_images[bg] = pygame.transform.smoothscale(pygame.image.load(f"assets/images/bg_{bg.lower()}.png").convert(), (WINDOW_WIDTH, WINDOW_HEIGHT))
                except: self.bg_images[bg] = None 
        
        self.swaps = 0
        self.btn_swap_sub = Button(cx - 100, st_y+gp_y*2, 45, 45, "<", COLOR_PANEL, font_size=30)
        self.btn_swap_add = Button(cx + 50, st_y+gp_y*2, 45, 45, ">", COLOR_PANEL, font_size=30)
        
        self.moves = 51 # 51 = INF
        self.btn_move_sub = Button(cx - 100, st_y+gp_y*3, 45, 45, "<", COLOR_PANEL, font_size=30)
        self.btn_move_add = Button(cx + 50, st_y+gp_y*3, 45, 45, ">", COLOR_PANEL, font_size=30)

        self.sizes = [3, 5, 7, 10]; self.size_idx = 3 
        self.btn_size_sub = Button(cx - 100, st_y+gp_y*4, 45, 45, "<", COLOR_PANEL, font_size=30)
        self.btn_size_add = Button(cx + 50, st_y+gp_y*4, 45, 45, ">", COLOR_PANEL, font_size=30)
        
        self.pipe_active = {ptype: True for ptype in self.pipe_types}; self.pipe_btns = {}
        start_x = WINDOW_WIDTH - 210; start_y = 150
        for i, ptype in enumerate(self.pipe_types):
            self.pipe_btns[ptype] = Button(start_x + (i % 2) * 80, start_y + (i // 2) * 80, 60, 60, "", C_BRIGHT_CYAN, font_size=36)

    def load_level(self, level_idx): self.custom_id = level_idx

    def handle_event(self, event, unlocked_bgs):
        m_pos = pygame.mouse.get_pos(); m_pre = pygame.mouse.get_pressed()
        for btn in [self.btn_back, self.btn_play, self.btn_rock_sub, self.btn_rock_add, self.btn_bg_sub, self.btn_bg_add, self.btn_swap_sub, self.btn_swap_add, self.btn_move_sub, self.btn_move_add, self.btn_size_sub, self.btn_size_add]:
            btn.check_hover(m_pos)
        for btn in self.pipe_btns.values(): btn.check_hover(m_pos)

        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.btn_back.is_clicked(m_pos, m_pre): self.next_state = STATE_LEVEL_SELECT
            elif self.btn_play.is_clicked(m_pos, m_pre): 
                if self.bgs[self.bg_idx] in unlocked_bgs: self.next_state = STATE_GAME_PLAY
            elif self.btn_rock_sub.is_clicked(m_pos, m_pre): self.rocks = max(0, self.rocks - 1)
            elif self.btn_rock_add.is_clicked(m_pos, m_pre): self.rocks = min(20, self.rocks + 1)
            elif self.btn_bg_sub.is_clicked(m_pos, m_pre): self.bg_idx = (self.bg_idx - 1) % len(self.bgs)
            elif self.btn_bg_add.is_clicked(m_pos, m_pre): self.bg_idx = (self.bg_idx + 1) % len(self.bgs)
            elif self.btn_swap_sub.is_clicked(m_pos, m_pre): self.swaps = max(0, self.swaps - 1)
            elif self.btn_swap_add.is_clicked(m_pos, m_pre): self.swaps = min(21, self.swaps + 1) 
            elif self.btn_move_sub.is_clicked(m_pos, m_pre): self.moves = max(0, self.moves - 1)
            elif self.btn_move_add.is_clicked(m_pos, m_pre): self.moves = min(51, self.moves + 1) 
            elif self.btn_size_sub.is_clicked(m_pos, m_pre): self.size_idx = (self.size_idx - 1) % len(self.sizes)
            elif self.btn_size_add.is_clicked(m_pos, m_pre): self.size_idx = (self.size_idx + 1) % len(self.sizes)
            
            for ptype, btn in self.pipe_btns.items():
                if btn.is_clicked(m_pos, m_pre):
                    self.pipe_active[ptype] = not self.pipe_active[ptype]
                    btn.bg_color = C_BRIGHT_CYAN if self.pipe_active[ptype] else (80, 80, 80)

    def draw_text_outline(self, screen, text, font, text_color, outline_color, center_pos, align="center"):
        for dx, dy in [(-2,-2), (2,2), (-2,2), (2,-2)]:
            txt = font.render(text, True, outline_color)
            r = txt.get_rect(center=(center_pos[0]+dx, center_pos[1]+dy)) if align=="center" else txt.get_rect(topleft=(center_pos[0]+dx, center_pos[1]+dy))
            screen.blit(txt, r)
        txt = font.render(text, True, text_color)
        r = txt.get_rect(center=center_pos) if align=="center" else txt.get_rect(topleft=center_pos)
        screen.blit(txt, r)

    def draw(self, screen, unlocked_bgs):
        current_bg = self.bgs[self.bg_idx]
        is_unlocked = current_bg in unlocked_bgs
        if self.bg_images.get(current_bg): screen.blit(self.bg_images[current_bg], (0, 0))
        else: screen.fill(COLOR_BG_DARK)
            
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA); overlay.fill((0, 0, 0, 170)); screen.blit(overlay, (0, 0))
        self.draw_text_outline(screen, f"SETUP CUSTOM C{self.custom_id+1}", self.font_title, COLOR_GLOW_GOLD, (0,0,0), (WINDOW_WIDTH//2, 50))
        
        st_y = 120; gp_y = 65
        cx_lbl = WINDOW_WIDTH//4 - 20; cx_btn = WINDOW_WIDTH//2; offset = 22
        
        # 5 Hàng Custom
        self.draw_text_outline(screen, "ROCKS", self.font_label, COLOR_TEXT_MAIN, (0,0,0), (cx_lbl, st_y+offset), "center")
        self.btn_rock_sub.draw(screen); self.btn_rock_add.draw(screen)
        self.draw_text_outline(screen, f"{self.rocks:02d}", self.font_val, COLOR_GLOW_BLUE, (0,0,0), (cx_btn, st_y+offset))
        
        self.draw_text_outline(screen, "BACKGROUND", self.font_label, COLOR_TEXT_MAIN, (0,0,0), (cx_lbl, st_y+gp_y+offset), "center")
        self.btn_bg_sub.draw(screen); self.btn_bg_add.draw(screen)
        self.draw_text_outline(screen, f"{self.bgs[self.bg_idx]}", self.font_val, COLOR_GLOW_BLUE, (0,0,0), (cx_btn, st_y+gp_y+offset), "center")
        
        self.draw_text_outline(screen, "PIPE TRADES", self.font_label, COLOR_TEXT_MAIN, (0,0,0), (cx_lbl, st_y+gp_y*2+offset), "center")
        self.btn_swap_sub.draw(screen); self.btn_swap_add.draw(screen)
        self.draw_text_outline(screen, "INF" if self.swaps>20 else f"{self.swaps:02d}", self.font_val, COLOR_GLOW_BLUE, (0,0,0), (cx_btn, st_y+gp_y*2+offset))

        self.draw_text_outline(screen, "MAX MOVES", self.font_label, COLOR_TEXT_MAIN, (0,0,0), (cx_lbl, st_y+gp_y*3+offset), "center")
        self.btn_move_sub.draw(screen); self.btn_move_add.draw(screen)
        self.draw_text_outline(screen, "INF" if self.moves>50 else f"{self.moves:02d}", self.font_val, COLOR_GLOW_BLUE, (0,0,0), (cx_btn, st_y+gp_y*3+offset))

        self.draw_text_outline(screen, "BOARD SIZE", self.font_label, COLOR_TEXT_MAIN, (0,0,0), (cx_lbl, st_y+gp_y*4+offset), "center")
        self.btn_size_sub.draw(screen); self.btn_size_add.draw(screen)
        sz = self.sizes[self.size_idx]
        self.draw_text_outline(screen, f"{sz}x{sz}", self.font_val, COLOR_GLOW_BLUE, (0,0,0), (cx_btn, st_y+gp_y*4+offset))
        
        self.draw_text_outline(screen, "ALLOWED PIPES", self.font_label, COLOR_TEXT_MAIN, (0,0,0), (WINDOW_WIDTH - 140, 110), "center")
        for ptype, btn in self.pipe_btns.items():
            btn.draw(screen) 
            # Hiệu ứng Holo Cyberpunk khi chọn ống
            if self.pipe_active[ptype]: 
                pygame.draw.rect(screen, COLOR_GLOW_BLUE, btn.rect, 3, border_radius=10)
                # Đổ bóng Glow ra ngoài
                pygame.draw.rect(screen, (0, 255, 255, 100), btn.rect.inflate(8,8), 2, border_radius=10) 
            if self.pipe_imgs[ptype]: screen.blit(self.pipe_imgs[ptype], self.pipe_imgs[ptype].get_rect(center=btn.rect.center))
        
        pygame.draw.line(screen, (100, 100, 120), (50, WINDOW_HEIGHT - 100), (WINDOW_WIDTH - 50, WINDOW_HEIGHT - 100), 2)
        self.btn_back.draw(screen)
        if not is_unlocked:
            self.draw_text_outline(screen, "LOCKED! BUY IN SHOP", get_en_font(20), COLOR_PURCHASE, (0,0,0), (WINDOW_WIDTH//2, WINDOW_HEIGHT - 115))
            self.btn_play.bg_color = (80, 80, 80)
        else: self.btn_play.bg_color = C_BRIGHT_GREEN
        self.btn_play.draw(screen)


class PauseMenu:
    def __init__(self):
        self.overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.overlay.set_alpha(210) 
        self.overlay.fill((0, 0, 0))
        center_x, center_y = WINDOW_WIDTH//2, WINDOW_HEIGHT//2
        btn_w, btn_h = 320, 60
        btn_font = 24
        start_x = center_x - btn_w//2
        self.btn_restart = Button(start_x, center_y-120, btn_w, btn_h, "RESTART", (52, 152, 219), font_size=btn_font)
        self.btn_ai = Button(start_x, center_y-40, btn_w, btn_h, "AI SOLVE (-100)", (155, 89, 182), font_size=btn_font)
        self.btn_exit = Button(start_x, center_y+40, btn_w, btn_h, "EXIT", COLOR_PURCHASE, font_size=btn_font)
        self.action = None 

    def handle_event(self, event):
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()
        self.btn_restart.check_hover(mouse_pos)
        self.btn_ai.check_hover(mouse_pos)
        self.btn_exit.check_hover(mouse_pos)
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.btn_restart.is_clicked(mouse_pos, mouse_pressed): self.action = "RESTART"
            elif self.btn_ai.is_clicked(mouse_pos, mouse_pressed): self.action = "AI_SOLVE"
            elif self.btn_exit.is_clicked(mouse_pos, mouse_pressed): self.action = "EXIT"

    def draw(self, screen): 
        screen.blit(self.overlay, (0, 0))
        self.btn_restart.draw(screen)
        self.btn_ai.draw(screen)
        self.btn_exit.draw(screen)


class TutorialPopup:
    def __init__(self):
        self.overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.overlay.set_alpha(200)
        self.overlay.fill((0, 0, 0))
        self.font_title = get_vn_font(40, bold=True)
        self.font_text = get_vn_font(26, bold=False)
        self.popup_rect = pygame.Rect(WINDOW_WIDTH//2-320, WINDOW_HEIGHT//2-200, 640, 400)
        self.btn_understand = Button(WINDOW_WIDTH//2-140, WINDOW_HEIGHT//2+110, 280, 60, "ĐÃ HIỂU!", COLOR_GLOW_BLUE, is_vn=True, font_size=26)
        self.action = None

    def handle_event(self, event):
        mouse_pos = pygame.mouse.get_pos()
        self.btn_understand.check_hover(mouse_pos)
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.btn_understand.is_clicked(mouse_pos, pygame.mouse.get_pressed()): 
                self.action = "UNDERSTOOD"

    def draw_text_outline(self, screen, text, font, text_color, outline_color, pos, center=False):
        outline_width = 2
        for dx in [-outline_width, 0, outline_width]:
            for dy in [-outline_width, 0, outline_width]:
                if dx != 0 or dy != 0:
                    txt_surface = font.render(text, True, outline_color)
                    rect = txt_surface.get_rect(center=pos) if center else txt_surface.get_rect(topleft=pos)
                    screen.blit(txt_surface, rect)
        txt_surface = font.render(text, True, text_color)
        rect = txt_surface.get_rect(center=pos) if center else txt_surface.get_rect(topleft=pos)
        screen.blit(txt_surface, rect)

    def draw(self, screen):
        screen.blit(self.overlay, (0, 0))
        pygame.draw.rect(screen, COLOR_PANEL, self.popup_rect, border_radius=15)
        pygame.draw.rect(screen, COLOR_GLOW_BLUE, self.popup_rect, 4, border_radius=15)
        self.draw_text_outline(screen, "HƯỚNG DẪN CƠ BẢN", self.font_title, COLOR_GLOW_BLUE, (0, 0, 0), (WINDOW_WIDTH//2, self.popup_rect.top+45), center=True)
        instructions = ["1. Click chuột TRÁI để xoay ống.", "2. Nối thông nước từ GÓC TRÁI-TRÊN.", "3. Click HINT để xem gợi ý (FREE)", "MỤC TIÊU: Nước chảy đến PHẢI-DƯỚI!"]
        for i, text in enumerate(instructions): 
            color = COLOR_GLOW_YELLOW if i==3 else COLOR_TEXT_MAIN
            self.draw_text_outline(screen, text, self.font_text, color, (0, 0, 0), (self.popup_rect.left+40, self.popup_rect.top+115+i*48))
        self.btn_understand.draw(screen)


class WinPopup:
    def __init__(self):
        self.action = None; self.earned_coins = 0; self.is_win = True
        # Phóng to Title lên 55 và Reward lên 40 cho bự chà bá
        self.font_title = get_en_font(55); self.font_reward = get_en_font(40)
        btn_w, btn_h = 180, 60; btn_font = 20; y_pos = WINDOW_HEIGHT//2+70
        self.btn_replay = Button(WINDOW_WIDTH//2-290, y_pos, btn_w, btn_h, "REPLAY", (52, 152, 219), font_size=btn_font)
        self.btn_next = Button(WINDOW_WIDTH//2-90, y_pos, btn_w, btn_h, "NEXT", COLOR_GLOW_BLUE, font_size=btn_font)
        self.btn_menu = Button(WINDOW_WIDTH//2+110, y_pos, btn_w, btn_h, "MENU", COLOR_PURCHASE, font_size=btn_font)
        # Nút mua thêm lượt màu Vàng rực rỡ
        self.btn_buy_moves = Button(WINDOW_WIDTH//2-90, y_pos, btn_w, btn_h, "+5 MOVES (100)", C_BRIGHT_GOLD, font_size=18)

    def handle_event(self, event):
        mouse_pos = pygame.mouse.get_pos(); mouse_pressed = pygame.mouse.get_pressed()
        self.btn_replay.check_hover(mouse_pos); self.btn_next.check_hover(mouse_pos); self.btn_menu.check_hover(mouse_pos)
        if not self.is_win: self.btn_buy_moves.check_hover(mouse_pos) # Hover nút mua
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.btn_replay.is_clicked(mouse_pos, mouse_pressed): self.action = "REPLAY"
            elif self.is_win and self.btn_next.is_clicked(mouse_pos, mouse_pressed): self.action = "NEXT"
            elif self.btn_menu.is_clicked(mouse_pos, mouse_pressed): self.action = "MENU"
            elif not self.is_win and self.btn_buy_moves.is_clicked(mouse_pos, mouse_pressed): self.action = "BUY_MOVES"

    def draw_text_outline(self, screen, text, font, text_color, outline_color, center_pos):
        for dx, dy in [(-3,-3), (3,3), (-3,3), (3,-3)]:
            txt = font.render(text, True, outline_color); screen.blit(txt, txt.get_rect(center=(center_pos[0]+dx, center_pos[1]+dy)))
        txt = font.render(text, True, text_color); screen.blit(txt, txt.get_rect(center=center_pos))

    def draw(self, screen):
        ov = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA); ov.fill((0, 0, 0, 190)); screen.blit(ov, (0, 0))
        box_w, box_h = 650, 300; box_x, box_y = (WINDOW_WIDTH - box_w)//2, (WINDOW_HEIGHT - box_h)//2
        pygame.draw.rect(screen, COLOR_PANEL, (box_x, box_y, box_w, box_h), border_radius=15)
        
        if self.is_win:
            pygame.draw.rect(screen, COLOR_GLOW_BLUE, (box_x, box_y, box_w, box_h), 5, border_radius=15)
            self.draw_text_outline(screen, "LEVEL COMPLETED!", self.font_title, COLOR_GLOW_BLUE, (0,0,0), (WINDOW_WIDTH//2, box_y+60))
            # Hạ trục Y xuống 140 để chữ Reward to không đè lên Title
            self.draw_text_outline(screen, f"REWARD: +{self.earned_coins} COINS", self.font_reward, COLOR_GLOW_YELLOW, (0,0,0), (WINDOW_WIDTH//2, box_y+140))
            self.btn_replay.rect.x = WINDOW_WIDTH//2-290; self.btn_menu.rect.x = WINDOW_WIDTH//2+110
            self.btn_next.draw(screen)
        else:
            pygame.draw.rect(screen, (231, 76, 60), (box_x, box_y, box_w, box_h), 5, border_radius=15)
            self.draw_text_outline(screen, "GAME OVER!", self.font_title, (231, 76, 60), (0,0,0), (WINDOW_WIDTH//2, box_y+60))
            # Hạ trục Y xuống 140 tương tự
            self.draw_text_outline(screen, "OUT OF MOVES!", self.font_reward, (255, 255, 255), (0,0,0), (WINDOW_WIDTH//2, box_y+140))
            
            # Căn lại tọa độ để hiển thị đủ 3 nút
            self.btn_replay.rect.x = WINDOW_WIDTH//2-290
            self.btn_buy_moves.rect.x = WINDOW_WIDTH//2-90
            self.btn_menu.rect.x = WINDOW_WIDTH//2+110
            self.btn_buy_moves.draw(screen)
            
        self.btn_replay.draw(screen); self.btn_menu.draw(screen)


class SkinScreen:
    def __init__(self):
        self.font_title = get_en_font(60); self.font_name = get_en_font(40); self.font_price = get_en_font(24)
        self.next_state = None
        # TỪ ĐIỂN SKIN ĐỒNG GIÁ 1000 (Trừ Standard miễn phí)
        self.skins = [
            {"id": "DEFAULT", "name": "STANDARD", "border": (50, 30, 20), "metal": (190, 115, 60), "on": (150, 255, 220), "glow": (0, 200, 150), "bg": (15,10,25), "price": 0},
            {"id": "CYBER_NEON", "name": "CYBER NEON", "border": (20, 20, 30), "metal": (40, 40, 60), "on": (255, 100, 255), "glow": (200, 0, 200), "bg": (20,10,25), "price": 1000},
            {"id": "MAGMA_FORGE", "name": "MAGMA FORGE", "border": (40, 10, 10), "metal": (80, 20, 20), "on": (255, 200, 100), "glow": (200, 50, 0), "bg": (30,10,10), "price": 1000},
            {"id": "BIO_PLANT", "name": "BIO PLANT", "border": (20, 30, 10), "metal": (40, 70, 30), "on": (150, 255, 150), "glow": (50, 200, 50), "bg": (15,25,15), "price": 1000},
            {"id": "GOLDEN_VIP", "name": "GOLDEN VIP", "border": (100, 70, 0), "metal": (200, 150, 0), "on": (255, 255, 200), "glow": (255, 180, 0), "bg": (30,25,10), "price": 1000}
        ]
        self.selected_idx = 0
        self.btn_prev = Button(WINDOW_WIDTH//2 - 250, 270, 60, 60, "<", COLOR_PANEL, font_size=40)
        self.btn_next = Button(WINDOW_WIDTH//2 + 190, 270, 60, 60, ">", COLOR_PANEL, font_size=40)
        self.btn_action = Button(WINDOW_WIDTH//2 - 125, 480, 250, 60, "EQUIP", C_BRIGHT_GREEN, font_size=30)
        self.btn_back = Button(20, 20, 60, 60, "X", COLOR_PURCHASE, font_size=36)

    def handle_event(self, event, player_coins, unlocked_skins, equipped_skin):
        m_pos = pygame.mouse.get_pos(); m_pre = pygame.mouse.get_pressed()
        for btn in [self.btn_prev, self.btn_next, self.btn_action, self.btn_back]: btn.check_hover(m_pos)

        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.btn_back.is_clicked(m_pos, m_pre): self.next_state = STATE_DASHBOARD
            elif self.btn_prev.is_clicked(m_pos, m_pre): self.selected_idx = (self.selected_idx - 1) % len(self.skins)
            elif self.btn_next.is_clicked(m_pos, m_pre): self.selected_idx = (self.selected_idx + 1) % len(self.skins)
            elif self.btn_action.is_clicked(m_pos, m_pre):
                skin = self.skins[self.selected_idx]
                if skin["id"] in unlocked_skins:
                    if equipped_skin != skin["id"]: return "EQUIP_" + skin["id"] # ĐÃ CÓ THÌ TRANG BỊ
                elif player_coins >= skin["price"]: return "BUY_" + skin["id"] # CHƯA CÓ THÌ PHẢI MUA
        return None

    def draw_text_outline(self, screen, text, font, text_color, outline_color, center_pos):
        for dx, dy in [(-2,-2), (2,2), (-2,2), (2,-2)]:
            txt = font.render(text, True, outline_color); screen.blit(txt, txt.get_rect(center=(center_pos[0]+dx, center_pos[1]+dy)))
        txt = font.render(text, True, text_color); screen.blit(txt, txt.get_rect(center=center_pos))

    def draw(self, screen, player_coins, unlocked_skins, equipped_skin):
        skin = self.skins[self.selected_idx]
        screen.fill(skin["bg"]) 

        self.draw_text_outline(screen, "SKIN SHOP", self.font_title, COLOR_GLOW_GOLD, (0,0,0), (WINDOW_WIDTH//2, 60))
        self.draw_text_outline(screen, f"COINS: {player_coins}", self.font_price, COLOR_GLOW_YELLOW, (0,0,0), (WINDOW_WIDTH-100, 30))

        cx, cy = WINDOW_WIDTH//2, 300
        pygame.draw.rect(screen, COLOR_PANEL, (cx - 150, cy - 120, 300, 240), border_radius=20)
        pygame.draw.rect(screen, skin["glow"], (cx - 150, cy - 120, 300, 240), 4, border_radius=20)

        # ====== VẼ MÔ PHỎNG ỐNG NƯỚC THEO CHỦ ĐỀ SKIN ======
        c_border, c_metal = skin["border"], skin["metal"]
        p_on, p_glow = skin["on"], skin["glow"]
        pygame.draw.rect(screen, c_border, (cx - 104, cy - 20, 208, 40), border_radius=5)
        pygame.draw.rect(screen, c_metal, (cx - 100, cy - 14, 200, 28), border_radius=2)
        pygame.draw.rect(screen, p_on, (cx - 100, cy - 6, 200, 12))
        pygame.draw.rect(screen, p_glow, (cx - 100, cy - 2, 200, 4))
        pygame.draw.circle(screen, c_border, (cx, cy), 30)
        pygame.draw.circle(screen, c_metal, (cx, cy), 24)
        pygame.draw.circle(screen, p_on, (cx, cy), 14)
        pygame.draw.circle(screen, p_glow, (cx, cy), 6)

        self.draw_text_outline(screen, skin["name"], self.font_name, p_on, (0,0,0), (cx, 400))

        # LOGIC NÚT BẤM: CHƯA MUA -> HIỆN GIÁ, ĐÃ MUA -> HIỆN TRANG BỊ
        if skin["id"] == equipped_skin:
            self.btn_action.text = "EQUIPPED"; self.btn_action.bg_color = (80, 80, 80)
        elif skin["id"] in unlocked_skins:
            self.btn_action.text = "EQUIP"; self.btn_action.bg_color = C_BRIGHT_CYAN
        else:
            self.btn_action.text = f"BUY ({skin['price']})"; 
            self.btn_action.bg_color = C_BRIGHT_GREEN if player_coins >= skin["price"] else COLOR_PURCHASE

        self.btn_prev.draw(screen); self.btn_next.draw(screen)
        self.btn_action.draw(screen); self.btn_back.draw(screen)


class QuestsScreen:
    def __init__(self, quests=None):
        self.quests = quests or []
        self.next_state = None
        self.font = get_vn_font(45, bold=True)
        self.font_card_title = get_vn_font(24, bold=True)
        self.font_card_desc = get_vn_font(18, bold=False)
        self.font_small = get_vn_font(16, bold=False)
        try:
            raw_bg = pygame.image.load(BG_GAME_PATH).convert()
            self.bg = pygame.transform.smoothscale(raw_bg, (WINDOW_WIDTH, WINDOW_HEIGHT))
        except: self.bg = None
        self.btn_back = Button(WINDOW_WIDTH - 75, 25, 50, 50, "X", COLOR_PURCHASE, font_size=30, is_vn=False)
        self.quest_buttons = {}
        self.notifications = []
        card_x, card_y, card_h, gap = 50, 100, 85, 10
        for i, quest in enumerate(QUEST_DEFINITIONS):
            y = card_y + i * (card_h + gap)
            btn = Button(card_x + 710, y + 18, 190, 48, "NHẬN", (46, 204, 113), font_size=20, is_vn=True)
            self.quest_buttons[quest["id"]] = btn

    def add_notification(self, text, color=(255, 215, 0)):
        self.notifications.append({"text": text, "x": WINDOW_WIDTH // 2, "y": WINDOW_HEIGHT - 40, "alpha": 255, "color": color})

    def _quest_progress(self, quest_data, quest):
        stats = quest_data.get("stats", {})
        return int(stats.get(quest["metric"], 0))

    def _is_claimed(self, quest_data, quest_id):
        return quest_id in quest_data.get("claimed", [])

    def _is_completed(self, quest_data, quest):
        return self._quest_progress(quest_data, quest) >= int(quest["target"])

    def handle_event(self, event, quest_data):
        mouse_pos = pygame.mouse.get_pos()
        self.btn_back.check_hover(mouse_pos)
        for quest in QUEST_DEFINITIONS:
            btn = self.quest_buttons[quest["id"]]
            btn.check_hover(mouse_pos)
        if event.type == pygame.MOUSEBUTTONDOWN and self.btn_back.is_clicked(mouse_pos, pygame.mouse.get_pressed()):
            self.next_state = STATE_DASHBOARD
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pressed = pygame.mouse.get_pressed()
            for quest in QUEST_DEFINITIONS:
                quest_id = quest["id"]
                btn = self.quest_buttons[quest_id]
                if self._is_claimed(quest_data, quest_id): continue
                if not self._is_completed(quest_data, quest): continue
                if btn.is_clicked(mouse_pos, pressed): return ("CLAIM_QUEST", quest_id)
        return None

    def draw_text_outline(self, screen, text, font, text_color, outline_color, center_pos):
        outline_width = 2
        for dx in [-outline_width, 0, outline_width]:
            for dy in [-outline_width, 0, outline_width]:
                if dx != 0 or dy != 0:
                    txt_surface = font.render(text, True, outline_color)
                    screen.blit(txt_surface, txt_surface.get_rect(center=(center_pos[0]+dx, center_pos[1]+dy)))
        txt_surface = font.render(text, True, text_color)
        screen.blit(txt_surface, txt_surface.get_rect(center=center_pos))

    def draw(self, screen, quest_data):
        if hasattr(self, 'bg') and self.bg: screen.blit(self.bg, (0, 0))
        else: screen.fill(COLOR_BG_DARK)
        self.draw_text_outline(screen, "NHIỆM VỤ", self.font, (0, 255, 255), (0, 0, 0), (WINDOW_WIDTH//2, 55))
        card_x, card_y, card_w, card_h, gap = 50, 100, 920, 85, 10
        for i, quest in enumerate(QUEST_DEFINITIONS):
            y = card_y + i * (card_h + gap)
            progress = self._quest_progress(quest_data, quest)
            target, clamped = int(quest["target"]), min(progress, int(quest["target"]))
            completed = progress >= target
            claimed = self._is_claimed(quest_data, quest["id"])
            bg = (40, 45, 57) if not completed else (34, 72, 53)
            border = (115, 127, 159) if not completed else (46, 204, 113)
            pygame.draw.rect(screen, bg, (card_x, y, card_w, card_h), border_radius=12)
            pygame.draw.rect(screen, border, (card_x, y, card_w, card_h), 2, border_radius=12)
            title_surface = self.font_card_title.render(quest["title"], True, (255, 255, 255))
            screen.blit(title_surface, (card_x + 22, y + 14))
            desc_text = f"{quest['desc']}  | THƯỞNG: +{quest['reward']} XU"
            desc_surface = self.font_card_desc.render(desc_text, True, (222, 224, 230))
            screen.blit(desc_surface, (card_x + 22, y + 42))
            bar_x, bar_y, bar_w, bar_h = card_x + 22, y + 66, 440, 11
            pygame.draw.rect(screen, (18, 20, 25), (bar_x, bar_y, bar_w, bar_h), border_radius=6)
            fill_w = int(bar_w * (clamped / target)) if target > 0 else 0
            if fill_w > 0: pygame.draw.rect(screen, (75, 166, 235), (bar_x, bar_y, fill_w, bar_h), border_radius=6)
            pygame.draw.rect(screen, (190, 196, 210), (bar_x, bar_y, bar_w, bar_h), 1, border_radius=6)
            progress_text = f"Tiến độ: {clamped}/{target}"
            progress_surface = self.font_small.render(progress_text, True, (245, 245, 245))
            screen.blit(progress_surface, (bar_x + bar_w + 40, y + 60))
            btn = self.quest_buttons[quest["id"]]
            btn.rect.x, btn.rect.y = card_x + 710, y + 18
            if claimed: btn.text, btn.bg_color, btn.is_enabled = "ĐÃ NHẬN", (110, 110, 110), False
            elif completed: btn.text, btn.bg_color, btn.is_enabled = "NHẬN", (46, 204, 113), True
            else: btn.text, btn.bg_color, btn.is_enabled = "CHƯA XONG", (130, 130, 130), False
            btn.draw(screen)
        for notif in self.notifications[:]:
            self.draw_text_outline(screen, notif["text"], get_en_font(28), notif["color"], (0, 0, 0), (notif["x"], notif["y"]))
            notif["y"] -= 1; notif["alpha"] -= 4
            if notif["alpha"] <= 0: self.notifications.remove(notif)
        self.btn_back.draw(screen)

# ==========================================
# HÀM VẼ ỐNG NƯỚC VECTOR DÙNG CHUNG
# ==========================================
def generate_pipe_icon(ptype, size=44):
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    center = size // 2
    outer_w, metal_w, water_w = 22, 16, 6
    c_border, c_metal, c_water = (50, 30, 20), (190, 115, 60), (40, 50, 45)
    
    conns = {'I': [1,0,1,0], 'L': [1,1,0,0], 'T': [1,1,1,0], '+': [1,1,1,1], 'C': [1,0,0,0], 'P': [1,0,0,0], 'O': [1,0,1,0], 'X': [1,1,1,1]}.get(ptype, [0,0,0,0])
    
    pygame.draw.circle(surf, c_border, (center, center), outer_w//2)
    for i, c in enumerate(conns):
        if c: pygame.draw.line(surf, c_border, (center, center), [(center,0), (size,center), (center,size), (0,center)][i], outer_w)
        
    pygame.draw.circle(surf, c_metal, (center, center), metal_w//2)
    for i, c in enumerate(conns):
        if c: pygame.draw.line(surf, c_metal, (center, center), [(center,0), (size,center), (center,size), (0,center)][i], metal_w)
        
    pygame.draw.circle(surf, c_water, (center, center), water_w//2)
    for i, c in enumerate(conns):
        if c: pygame.draw.line(surf, c_water, (center, center), [(center,0), (size,center), (center,size), (0,center)][i], water_w)
        
    if ptype in ['T', '+']:
        pygame.draw.circle(surf, c_border, (center, center), metal_w//2 + 2)
        pygame.draw.circle(surf, (230, 180, 60), (center, center), metal_w//2)
        pygame.draw.circle(surf, c_water, (center, center), 3)
    elif ptype == 'P':
        pygame.draw.circle(surf, (138, 43, 226), (center, center), metal_w//2 + 6)
        pygame.draw.circle(surf, (75, 0, 130), (center, center), metal_w//2 + 2)
        pygame.draw.circle(surf, (10, 5, 20), (center, center), metal_w//2)
    elif ptype == 'C':
        pygame.draw.circle(surf, c_border, (center, center), metal_w//2 + 2)
        pygame.draw.circle(surf, (220, 50, 40), (center, center), metal_w//2)
        pygame.draw.circle(surf, (120, 20, 20), (center, center), metal_w//2 - 2)
    elif ptype == 'O':
        pts = [(center-6, center-8), (center+6, center-8), (center+6, center+1), (center+10, center+1), (center, center+10), (center-10, center+1), (center-6, center+1)]
        pygame.draw.polygon(surf, c_border, pts)
        pygame.draw.polygon(surf, (60, 80, 70), pts, 0)
    elif ptype == 'X':
        bridge = pygame.Rect(center - metal_w//2, center - metal_w//2, metal_w, metal_w)
        pygame.draw.rect(surf, c_border, bridge.inflate(4, 4), border_radius=3)
        pygame.draw.rect(surf, c_metal, bridge.inflate(1, 1), border_radius=3)
    return surf

# ==========================================
# MÀN HÌNH POPUP CHỌN ỐNG KHI TRADE (TRONG GAME)
# ==========================================
class TradePopup:
    def __init__(self):
        self.pipe_types = ['I', 'L', 'T', '+', 'C', 'P', 'O', 'X']
        self.pipe_imgs = {pt: generate_pipe_icon(pt, 50) for pt in self.pipe_types}
        self.btns = {}
        
        box_w, box_h = 500, 360
        start_x = WINDOW_WIDTH//2 - box_w//2 + 50
        start_y = WINDOW_HEIGHT//2 - box_h//2 + 100
        
        for i, pt in enumerate(self.pipe_types):
            bx = start_x + (i % 4) * 100
            by = start_y + (i // 4) * 100
            self.btns[pt] = Button(bx, by, 80, 80, "", C_BRIGHT_CYAN, font_size=30)
            
        self.btn_cancel = Button(WINDOW_WIDTH//2 - 100, WINDOW_HEIGHT//2 + box_h//2 - 40, 200, 50, "CANCEL", COLOR_PURCHASE, font_size=24)
        
    def handle_event(self, event):
        m_pos = pygame.mouse.get_pos(); m_pre = pygame.mouse.get_pressed()
        self.btn_cancel.check_hover(m_pos)
        for btn in self.btns.values(): btn.check_hover(m_pos)
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.btn_cancel.is_clicked(m_pos, m_pre): return "CANCEL"
            for pt, btn in self.btns.items():
                if btn.is_clicked(m_pos, m_pre): return pt
        return None
        
    def draw(self, screen):
        ov = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        ov.fill((0,0,0,210)); screen.blit(ov, (0,0))
        
        box_w, box_h = 500, 360
        box_x, box_y = WINDOW_WIDTH//2 - box_w//2, WINDOW_HEIGHT//2 - box_h//2
        pygame.draw.rect(screen, COLOR_PANEL, (box_x, box_y, box_w, box_h), border_radius=15)
        pygame.draw.rect(screen, COLOR_GLOW_GOLD, (box_x, box_y, box_w, box_h), 4, border_radius=15)
        
        t = get_en_font(40).render("SELECT PIPE", True, COLOR_GLOW_GOLD)
        screen.blit(t, t.get_rect(center=(WINDOW_WIDTH//2, box_y + 40)))
        
        for pt, btn in self.btns.items():
            btn.draw(screen)
            if self.pipe_imgs[pt]: screen.blit(self.pipe_imgs[pt], self.pipe_imgs[pt].get_rect(center=btn.rect.center))
            
        self.btn_cancel.draw(screen)