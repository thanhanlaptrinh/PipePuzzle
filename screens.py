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

class Button:
    def __init__(self, x, y, w, h, text, bg_color, text_color=(255, 255, 255), disable_hover_effect=False, font_size=28):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.bg_color = bg_color
        self.text_color = text_color
        self.is_hovered = False
        self.is_enabled = True
        self.disable_hover_effect = disable_hover_effect 
        self.font = pygame.font.SysFont('tahoma', font_size, bold=True) 

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

        self.draw_text_outline(screen, self.text, self.font, current_text, (0, 0, 0), self.rect.center)

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
    def __init__(self, x, y, w, h, title, desc, price, img_path, action_id, font_size_title=22):
        self.rect = pygame.Rect(x, y, w, h)
        self.title = title
        self.desc = desc
        self.price = price
        self.action_id = action_id
        
        try:
            raw_img = pygame.image.load(img_path).convert_alpha()
            img_size = min(120, w - 40, h - 140)
            self.img = pygame.transform.smoothscale(raw_img, (img_size, img_size))
        except: self.img = None

        self.font_title = pygame.font.SysFont('tahoma', font_size_title, bold=True)
        self.font_desc = pygame.font.SysFont('tahoma', 16, bold=False)
        
        btn_w, btn_h = 140, 45
        self.btn_buy = Button(x + (w - btn_w)//2, y + h - 60, btn_w, btn_h, f"{price} XU", COLOR_PURCHASE, font_size=20)

    def check_hover(self, mouse_pos, scroll_y=0):
        adjusted_mouse_pos = (mouse_pos[0], mouse_pos[1] + scroll_y)
        self.btn_buy.check_hover(adjusted_mouse_pos)

    def is_clicked(self, mouse_pos, mouse_pressed, scroll_y=0):
        adjusted_mouse_pos = (mouse_pos[0], mouse_pos[1] + scroll_y)
        return self.btn_buy.is_clicked(adjusted_mouse_pos, mouse_pressed)

    def draw(self, surface):
        pygame.draw.rect(surface, COLOR_PANEL, self.rect, border_radius=15)
        pygame.draw.rect(surface, (60, 50, 80), self.rect, width=2, border_radius=15)
        
        txt_title = self.font_title.render(self.title, True, COLOR_GLOW_BLUE)
        surface.blit(txt_title, (self.rect.x + 20, self.rect.y + 15))
        
        txt_desc = self.font_desc.render(self.desc, True, COLOR_TEXT_DESC)
        surface.blit(txt_desc, (self.rect.x + 20, self.rect.y + 45))
        
        if self.img:
            img_rect = self.img.get_rect(center=(self.rect.centerx, self.rect.y + 135))
            surface.blit(self.img, img_rect)
            
        self.btn_buy.draw(surface)


class ShopScreen:
    def __init__(self):
        self.next_state = None
        self.font_title = pygame.font.SysFont('tahoma', 70, bold=True)
        self.font_menu = pygame.font.SysFont('tahoma', 32, bold=True)

        try:
            raw_bg = pygame.image.load("assets/images/shop_bg.png").convert()
            self.bg = pygame.transform.smoothscale(raw_bg, (WINDOW_WIDTH, WINDOW_HEIGHT))
        except: self.bg = None
        
        try:
            self.img_coin = pygame.image.load("assets/images/coin_icon.png").convert_alpha()
            self.img_coin = pygame.transform.smoothscale(self.img_coin, (30, 30))
        except: self.img_coin = None

        self.btn_back = Button(20, 20, 140, 50, "< MENU", (0, 0, 0, 0), (255, 255, 255))

        self.menu_width = 220
        self.menu_rect = pygame.Rect(0, 100, self.menu_width, WINDOW_HEIGHT - 100)
        self.content_rect = pygame.Rect(self.menu_width, 100, WINDOW_WIDTH - self.menu_width - 25, WINDOW_HEIGHT - 100)
        
        self.scroll_y = 0
        self.is_dragging_scroll = False
        self.scrollbar_rect = pygame.Rect(WINDOW_WIDTH - 20, 110, 15, WINDOW_HEIGHT - 120)
        self.thumb_height = 100 
        self.thumb_rect = pygame.Rect(WINDOW_WIDTH - 20, 110, 15, self.thumb_height)

        self.shop_items = []
        
        card_w, card_h = 260, 280
        start_x = 30
        
        self.y_items = 20
        self.shop_items.append(ShopItemCard(start_x, self.y_items + 50, card_w, card_h, 
                                           "1 x CÂY CUỐC", "Đập vỡ 1 viên đá cản đường", 100, 
                                           "assets/images/shop_pickaxe_1.png", "BUY_PICKAXE_1"))
        self.shop_items.append(ShopItemCard(start_x + card_w + 30, self.y_items + 50, card_w, card_h, 
                                           "3 x GÓI CUỐC", "Tiết kiệm 50 xu (Mua khi hết)", 250, 
                                           "assets/images/shop_pickaxe_3.png", "BUY_PICKAXE_3"))

        self.y_skins = self.y_items + card_h + 100 
        
        self.y_acts = self.y_skins + 150 
        for i in range(2, 6): 
            row = (i-2) // 2
            col = (i-2) % 2
            ax = start_x + col * (card_w + 30)
            ay = self.y_acts + 50 + row * (card_h + 30)
            self.shop_items.append(ShopItemCard(ax, ay, card_w, card_h, 
                                               f"MỞ ACT {i}", f"Unlock Chap {i} (12 màn mới)", 1500, 
                                               "assets/images/shop_act_icon.png", f"BUY_ACT_{i}", font_size_title=26))

        self.total_content_height = ay + card_h + 50 
        
        if self.total_content_height > self.content_rect.h:
            ratio = self.content_rect.h / self.total_content_height
            self.thumb_height = max(30, int(self.scrollbar_rect.h * ratio))
            self.thumb_rect.h = self.thumb_height
        else: self.thumb_height = self.scrollbar_rect.h; self.thumb_rect.h = self.thumb_height

        self.notif_msg = ""; self.notif_alpha = 0; self.notif_color = (255, 255, 255)

    def show_notif(self, msg, color):
        self.notif_msg = msg; self.notif_color = color; self.notif_alpha = 255

    def handle_event(self, event, coins, pickaxes, unlocked_levels):
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
            self.scroll_y = max(0, min(max_scroll, self.scroll_y - event.y * 40))

        if max_scroll > 0:
            thumb_ratio = self.scroll_y / max_scroll
            self.thumb_rect.y = self.scrollbar_rect.y + int(thumb_ratio * (self.scrollbar_rect.h - self.thumb_height))

        if self.content_rect.collidepoint(mouse_pos):
            content_mouse_pos = (mouse_pos[0] - self.content_rect.x, mouse_pos[1] - self.content_rect.y + self.scroll_y)
        else:
            content_mouse_pos = (-100, -100) 

        for item in self.shop_items:
            item.check_hover(content_mouse_pos) 
            
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if item.is_clicked(content_mouse_pos, mouse_pressed):
                    act_num_str = item.action_id.split('_')[-1]
                    
                    if item.action_id == "BUY_PICKAXE_1":
                        if pickaxes >= 3: self.show_notif("TÚI CUỐC ĐÃ ĐẦY (TỐI ĐA 3)!", (231, 76, 60))
                        elif coins >= 100: self.show_notif("MUA THÀNH CÔNG 1 CUỐC!", (46, 204, 113)); return "BUY_PICKAXE_1"
                        else: self.show_notif("KHÔNG ĐỦ XU!", (231, 76, 60))
                    elif item.action_id == "BUY_PICKAXE_3":
                        if pickaxes > 0: self.show_notif("CHỈ MUA KHI HẾT SẠCH CUỐC!", COLOR_GLOW_YELLOW)
                        elif coins >= 250: self.show_notif("MUA THÀNH CÔNG 3 CUỐC!", (46, 204, 113)); return "BUY_PICKAXE_3"
                        else: self.show_notif("KHÔNG ĐỦ XU!", (231, 76, 60))
                    elif item.action_id.startswith("BUY_ACT_") and act_num_str.isdigit():
                        act_num = int(act_num_str)
                        act_start_lvl = (act_num - 1) * 12 + 1
                        if unlocked_levels >= act_start_lvl: self.show_notif(f"BẠN ĐÃ CÓ CHAPTER {act_num} RỒI!", COLOR_GLOW_YELLOW)
                        elif coins >= 1500: self.show_notif(f"MUA CHAPTER {act_num} THÀNH CÔNG!", COLOR_GLOW_BLUE); return item.action_id
                        else: self.show_notif(f"KHÔNG ĐỦ 1500 XU ĐỂ MUA ACT {act_num}!", (231, 76, 60))
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.btn_back.is_clicked(mouse_pos, mouse_pressed): self.next_state = STATE_DASHBOARD

        return None

    def draw_text_outline(self, screen, text, font, text_color, outline_color, center_pos, align="center"):
        outline_width = 2
        for dx in [-outline_width, 0, outline_width]:
            for dy in [-outline_width, 0, outline_width]:
                if dx != 0 or dy != 0:
                    txt_surface = font.render(text, True, outline_color)
                    if align == "center": rect = txt_surface.get_rect(center=center_pos)
                    else: rect = txt_surface.get_rect(topleft=center_pos)
                    screen.blit(txt_surface, rect)
        txt_surface = font.render(text, True, text_color)
        if align == "center": rect = txt_surface.get_rect(center=center_pos)
        else: rect = txt_surface.get_rect(topleft=center_pos)
        screen.blit(txt_surface, rect)

    def draw(self, screen, coins, pickaxes): 
        if self.bg: screen.blit(self.bg, (0, 0))
        else: screen.fill(COLOR_BG_DARK)
        
        self.draw_text_outline(screen, "SHOP", self.font_title, (255, 255, 255), (0, 0, 0), (WINDOW_WIDTH//2 - 60, 50))
        
        font_info = pygame.font.SysFont("tahoma", 26, bold=True)
        box_xu_rect = pygame.Rect(WINDOW_WIDTH - 250, 25, 220, 50)
        pygame.draw.rect(screen, (255, 255, 255), box_xu_rect, border_radius=10) 
        pygame.draw.rect(screen, (200, 200, 200), box_xu_rect, 2, border_radius=10) 
        
        if self.img_coin: 
            screen.blit(self.img_coin, (box_xu_rect.x + 10, box_xu_rect.y + 10))
            
        self.draw_text_outline(screen, f": {coins} XU", font_info, (241, 196, 15), (0,0,0), (box_xu_rect.x + 45, box_xu_rect.y + 10), "left")
        self.btn_back.draw(screen)

        pygame.draw.rect(screen, COLOR_PANEL, self.menu_rect)
        pygame.draw.line(screen, COLOR_GLOW_BLUE, (self.menu_width, 100), (self.menu_width, WINDOW_HEIGHT), 3) 
        
        menu_scroll_surf = pygame.Surface((self.menu_width, self.total_content_height), pygame.SRCALPHA)
        
        color_items = COLOR_GLOW_YELLOW if self.scroll_y < self.y_skins - 100 else COLOR_TEXT_DESC
        color_skins = COLOR_GLOW_YELLOW if self.y_skins - 100 <= self.scroll_y < self.y_acts - 100 else COLOR_TEXT_DESC
        color_chaps = COLOR_GLOW_YELLOW if self.scroll_y >= self.y_acts - 100 else COLOR_TEXT_DESC

        self.draw_text_outline(menu_scroll_surf, "ITEMS", self.font_menu, color_items, (0,0,0), (self.menu_width//2, self.y_items + 20))
        self.draw_text_outline(menu_scroll_surf, "SKINS", self.font_menu, color_skins, (0,0,0), (self.menu_width//2, self.y_skins + 20))
        self.draw_text_outline(menu_scroll_surf, "CHAPS", self.font_menu, color_chaps, (0,0,0), (self.menu_width//2, self.y_acts + 20))

        screen.blit(menu_scroll_surf, self.menu_rect.topleft, (0, self.scroll_y, self.menu_width, self.menu_rect.h))

        self.content_surface = pygame.Surface((self.content_rect.w, self.total_content_height), pygame.SRCALPHA)
        font_header = pygame.font.SysFont('tahoma', 24, bold=True)

        txt_h_items = font_header.render("VẬT PHẨM ĐÁNH ĐÁ", True, COLOR_GLOW_YELLOW)
        self.content_surface.blit(txt_h_items, (40, self.y_items))
        pygame.draw.line(self.content_surface, COLOR_GLOW_BLUE, (30, self.y_items + 35), (self.content_rect.w - 50, self.y_items + 35), 2)

        txt_h_skins = font_header.render("SKINS ỐNG NƯỚC (Sắp ra mắt)", True, (150, 150, 150))
        self.content_surface.blit(txt_h_skins, (40, self.y_skins))
        pygame.draw.line(self.content_surface, COLOR_GLOW_BLUE, (30, self.y_skins + 35), (self.content_rect.w - 50, self.y_skins + 35), 2)

        txt_h_acts = font_header.render("MỞ KHÓA MÀN CHƠI (CHAPTERS)", True, (155, 89, 182))
        self.content_surface.blit(txt_h_acts, (40, self.y_acts))
        pygame.draw.line(self.content_surface, (155, 89, 182), (30, self.y_acts + 35), (self.content_rect.w - 50, self.y_acts + 35), 2)

        for item in self.shop_items: item.draw(self.content_surface)
        
        screen.blit(self.content_surface, self.content_rect.topleft, (0, self.scroll_y, self.content_rect.w, self.content_rect.h))

        if self.thumb_height < self.scrollbar_rect.h: 
            pygame.draw.rect(screen, COLOR_BG_DARK, self.scrollbar_rect, border_radius=5) 
            pygame.draw.rect(screen,COLOR_GLOW_BLUE, self.thumb_rect, border_radius=5) 

        if self.notif_alpha > 0:
            font_notif = pygame.font.SysFont('tahoma', 30, bold=True)
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
        self.font_title = pygame.font.SysFont('tahoma', 70, bold=True)
        self.font_prompt = pygame.font.SysFont('tahoma', 32, bold=True) 
        self.font_input = pygame.font.SysFont('tahoma', 40, bold=True) 
        self.font_error = pygame.font.SysFont('tahoma', 22, bold=True) 
        self.player_name = ""; self.next_state = None; self.error_msg = ""
        box_w, box_h = 450, 70
        self.input_rect = pygame.Rect((WINDOW_WIDTH - box_w) // 2, (WINDOW_HEIGHT - box_h) // 2 + 40, box_w, box_h)
        self.btn_start = Button((WINDOW_WIDTH - 200) // 2, self.input_rect.bottom + 50, 200, 60, "BẮT ĐẦU", COLOR_GLOW_BLUE, font_size=32)
        self.cursor_visible = True; self.last_blink = pygame.time.get_ticks()

    def draw_text_outline(self, screen, text, font, text_color, outline_color, center_pos):
        outline_width = 3 
        for dx in [-outline_width, 0, outline_width]:
            for dy in [-outline_width, 0, outline_width]:
                if (dx != 0 or dy != 0):
                    txt_surface = font.render(text, True, outline_color)
                    screen.blit(txt_surface, txt_surface.get_rect(center=(center_pos[0]+dx, center_pos[1]+dy)))
        txt_surface = font.render(text, True, text_color)
        screen.blit(txt_surface, txt_surface.get_rect(center=center_pos))

    def handle_event(self, event):
        mouse_pos = pygame.mouse.get_pos(); self.btn_start.check_hover(mouse_pos)
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.btn_start.is_clicked(mouse_pos, pygame.mouse.get_pressed()):
                if len(self.player_name.strip()) > 0: self.next_state = STATE_DASHBOARD
                else: self.error_msg = "Vui lòng nhập tên!"
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                if len(self.player_name.strip()) > 0: self.next_state = STATE_DASHBOARD
                else: self.error_msg = "Vui lòng nhập tên!"
            elif event.key == pygame.K_BACKSPACE: 
                self.player_name = self.player_name[:-1]
                self.error_msg = ""
            else:
                if len(self.player_name) < 12: 
                    self.player_name += event.unicode
                    self.error_msg = ""
        return None

    def draw(self, screen):
        screen.fill(COLOR_BG_DARK)
        self.draw_text_outline(screen, "PIPE PUZZLE", self.font_title, COLOR_TEXT_MAIN, (0, 0, 0), (WINDOW_WIDTH // 2, 120))
        prompt_y = self.input_rect.top - 60
        self.draw_text_outline(screen, "Nhập tên của bạn:", self.font_prompt, COLOR_TEXT_DESC, (0, 0, 0), (WINDOW_WIDTH // 2, prompt_y))
        pygame.draw.rect(screen, (25, 25, 30), self.input_rect, border_radius=12)
        pygame.draw.rect(screen, COLOR_GLOW_BLUE, self.input_rect, width=3, border_radius=12)
        
        txt_surface = self.font_input.render(self.player_name, True, (255, 255, 255))
        txt_rect = txt_surface.get_rect(center=self.input_rect.center)
        screen.blit(txt_surface, txt_rect)
        
        current_time = pygame.time.get_ticks()
        if current_time - self.last_blink > 500: 
            self.cursor_visible = not self.cursor_visible
            self.last_blink = current_time
        if self.cursor_visible:
            cursor_x = txt_rect.right + 5 if len(self.player_name) > 0 else self.input_rect.centerx
            cursor_y_start = self.input_rect.centery - 20
            cursor_y_end = self.input_rect.centery + 20
            pygame.draw.line(screen, COLOR_GLOW_BLUE, (cursor_x, cursor_y_start), (cursor_x, cursor_y_end), 4)
            
        self.btn_start.draw(screen)
        if self.error_msg: 
            self.draw_text_outline(screen, self.error_msg, self.font_error, (231, 76, 60), (0, 0, 0), (WINDOW_WIDTH // 2, self.btn_start.rect.bottom + 40))


class DashboardScreen:
    def __init__(self):
        self.font_title = pygame.font.SysFont('tahoma', 70, bold=True)
        self.font_btn = pygame.font.SysFont('tahoma', 36, bold=True)
        self.font_small = pygame.font.SysFont('tahoma', 22, bold=True)
        self.next_state = None
        
        self.btn_play = Button(WINDOW_WIDTH//2 - 150, 250, 300, 60, "CHỌN MÀN CHƠI", COLOR_GLOW_BLUE, font_size=32)
        self.btn_shop = Button(WINDOW_WIDTH//2 - 150, 340, 300, 60, "CỬA HÀNG", COLOR_GLOW_YELLOW, font_size=32)
        self.btn_quests = Button(WINDOW_WIDTH//2 - 150, 430, 300, 60, "NHIỆM VỤ", (155, 89, 182), font_size=32)
        self.btn_skin = Button(WINDOW_WIDTH - 150, WINDOW_HEIGHT - 80, 120, 50, "SKIN", COLOR_GLOW_BLUE, font_size=28)
        self.btn_options = Button(30, WINDOW_HEIGHT - 80, 160, 50, "OPTIONS", (100, 100, 100))
        
        self.show_options_popup = False
        self.show_giftcode_popup = False
        self.giftcode_input = ""
        self.notifications = [] 
        
        box_w, box_h = 600, 450
        box_x, box_y = (WINDOW_WIDTH - box_w)//2, (WINDOW_HEIGHT - box_h)//2
        self.btn_opt_exit = Button(box_x + 40, box_y + 350, 150, 50, "THOÁT", COLOR_PURCHASE)
        self.btn_opt_rename = Button(box_x + 225, box_y + 350, 150, 50, "ĐỔI TÊN", COLOR_GLOW_BLUE)
        self.btn_opt_giftcode = Button(box_x + 410, box_y + 350, 150, 50, "GIFTCODE", COLOR_GLOW_YELLOW, disable_hover_effect=True)
        self.btn_opt_close = Button(box_x + box_w - 50, box_y + 10, 40, 40, "X", COLOR_PURCHASE)
        
        self.music_vol = 1.0
        self.sfx_vol = 1.0
        self.rect_music_slider = pygame.Rect(box_x + 220, box_y + 155, 300, 25)
        self.rect_sfx_slider = pygame.Rect(box_x + 220, box_y + 255, 300, 25)
        self.is_dragging_music = False
        self.is_dragging_sfx = False
        
        try:
            self.bg_sky = pygame.image.load("assets/images/sky.png").convert()
            self.bg_sky = pygame.transform.smoothscale(self.bg_sky, (WINDOW_WIDTH, WINDOW_HEIGHT))
        except: 
            self.bg_sky = None

    def handle_event(self, event, redeemed_codes):
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()
        
        if self.show_giftcode_popup:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    code = self.giftcode_input.upper()
                    if code in redeemed_codes: 
                        self.notifications.append({'text': "ĐÃ SỬ DỤNG!", 'x': WINDOW_WIDTH//2, 'y': WINDOW_HEIGHT//2, 'alpha': 255, 'color': COLOR_PURCHASE})
                        self.show_giftcode_popup = False
                        self.show_options_popup = True
                        self.giftcode_input = ""
                        return None
                    elif code == "UNPIPE": 
                        self.notifications.append({'text': "UNLOCK ALL LVL!", 'x': WINDOW_WIDTH//2, 'y': WINDOW_HEIGHT//2, 'alpha': 255, 'color': COLOR_GLOW_BLUE})
                        self.show_giftcode_popup = False
                        self.show_options_popup = True
                        self.giftcode_input = ""
                        return "UNLOCK_ALL"
                    elif code == "PIPEGOLD": 
                        self.notifications.append({'text': "+10.000 COIN", 'x': WINDOW_WIDTH//2, 'y': WINDOW_HEIGHT//2, 'alpha': 255, 'color': COLOR_GLOW_YELLOW})
                        self.show_giftcode_popup = False
                        self.show_options_popup = True
                        self.giftcode_input = ""
                        return "ADD_COINS"
                    else: 
                        self.notifications.append({'text': "KHÔNG HỢP LỆ!", 'x': WINDOW_WIDTH//2, 'y': WINDOW_HEIGHT//2, 'alpha': 255, 'color': COLOR_PURCHASE})
                        self.show_giftcode_popup = False
                        self.show_options_popup = True
                        self.giftcode_input = ""
                        return None
                elif event.key == pygame.K_BACKSPACE: 
                    self.giftcode_input = self.giftcode_input[:-1]
                elif event.key == pygame.K_ESCAPE: 
                    self.show_giftcode_popup = False
                    self.show_options_popup = True 
                else:
                    if len(self.giftcode_input) < 15: 
                        self.giftcode_input += event.unicode
            return None
            
        if self.show_options_popup:
            self.btn_opt_exit.check_hover(mouse_pos)
            self.btn_opt_rename.check_hover(mouse_pos)
            self.btn_opt_giftcode.check_hover(mouse_pos)
            self.btn_opt_close.check_hover(mouse_pos)
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.btn_opt_close.is_clicked(mouse_pos, mouse_pressed): 
                    self.show_options_popup = False
                elif self.btn_opt_exit.is_clicked(mouse_pos, mouse_pressed): 
                    import sys
                    pygame.quit()
                    sys.exit()
                elif self.btn_opt_rename.is_clicked(mouse_pos, mouse_pressed): 
                    self.next_state = STATE_MENU_NAME
                    self.show_options_popup = False
                elif self.btn_opt_giftcode.is_clicked(mouse_pos, mouse_pressed): 
                    self.show_options_popup = False
                    self.show_giftcode_popup = True
                    self.giftcode_input = ""
                    
                if mouse_pressed[0]:
                    if self.rect_music_slider.collidepoint(mouse_pos): self.is_dragging_music = True
                    if self.rect_sfx_slider.collidepoint(mouse_pos): self.is_dragging_sfx = True
                    
            elif event.type == pygame.MOUSEBUTTONUP: 
                self.is_dragging_music = False
                self.is_dragging_sfx = False
                
            if self.is_dragging_music or (mouse_pressed[0] and self.rect_music_slider.collidepoint(mouse_pos)): 
                self.music_vol = max(0.0, min(1.0, (mouse_pos[0] - self.rect_music_slider.x) / self.rect_music_slider.width))
                pygame.mixer.music.set_volume(self.music_vol)
                
            if self.is_dragging_sfx or (mouse_pressed[0] and self.rect_sfx_slider.collidepoint(mouse_pos)): 
                self.sfx_vol = max(0.0, min(1.0, (mouse_pos[0] - self.rect_sfx_slider.x) / self.rect_sfx_slider.width))
            return None
            
        self.btn_play.check_hover(mouse_pos)
        self.btn_shop.check_hover(mouse_pos)
        self.btn_quests.check_hover(mouse_pos)
        self.btn_skin.check_hover(mouse_pos)
        self.btn_options.check_hover(mouse_pos)
        
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
        
        font_info = pygame.font.SysFont("tahoma", 32, bold=True)
        self.draw_text_outline(screen, f"PLAYER: {player_name}", font_info, COLOR_TEXT_MAIN, (0,0,0), (220, 40))
        self.draw_text_outline(screen, f"COIN: {coins}", font_info, COLOR_GLOW_YELLOW, (0,0,0), (WINDOW_WIDTH - 220, 40))
        self.draw_text_outline(screen, "PIPE PUZZLE", self.font_title, COLOR_TEXT_MAIN, (0, 0, 0), (WINDOW_WIDTH//2, 120))
        
        self.btn_play.draw(screen)
        self.btn_shop.draw(screen)
        self.btn_quests.draw(screen)
        self.btn_skin.draw(screen)
        self.btn_options.draw(screen)
        
        if self.show_options_popup:
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 200))
            screen.blit(overlay, (0, 0))
            box_w, box_h = 600, 450
            box_x, box_y = (WINDOW_WIDTH - box_w)//2, (WINDOW_HEIGHT - box_h)//2
            pygame.draw.rect(screen, COLOR_PANEL, (box_x, box_y, box_w, box_h), border_radius=15)
            pygame.draw.rect(screen, COLOR_GLOW_BLUE, (box_x, box_y, box_w, box_h), 4, border_radius=15)
            
            self.draw_text_outline(screen, "OPTIONS", self.font_title, COLOR_GLOW_BLUE, (0,0,0), (WINDOW_WIDTH//2, box_y + 70))
            self.draw_text_outline(screen, "NHẠC NỀN", self.font_small, COLOR_TEXT_MAIN, (0,0,0), (box_x + 120, box_y + 165))
            
            pygame.draw.rect(screen, COLOR_BG_DARK, self.rect_music_slider, border_radius=10)
            fill_music_w = int(self.rect_music_slider.width * self.music_vol)
            if fill_music_w > 0: 
                pygame.draw.rect(screen, COLOR_GLOW_BLUE, pygame.Rect(self.rect_music_slider.x, self.rect_music_slider.y, fill_music_w, self.rect_music_slider.height), border_radius=10)
            pygame.draw.rect(screen, (255, 255, 255), self.rect_music_slider, 3, border_radius=10)
            pygame.draw.circle(screen, (255, 255, 255), (self.rect_music_slider.x + fill_music_w, self.rect_music_slider.centery), 15)
            pygame.draw.circle(screen, (0, 0, 0), (self.rect_music_slider.x + fill_music_w, self.rect_music_slider.centery), 15, 3) 
            
            self.draw_text_outline(screen, "HIỆU ỨNG", self.font_small, COLOR_TEXT_MAIN, (0,0,0), (box_x + 120, box_y + 265))
            
            pygame.draw.rect(screen, COLOR_BG_DARK, self.rect_sfx_slider, border_radius=10)
            fill_sfx_w = int(self.rect_sfx_slider.width * self.sfx_vol)
            if fill_sfx_w > 0: 
                pygame.draw.rect(screen, COLOR_GLOW_BLUE, pygame.Rect(self.rect_sfx_slider.x, self.rect_sfx_slider.y, fill_sfx_w, self.rect_sfx_slider.height), border_radius=10)
            pygame.draw.rect(screen, (255, 255, 255), self.rect_sfx_slider, 3, border_radius=10)
            pygame.draw.circle(screen, (255, 255, 255), (self.rect_sfx_slider.x + fill_sfx_w, self.rect_sfx_slider.centery), 15)
            pygame.draw.circle(screen, (0, 0, 0), (self.rect_sfx_slider.x + fill_sfx_w, self.rect_sfx_slider.centery), 15, 3)
            
            self.btn_opt_exit.draw(screen)
            self.btn_opt_rename.draw(screen)
            self.btn_opt_giftcode.draw(screen)
            self.btn_opt_close.draw(screen)
            
        elif self.show_giftcode_popup:
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 200))
            screen.blit(overlay, (0, 0))
            box_w, box_h = 500, 250
            box_x, box_y = (WINDOW_WIDTH - box_w)//2, (WINDOW_HEIGHT - box_h)//2
            pygame.draw.rect(screen, COLOR_PANEL, (box_x, box_y, box_w, box_h), border_radius=15)
            pygame.draw.rect(screen, COLOR_GLOW_YELLOW, (box_x, box_y, box_w, box_h), 4, border_radius=15)
            
            self.draw_text_outline(screen, "NHẬP MÃ BÍ MẬT:", self.font_btn, COLOR_TEXT_MAIN, (0,0,0), (WINDOW_WIDTH//2, box_y + 50))
            pygame.draw.rect(screen, COLOR_BG_DARK, (box_x + 20, box_y + 100, box_w - 40, 60), border_radius=10)
            pygame.draw.rect(screen, COLOR_GLOW_BLUE, (box_x + 20, box_y + 100, box_w - 40, 60), 3, border_radius=10)
            
            txt_input = self.font_btn.render(self.giftcode_input + "_", True, COLOR_GLOW_YELLOW)
            screen.blit(txt_input, (box_x + 40, box_y + 110))
            self.draw_text_outline(screen, "ENTER xác nhận - ESC để Hủy", self.font_small, (150, 150, 150), (0,0,0), (WINDOW_WIDTH//2, box_y + 200))
            
        font_notif = pygame.font.SysFont("tahoma", 45, bold=True)
        for notif in self.notifications[:]: 
            self.draw_text_outline(screen, notif['text'], font_notif, notif['color'], (0,0,0), (notif['x'], notif['y']))
            notif['y'] -= 2
            notif['alpha'] -= 4
            if notif['alpha'] <= 0: 
                self.notifications.remove(notif)

class LevelSelectScreen:
    def __init__(self):
        self.font_title = pygame.font.SysFont('tahoma', 60, bold=True)
        self.font_act = pygame.font.SysFont('tahoma', 36, bold=True)
        self.next_state = None
        self.selected_level = None
        self.selected_act = 1 
        self.btn_back = Button(20, 20, 120, 50, "< MENU", (0, 0, 0, 0), (255, 255, 255))
        
        grid_w, grid_h = 420, 290
        start_x, start_y = (WINDOW_WIDTH - grid_w) // 2, 200
        mid_y = start_y + grid_h // 2
        
        self.btn_act_prev = Button(start_x - 100, mid_y - 40, 80, 80, "<", (0, 0, 0, 0), (255, 255, 255), font_size=50)
        self.btn_next = Button(start_x + grid_w + 20, mid_y - 40, 80, 80, ">", (0, 0, 0, 0), (255, 255, 255), font_size=50)
        self.level_buttons = []
        level_btn_size = 90
        padding = 10
        
        for i in range(12): 
            self.level_buttons.append(Button(start_x + (i%4)*(level_btn_size+padding), start_y + (i//4)*(level_btn_size+padding), level_btn_size, level_btn_size, "", COLOR_GLOW_BLUE, font_size=36))
            
        self.act_backgrounds = {}
        for i in range(1, 6): 
            try: 
                raw_bg = pygame.image.load(f"assets/images/bg_act{i}.jpg").convert()
                self.act_backgrounds[i] = pygame.transform.smoothscale(raw_bg, (WINDOW_WIDTH, WINDOW_HEIGHT))
            except: 
                fallback_bg = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
                fallback_bg.fill(COLOR_BG_DARK)
                self.act_backgrounds[i] = fallback_bg

    def handle_event(self, event, unlocked_levels):
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()
        self.btn_back.check_hover(mouse_pos)
        self.btn_act_prev.check_hover(mouse_pos)
        self.btn_next.check_hover(mouse_pos)
        
        for i, btn in enumerate(self.level_buttons): 
            level_num = (self.selected_act-1)*12+i+1
            btn.text = str(level_num)
            btn.is_enabled = level_num <= unlocked_levels
            btn.check_hover(mouse_pos)
            
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.btn_back.is_clicked(mouse_pos, mouse_pressed): 
                self.next_state = STATE_DASHBOARD
            elif self.btn_act_prev.is_clicked(mouse_pos, mouse_pressed):
                if self.selected_act > 1: 
                    self.selected_act -= 1
            elif self.btn_next.is_clicked(mouse_pos, mouse_pressed):
                if self.selected_act < 5: 
                    self.selected_act += 1
            for i, btn in enumerate(self.level_buttons):
                if btn.is_clicked(mouse_pos, mouse_pressed) and btn.is_enabled: 
                    self.selected_level = (self.selected_act-1)*12+i+1
                    self.next_state = STATE_GAME_PLAY
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

    def draw(self, screen):
        screen.blit(self.act_backgrounds.get(self.selected_act), (0, 0))
        self.draw_text_outline(screen, "CHỌN MÀN CHƠI", self.font_title, COLOR_TEXT_MAIN, (0, 0, 0), (WINDOW_WIDTH // 2, 80))
        self.draw_text_outline(screen, f"ACT {self.selected_act}", self.font_act, COLOR_GLOW_BLUE, (0, 0, 0), (WINDOW_WIDTH // 2, 140))
        for btn in self.level_buttons: 
            btn.draw(screen)
        self.btn_back.draw(screen)
        
        if self.selected_act > 1: 
            self.btn_act_prev.draw(screen)
        if self.selected_act < 5: 
            self.btn_next.draw(screen)

class PauseMenu:
    def __init__(self):
        self.overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.overlay.set_alpha(200)
        self.overlay.fill((0, 0, 0))
        center_x, center_y = WINDOW_WIDTH//2, WINDOW_HEIGHT//2
        btn_w, btn_h = 260, 50
        start_x = center_x - btn_w//2
        self.btn_restart = Button(start_x, center_y-100, btn_w, btn_h, "CHƠI LẠI", (52, 152, 219))
        self.btn_ai = Button(start_x, center_y-30, btn_w, btn_h, "AI GIẢI (-100)", (155, 89, 182))
        self.btn_exit = Button(start_x, center_y+40, btn_w, btn_h, "THOÁT MÀN", COLOR_PURCHASE)
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
        self.font_title = pygame.font.SysFont('tahoma', 40, bold=True)
        self.font_text = pygame.font.SysFont('tahoma', 26, bold=True)
        self.popup_rect = pygame.Rect(WINDOW_WIDTH//2-320, WINDOW_HEIGHT//2-200, 640, 400)
        self.btn_understand = Button(WINDOW_WIDTH//2-120, WINDOW_HEIGHT//2+100, 240, 50, "ĐÃ HIỂU!", COLOR_GLOW_BLUE)
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
        self.draw_text_outline(screen, "HƯỚNG DẪN CƠ BẢN", self.font_title, COLOR_GLOW_BLUE, (0, 0, 0), (WINDOW_WIDTH//2, self.popup_rect.top+40), center=True)
        instructions = ["1. Click chuột TRÁI để xoay ống.", "2. Nối thông nước từ GÓC TRÁI-TRÊN.", "3. Click 'AI GIẢI' trên MENU nếu bị kẹt.", "MỤC TIÊU: Nước chảy đến PHẢI-DƯỚI!"]
        for i, text in enumerate(instructions): 
            color = COLOR_GLOW_YELLOW if i==3 else COLOR_TEXT_MAIN
            self.draw_text_outline(screen, text, self.font_text, color, (0, 0, 0), (self.popup_rect.left+40, self.popup_rect.top+110+i*45))
        self.btn_understand.draw(screen)

class WinPopup:
    def __init__(self):
        self.action = None
        self.earned_coins = 0
        self.font_title = pygame.font.SysFont('tahoma', 50, bold=True)
        self.font_reward = pygame.font.SysFont('tahoma', 36, bold=True)
        btn_w, btn_h = 170, 50
        y_pos = WINDOW_HEIGHT//2+60
        self.btn_replay = Button(WINDOW_WIDTH//2-275, y_pos, btn_w, btn_h, "CHƠI LẠI", (52, 152, 219))
        self.btn_next = Button(WINDOW_WIDTH//2-85, y_pos, btn_w, btn_h, "TIẾP THEO", COLOR_GLOW_BLUE)
        self.btn_menu = Button(WINDOW_WIDTH//2+105, y_pos, btn_w, btn_h, "MENU", COLOR_PURCHASE)

    def handle_event(self, event):
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()
        self.btn_replay.check_hover(mouse_pos)
        self.btn_next.check_hover(mouse_pos)
        self.btn_menu.check_hover(mouse_pos)
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.btn_replay.is_clicked(mouse_pos, mouse_pressed): self.action = "REPLAY"
            elif self.btn_next.is_clicked(mouse_pos, mouse_pressed): self.action = "NEXT"
            elif self.btn_menu.is_clicked(mouse_pos, mouse_pressed): self.action = "MENU"
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

    def draw(self, screen):
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        box_w, box_h = 620, 280
        box_x, box_y = (WINDOW_WIDTH - box_w)//2, (WINDOW_HEIGHT - box_h)//2
        pygame.draw.rect(screen, COLOR_PANEL, (box_x, box_y, box_w, box_h), border_radius=15)
        pygame.draw.rect(screen, COLOR_GLOW_BLUE, (box_x, box_y, box_w, box_h), 4, border_radius=15)
        self.draw_text_outline(screen, "HOÀN THÀNH MÀN CHƠI!", self.font_title, COLOR_GLOW_BLUE, (0, 0, 0), (WINDOW_WIDTH//2, box_y+60))
        self.draw_text_outline(screen, f"PHẦN THƯỞNG: +{self.earned_coins} COIN", self.font_reward, COLOR_GLOW_YELLOW, (0, 0, 0), (WINDOW_WIDTH//2, box_y+130))
        self.btn_replay.draw(screen)
        self.btn_next.draw(screen)
        self.btn_menu.draw(screen)

class SkinScreen:
    def __init__(self):
        self.next_state = None
        self.font = pygame.font.SysFont('tahoma', 40, bold=True)
        self.btn_back = Button(20, 20, 150, 50, "< MENU", (0, 0, 0, 0), (255, 255, 255))

    def handle_event(self, event):
        mouse_pos = pygame.mouse.get_pos()
        self.btn_back.check_hover(mouse_pos)
        if event.type == pygame.MOUSEBUTTONDOWN and self.btn_back.is_clicked(mouse_pos, pygame.mouse.get_pressed()): 
            self.next_state = STATE_DASHBOARD

    def draw_text_outline(self, screen, text, font, text_color, outline_color, center_pos):
        outline_width = 2
        for dx in [-outline_width, 0, outline_width]:
            for dy in [-outline_width, 0, outline_width]:
                if dx != 0 or dy != 0:
                    txt_surface = font.render(text, True, outline_color)
                    screen.blit(txt_surface, txt_surface.get_rect(center=(center_pos[0]+dx, center_pos[1]+dy)))
        txt_surface = font.render(text, True, text_color)
        screen.blit(txt_surface, txt_surface.get_rect(center=center_pos))

    def draw(self, screen): 
        screen.fill(COLOR_BG_DARK)
        self.draw_text_outline(screen, "CHỌN SKIN (Đang phát triển)", self.font, COLOR_GLOW_YELLOW, (0, 0, 0), (WINDOW_WIDTH//2, WINDOW_HEIGHT//2))
        self.btn_back.draw(screen)

# =======================================================
# MÀN HÌNH NHIỆM VỤ MỚI (Của nhánh UI3)
# =======================================================
class QuestsScreen:
    def __init__(self, quests=None):
        self.quests = quests or []
        self.next_state = None
        self.font = pygame.font.SysFont('tahoma', 44, bold=True)
        self.font_card_title = pygame.font.SysFont('tahoma', 24, bold=True)
        self.font_card_desc = pygame.font.SysFont('tahoma', 19, bold=True)
        self.font_small = pygame.font.SysFont('tahoma', 17, bold=True)
        self.btn_back = Button(20, 20, 140, 50, "< MENU", (0, 0, 0, 0), (255, 255, 255))
        self.quest_buttons = {}
        self.notifications = []

        card_x = 50
        card_y = 95
        card_h = 82
        gap = 8
        
        # Đảm bảo QUEST_DEFINITIONS đã được khai báo trong settings.py
        for i, quest in enumerate(QUEST_DEFINITIONS):
            y = card_y + i * (card_h + gap)
            btn = Button(card_x + 715, y + 20, 180, 40, "NHẬN", (46, 204, 113))
            btn.font = pygame.font.SysFont('tahoma', 24, bold=True)
            self.quest_buttons[quest["id"]] = btn

    def add_notification(self, text, color=(255, 215, 0)):
        self.notifications.append(
            {
                "text": text,
                "x": WINDOW_WIDTH // 2,
                "y": WINDOW_HEIGHT - 40,
                "alpha": 255,
                "color": color,
            }
        )

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
                if self._is_claimed(quest_data, quest_id):
                    continue
                if not self._is_completed(quest_data, quest):
                    continue
                if btn.is_clicked(mouse_pos, pressed):
                    return ("CLAIM_QUEST", quest_id)

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
        screen.fill(COLOR_BG_DARK)
        self.draw_text_outline(screen, "NHIỆM VỤ", self.font, (0, 255, 255), (0, 0, 0), (WINDOW_WIDTH//2, 52))

        card_x = 50
        card_y = 95
        card_w = 900
        card_h = 82
        gap = 8

        for i, quest in enumerate(QUEST_DEFINITIONS):
            y = card_y + i * (card_h + gap)
            progress = self._quest_progress(quest_data, quest)
            target = int(quest["target"])
            clamped = min(progress, target)
            completed = progress >= target
            claimed = self._is_claimed(quest_data, quest["id"])

            bg = (40, 45, 57) if not completed else (34, 72, 53)
            border = (115, 127, 159) if not completed else (46, 204, 113)
            pygame.draw.rect(screen, bg, (card_x, y, card_w, card_h), border_radius=12)
            pygame.draw.rect(screen, border, (card_x, y, card_w, card_h), 2, border_radius=12)

            title_surface = self.font_card_title.render(quest["title"], True, (255, 255, 255))
            title_shadow = self.font_card_title.render(quest["title"], True, (0, 0, 0))
            screen.blit(title_shadow, (card_x + 22 + 2, y + 12 + 2))
            screen.blit(title_surface, (card_x + 22, y + 12))

            desc_text = f"{quest['desc']}  |  THƯỞNG: +{quest['reward']} coin"
            desc_surface = self.font_card_desc.render(desc_text, True, (222, 224, 230))
            desc_shadow = self.font_card_desc.render(desc_text, True, (0, 0, 0))
            screen.blit(desc_shadow, (card_x + 22 + 2, y + 40 + 2))
            screen.blit(desc_surface, (card_x + 22, y + 40))

            bar_x, bar_y, bar_w, bar_h = card_x + 22, y + 63, 430, 10
            pygame.draw.rect(screen, (18, 20, 25), (bar_x, bar_y, bar_w, bar_h), border_radius=6)
            fill_w = int(bar_w * (clamped / target)) if target > 0 else 0
            if fill_w > 0:
                pygame.draw.rect(screen, (75, 166, 235), (bar_x, bar_y, fill_w, bar_h), border_radius=6)
            pygame.draw.rect(screen, (190, 196, 210), (bar_x, bar_y, bar_w, bar_h), 1, border_radius=6)

            progress_text = f"Tiến độ: {clamped}/{target}"
            progress_surface = self.font_small.render(progress_text, True, (245, 245, 245))
            progress_shadow = self.font_small.render(progress_text, True, (0, 0, 0))
            progress_x = bar_x + bar_w + 38
            progress_y = y + 57
            screen.blit(progress_shadow, (progress_x + 2, progress_y + 2))
            screen.blit(progress_surface, (progress_x, progress_y))

            btn = self.quest_buttons[quest["id"]]
            btn.rect.x = card_x + 715
            btn.rect.y = y + 20
            if claimed:
                btn.text = "ĐÃ NHẬN"
                btn.bg_color = (110, 110, 110)
                btn.is_enabled = False
            elif completed:
                btn.text = "NHẬN"
                btn.bg_color = (46, 204, 113)
                btn.is_enabled = True
            else:
                btn.text = "CHƯA XONG"
                btn.bg_color = (130, 130, 130)
                btn.is_enabled = False
            btn.draw(screen)

        font_notif = pygame.font.SysFont("tahoma", 30, bold=True)
        for notif in self.notifications[:]:
            self.draw_text_outline(screen, notif["text"], font_notif, notif["color"], (0, 0, 0), (notif["x"], notif["y"]))
            notif["y"] -= 1
            notif["alpha"] -= 4
            if notif["alpha"] <= 0:
                self.notifications.remove(notif)

        self.btn_back.draw(screen)