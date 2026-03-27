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
        font_io = pygame.font.SysFont('tahoma', 16, bold=True)

        for row in range(ROWS):
            for col in range(COLS):
                x = offset_x + col * TILE_SIZE
                y = offset_y + row * TILE_SIZE
                rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
                pygame.draw.rect(screen, GRID_COLOR, rect, 1) # Vẽ viền

                # Vẽ nền IN/OUT
                if row == 0 and col == 0: pygame.draw.rect(screen, (50, 60, 80), rect.inflate(-2, -2))
                elif row == ROWS - 1 and col == COLS - 1: pygame.draw.rect(screen, (40, 40, 40), rect.inflate(-2, -2))

                node = self.grid[row][col]
                
                # --- LOGIC HOẠT ẢNH MƯỢT MÀ ---
                # Trượt từ từ góc hiện tại về góc mục tiêu (Tốc độ xoay 0.3)
                if abs(node.target_angle - node.angle) > 0.1:
                    node.angle += (node.target_angle - node.angle) * 0.3
                else:
                    node.angle = node.target_angle

                # Vẽ ống nước lên một TẤM KÍNH trong suốt (Surface) thay vì vẽ thẳng lên screen
                pipe_surface = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
                center = TILE_SIZE // 2
                thickness = 12
                
                draw_color = PIPE_COLOR_ON if node.is_powered else PIPE_COLOR_OFF
                circle_radius = thickness // 2 + 2 if node.is_powered else thickness // 2
                
                # VẼ HÌNH DÁNG GỐC LÊN TẤM KÍNH
                pygame.draw.circle(pipe_surface, draw_color, (center, center), circle_radius)
                if node.base_connections[0]: pygame.draw.line(pipe_surface, draw_color, (center, center), (center, 0), thickness)
                if node.base_connections[1]: pygame.draw.line(pipe_surface, draw_color, (center, center), (TILE_SIZE, center), thickness)
                if node.base_connections[2]: pygame.draw.line(pipe_surface, draw_color, (center, center), (center, TILE_SIZE), thickness)
                if node.base_connections[3]: pygame.draw.line(pipe_surface, draw_color, (center, center), (0, center), thickness)

                # XOAY TẤM KÍNH THEO GÓC VÀ DÁN VÀO MÀN HÌNH
                rotated_surface = pygame.transform.rotate(pipe_surface, node.angle)
                rot_rect = rotated_surface.get_rect(center=(x + center, y + center))
                screen.blit(rotated_surface, rot_rect)

                # --- VẼ VAN IN/OUT ĐÈ LÊN TRÊN CÙNG (Không bị xoay theo) ---
                if row == 0 and col == 0:
                    cx, cy = x + TILE_SIZE // 2, y + TILE_SIZE // 2
                    pygame.draw.circle(screen, (200, 200, 255), (cx, cy), circle_radius + 6, 2)
                    pygame.draw.circle(screen, (255, 100, 100), (cx, cy), circle_radius + 3, 2)
                elif row == ROWS - 1 and col == COLS - 1:
                    cx, cy = x + TILE_SIZE // 2, y + TILE_SIZE // 2
                    pygame.draw.circle(screen, (80, 80, 80), (cx, cy), TILE_SIZE // 2 - 8, 2)
                    pygame.draw.line(screen, (80, 80, 80), (cx, y + 5), (cx, y + TILE_SIZE - 5), 1)
                    pygame.draw.line(screen, (80, 80, 80), (x + 5, cy), (x + TILE_SIZE - 5, cy), 1)

        

