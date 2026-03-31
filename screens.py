import pygame
from settings import *

class Button:
    def __init__(self, x, y, w, h, text, bg_color, text_color=(255, 255, 255), disable_hover_effect=False):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.bg_color = bg_color
        self.text_color = text_color
        self.is_hovered = False
        self.is_enabled = True
        self.disable_hover_effect = disable_hover_effect 
        self.font = pygame.font.SysFont('tahoma', 28, bold=True) 

    def check_hover(self, mouse_pos):
        if self.is_enabled:
            self.is_hovered = self.rect.collidepoint(mouse_pos)
        else:
            self.is_hovered = False

    def is_clicked(self, mouse_pos, mouse_pressed):
        return self.is_enabled and self.rect.collidepoint(mouse_pos) and mouse_pressed[0]

    def draw(self, screen):
        if not self.is_enabled:
            current_bg = (100, 100, 100)
            current_text = (150, 150, 150)
            border_color = (100, 100, 100)
            border_width = 2
        elif self.is_hovered and self.bg_color != (0, 0, 0, 0) and not self.disable_hover_effect:
            current_bg = (min(255, self.bg_color[0] + 30), min(255, self.bg_color[1] + 30), min(255, self.bg_color[2] + 30))
            current_text = (255, 215, 0) 
            border_color = (0, 255, 255) 
            border_width = 3
        else:
            current_bg = self.bg_color
            current_text = self.text_color
            border_color = (200, 200, 200) 
            border_width = 2

        if current_bg != (0, 0, 0, 0):
            pygame.draw.rect(screen, current_bg, self.rect, border_radius=10)
            pygame.draw.rect(screen, border_color, self.rect, width=border_width, border_radius=10)

        self.draw_text_outline(screen, self.text, self.font, current_text, (0, 0, 0), self.rect.center)

    def draw_text_outline(self, screen, text, font, text_color, outline_color, center_pos):
        outline_width = 2 
        for dx in [-outline_width, 0, outline_width]:
            for dy in [-outline_width, 0, outline_width]:
                if dx != 0 or dy != 0:
                    txt_surface = font.render(text, True, outline_color)
                    screen.blit(txt_surface, txt_surface.get_rect(center=(center_pos[0]+dx, center_pos[1]+dy)))
        
        txt_surface = font.render(text, True, text_color)
        screen.blit(txt_surface, txt_surface.get_rect(center=center_pos))


class StartScreen:
    def __init__(self):
        self.font_title = pygame.font.SysFont('tahoma', 70, bold=True)
        self.font_prompt = pygame.font.SysFont('tahoma', 32, bold=True) 
        self.font_input = pygame.font.SysFont('tahoma', 40, bold=True) 
        self.font_error = pygame.font.SysFont('tahoma', 22, bold=True) 

        self.player_name = ""
        self.next_state = None
        self.error_msg = ""

        box_w, box_h = 450, 70
        self.input_rect = pygame.Rect((WINDOW_WIDTH - box_w) // 2, (WINDOW_HEIGHT - box_h) // 2 + 40, box_w, box_h)
        self.btn_start = Button((WINDOW_WIDTH - 200) // 2, self.input_rect.bottom + 50, 200, 60, "BẮT ĐẦU", (46, 204, 113))

        self.cursor_visible = True
        self.last_blink = pygame.time.get_ticks()

    def draw_text_outline(self, screen, text, font, text_color, outline_color, center_pos):
        outline_width = 3 
        for dx in [-outline_width, 0, outline_width]:
            for dy in [-outline_width, 0, outline_width]:
                if dx != 0 or dy != 0:
                    txt_surface = font.render(text, True, outline_color)
                    screen.blit(txt_surface, txt_surface.get_rect(center=(center_pos[0]+dx, center_pos[1]+dy)))
        txt_surface = font.render(text, True, text_color)
        screen.blit(txt_surface, txt_surface.get_rect(center=center_pos))

    def handle_event(self, event):
        mouse_pos = pygame.mouse.get_pos()
        self.btn_start.check_hover(mouse_pos)

        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.btn_start.is_clicked(mouse_pos, pygame.mouse.get_pressed()):
                if len(self.player_name.strip()) > 0: self.next_state = STATE_DASHBOARD
                else: self.error_msg = "Vui lòng nhập tên của bạn!"

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                if len(self.player_name.strip()) > 0: self.next_state = STATE_DASHBOARD
                else: self.error_msg = "Vui lòng nhập tên của bạn!"
            elif event.key == pygame.K_BACKSPACE:
                self.player_name = self.player_name[:-1]
                self.error_msg = "" 
            else:
                if len(self.player_name) < 12: 
                    self.player_name += event.unicode
                    self.error_msg = "" 
        return None

    def draw(self, screen):
        screen.fill((0, 0, 0))
        self.draw_text_outline(screen, "PIPE PUZZLE", self.font_title, (0, 255, 255), (0, 0, 0), (WINDOW_WIDTH // 2, 120))
        
        prompt_y = self.input_rect.top - 60
        self.draw_text_outline(screen, "Nhập tên của bạn:", self.font_prompt, (255, 255, 255), (0, 0, 0), (WINDOW_WIDTH // 2, prompt_y))

        pygame.draw.rect(screen, (25, 25, 25), self.input_rect, border_radius=12)
        pygame.draw.rect(screen, (0, 255, 255), self.input_rect, width=3, border_radius=12)

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
            pygame.draw.line(screen, (0, 255, 255), (cursor_x, cursor_y_start), (cursor_x, cursor_y_end), 4)

        self.btn_start.draw(screen)
        if self.error_msg:
            self.draw_text_outline(screen, self.error_msg, self.font_error, (231, 76, 60), (0, 0, 0), (WINDOW_WIDTH // 2, self.btn_start.rect.bottom + 40))


class DashboardScreen:
    def __init__(self):
        self.font_title = pygame.font.SysFont('tahoma', 70, bold=True)
        self.font_btn = pygame.font.SysFont('tahoma', 36, bold=True) 
        self.font_small = pygame.font.SysFont('tahoma', 22, bold=True)
        self.next_state = None
        
        self.btn_play = Button(WINDOW_WIDTH//2 - 150, 250, 300, 60, "CHỌN MÀN CHƠI", (46, 204, 113))
        self.btn_shop = Button(WINDOW_WIDTH//2 - 150, 340, 300, 60, "CỬA HÀNG", (52, 152, 219))
        self.btn_quests = Button(WINDOW_WIDTH//2 - 150, 430, 300, 60, "NHIỆM VỤ", (155, 89, 182))
        self.btn_skin = Button(WINDOW_WIDTH - 150, WINDOW_HEIGHT - 80, 120, 50, "SKIN", (241, 196, 15))
        self.btn_options = Button(30, WINDOW_HEIGHT - 80, 160, 50, "OPTIONS", (100, 100, 100))
        
        self.show_options_popup = False
        self.show_giftcode_popup = False
        self.giftcode_input = ""
        self.notifications = [] 

        box_w, box_h = 600, 450
        box_x, box_y = (WINDOW_WIDTH - box_w)//2, (WINDOW_HEIGHT - box_h)//2
        self.btn_opt_exit = Button(box_x + 40, box_y + 350, 150, 50, "THOÁT", (231, 76, 60))
        self.btn_opt_rename = Button(box_x + 225, box_y + 350, 150, 50, "ĐỔI TÊN", (52, 152, 219))
        
        self.btn_opt_giftcode = Button(box_x + 410, box_y + 350, 150, 50, "GIFTCODE", (241, 196, 15), (255, 255, 255), disable_hover_effect=True)
        self.btn_opt_close = Button(box_x + box_w - 50, box_y + 10, 40, 40, "X", (231, 76, 60))

        self.music_vol = 1.0
        self.sfx_vol = 1.0
        self.rect_music_slider = pygame.Rect(box_x + 220, box_y + 155, 300, 25)
        self.rect_sfx_slider = pygame.Rect(box_x + 220, box_y + 255, 300, 25)
        self.is_dragging_music = False
        self.is_dragging_sfx = False

        # GHI NHẬN: Nền Sky của bạn Sếp
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
                        self.notifications.append({'text': "MÃ NÀY ĐÃ SỬ DỤNG!", 'x': WINDOW_WIDTH//2, 'y': WINDOW_HEIGHT//2, 'alpha': 255, 'color': (231, 76, 60)})
                        self.show_giftcode_popup = False
                        self.show_options_popup = True 
                        self.giftcode_input = ""
                        return None
                    elif code == "UNPIPE":
                        self.notifications.append({'text': "ĐÃ MỞ KHÓA MAX LEVEL!", 'x': WINDOW_WIDTH//2, 'y': WINDOW_HEIGHT//2, 'alpha': 255, 'color': (46, 204, 113)})
                        self.show_giftcode_popup = False
                        self.show_options_popup = True
                        self.giftcode_input = ""
                        return "UNLOCK_ALL"
                    elif code == "PIPEGOLD":
                        self.notifications.append({'text': "+10.000 COIN", 'x': WINDOW_WIDTH//2, 'y': WINDOW_HEIGHT//2, 'alpha': 255, 'color': (255, 215, 0)})
                        self.show_giftcode_popup = False
                        self.show_options_popup = True
                        self.giftcode_input = ""
                        return "ADD_COINS"
                    else:
                        self.notifications.append({'text': "MÃ KHÔNG HỢP LỆ!", 'x': WINDOW_WIDTH//2, 'y': WINDOW_HEIGHT//2, 'alpha': 255, 'color': (231, 76, 60)})
                        self.show_giftcode_popup = False
                        self.show_options_popup = True
                        self.giftcode_input = ""
                        return None
                elif event.key == pygame.K_BACKSPACE: self.giftcode_input = self.giftcode_input[:-1]
                elif event.key == pygame.K_ESCAPE:
                    self.show_giftcode_popup = False
                    self.show_options_popup = True 
                else:
                    if len(self.giftcode_input) < 15: self.giftcode_input += event.unicode
            return None

        if self.show_options_popup:
            self.btn_opt_exit.check_hover(mouse_pos)
            self.btn_opt_rename.check_hover(mouse_pos)
            self.btn_opt_giftcode.check_hover(mouse_pos)
            self.btn_opt_close.check_hover(mouse_pos)

            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.btn_opt_close.is_clicked(mouse_pos, mouse_pressed): self.show_options_popup = False
                elif self.btn_opt_exit.is_clicked(mouse_pos, mouse_pressed):
                    import sys; pygame.quit(); sys.exit()
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
                rel_x = mouse_pos[0] - self.rect_music_slider.x
                self.music_vol = max(0.0, min(1.0, rel_x / self.rect_music_slider.width)) 
                
            if self.is_dragging_sfx or (mouse_pressed[0] and self.rect_sfx_slider.collidepoint(mouse_pos)):
                rel_x = mouse_pos[0] - self.rect_sfx_slider.x
                self.sfx_vol = max(0.0, min(1.0, rel_x / self.rect_sfx_slider.width))
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
        if self.bg_sky:
            screen.blit(self.bg_sky, (0, 0))
        else:
            screen.fill((30, 30, 30))
        
        font_info = pygame.font.SysFont("tahoma", 32, bold=True)
        self.draw_text_outline(screen, f"PLAYER: {player_name}", font_info, (255, 255, 255), (0,0,0), (220, 40))
        self.draw_text_outline(screen, f"COIN: {coins}", font_info, (255, 215, 0), (0,0,0), (WINDOW_WIDTH - 220, 40))
        self.draw_text_outline(screen, "PIPE PUZZLE", self.font_title, (0, 255, 255), (0, 0, 0), (WINDOW_WIDTH//2, 120))

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
            pygame.draw.rect(screen, (40, 45, 50), (box_x, box_y, box_w, box_h), border_radius=15)
            pygame.draw.rect(screen, (0, 255, 255), (box_x, box_y, box_w, box_h), 4, border_radius=15)
            
            self.draw_text_outline(screen, "OPTIONS", self.font_title, (0, 255, 255), (0,0,0), (WINDOW_WIDTH//2, box_y + 70))
            
            self.draw_text_outline(screen, "NHẠC NỀN", self.font_small, (255, 255, 255), (0,0,0), (box_x + 120, box_y + 165))
            pygame.draw.rect(screen, (20, 20, 20), self.rect_music_slider, border_radius=10)
            fill_music_w = int(self.rect_music_slider.width * self.music_vol)
            if fill_music_w > 0:
                pygame.draw.rect(screen, (46, 204, 113), pygame.Rect(self.rect_music_slider.x, self.rect_music_slider.y, fill_music_w, self.rect_music_slider.height), border_radius=10)
            pygame.draw.rect(screen, (255, 255, 255), self.rect_music_slider, 3, border_radius=10)
            circle_x = self.rect_music_slider.x + fill_music_w
            circle_y = self.rect_music_slider.centery
            pygame.draw.circle(screen, (255, 255, 255), (circle_x, circle_y), 15)
            pygame.draw.circle(screen, (0, 0, 0), (circle_x, circle_y), 15, 3) 

            self.draw_text_outline(screen, "HIỆU ỨNG", self.font_small, (255, 255, 255), (0,0,0), (box_x + 120, box_y + 265))
            pygame.draw.rect(screen, (20, 20, 20), self.rect_sfx_slider, border_radius=10)
            fill_sfx_w = int(self.rect_sfx_slider.width * self.sfx_vol)
            if fill_sfx_w > 0:
                pygame.draw.rect(screen, (46, 204, 113), pygame.Rect(self.rect_sfx_slider.x, self.rect_sfx_slider.y, fill_sfx_w, self.rect_sfx_slider.height), border_radius=10)
            pygame.draw.rect(screen, (255, 255, 255), self.rect_sfx_slider, 3, border_radius=10)
            circle_x = self.rect_sfx_slider.x + fill_sfx_w
            circle_y = self.rect_sfx_slider.centery
            pygame.draw.circle(screen, (255, 255, 255), (circle_x, circle_y), 15)
            pygame.draw.circle(screen, (0, 0, 0), (circle_x, circle_y), 15, 3)

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
            pygame.draw.rect(screen, (40, 45, 50), (box_x, box_y, box_w, box_h), border_radius=15)
            pygame.draw.rect(screen, (255, 215, 0), (box_x, box_y, box_w, box_h), 4, border_radius=15)
            
            self.draw_text_outline(screen, "NHẬP MÃ BÍ MẬT:", self.font_btn, (255, 255, 255), (0,0,0), (WINDOW_WIDTH//2, box_y + 50))
            pygame.draw.rect(screen, (20, 20, 20), (box_x + 20, box_y + 100, box_w - 40, 60), border_radius=10)
            pygame.draw.rect(screen, (0, 255, 255), (box_x + 20, box_y + 100, box_w - 40, 60), 3, border_radius=10)
            
            txt_input = self.font_btn.render(self.giftcode_input + "_", True, (255, 215, 0))
            screen.blit(txt_input, (box_x + 40, box_y + 110))
            self.draw_text_outline(screen, "ENTER xác nhận - ESC để Hủy", self.font_small, (150, 150, 150), (0,0,0), (WINDOW_WIDTH//2, box_y + 200))

        font_notif = pygame.font.SysFont("tahoma", 45, bold=True)
        for notif in self.notifications[:]: 
            self.draw_text_outline(screen, notif['text'], font_notif, notif['color'], (0,0,0), (notif['x'], notif['y']))
            notif['y'] -= 2       
            notif['alpha'] -= 4   
            if notif['alpha'] <= 0: self.notifications.remove(notif)


class LevelSelectScreen:
    def __init__(self):
        self.font_title = pygame.font.SysFont('tahoma', 60, bold=True)
        self.font_act = pygame.font.SysFont('tahoma', 36, bold=True) 
        self.next_state = None
        self.selected_level = None
        self.selected_act = 1 

        self.btn_back = Button(20, 20, 120, 50, "MENU", (0, 0, 0, 0), (255, 255, 255))
        
        grid_w, grid_h = 420, 290
        start_x, start_y = (WINDOW_WIDTH - grid_w) // 2, 200
        mid_y = start_y + grid_h // 2
        
        self.btn_act_prev = Button(start_x - 100, mid_y - 40, 80, 80, "<", (0, 0, 0, 0), (255, 255, 255))
        self.btn_next = Button(start_x + grid_w + 20, mid_y - 40, 80, 80, ">", (0, 0, 0, 0), (255, 255, 255))
        
        self.level_buttons = []
        level_btn_size = 90
        padding = 10
        
        for i in range(12):
            row = i // 4
            col = i % 4
            x = start_x + col * (level_btn_size + padding)
            y = start_y + row * (level_btn_size + padding)
            self.level_buttons.append(Button(x, y, level_btn_size, level_btn_size, "", (46, 204, 113)))

        self.act_backgrounds = {}
        for i in range(1, 6): 
            path = f"assets/images/bg_act{i}.jpg"
            try:
                raw_bg = pygame.image.load(path).convert()
                self.act_backgrounds[i] = pygame.transform.smoothscale(raw_bg, (WINDOW_WIDTH, WINDOW_HEIGHT))
            except Exception:
                fallback_bg = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
                fallback_bg.fill((30, 30, 30))
                self.act_backgrounds[i] = fallback_bg

    def handle_event(self, event, unlocked_levels):
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()

        self.btn_back.check_hover(mouse_pos)
        self.btn_act_prev.check_hover(mouse_pos)
        self.btn_next.check_hover(mouse_pos)

        for i, btn in enumerate(self.level_buttons):
            level_num = (self.selected_act - 1) * 12 + i + 1
            btn.text = str(level_num)
            btn.is_enabled = level_num <= unlocked_levels
            btn.check_hover(mouse_pos)

        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.btn_back.is_clicked(mouse_pos, mouse_pressed): self.next_state = STATE_DASHBOARD
            elif self.btn_act_prev.is_clicked(mouse_pos, mouse_pressed):
                if self.selected_act > 1: self.selected_act -= 1
            elif self.btn_next.is_clicked(mouse_pos, mouse_pressed):
                if self.selected_act < 5: self.selected_act += 1

            for i, btn in enumerate(self.level_buttons):
                if btn.is_clicked(mouse_pos, mouse_pressed) and btn.is_enabled:
                    self.selected_level = (self.selected_act - 1) * 12 + i + 1
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
        self.draw_text_outline(screen, "CHỌN MÀN CHƠI", self.font_title, (0, 255, 255), (0, 0, 0), (WINDOW_WIDTH // 2, 80))
        self.draw_text_outline(screen, f"ACT {self.selected_act}", self.font_act, (255, 255, 255), (0, 0, 0), (WINDOW_WIDTH // 2, 140))

        for btn in self.level_buttons: btn.draw(screen)
        self.btn_back.draw(screen)
        if self.selected_act > 1: self.btn_act_prev.draw(screen)
        if self.selected_act < 5: self.btn_next.draw(screen)


class PauseMenu:
    def __init__(self):
        self.overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.overlay.set_alpha(200)
        self.overlay.fill((0, 0, 0))
        center_x, center_y = WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2
        
        # --- ĐÃ TĂNG CHIỀU RỘNG NÚT LÊN 260 ĐỂ KHÔNG TRÀN CHỮ ---
        btn_w = 260
        btn_h = 50
        start_x = center_x - (btn_w // 2)
        
        self.btn_restart = Button(start_x, center_y - 100, btn_w, btn_h, "CHƠI LẠI", (52, 152, 219))
        self.btn_ai = Button(start_x, center_y - 30, btn_w, btn_h, "AI GIẢI (-100)", (155, 89, 182))
        self.btn_exit = Button(start_x, center_y + 40, btn_w, btn_h, "THOÁT MÀN", (231, 76, 60))
        self.action = None 
        
        self.error_msg = ""
        self.error_alpha = 0
        self.font_err = pygame.font.SysFont('tahoma', 28, bold=True)
        
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
        screen.blit(self.overlay, (0, 0))
        self.btn_restart.draw(screen)
        self.btn_ai.draw(screen)
        self.btn_exit.draw(screen)
        
        if self.error_alpha > 0:
            self.draw_text_outline(screen, self.error_msg, self.font_err, (255, 50, 50), (0, 0, 0), (WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + 130))
            self.error_alpha -= 5


class TutorialPopup:
    def __init__(self):
        self.overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.overlay.set_alpha(200)
        self.overlay.fill((0, 0, 0))
        
        self.font_title = pygame.font.SysFont('tahoma', 40, bold=True)
        self.font_text = pygame.font.SysFont('tahoma', 26, bold=True) 
        self.popup_rect = pygame.Rect(WINDOW_WIDTH//2 - 320, WINDOW_HEIGHT//2 - 200, 640, 400)
        self.btn_understand = Button(WINDOW_WIDTH//2 - 120, WINDOW_HEIGHT//2 + 100, 240, 50, "ĐÃ HIỂU!", (46, 204, 113))
        self.action = None

    def handle_event(self, event):
        mouse_pos = pygame.mouse.get_pos()
        self.btn_understand.check_hover(mouse_pos)
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.btn_understand.is_clicked(mouse_pos, pygame.mouse.get_pressed()): self.action = "UNDERSTOOD"

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
        pygame.draw.rect(screen, (40, 45, 50), self.popup_rect, border_radius=15)
        pygame.draw.rect(screen, (46, 204, 113), self.popup_rect, 4, border_radius=15)
        
        self.draw_text_outline(screen, "HƯỚNG DẪN CƠ BẢN", self.font_title, (46, 204, 113), (0, 0, 0), (WINDOW_WIDTH//2, self.popup_rect.top + 40), center=True)
        instructions = [
            "1. Click chuột TRÁI để xoay ống.",
            "2. Nối thông dòng nước từ góc TRÁI-TRÊN.",
            "3. Click 'AI GIẢI' trên MENU nếu bị kẹt.",
            "MỤC TIÊU: Nước chảy đến PHẢI-DƯỚI!"
        ]
        
        for i, text in enumerate(instructions):
            color = (255, 215, 0) if i == 3 else (255, 255, 255)
            self.draw_text_outline(screen, text, self.font_text, color, (0, 0, 0), (self.popup_rect.left + 40, self.popup_rect.top + 110 + i*45))
        self.btn_understand.draw(screen)


class WinPopup:
    def __init__(self):
        self.action = None
        self.earned_coins = 0 
        self.font_title = pygame.font.SysFont('tahoma', 50, bold=True)
        self.font_reward = pygame.font.SysFont('tahoma', 36, bold=True)
        
        btn_w, btn_h = 170, 50
        y_pos = WINDOW_HEIGHT//2 + 60 
        self.btn_replay = Button(WINDOW_WIDTH//2 - 275, y_pos, btn_w, btn_h, "CHƠI LẠI", (52, 152, 219))
        self.btn_next = Button(WINDOW_WIDTH//2 - 85, y_pos, btn_w, btn_h, "TIẾP THEO", (46, 204, 113))
        self.btn_menu = Button(WINDOW_WIDTH//2 + 105, y_pos, btn_w, btn_h, "MENU", (231, 76, 60))

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
        pygame.draw.rect(screen, (40, 45, 50), (box_x, box_y, box_w, box_h), border_radius=15)
        pygame.draw.rect(screen, (46, 204, 113), (box_x, box_y, box_w, box_h), 4, border_radius=15)
        
        self.draw_text_outline(screen, "HOÀN THÀNH MÀN CHƠI!", self.font_title, (46, 204, 113), (0, 0, 0), (WINDOW_WIDTH//2, box_y + 60))
        self.draw_text_outline(screen, f"PHẦN THƯỞNG: +{self.earned_coins} COIN", self.font_reward, (255, 215, 0), (0, 0, 0), (WINDOW_WIDTH//2, box_y + 130))
        
        self.btn_replay.draw(screen)
        self.btn_next.draw(screen)
        self.btn_menu.draw(screen)


class SkinScreen:
    def __init__(self):
        self.next_state = None
        self.font = pygame.font.SysFont('tahoma', 40, bold=True)
        self.btn_back = Button(20, 20, 150, 50, "QUAY LẠI", (100, 100, 100))
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
        screen.fill((30, 30, 30))
        self.draw_text_outline(screen, "CHỌN SKIN (Đang phát triển)", self.font, (241, 196, 15), (0, 0, 0), (WINDOW_WIDTH//2, WINDOW_HEIGHT//2))
        self.btn_back.draw(screen)


class ShopScreen:
    def __init__(self):
        self.next_state = None
        self.font = pygame.font.SysFont('tahoma', 40, bold=True)
        self.btn_back = Button(20, 20, 150, 50, "QUAY LẠI", (100, 100, 100))

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
        screen.fill((30, 30, 30))
        self.draw_text_outline(screen, "CỬA HÀNG (Đang phát triển)", self.font, (52, 152, 219), (0, 0, 0), (WINDOW_WIDTH//2, WINDOW_HEIGHT//2))
        self.btn_back.draw(screen)


# ========================================================
# ĐÃ GỘP HOÀN HẢO CLASS NHIỆM VỤ (QUESTS SCREEN)
# ========================================================
class QuestsScreen:
    def __init__(self, quests_list):
        self.quests = quests_list  # Nhận list nhiệm vụ từ main.py truyền vào
        self.next_state = None
        
        # Load các font chữ xịn xò để hiển thị
        self.font_title = pygame.font.SysFont('tahoma', 50, bold=True)
        self.font_quest_title = pygame.font.SysFont('tahoma', 26, bold=True)
        self.font_quest_desc = pygame.font.SysFont('tahoma', 20, bold=True)
        
        self.btn_back = Button(20, 20, 150, 50, "QUAY LẠI", (100, 100, 100))

    def handle_event(self, event):
        mouse_pos = pygame.mouse.get_pos()
        self.btn_back.check_hover(mouse_pos)
        if event.type == pygame.MOUSEBUTTONDOWN and self.btn_back.is_clicked(mouse_pos, pygame.mouse.get_pressed()):
            self.next_state = STATE_DASHBOARD

    def draw_text_outline(self, screen, text, font, text_color, outline_color, center_pos=None, topleft_pos=None):
        """Hàm vẽ chữ viền đen. Hỗ trợ cả căn giữa (center) và căn góc (topleft)"""
        outline_width = 2
        for dx in [-outline_width, 0, outline_width]:
            for dy in [-outline_width, 0, outline_width]:
                if dx != 0 or dy != 0:
                    txt_surface = font.render(text, True, outline_color)
                    if topleft_pos:
                        screen.blit(txt_surface, (topleft_pos[0]+dx, topleft_pos[1]+dy))
                    else:
                        screen.blit(txt_surface, txt_surface.get_rect(center=(center_pos[0]+dx, center_pos[1]+dy)))
        txt_surface = font.render(text, True, text_color)
        if topleft_pos:
            screen.blit(txt_surface, topleft_pos)
        else:
            screen.blit(txt_surface, txt_surface.get_rect(center=center_pos))

    def draw(self, screen): 
        screen.fill((30, 30, 30))
        
        # Vẽ tiêu đề bự
        self.draw_text_outline(screen, "BẢNG NHIỆM VỤ", self.font_title, (155, 89, 182), (0, 0, 0), center_pos=(WINDOW_WIDTH//2, 60))
        
        # Vẽ các nhiệm vụ từ danh sách
        y_offset = 150
        for quest in self.quests:
            # 1. Khung xám cho mỗi nhiệm vụ
            quest_rect = pygame.Rect(100, y_offset, WINDOW_WIDTH - 200, 90)
            pygame.draw.rect(screen, (40, 45, 50), quest_rect, border_radius=10)
            pygame.draw.rect(screen, (155, 89, 182), quest_rect, width=2, border_radius=10)
            
            # 2. Tên nhiệm vụ (Màu xanh nếu xong, Trắng nếu chưa)
            text_color = (46, 204, 113) if quest["completed"] else (255, 255, 255)
            self.draw_text_outline(screen, quest["title"], self.font_quest_title, text_color, (0,0,0), topleft_pos=(120, y_offset + 15))
            
            # 3. Tiến độ (Màu xám)
            progress_text = f"Tiến độ: {quest['progress']} / {quest['goal']}"
            self.draw_text_outline(screen, progress_text, self.font_quest_desc, (200, 200, 200), (0,0,0), topleft_pos=(120, y_offset + 55))
            
            # 4. Phần thưởng (Màu Vàng)
            reward_text = f"Thưởng: {quest['reward']['coins']} XU"
            self.draw_text_outline(screen, reward_text, self.font_quest_title, (255, 215, 0), (0,0,0), topleft_pos=(500, y_offset + 30))
            
            # 5. Trạng thái (Chữ Xanh "ĐÃ NHẬN" hoặc Đỏ "ĐANG LÀM")
            status_text = "ĐÃ NHẬN" if quest["completed"] else "CHƯA XONG"
            status_color = (46, 204, 113) if quest["completed"] else (231, 76, 60)
            self.draw_text_outline(screen, status_text, self.font_quest_title, status_color, (0,0,0), topleft_pos=(750, y_offset + 30))

            y_offset += 110 # Đẩy dòng xuống cho nhiệm vụ tiếp theo

        # Vẽ nút Quay Lại
        self.btn_back.draw(screen)