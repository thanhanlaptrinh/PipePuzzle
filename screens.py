# screens.py (Đã sửa lỗi font Tiếng Việt Unicode)
import pygame
# Import thêm settings để lấy FONT_PATH
from settings import *

class Button:
    def __init__(self, x, y, width, height, text, color, text_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.text_color = text_color
        
        # Hạ cỡ chữ của tất cả các nút xuống 30 cho thanh lịch
        self.font = pygame.font.SysFont('tahoma', 30, bold=True)
        self.is_hovered = False

    def draw(self, screen):
        draw_color = (min(self.color[0]+30, 255), min(self.color[1]+30, 255), min(self.color[2]+30, 255)) if self.is_hovered else self.color
        pygame.draw.rect(screen, draw_color, self.rect, border_radius=12)
        text_surf = self.font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

    def check_hover(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)

    def is_clicked(self, mouse_pos, mouse_pressed):
        return self.is_hovered and mouse_pressed[0]

class StartScreen:  
    def __init__(self):
        self.player_name = ""
        # Tăng cỡ chữ và in đậm cho rõ nét
        self.font_title = pygame.font.SysFont('tahoma', 75, bold=True)
        self.font_sub = pygame.font.SysFont('tahoma', 32, bold=True)
        
        self.background = None
        try:
            raw_bg = pygame.image.load(BG_START_PATH).convert()
            self.background = pygame.transform.smoothscale(raw_bg, (WINDOW_WIDTH, WINDOW_HEIGHT))
        except pygame.error as e:
            print(f"Warning: Không thể tải hình nền {BG_START_PATH}. Lỗi: {e}")

        # Căn chỉnh lại tọa độ ô nhập tên cho nằm ngay chính giữa tỷ lệ vàng
        center_x = WINDOW_WIDTH // 2
        center_y = WINDOW_HEIGHT // 2
        self.input_rect = pygame.Rect(center_x - 175, center_y - 20, 350, 60) # Mở rộng ô một chút
        
        self.cursor_visible = True
        self.cursor_timer = 0
        self.next_state = STATE_MENU_NAME 

        self.btn_giftcode = Button(20, WINDOW_HEIGHT - 70, 150, 50, "GIFTCODE", (155, 89, 182), (255, 255, 255))
        self.show_giftcode_popup = False
        self.giftcode_input = ""

    # --- HÀM VẼ CHỮ CÓ ĐỔ BÓNG ĐỂ NỔI BẬT TRÊN MỌI NỀN ---
    def draw_shadow_text(self, screen, text, font, color, center_pos):
        # 1. Vẽ bóng đen đằng sau (lệch 3 pixel)
        shadow = font.render(text, True, (0, 0, 0))
        screen.blit(shadow, shadow.get_rect(center=(center_pos[0] + 3, center_pos[1] + 3)))
        # 2. Vẽ chữ màu thật đè lên trên
        main_text = font.render(text, True, color)
        screen.blit(main_text, main_text.get_rect(center=center_pos))

    def handle_event(self, event):
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()

        # ---> ĐOẠN XỬ LÝ KHUNG NHẬP GIFTCODE <---
        if self.show_giftcode_popup:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if self.giftcode_input.upper() == "HACKERPRO":
                        return "UNLOCK_ALL" # Gửi tín hiệu hack thành công
                    self.show_giftcode_popup = False
                    self.giftcode_input = ""
                elif event.key == pygame.K_BACKSPACE:
                    self.giftcode_input = self.giftcode_input[:-1]
                elif event.key == pygame.K_ESCAPE:
                    self.show_giftcode_popup = False
                else:
                    if len(self.giftcode_input) < 15:
                        self.giftcode_input += event.unicode
            return None # Nếu đang mở popup thì chặn các sự kiện click khác

        # Kiểm tra click nút Giftcode
        self.btn_giftcode.check_hover(mouse_pos)
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.btn_giftcode.is_clicked(mouse_pos, mouse_pressed):
                self.show_giftcode_popup = True
                self.giftcode_input = ""
                return None

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                self.player_name = self.player_name[:-1]
            elif event.key == pygame.K_RETURN:
                if len(self.player_name) > 0:
                    self.next_state = STATE_DASHBOARD
            else:
                if event.unicode.isalpha() or event.unicode.isdigit():
                    if len(self.player_name) < 12:
                        self.player_name += event.unicode

    def draw(self, screen):
        if self.background:
            screen.blit(self.background, (0, 0))
        else:
            screen.fill(BG_COLOR)
            
        center_x = WINDOW_WIDTH // 2
        center_y = WINDOW_HEIGHT // 2

        # 1. Vẽ Tiêu đề có bóng đen
        self.draw_shadow_text(screen, "PIPE PUZZLE", self.font_title, PIPE_COLOR_ON, (center_x, center_y - 130))
        
        # 2. Vẽ Hướng dẫn có bóng đen
        self.draw_shadow_text(screen, "Nhập tên của bạn:", self.font_sub, TEXT_COLOR, (center_x, center_y - 65))
        
        # 3. Vẽ ô nhập tên (Thêm viền Neon)
        pygame.draw.rect(screen, INPUT_BOX_COLOR, self.input_rect, 0, 15) # Nền xám, bo góc
        pygame.draw.rect(screen, PIPE_COLOR_ON, self.input_rect, 3, 15)   # Viền Neon xanh rực
        
        # 4. Vẽ tên người chơi
        if len(self.player_name) > 0:
            name_surf = self.font_sub.render(self.player_name, True, TEXT_COLOR)
            name_rect = name_surf.get_rect(center=self.input_rect.center)
            screen.blit(name_surf, name_rect)
        else:
            name_rect = pygame.Rect(self.input_rect.centerx, self.input_rect.centery, 0, 0)
            
        # 5. Con trỏ nhấp nháy
        self.cursor_timer += 1
        if self.cursor_timer >= 30:
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = 0
            
        if self.cursor_visible:
            cursor_x = name_rect.right + 5 if len(self.player_name) > 0 else self.input_rect.centerx
            pygame.draw.line(screen, TEXT_COLOR, (cursor_x, self.input_rect.centery - 18), (cursor_x, self.input_rect.centery + 18), 3)
            
        # 6. Chữ Hint khi đã nhập tên
        if len(self.player_name) > 0:
            self.draw_shadow_text(screen, "Nhấn ENTER để bắt đầu", self.font_sub, HIGHLIGHT_COLOR, (center_x, center_y + 80))

class DashboardScreen:
    def __init__(self):
        self.font_title = pygame.font.SysFont('tahoma', 60, bold=True)
        self.font_btn = pygame.font.SysFont('tahoma', 32, bold=True)
        self.next_state = None
        
        self.btn_play = Button(WINDOW_WIDTH//2 - 150, 250, 300, 60, "CHỌN MÀN CHƠI", (0, 200, 200), (0, 0, 0))
        self.btn_shop = Button(WINDOW_WIDTH//2 - 150, 340, 300, 60, "CỬA HÀNG", (52, 152, 219), (255, 255, 255))
        self.btn_quests = Button(WINDOW_WIDTH//2 - 150, 430, 300, 60, "NHIỆM VỤ", (155, 89, 182), (255, 255, 255))
        self.btn_skin = Button(WINDOW_WIDTH - 150, WINDOW_HEIGHT - 80, 120, 50, "SKIN", (241, 196, 15), (0, 0, 0))
        
        # ---> NÚT GIFTCODE NẰM Ở ĐÂY RỒI NHÉ SẾP <---
        self.btn_giftcode = Button(30, WINDOW_HEIGHT - 80, 160, 50, "GIFTCODE", (155, 89, 182), (255, 255, 255))
        self.show_giftcode_popup = False
        self.giftcode_input = ""

    def handle_event(self, event):
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()

        # Xử lý Popup Giftcode
        if self.show_giftcode_popup:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if self.giftcode_input.upper() == "HACKERPRO":
                        return "UNLOCK_ALL"
                    self.show_giftcode_popup = False
                    self.giftcode_input = ""
                elif event.key == pygame.K_BACKSPACE:
                    self.giftcode_input = self.giftcode_input[:-1]
                elif event.key == pygame.K_ESCAPE:
                    self.show_giftcode_popup = False
                else:
                    if len(self.giftcode_input) < 15:
                        self.giftcode_input += event.unicode
            return None

        self.btn_play.check_hover(mouse_pos)
        self.btn_shop.check_hover(mouse_pos)
        self.btn_quests.check_hover(mouse_pos)
        self.btn_skin.check_hover(mouse_pos)
        self.btn_giftcode.check_hover(mouse_pos)

        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.btn_play.is_clicked(mouse_pos, mouse_pressed): self.next_state = STATE_LEVEL_SELECT
            elif self.btn_shop.is_clicked(mouse_pos, mouse_pressed): self.next_state = STATE_SHOP
            elif self.btn_quests.is_clicked(mouse_pos, mouse_pressed): self.next_state = STATE_QUESTS
            elif self.btn_skin.is_clicked(mouse_pos, mouse_pressed): self.next_state = STATE_SKIN
            elif self.btn_giftcode.is_clicked(mouse_pos, mouse_pressed):
                self.show_giftcode_popup = True
                self.giftcode_input = ""
        return None

    def draw(self, screen, player_name, coins):
        screen.fill((30, 30, 30)) # Sếp có thể thay bằng self.bg nếu sau này có nền
        
        pygame.draw.rect(screen, (50, 50, 50), (0, 0, WINDOW_WIDTH, 80))
        
        font_info = pygame.font.SysFont('tahoma', 32, bold=True)
        name_text = font_info.render(f"PLAYER: {player_name}", True, (255, 255, 255))
        screen.blit(name_text, (30, 20))
        
        coins_text = font_info.render(f"XU: {coins}", True, (255, 215, 0))
        screen.blit(coins_text, (WINDOW_WIDTH - 200, 20))

        title = self.font_title.render("PIPE PUZZLE", True, (0, 255, 255))
        screen.blit(title, title.get_rect(center=(WINDOW_WIDTH//2, 150)))

        self.btn_play.draw(screen)
        self.btn_shop.draw(screen)
        self.btn_quests.draw(screen)
        self.btn_skin.draw(screen)
        
        # VẼ NÚT GIFTCODE
        self.btn_giftcode.draw(screen)

        # VẼ POPUP
        if self.show_giftcode_popup:
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))
            
            box_w, box_h = 400, 200
            box_x, box_y = (WINDOW_WIDTH - box_w)//2, (WINDOW_HEIGHT - box_h)//2
            pygame.draw.rect(screen, (40, 45, 50), (box_x, box_y, box_w, box_h), border_radius=15)
            pygame.draw.rect(screen, (155, 89, 182), (box_x, box_y, box_w, box_h), 4, border_radius=15)
            
            font_chapter = pygame.font.SysFont('tahoma', 36, bold=True)
            txt_title = font_chapter.render("NHẬP MÃ BÍ MẬT:", True, (255, 255, 255))
            screen.blit(txt_title, txt_title.get_rect(center=(WINDOW_WIDTH//2, box_y + 40)))
            
            pygame.draw.rect(screen, (20, 20, 20), (box_x + 20, box_y + 80, box_w - 40, 50))
            txt_input = font_chapter.render(self.giftcode_input + "_", True, (255, 215, 0))
            screen.blit(txt_input, (box_x + 30, box_y + 85))
            
            font_btn = pygame.font.SysFont('tahoma', 24, bold=True)
            txt_hint = font_btn.render("Ấn ENTER để xác nhận", True, (150, 150, 150))
            screen.blit(txt_hint, txt_hint.get_rect(center=(WINDOW_WIDTH//2, box_y + 160)))


class LevelSelectScreen:
    def __init__(self):
        self.font_title = pygame.font.SysFont('tahoma', 50, bold=True)
        self.font_chapter = pygame.font.SysFont('tahoma', 36, bold=True)
        self.font_btn = pygame.font.SysFont('tahoma', 24, bold=True)
        self.next_state = None
        self.selected_level = 1
        
        self.current_chapter = 1 # Trang Act hiện tại
        self.max_chapters = 5    # Tổng số trang (5 Act)
        
        self.btn_menu = Button(20, 20, 150, 50, "<- MENU", (149, 165, 166), (255, 255, 255))
        
        # ĐÃ XÓA SẠCH BIẾN NÚT GIFTCODE Ở ĐÂY
        
        # Nút chuyển trang (Act)
        self.btn_prev_chap = Button(WINDOW_WIDTH // 2 - 250, 110, 50, 50, "<", (52, 152, 219), (255, 255, 255))
        self.btn_next_chap = Button(WINDOW_WIDTH // 2 + 200, 110, 50, 50, ">", (52, 152, 219), (255, 255, 255))

    def get_chapter_name(self):
        return f"ACT {self.current_chapter}"

    def handle_event(self, event, unlocked_levels):
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()

        # ĐÃ XÓA SẠCH LOGIC GÕ BÀN PHÍM GIFTCODE Ở ĐÂY

        self.btn_menu.check_hover(mouse_pos)
        self.btn_prev_chap.check_hover(mouse_pos)
        self.btn_next_chap.check_hover(mouse_pos)

        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.btn_menu.is_clicked(mouse_pos, mouse_pressed):
                self.next_state = STATE_DASHBOARD
            
            # Xử lý nút Lật trang
            elif self.btn_prev_chap.is_clicked(mouse_pos, mouse_pressed) and self.current_chapter > 1:
                self.current_chapter -= 1
            elif self.btn_next_chap.is_clicked(mouse_pos, mouse_pressed) and self.current_chapter < self.max_chapters:
                self.current_chapter += 1

            # Check click vào 12 nút màn chơi
            start_x = (WINDOW_WIDTH - (4 * 110)) // 2 + 10 
            start_y = 200
            for i in range(12):
                row = i // 4
                col = i % 4
                rect = pygame.Rect(start_x + col * 110, start_y + row * 110, 80, 80)
                
                if rect.collidepoint(mouse_pos):
                    actual_level = (self.current_chapter - 1) * 12 + (i + 1)
                    if actual_level <= unlocked_levels:
                        self.selected_level = actual_level
                        self.next_state = STATE_GAME_PLAY
        return None

    def draw(self, screen, unlocked_levels):
        # Tiêu đề
        title = self.font_title.render("CHỌN MÀN CHƠI", True, (255, 215, 0))
        screen.blit(title, title.get_rect(center=(WINDOW_WIDTH // 2, 50)))
        
        self.btn_menu.draw(screen)
        
        # ĐÃ XÓA SẠCH LỆNH VẼ NÚT GIFTCODE Ở ĐÂY

        # Vẽ tên Act và nút Lật trang
        chap_name = self.font_chapter.render(self.get_chapter_name(), True, (200, 255, 255))
        screen.blit(chap_name, chap_name.get_rect(center=(WINDOW_WIDTH // 2, 135)))
        
        if self.current_chapter > 1: self.btn_prev_chap.draw(screen)
        if self.current_chapter < self.max_chapters: self.btn_next_chap.draw(screen)

        # Vẽ lưới 12 ô Level
        start_x = (WINDOW_WIDTH - (4 * 110)) // 2 + 10
        start_y = 200
        for i in range(12):
            row = i // 4
            col = i % 4
            rect = pygame.Rect(start_x + col * 110, start_y + row * 110, 80, 80)
            
            actual_level = (self.current_chapter - 1) * 12 + (i + 1)
            display_num = str(i + 1) 
            
            if actual_level <= unlocked_levels:
                pygame.draw.rect(screen, (46, 204, 113), rect, border_radius=15)
                pygame.draw.rect(screen, (39, 174, 96), rect, 4, border_radius=15)
                lvl_text = self.font_title.render(display_num, True, (255, 255, 255))
            else:
                pygame.draw.rect(screen, (80, 80, 80), rect, border_radius=15)
                pygame.draw.rect(screen, (50, 50, 50), rect, 4, border_radius=15)
                lvl_text = self.font_title.render("X", True, (150, 150, 150))

            screen.blit(lvl_text, lvl_text.get_rect(center=rect.center))

class PauseMenu:
    def __init__(self):
        self.overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.overlay.set_alpha(200)
        self.overlay.fill((0, 0, 0))
        center_x, center_y = WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2
        
        # --- VẼ NÚT TIẾNG VIỆT ---
        self.btn_restart = Button(center_x - 100, center_y - 100, 200, 50, "CHƠI LẠI", PIPE_COLOR_ON, (0, 0, 0))
        self.btn_ai = Button(center_x - 100, center_y - 30, 200, 50, "AI GIẢI", (150, 100, 200), (255, 255, 255))
        self.btn_exit = Button(center_x - 100, center_y + 40, 200, 50, "THOÁT MÀN", (200, 50, 50), (255, 255, 255))
        self.action = None 
        
    def handle_event(self, event):
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()
        self.btn_restart.check_hover(mouse_pos); self.btn_ai.check_hover(mouse_pos); self.btn_exit.check_hover(mouse_pos)
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.btn_restart.is_clicked(mouse_pos, mouse_pressed): self.action = "RESTART"
            elif self.btn_ai.is_clicked(mouse_pos, mouse_pressed): self.action = "AI_SOLVE"
            elif self.btn_exit.is_clicked(mouse_pos, mouse_pressed): self.action = "EXIT"

    def draw(self, screen):
        screen.blit(self.overlay, (0, 0))
        self.btn_restart.draw(screen); self.btn_ai.draw(screen); self.btn_exit.draw(screen)

        self.btn_giftcode.draw(screen)

        if self.show_giftcode_popup:
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))
            
            box_w, box_h = 400, 200
            box_x, box_y = (WINDOW_WIDTH - box_w)//2, (WINDOW_HEIGHT - box_h)//2
            pygame.draw.rect(screen, (40, 45, 50), (box_x, box_y, box_w, box_h), border_radius=15)
            pygame.draw.rect(screen, (155, 89, 182), (box_x, box_y, box_w, box_h), 4, border_radius=15)
            
            font_chapter = pygame.font.SysFont('tahoma', 36, bold=True)
            txt_title = font_chapter.render("NHẬP MÃ BÍ MẬT:", True, (255, 255, 255))
            screen.blit(txt_title, txt_title.get_rect(center=(WINDOW_WIDTH//2, box_y + 40)))
            
            pygame.draw.rect(screen, (20, 20, 20), (box_x + 20, box_y + 80, box_w - 40, 50))
            txt_input = font_chapter.render(self.giftcode_input + "_", True, (255, 215, 0))
            screen.blit(txt_input, (box_x + 30, box_y + 85))
            
            font_btn = pygame.font.SysFont('tahoma', 24, bold=True)
            txt_hint = font_btn.render("Ấn ENTER để xác nhận", True, (150, 150, 150))
            screen.blit(txt_hint, txt_hint.get_rect(center=(WINDOW_WIDTH//2, box_y + 160)))

class TutorialPopup:
    def __init__(self):
        self.overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.overlay.set_alpha(200)
        self.overlay.fill((0, 0, 0))
        
        # Hạ cỡ chữ Tiêu đề xuống 36, chữ nội dung xuống 22
        self.font_title = pygame.font.SysFont('tahoma', 36, bold=True)
        self.font_text = pygame.font.SysFont('tahoma', 22)
        
        # NỚI RỘNG KHUNG BẢNG: Từ 500 lên 640 pixel để chữ thở
        self.popup_rect = pygame.Rect(WINDOW_WIDTH//2 - 320, WINDOW_HEIGHT//2 - 200, 640, 400)
        
        # Nút bấm căn giữa lại
        self.btn_understand = Button(WINDOW_WIDTH//2 - 120, WINDOW_HEIGHT//2 + 100, 240, 50, "TÔI ĐÃ HIỂU!", PIPE_COLOR_ON, (0, 0, 0))
        self.action = None

    def handle_event(self, event):
        mouse_pos = pygame.mouse.get_pos()
        self.btn_understand.check_hover(mouse_pos)
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.btn_understand.is_clicked(mouse_pos, pygame.mouse.get_pressed()): 
                self.action = "UNDERSTOOD"

    def draw(self, screen):
        screen.blit(self.overlay, (0, 0))
        pygame.draw.rect(screen, INPUT_BOX_COLOR, self.popup_rect, border_radius=15)
        pygame.draw.rect(screen, PIPE_COLOR_ON, self.popup_rect, 2, border_radius=15)
        
        title_surf = self.font_title.render("HƯỚNG DẪN CƠ BẢN", True, PIPE_COLOR_ON)
        screen.blit(title_surf, title_surf.get_rect(center=(WINDOW_WIDTH//2, self.popup_rect.top + 40)))
        
        instructions = [
            "1. Click chuột TRÁI vào ống nước để xoay 90 độ.",
            "2. Nối thông dòng nước (màu neon) từ góc TRÁI-TRÊN.",
            "3. Dùng nút 'AI GIẢI' trên MENU nếu bạn bị kẹt.",
            "MỤC TIÊU: Dẫn nước chạm tới góc PHẢI-DƯỚI!"
        ]
        
        # Thụt lề vào 40px cho đẹp
        for i, text in enumerate(instructions):
            color = HIGHLIGHT_COLOR if i == 3 else TEXT_COLOR
            text_surf = self.font_text.render(text, True, color)
            screen.blit(text_surf, (self.popup_rect.left + 40, self.popup_rect.top + 110 + i*45))
            
        self.btn_understand.draw(screen)

# Placeholder cho Shop và Quests (Team se code sau)
class ShopScreen:
    def __init__(self):
        self.next_state = None
        self.font = pygame.font.SysFont('tahoma', 40)
    def handle_event(self, e): pass
    def draw(self, s): s.fill(BG_COLOR); s.blit(self.font.render("CỬA HÀNG (Team se code sau)", True, TEXT_COLOR), (200, 300))

class QuestsScreen:
    def __init__(self):
        self.next_state = None
        self.font = pygame.font.SysFont('tahoma', 40)
    def handle_event(self, e): pass
    def draw(self, s): s.fill(BG_COLOR); s.blit(self.font.render("NHIỆM VỤ (Team se code sau)", True, TEXT_COLOR), (200, 300))

class WinPopup:
    def __init__(self):
        self.overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.overlay.set_alpha(220)
        self.overlay.fill((0, 0, 0))
        self.font = pygame.font.SysFont('tahoma', 50, bold=True) 
        self.action = None
        
        self.popup_rect = pygame.Rect(WINDOW_WIDTH//2 - 250, WINDOW_HEIGHT//2 - 150, 500, 300)
        
        
        # 2 nút MENU và CHƠI TIẾP
        self.btn_next = Button(WINDOW_WIDTH//2 - 120, 250, 240, 60, "CHƠI TIẾP", (46, 204, 113), (255,255,255))
        
        # --- THÊM NÚT CHƠI LẠI Ở ĐÂY ---
        self.btn_replay = Button(WINDOW_WIDTH//2 - 120, 330, 240, 60, "CHƠI LẠI", (230, 126, 34), (255,255,255)) 
        
        self.btn_menu = Button(WINDOW_WIDTH//2 - 120, 410, 240, 60, "VỀ MENU", (149, 165, 166), (255,255,255))
        

    def handle_event(self, event):
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()
        
        self.btn_next.check_hover(mouse_pos)
        self.btn_replay.check_hover(mouse_pos) # Nhớ check hover cho nút mới
        self.btn_menu.check_hover(mouse_pos)
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.btn_next.is_clicked(mouse_pos, mouse_pressed):
                self.action = "NEXT"
            elif self.btn_replay.is_clicked(mouse_pos, mouse_pressed): # BẮT SỰ KIỆN CLICK
                self.action = "REPLAY"
            elif self.btn_menu.is_clicked(mouse_pos, mouse_pressed):
                self.action = "MENU"

    def draw(self, screen):
        # Kích thước khung mới: Rộng 500, Cao 400 (bọc dư sức 3 nút)
        popup_width = 540
        popup_height = 400  
        popup_x = WINDOW_WIDTH // 2 - popup_width // 2
        popup_y = 130 # Kéo khung dịch lên trên một chút
        
        # 1. Vẽ nền xám đen cho khung (bo góc 20)
        pygame.draw.rect(screen, (40, 45, 50), (popup_x, popup_y, popup_width, popup_height), border_radius=20)
        
        # 2. Vẽ viền vàng hoàng kim (dày 5px, bo góc 20)
        pygame.draw.rect(screen, (255, 215, 0), (popup_x, popup_y, popup_width, popup_height), 5, border_radius=20)
        
        # 3. Vẽ chữ Tiêu đề (căn ra giữa, nhích xuống một xíu so với mép trên của khung)
        text_surf = self.font.render("HỆ THỐNG ĐÃ KẾT NỐI!", True, (255, 215, 0))
        screen.blit(text_surf, text_surf.get_rect(center=(WINDOW_WIDTH//2, 190)))
        
        # 4. Vẽ 3 cái nút của Sếp
        self.btn_next.draw(screen)
        self.btn_replay.draw(screen)
        self.btn_menu.draw(screen)

class SkinScreen:
    def __init__(self):
        self.next_state = None
        self.font = pygame.font.SysFont('tahoma', 40)
        self.btn_back = Button(20, 20, 150, 50, "QUAY LẠI", INPUT_BOX_COLOR, TEXT_COLOR)
    def handle_event(self, event):
        mouse_pos = pygame.mouse.get_pos()
        self.btn_back.check_hover(mouse_pos)
        if event.type == pygame.MOUSEBUTTONDOWN and self.btn_back.is_clicked(mouse_pos, pygame.mouse.get_pressed()):
            self.next_state = STATE_DASHBOARD
    def draw(self, screen): 
        screen.fill(BG_COLOR)
        screen.blit(self.font.render("CHỌN SKIN (Tính năng đang phát triển)", True, HIGHLIGHT_COLOR), (WINDOW_WIDTH//2 - 300, 300))
        self.btn_back.draw(screen)

class ShopScreen:
    def __init__(self):
        self.next_state = None
        self.font = pygame.font.SysFont('tahoma', 40, bold=True)
        # Nút Quay lại góc trên bên trái
        self.btn_back = Button(20, 20, 150, 50, "QUAY LẠI", INPUT_BOX_COLOR, TEXT_COLOR)

    def handle_event(self, event):
        mouse_pos = pygame.mouse.get_pos()
        self.btn_back.check_hover(mouse_pos)
        
        # Bắt sự kiện click vào nút
        if event.type == pygame.MOUSEBUTTONDOWN and self.btn_back.is_clicked(mouse_pos, pygame.mouse.get_pressed()):
            self.next_state = STATE_DASHBOARD

    def draw(self, screen): 
        screen.fill(BG_COLOR)
        # Bố trí dòng chữ ngay chính giữa cho đẹp
        text_surf = self.font.render("CỬA HÀNG (Tính năng đang phát triển)", True, (50, 150, 200))
        screen.blit(text_surf, text_surf.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2)))
        self.btn_back.draw(screen)

class QuestsScreen:
    def __init__(self):
        self.next_state = None
        self.font = pygame.font.SysFont('tahoma', 40, bold=True)
        # Nút Quay lại góc trên bên trái
        self.btn_back = Button(20, 20, 150, 50, "QUAY LẠI", INPUT_BOX_COLOR, TEXT_COLOR)

    def handle_event(self, event):
        mouse_pos = pygame.mouse.get_pos()
        self.btn_back.check_hover(mouse_pos)
        
        # Bắt sự kiện click vào nút
        if event.type == pygame.MOUSEBUTTONDOWN and self.btn_back.is_clicked(mouse_pos, pygame.mouse.get_pressed()):
            self.next_state = STATE_DASHBOARD

    def draw(self, screen): 
        screen.fill(BG_COLOR)
        text_surf = self.font.render("NHIỆM VỤ (Tính năng đang phát triển)", True, (150, 100, 200))
        screen.blit(text_surf, text_surf.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2)))
        self.btn_back.draw(screen)