# board.py
import pygame
import random
from settings import *

class Node:
    BASE_PIPES = {
        'I': [True, False, True, False],
        'L': [True, True, False, False],
        'T': [True, True, True, False],
        '+': [True, True, True, True],
        'E': [True, False, False, False] # THÊM ỐNG MỚI: 'E' (End - Ống cụt 1 đầu)
    }
    def __init__(self, row, col, pipe_type):
        self.row = row
        self.col = col
        self.pipe_type = pipe_type
        self.connections = self.BASE_PIPES[pipe_type].copy()
        
        self.base_connections = self.BASE_PIPES[pipe_type].copy()
        self.angle = 0         
        self.target_angle = 0  
        self.is_powered = False
        
        # --- CỜ KHÓA ỐNG ---
        self.is_fixed = False 

    def rotate(self):
        # Nếu ống bị khóa (như IN/OUT) thì chặn không cho xoay
        if self.is_fixed: 
            return 
            
        self.connections = [self.connections[-1]] + self.connections[:-1]
        self.target_angle -= 90 

class Board:
    def __init__(self, level_id=1):
        self.grid = []
        self.pipe_types = ['I', 'L', 'T', '+']
        self.level_id = level_id # Lưu ID màn chơi
        self.generate_board()
        self.update_connectivity()

    def check_win(self):        
        return self.grid[ROWS-1][COLS-1].is_powered
    
    def generate_board(self):
        self.grid = []
        random.seed(self.level_id)
        
        # 1. Tạo lưới random bình thường (Lưu ý: Không random ra ống 'E')
        for row in range(ROWS):
            grid_row = []
            for col in range(COLS):
                node = Node(row, col, random.choice(self.pipe_types))
                for _ in range(random.randint(0, 3)): 
                    node.rotate()
                node.angle = node.target_angle 
                grid_row.append(node)
            self.grid.append(grid_row)
        random.seed() # Xóa hạt giống
        
        in_node = Node(0, 0, 'E') # Lấy ống 1 đầu
        in_node.rotate()          # Xoay 1 lần (Từ hướng LÊN chuyển sang hướng PHẢI)
        in_node.angle = in_node.target_angle
        in_node.is_fixed = True   # KHÓA CHẶT (Không cho click xoay nữa)
        self.grid[0][0] = in_node # Lắp đè lên ô góc trái-trên

        out_node = Node(ROWS-1, COLS-1, 'E') # Lấy ống 1 đầu
        out_node.rotate()
        out_node.rotate()
        out_node.rotate()         # Xoay 3 lần (Từ hướng LÊN chuyển sang hướng TRÁI)
        out_node.angle = out_node.target_angle
        out_node.is_fixed = True  # KHÓA CHẶT
        self.grid[ROWS-1][COLS-1] = out_node # Lắp đè lên ô góc phải-dưới

    def handle_click(self, mouse_x, mouse_y):
        offset_x = (WINDOW_WIDTH - (COLS * TILE_SIZE)) // 2
        offset_y = (WINDOW_HEIGHT - (ROWS * TILE_SIZE)) // 2
        col = (mouse_x - offset_x) // TILE_SIZE
        row = (mouse_y - offset_y) // TILE_SIZE
        
        if 0 <= row < ROWS and 0 <= col < COLS:
            self.grid[row][col].rotate()
            self.update_connectivity()

    def update_connectivity(self):
        for row in range(ROWS):
            for col in range(COLS):
                self.grid[row][col].is_powered = False

        start_node = self.grid[0][0]
        start_node.is_powered = True
        
        queue = [start_node]
        visited = set([(0,0)])
        neighbor_offsets = [(-1, 0), (0, 1), (1, 0), (0, -1)]
        opposite_direction = {0: 2, 1: 3, 2: 0, 3: 1}

        while queue:
            current = queue.pop(0)
            for direction in range(4):
                if not current.connections[direction]: continue
                
                dr, dc = neighbor_offsets[direction]
                n_row, n_col = current.row + dr, current.col + dc
                
                if not (0 <= n_row < ROWS and 0 <= n_col < COLS): continue
                if (n_row, n_col) in visited: continue

                neighbor = self.grid[n_row][n_col]
                opposite_dir = opposite_direction[direction]
                
                if neighbor.connections[opposite_dir]:
                    neighbor.is_powered = True
                    visited.add((n_row, n_col))
                    queue.append(neighbor)

    def draw(self, screen):
        offset_x = (WINDOW_WIDTH - (COLS * TILE_SIZE)) // 2
        offset_y = (WINDOW_HEIGHT - (ROWS * TILE_SIZE)) // 2

        panel = pygame.Surface((COLS * TILE_SIZE + 40, ROWS * TILE_SIZE + 40), pygame.SRCALPHA)
        pygame.draw.rect(panel, (30, 35, 45, 210), panel.get_rect(), border_radius=15) # Màu xám xanh trong suốt
        pygame.draw.rect(panel, (100, 100, 100), panel.get_rect(), 3, border_radius=15) # Viền thép
        screen.blit(panel, (offset_x - 20, offset_y - 20))

        for row in range(ROWS):
            for col in range(COLS):
                x = offset_x + col * TILE_SIZE
                y = offset_y + row * TILE_SIZE
                rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
                
                # 1. Làm mờ viền ô lưới cho ống nước nổi bật hơn
                pygame.draw.rect(screen, (50, 50, 50), rect, 1)

                # 2. Vẽ nền IN/OUT
                if row == 0 and col == 0: pygame.draw.rect(screen, (50, 60, 80), rect.inflate(-2, -2))
                elif row == ROWS - 1 and col == COLS - 1: pygame.draw.rect(screen, (40, 40, 40), rect.inflate(-2, -2))

                node = self.grid[row][col]
                
                # --- LOGIC HOẠT ẢNH XOAY ---
                if abs(node.target_angle - node.angle) > 0.1:
                    node.angle += (node.target_angle - node.angle) * 0.3
                else:
                    node.angle = node.target_angle

                pipe_surface = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
                center = TILE_SIZE // 2
                
                # =======================================================
                # BỘ THÔNG SỐ VẼ ỐNG XỊN SÒ (GIỐNG HÌNH NỀN)
                # =======================================================
                outer_w = 24  # Độ dày viền ngoài
                metal_w = 18  # Độ dày thân kim loại
                water_w = 8   # Độ dày lõi nước
                flange_w = 30 # Độ rộng khớp nối (đầu ống)
                flange_t = 5  # Độ dày khớp nối
                
                c_border = (30, 35, 40)   # Viền đen/xám đậm
                c_metal = (140, 150, 160) # Thân Kim loại xám
                c_water = (0, 230, 255) if node.is_powered else (70, 80, 90) # Nước xanh neon hoặc cạn khô
                c_brass = (210, 150, 50)  # Màu đồng thau (vàng cam) cho cụm giữa
                
                dirs = node.base_connections
                
                # LỚP 1: Vẽ Viền Đen Bao Ngoài
                pygame.draw.circle(pipe_surface, c_border, (center, center), outer_w // 2)
                for i, has_conn in enumerate(dirs):
                    if has_conn:
                        end_pos = [(center, 0), (TILE_SIZE, center), (center, TILE_SIZE), (0, center)][i]
                        pygame.draw.line(pipe_surface, c_border, (center, center), end_pos, outer_w)

                # LỚP 2: Vẽ Thân Kim Loại Xám
                pygame.draw.circle(pipe_surface, c_metal, (center, center), metal_w // 2)
                for i, has_conn in enumerate(dirs):
                    if has_conn:
                        end_pos = [(center, 0), (TILE_SIZE, center), (center, TILE_SIZE), (0, center)][i]
                        pygame.draw.line(pipe_surface, c_metal, (center, center), end_pos, metal_w)

                # LỚP 3: Vẽ Lõi Nước Ở Giữa
                pygame.draw.circle(pipe_surface, c_water, (center, center), water_w // 2)
                for i, has_conn in enumerate(dirs):
                    if has_conn:
                        end_pos = [(center, 0), (TILE_SIZE, center), (center, TILE_SIZE), (0, center)][i]
                        pygame.draw.line(pipe_surface, c_water, (center, center), end_pos, water_w)

                # LỚP 4: Vẽ Khớp Nối (Flanges) ở các đầu cắm
                for i, has_conn in enumerate(dirs):
                    if has_conn:
                        if i == 0: pygame.draw.rect(pipe_surface, c_border, (center - flange_w//2, 0, flange_w, flange_t))
                        if i == 1: pygame.draw.rect(pipe_surface, c_border, (TILE_SIZE - flange_t, center - flange_w//2, flange_t, flange_w))
                        if i == 2: pygame.draw.rect(pipe_surface, c_border, (center - flange_w//2, TILE_SIZE - flange_t, flange_w, flange_t))
                        if i == 3: pygame.draw.rect(pipe_surface, c_border, (0, center - flange_w//2, flange_t, flange_w))

                # LỚP 5: Vẽ Trục Van Đồng Thau (Chỉ dành cho ống cong L, ngã ba T, ngã tư +)
                if node.pipe_type in ['L', 'T', '+']:
                    pygame.draw.circle(pipe_surface, c_border, (center, center), metal_w // 2 + 2)
                    pygame.draw.circle(pipe_surface, c_brass, (center, center), metal_w // 2)
                    pygame.draw.circle(pipe_surface, c_water, (center, center), water_w // 2)

                # XOAY VÀ DÁN LÊN MÀN HÌNH CHÍNH
                rotated_surface = pygame.transform.rotate(pipe_surface, node.angle)
                rot_rect = rotated_surface.get_rect(center=(x + center, y + center))
                screen.blit(rotated_surface, rot_rect)

                # --- VẼ CỐ ĐỊNH VAN IN/OUT ĐÈ LÊN TRÊN CÙNG ---
                if row == 0 and col == 0:
                    cx, cy = x + TILE_SIZE // 2, y + TILE_SIZE // 2
                    pygame.draw.circle(screen, (200, 200, 255), (cx, cy), metal_w // 2 + 6, 2)
                    pygame.draw.circle(screen, (255, 100, 100), (cx, cy), metal_w // 2 + 3, 2)
                elif row == ROWS - 1 and col == COLS - 1:
                    cx, cy = x + TILE_SIZE // 2, y + TILE_SIZE // 2
                    pygame.draw.circle(screen, (80, 80, 80), (cx, cy), TILE_SIZE // 2 - 8, 2)
                    pygame.draw.line(screen, (80, 80, 80), (cx, y + 5), (cx, y + TILE_SIZE - 5), 1)
                    pygame.draw.line(screen, (80, 80, 80), (x + 5, cy), (x + TILE_SIZE - 5, cy), 1)

        

