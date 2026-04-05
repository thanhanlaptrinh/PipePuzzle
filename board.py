# board.py
import pygame
import pygame.gfxdraw
import random
from settings import *

SKIN_THEMES = {
    "DEFAULT": {"border": (50, 30, 20), "metal": (190, 115, 60), "brass": (230, 180, 60), "on": (150, 255, 220), "glow": (0, 200, 150), "water_off": (40, 50, 45)},
    "CYBER_NEON": {"border": (20, 20, 30), "metal": (40, 40, 60), "brass": (80, 80, 120), "on": (255, 100, 255), "glow": (200, 0, 200), "water_off": (30, 20, 40)},
    "MAGMA_FORGE": {"border": (40, 10, 10), "metal": (80, 20, 20), "brass": (120, 40, 20), "on": (255, 200, 100), "glow": (200, 50, 0), "water_off": (50, 20, 20)},
    "BIO_PLANT": {"border": (20, 30, 10), "metal": (40, 70, 30), "brass": (80, 120, 40), "on": (150, 255, 150), "glow": (50, 200, 50), "water_off": (20, 40, 20)},
    "GOLDEN_VIP": {"border": (100, 70, 0), "metal": (200, 150, 0), "brass": (255, 220, 50), "on": (255, 255, 200), "glow": (255, 180, 0), "water_off": (120, 100, 50)}
}
CURRENT_SKIN_ID = "DEFAULT"

class Node:
    PIPE_TYPES = {
        'I': [1, 0, 1, 0], 'L': [1, 1, 0, 0], 'T': [1, 1, 1, 0], '+': [1, 1, 1, 1],
        'C': [1, 0, 0, 0], 'P': [1, 0, 0, 0], 'O': [1, 0, 1, 0], 'X': [1, 1, 1, 1]
    }
    def __init__(self, row, col, pipe_type):
        self.row, self.col, self.pipe_type = row, col, pipe_type
        self.base_conns = list(self.PIPE_TYPES.get(pipe_type, [0, 0, 0, 0]))
        self.conns = list(self.base_conns)
        self.angle, self.target_angle = 0, 0
        self.is_powered, self.is_fixed, self.is_rock = False, False, False

    def rotate(self, direction=1):
        if self.is_fixed or self.is_rock or self.pipe_type in ['+', 'X']: return 
        if direction == 1: 
            self.conns = [self.conns[-1]] + self.conns[:-1]
            self.target_angle -= 90 
        else: 
            self.conns = self.conns[1:] + [self.conns[0]]
            self.target_angle += 90 

    def make_rock(self):
        self.is_rock = True; self.conns = [0, 0, 0, 0] 

    def break_rock(self):
        self.is_rock = False
        temp_conns = list(self.base_conns)
        rotations = (int(self.target_angle) // -90) % 4 # ĐÃ FIX LỖI TOÁN HỌC XOAY GÓC
        for _ in range(rotations): temp_conns = [temp_conns[-1]] + temp_conns[:-1]
        self.conns = temp_conns

class Board:
    def __init__(self, level_id=1, difficulty=DIFF_NORMAL, custom_data=None):
        self.level_id = level_id
        self.difficulty = difficulty
        self.custom_data = custom_data 
        self.portals = [] 
        
        # Đọc kích thước từ file Custom nếu có, ngược lại dùng mặc định
        if self.custom_data and "size" in self.custom_data:
            self.rows = self.cols = self.custom_data["size"]
        else:
            if self.level_id == 1: self.rows, self.cols = 3, 3
            elif self.level_id == 2: self.rows, self.cols = 5, 5
            elif self.level_id in [3, 4]: self.rows, self.cols = 7, 7
            else: self.rows, self.cols = 10, 10
            
        self.grid = []
        self.generate_board() 
        self.update_connectivity()

    def break_rock(self, mouse_x, mouse_y):
        offset_x = (WINDOW_WIDTH - (self.cols * TILE_SIZE)) // 2
        offset_y = (WINDOW_HEIGHT - (self.rows * TILE_SIZE)) // 2
        col, row = (mouse_x - offset_x) // TILE_SIZE, (mouse_y - offset_y) // TILE_SIZE
        if 0 <= row < self.rows and 0 <= col < self.cols:
            if self.grid[row][col].is_rock:
                self.grid[row][col].break_rock(); self.update_connectivity(); return True
        return False  
    
    def check_win(self): return self.grid[self.rows-1][self.cols-1].is_powered
    
    def generate_board(self):
        self.grid = []
        random.seed(self.level_id + self.difficulty * 1000) 
        for r in range(self.rows): self.grid.append([None for _ in range(self.cols)])
        req_conns = [[[False]*4 for _ in range(self.cols)] for _ in range(self.rows)]
        req_conns[0][0][1] = True; req_conns[0][1][3] = True
        req_conns[self.rows-1][self.cols-1][3] = True; req_conns[self.rows-1][self.cols-2][1] = True
        
        visited = set([(0, 0), (self.rows-1, self.cols-1)]); stack = [(0, 1)]; visited.add((0, 1))
        while stack:
            r, c = stack[-1]; neighbors = []
            if r > 0 and (r-1, c) not in visited: neighbors.append((r-1, c, 0, 2))
            if c < self.cols-1 and (r, c+1) not in visited: neighbors.append((r, c+1, 1, 3))
            if r < self.rows-1 and (r+1, c) not in visited: neighbors.append((r+1, c, 2, 0))
            if c > 0 and (r, c-1) not in visited: neighbors.append((r, c-1, 3, 1))
            
            if neighbors:
                nr, nc, dir_out, dir_in = random.choice(neighbors)
                req_conns[r][c][dir_out] = True; req_conns[nr][nc][dir_in] = True
                visited.add((nr, nc)); stack.append((nr, nc))
            else: stack.pop()
                
        extra_paths = (self.rows * self.cols) // 3
        for _ in range(extra_paths):
            r, c = random.randint(0, self.rows-1), random.randint(0, self.cols-1)
            if (r, c) == (0, 0) or (r, c) == (self.rows-1, self.cols-1): continue
            direction = random.randint(0, 3)
            nr, nc = r + [-1, 0, 1, 0][direction], c + [0, 1, 0, -1][direction]
            if 0 <= nr < self.rows and 0 <= nc < self.cols:
                if (nr, nc) == (0, 0) or (nr, nc) == (self.rows-1, self.cols-1): continue
                req_conns[r][c][direction] = True; req_conns[nr][nc][[2, 3, 0, 1][direction]] = True

        self.portals = []
        if self.difficulty >= DIFF_NORMAL:
            dead_ends = [(r, c) for r in range(self.rows) for c in range(self.cols) if sum(req_conns[r][c]) == 1 and (r, c) not in [(0, 0), (self.rows-1, self.cols-1)]]
            if len(dead_ends) >= 2: self.portals = list(random.sample(dead_ends, 2))

        def get_pipe_type(conn, r, c):
            if (r, c) in [(0, 0), (self.rows-1, self.cols-1)]: return 'C' # ÉP BUỘC IN/OUT LÀ ỐNG CỤT
            if (r, c) in self.portals: return 'P'
            
            # --- ĐỌC DỮ LIỆU CUSTOM NẾU CÓ ---
            if getattr(self, 'custom_data', None):
                allowed = self.custom_data.get('pipes', ['I', 'L', 'T', '+', 'C', 'P', 'O', 'X'])
                if not allowed: allowed = ['I', 'L']
                req_count = sum(conn)
                valid = [p for p in allowed if sum(Node.PIPE_TYPES[p]) >= req_count]
                if valid: return random.choice(valid)
                return random.choice(allowed)
                
            count = sum(conn)
            if count == 4: return 'X' if self.difficulty == DIFF_HARD and random.random() < 0.25 else '+'
            if count == 3: return 'T'
            if count == 2:
                if conn[0] and conn[2]: return 'O' if self.difficulty == DIFF_HARD and random.random() < 0.25 else 'I'
                if conn[1] and conn[3]: return 'O' if self.difficulty == DIFF_HARD and random.random() < 0.25 else 'I'
                return 'L'
            if count == 1: return 'C' if self.difficulty >= DIFF_NORMAL else random.choice(['I', 'L'])
            return random.choice(['I','L'])

        for r in range(self.rows):
            for c in range(self.cols):
                node = Node(r, c, get_pipe_type(req_conns[r][c], r, c))
                if (r, c) in [(0, 0), (self.rows-1, self.cols-1)]: self.grid[r][c] = node; continue
                for _ in range(4):
                    covers = True
                    for i in range(4):
                        if req_conns[r][c][i] and not node.conns[i]: covers = False
                    if covers: break
                    node.rotate()
                self.grid[r][c] = node

        in_node, out_node = self.grid[0][0], self.grid[self.rows-1][self.cols-1]
        while not in_node.conns[1]: in_node.rotate() 
        in_node.angle = in_node.target_angle; in_node.is_fixed = True
        while not out_node.conns[3]: out_node.rotate() 
        out_node.angle = out_node.target_angle; out_node.is_fixed = True
        
        for r in range(self.rows):
            for c in range(self.cols):
                if not getattr(self.grid[r][c], 'is_fixed', False):
                    for _ in range(random.randint(1, 3)): self.grid[r][c].rotate()
                    self.grid[r][c].angle = self.grid[r][c].target_angle

        # --- SINH ĐÁ THEO CUSTOM DATA HOẶC MẶC ĐỊNH ---
        if getattr(self, 'custom_data', None):
            num_rocks = self.custom_data.get('rocks', 0)
        elif self.difficulty > DIFF_EASY and self.level_id > 1:
            if self.rows <= 5: num_rocks = random.randint(3, 5) 
            elif self.rows == 7: num_rocks = random.randint(10, 13) 
            elif self.rows >= 10: num_rocks = random.randint(15, 20) 
            else: num_rocks = 0
            if self.difficulty == DIFF_NORMAL: num_rocks = max(0, num_rocks - 4)
        else: num_rocks = 0

        placed = 0; attempts = 0
        while placed < num_rocks and attempts < 500:
            rr, cc = random.randint(0, self.rows - 1), random.randint(0, self.cols - 1)
            node = self.grid[rr][cc]
            if not node.is_fixed and not node.is_rock and node.pipe_type not in ['P', '+', 'X']:
                node.make_rock(); placed += 1
            attempts += 1
        random.seed()

    def handle_click(self, mouse_x, mouse_y, is_left_click=True):
        offset_x = (WINDOW_WIDTH - (self.cols * TILE_SIZE)) // 2
        offset_y = (WINDOW_HEIGHT - (self.rows * TILE_SIZE)) // 2
        col = (mouse_x - offset_x) // TILE_SIZE
        row = (mouse_y - offset_y) // TILE_SIZE
        if 0 <= row < self.rows and 0 <= col < self.cols:
            node = self.grid[row][col]
            if not getattr(node, 'is_fixed', False) and not getattr(node, 'is_rock', False) and node.pipe_type not in ['+', 'X']:
                node.rotate(direction=1 if is_left_click else -1)
                self.update_connectivity()
                return True # Trả về True nếu xoay thành công để tính lượt
        return False

    def update_connectivity(self):
        for row in range(self.rows):
            for col in range(self.cols):
                self.grid[row][col].is_powered = False

        start_node = self.grid[0][0]
        if start_node.is_rock: return

        start_node.is_powered = True
        # Queue giờ lưu tuple: (node, hướng_nước_đi_vào)
        queue = [(start_node, -1)]
        visited = set([(0,0)])
        neighbor_offsets = [(-1, 0), (0, 1), (1, 0), (0, -1)]

        while queue:
            current, in_dir = queue.pop(0)

            # XỬ LÝ CỔNG DỊCH CHUYỂN
            if current.pipe_type == 'P':
                for pr, pc in self.portals:
                    if (pr, pc) != (current.row, current.col):
                        other_p = self.grid[pr][pc]
                        if not other_p.is_powered:
                            other_p.is_powered = True
                            visited.add((pr, pc))
                            queue.append((other_p, -1)) # Portal hoạt động như một nguồn nước mới

            for direction in range(4):
                if current.conns[direction] == 0: continue

                # XỬ LÝ CẦU VƯỢT: Chỉ cho nước chảy thẳng
                if current.pipe_type == 'X' and in_dir != -1:
                    if direction != (in_dir + 2) % 4:
                        continue

                dr, dc = neighbor_offsets[direction]
                n_row, n_col = current.row + dr, current.col + dc

                if not (0 <= n_row < self.rows and 0 <= n_col < self.cols): continue

                neighbor = self.grid[n_row][n_col]
                opposite_dir = (direction + 2) % 4

                if neighbor.conns[opposite_dir] == 1:
                    # XỬ LÝ ỐNG MỘT CHIỀU: Chặn dòng chảy ngược
                    if neighbor.pipe_type == 'O':
                        rotations = (int(neighbor.target_angle) // -90) % 4 
                        valid_entry_dir = rotations
                        if opposite_dir != valid_entry_dir:
                            continue

                    if (n_row, n_col) not in visited:
                        neighbor.is_powered = True
                        visited.add((n_row, n_col))
                        queue.append((neighbor, opposite_dir))

    def draw(self, screen):
        offset_x = (WINDOW_WIDTH - (self.cols * TILE_SIZE)) // 2
        offset_y = (WINDOW_HEIGHT - (self.rows * TILE_SIZE)) // 2

        # Bảng nền
        panel = pygame.Surface((self.cols * TILE_SIZE + 40, self.rows * TILE_SIZE + 40), pygame.SRCALPHA)
        pygame.draw.rect(panel, (25, 25, 30, 220), panel.get_rect(), border_radius=15) 
        pygame.draw.rect(panel, (180, 120, 50), panel.get_rect(), 3, border_radius=15)
        screen.blit(panel, (offset_x - 20, offset_y - 20))

        # Lấy theme hiện tại để tính màu lưới
        theme = SKIN_THEMES.get(CURRENT_SKIN_ID, SKIN_THEMES["DEFAULT"])
        # Pha màu lưới dựa trên màu Glow của nước (chia 6 rồi cộng thêm tí nền xám để ra màu mờ ảo)
        glow = theme["glow"]
        grid_color = (glow[0] // 6 + 15, glow[1] // 6 + 15, glow[2] // 6 + 15)

        # PASS 1: VẼ LƯỚI VÀ ỐNG BẰNG CODE VECTOR "STEAMPUNK"
        for row in range(self.rows):
            for col in range(self.cols):
                x = offset_x + col * TILE_SIZE; y = offset_y + row * TILE_SIZE
                rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
                
                # Vẽ lưới bằng màu đã pha mờ theo tông của Skin
                pygame.draw.rect(screen, grid_color, rect, 1)

                # Làm dịu màu nền của ô Đầu vào (Xanh) và Đầu ra (Đỏ) để đỡ gắt mắt
                if row == 0 and col == 0: pygame.draw.rect(screen, (20, 45, 45), rect.inflate(-2, -2))
                elif row == self.rows - 1 and col == self.cols - 1: pygame.draw.rect(screen, (45, 20, 20), rect.inflate(-2, -2))

                node = self.grid[row][col]
                if abs(node.target_angle - node.angle) > 0.1: node.angle += (node.target_angle - node.angle) * 0.3
                else: node.angle = node.target_angle

                pipe_surface = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
                center = TILE_SIZE // 2
                
                theme = SKIN_THEMES.get(CURRENT_SKIN_ID, SKIN_THEMES["DEFAULT"])
                outer_w = 26; metal_w = 20; water_w = 6; flange_w = 34; flange_t = 6  
                # Lấy toàn bộ màu kim loại, viền, nước từ Theme
                c_border = theme["border"]       
                c_metal = theme["metal"]      
                c_brass = theme["brass"]      
                c_water = theme["on"] if node.is_powered else theme["water_off"] 
                
                dirs = node.base_conns
            
                # 1. Vẽ thân ống ngoài cùng (Viền)
                pygame.gfxdraw.aacircle(pipe_surface, center, center, outer_w // 2, c_border)
                pygame.gfxdraw.filled_circle(pipe_surface, center, center, outer_w // 2, c_border)
                for i, has_conn in enumerate(dirs):
                    if has_conn:
                        end_pos = [(center, 0), (TILE_SIZE, center), (center, TILE_SIZE), (0, center)][i]
                        pygame.draw.line(pipe_surface, c_border, (center, center), end_pos, outer_w)

                # 2. Vẽ thân ống kim loại (Đồng)
                pygame.gfxdraw.aacircle(pipe_surface, center, center, metal_w // 2, c_metal)
                pygame.gfxdraw.filled_circle(pipe_surface, center, center, metal_w // 2, c_metal)
                for i, has_conn in enumerate(dirs):
                    if has_conn:
                        end_pos = [(center, 0), (TILE_SIZE, center), (center, TILE_SIZE), (0, center)][i]
                        pygame.draw.line(pipe_surface, c_metal, (center, center), end_pos, metal_w)

                # 3. Vẽ dòng nước (Glow Effect tương ứng Skin)
                if node.is_powered:
                    pygame.gfxdraw.filled_circle(pipe_surface, center, center, water_w // 2 + 3, theme["glow"])
                    for i, has_conn in enumerate(dirs):
                        if has_conn:
                            end_pos = [(center, 0), (TILE_SIZE, center), (center, TILE_SIZE), (0, center)][i]
                            pygame.draw.line(pipe_surface, theme["glow"], (center, center), end_pos, water_w + 4)

                pygame.gfxdraw.aacircle(pipe_surface, center, center, water_w // 2, c_water)
                pygame.gfxdraw.filled_circle(pipe_surface, center, center, water_w // 2, c_water)
                for i, has_conn in enumerate(dirs):
                    if has_conn:
                        end_pos = [(center, 0), (TILE_SIZE, center), (center, TILE_SIZE), (0, center)][i]
                        pygame.draw.line(pipe_surface, c_water, (center, center), end_pos, water_w)

                # 4. Vẽ mặt bích (Khớp nối có đinh tán)
                for i, has_conn in enumerate(dirs):
                    if has_conn:
                        f_rect = None
                        rivet1, rivet2 = None, None
                        if i == 0: 
                            f_rect = pygame.Rect(center - flange_w//2, 0, flange_w, flange_t)
                            rivet1, rivet2 = (center - flange_w//2 + 5, 3), (center + flange_w//2 - 5, 3)
                        elif i == 1: 
                            f_rect = pygame.Rect(TILE_SIZE - flange_t, center - flange_w//2, flange_t, flange_w)
                            rivet1, rivet2 = (TILE_SIZE - 3, center - flange_w//2 + 5), (TILE_SIZE - 3, center + flange_w//2 - 5)
                        elif i == 2: 
                            f_rect = pygame.Rect(center - flange_w//2, TILE_SIZE - flange_t, flange_w, flange_t)
                            rivet1, rivet2 = (center - flange_w//2 + 5, TILE_SIZE - 3), (center + flange_w//2 - 5, TILE_SIZE - 3)
                        elif i == 3: 
                            f_rect = pygame.Rect(0, center - flange_w//2, flange_t, flange_w)
                            rivet1, rivet2 = (3, center - flange_w//2 + 5), (3, center + flange_w//2 - 5)
                        
                        pygame.draw.rect(pipe_surface, c_border, f_rect)
                        pygame.draw.rect(pipe_surface, c_metal, f_rect.inflate(-2, -2))
                        pygame.draw.circle(pipe_surface, (30, 20, 10), rivet1, 2)
                        pygame.draw.circle(pipe_surface, (30, 20, 10), rivet2, 2)

                # =========================================================
                # 5. VẼ HÌNH THÁI TRUNG TÂM CHO CÁC ỐNG ĐẶC BIỆT (MỚI UPDATE)
                # =========================================================
                if node.pipe_type in ['T', '+']:
                    pygame.gfxdraw.filled_circle(pipe_surface, center, center, metal_w // 2 + 3, c_border)
                    pygame.gfxdraw.filled_circle(pipe_surface, center, center, metal_w // 2 + 1, c_brass)
                    for angle in [0, 45, 90, 135]:
                        surf = pygame.Surface((12, 12), pygame.SRCALPHA)
                        pygame.draw.line(surf, c_border, (6, 0), (6, 12), 3)
                        rot_surf = pygame.transform.rotate(surf, angle)
                        pipe_surface.blit(rot_surf, rot_surf.get_rect(center=(center, center)))
                    pygame.gfxdraw.filled_circle(pipe_surface, center, center, 4, c_water)
                    
                elif node.pipe_type == 'P': # PORTAL (HỐ ĐEN)
                    # Vòng tím to hơn, lõi đen thui cực kỳ dễ nhận biết
                    pygame.gfxdraw.filled_circle(pipe_surface, center, center, metal_w // 2 + 8, (138, 43, 226))
                    pygame.gfxdraw.filled_circle(pipe_surface, center, center, metal_w // 2 + 4, (75, 0, 130))
                    pygame.gfxdraw.filled_circle(pipe_surface, center, center, metal_w // 2, (10, 5, 20)) 
                    if node.is_powered:
                        pygame.gfxdraw.filled_circle(pipe_surface, center, center, water_w // 2, c_water)
                    
                elif node.pipe_type == 'C': # ỐNG CỤT (NẮP ĐỎ)
                    # Nắp bịt to màu đỏ bọc thép, không cho nước rỉ ra
                    pygame.gfxdraw.filled_circle(pipe_surface, center, center, metal_w // 2 + 4, c_border)
                    pygame.gfxdraw.filled_circle(pipe_surface, center, center, metal_w // 2 + 2, (220, 50, 40))
                    pygame.gfxdraw.filled_circle(pipe_surface, center, center, metal_w // 2 - 4, (120, 20, 20))
                    
                elif node.pipe_type == 'O': # MỘT CHIỀU (MŨI TÊN TO)
                    # Mũi tên khổng lồ chỉ hướng đi của dòng nước
                    pts = [
                        (center - 8, center - 12),  # Góc trên trái thân
                        (center + 8, center - 12),  # Góc trên phải thân
                        (center + 8, center + 2),   # Góc dưới phải thân
                        (center + 14, center + 2),  # Góc trên phải đầu nhọn
                        (center, center + 14),      # Mũi nhọn đỉnh
                        (center - 14, center + 2),  # Góc trên trái đầu nhọn
                        (center - 8, center + 2)    # Góc dưới trái thân
                    ]
                    color = theme["on"] if node.is_powered else theme["water_off"]
                    pygame.draw.polygon(pipe_surface, c_border, pts)
                    pygame.draw.polygon(pipe_surface, color, pts, 0)
                    pygame.draw.polygon(pipe_surface, (0, 0, 0), pts, 2)
                    
                elif node.pipe_type == 'X': # CẦU VƯỢT (KÈM MŨI TÊN CHỈ ĐƯỜNG)
                    bridge = pygame.Rect(center - metal_w//2, center - metal_w//2, metal_w, metal_w)
                    pygame.draw.rect(pipe_surface, c_border, bridge.inflate(6, 6), border_radius=4)
                    pygame.draw.rect(pipe_surface, c_metal, bridge.inflate(2, 2), border_radius=4)
                    if node.is_powered:
                        pygame.draw.line(pipe_surface, c_water, (center - metal_w//2, center), (center + metal_w//2, center), water_w)
                    
                    # 4 mũi tên nhỏ màu vàng cảnh báo "Chỉ được đi thẳng"
                    arr_color = (255, 200, 0)
                    pygame.draw.polygon(pipe_surface, arr_color, [(center-4, center-10), (center+4, center-10), (center, center-16)]) 
                    pygame.draw.polygon(pipe_surface, arr_color, [(center-4, center+10), (center+4, center+10), (center, center+16)]) 
                    pygame.draw.polygon(pipe_surface, arr_color, [(center-10, center-4), (center-10, center+4), (center-16, center)]) 
                    pygame.draw.polygon(pipe_surface, arr_color, [(center+10, center-4), (center+10, center+4), (center+16, center)]) 

                rotated_surface = pygame.transform.rotozoom(pipe_surface, node.angle, 1.0)
                rot_rect = rotated_surface.get_rect(center=(x + center, y + center))
                screen.blit(rotated_surface, rot_rect)

                if row == 0 and col == 0:
                    cx, cy = x + TILE_SIZE // 2, y + TILE_SIZE // 2
                    pygame.draw.circle(screen, (100, 255, 200), (cx, cy), metal_w // 2 + 6, 2)
                elif row == self.rows - 1 and col == self.cols - 1:
                    cx, cy = x + TILE_SIZE // 2, y + TILE_SIZE // 2
                    pygame.draw.circle(screen, (80, 80, 80), (cx, cy), TILE_SIZE // 2 - 8, 2)
                    
                if getattr(node, 'is_rock', False):
                    cx, cy = x + TILE_SIZE // 2, y + TILE_SIZE // 2
                    
                    # 1. Tạo hình đa giác bất đối xứng (Giống tảng đá vỡ)
                    rock_pts = [
                        (cx - 15, cy - 18), (cx + 5, cy - 20), (cx + 18, cy - 10),
                        (cx + 20, cy + 8),  (cx + 10, cy + 18), (cx - 10, cy + 20),
                        (cx - 18, cy + 10), (cx - 20, cy - 5)
                    ]
                    
                    # 2. Lớp bóng đen (Shadow) tạo cảm giác đá nổi bần bật lên mặt ống
                    shadow_pts = [(px + 3, py + 4) for px, py in rock_pts]
                    pygame.draw.polygon(screen, (20, 25, 30), shadow_pts)
                    
                    # 3. Khối đá chính màu xám đậm
                    pygame.draw.polygon(screen, (70, 75, 80), rock_pts)
                    pygame.draw.polygon(screen, (40, 45, 50), rock_pts, 3) # Viền đá
                    
                    # 4. Mảng highlight sáng tạo khối 3D (Mặt bắt sáng)
                    light_pts = [
                        (cx - 13, cy - 15), (cx + 3, cy - 17), 
                        (cx + 8, cy - 2), (cx - 8, cy)
                    ]
                    pygame.draw.polygon(screen, (90, 95, 100), light_pts)
                    
                    # 5. Các vết nứt chằng chịt, sâu hoắm
                    crack_color = (25, 25, 30)
                    pygame.draw.line(screen, crack_color, (cx - 10, cy - 5), (cx + 5, cy + 5), 2)
                    pygame.draw.line(screen, crack_color, (cx + 5, cy + 5), (cx + 15, cy - 2), 2)
                    pygame.draw.line(screen, crack_color, (cx + 2, cy + 2), (cx - 5, cy + 15), 2)
                    pygame.draw.line(screen, crack_color, (cx + 5, cy + 5), (cx + 12, cy + 12), 2)

        # PASS 2: VẼ HIỆU ỨNG GLOW Ở KHE NỐI GIỮA CÁC Ô THEO MÀU SKIN
        theme = SKIN_THEMES.get(CURRENT_SKIN_ID, SKIN_THEMES["DEFAULT"])
        for row in range(self.rows):
            for col in range(self.cols):
                node = self.grid[row][col]
                if not node.is_powered: continue
                
                x = offset_x + col * TILE_SIZE
                y = offset_y + row * TILE_SIZE
                
                if col < self.cols - 1 and node.conns[1]:
                    right_node = self.grid[row][col+1]
                    if right_node.is_powered and right_node.conns[3]:
                        seam_rect = pygame.Rect(x + TILE_SIZE - 5, y + TILE_SIZE // 2 - 5, 10, 10)
                        pygame.draw.rect(screen, theme["glow"], seam_rect.inflate(4, 4), border_radius=5)
                        pygame.draw.rect(screen, theme["on"], seam_rect, border_radius=3)

                if row < self.rows - 1 and node.conns[2]:
                    bottom_node = self.grid[row+1][col]
                    if bottom_node.is_powered and bottom_node.conns[0]:
                        seam_rect = pygame.Rect(x + TILE_SIZE // 2 - 5, y + TILE_SIZE - 5, 10, 10)
                        pygame.draw.rect(screen, theme["glow"], seam_rect.inflate(4, 4), border_radius=5)
                        pygame.draw.rect(screen, theme["on"], seam_rect, border_radius=3)