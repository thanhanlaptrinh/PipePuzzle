# board.py
import pygame
import pygame.gfxdraw
import random
from settings import *

class Node:
    BASE_PIPES = {
        'I': [True, False, True, False],
        'L': [True, True, False, False],
        'T': [True, True, True, False],
        '+': [True, True, True, True],
        'E': [True, False, False, False]
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
        self.is_fixed = False 
        self.is_rock = False # Mặc định không có đá

    def rotate(self):
        # ---> KHÓA CHẾT: Có đá đè lên hoặc là điểm Đầu/Cuối thì CẤM XOAY <---
        if self.is_fixed or getattr(self, 'is_rock', False): 
            return 
            
        self.connections = [self.connections[-1]] + self.connections[:-1]
        self.target_angle -= 90 

class Board:
    def __init__(self, level_id=1):
        self.level_id = level_id
        act = (self.level_id - 1) // 12 + 1
        
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
        col = (mouse_x - offset_x) // TILE_SIZE
        row = (mouse_y - offset_y) // TILE_SIZE
        
        if 0 <= row < self.rows and 0 <= col < self.cols:
            node = self.grid[row][col]
            if getattr(node, 'is_rock', False):
                node.is_rock = False # Vỡ đá!
                self.update_connectivity()
                return True
        return False 
    
    def check_win(self):        
        return self.grid[self.rows-1][self.cols-1].is_powered
    
    def generate_board(self):
        self.grid = []
        random.seed(self.level_id)
        
        for r in range(self.rows):
            self.grid.append([None for _ in range(self.cols)])
            
        req_conns = [[[False]*4 for _ in range(self.cols)] for _ in range(self.rows)]
        
        req_conns[0][0][1] = True; req_conns[0][1][3] = True
        req_conns[self.rows-1][self.cols-1][3] = True; req_conns[self.rows-1][self.cols-2][1] = True
        
        visited = set([(0, 0), (self.rows-1, self.cols-1)])
        stack = [(0, 1)]; visited.add((0, 1))
        
        while stack:
            r, c = stack[-1]
            neighbors = []
            if r > 0 and (r-1, c) not in visited: neighbors.append((r-1, c, 0, 2))
            if c < self.cols-1 and (r, c+1) not in visited: neighbors.append((r, c+1, 1, 3))
            if r < self.rows-1 and (r+1, c) not in visited: neighbors.append((r+1, c, 2, 0))
            if c > 0 and (r, c-1) not in visited: neighbors.append((r, c-1, 3, 1))
            
            if neighbors:
                nr, nc, dir_out, dir_in = random.choice(neighbors)
                req_conns[r][c][dir_out] = True
                req_conns[nr][nc][dir_in] = True
                visited.add((nr, nc))
                stack.append((nr, nc))
            else:
                stack.pop()
                
        extra_paths = (self.rows * self.cols) // 3
        for _ in range(extra_paths):
            r = random.randint(0, self.rows-1); c = random.randint(0, self.cols-1)
            if (r, c) == (0, 0) or (r, c) == (self.rows-1, self.cols-1): continue
            direction = random.randint(0, 3)
            nr, nc = r + [-1, 0, 1, 0][direction], c + [0, 1, 0, -1][direction]
            
            if 0 <= nr < self.rows and 0 <= nc < self.cols:
                if (nr, nc) == (0, 0) or (nr, nc) == (self.rows-1, self.cols-1): continue
                opp_dir = [2, 3, 0, 1][direction]
                req_conns[r][c][direction] = True
                req_conns[nr][nc][opp_dir] = True

        def get_pipe_type(conn):
            count = sum(conn)
            if count == 4: return '+'
            if count == 3: return 'T'
            if count == 2:
                if conn[0] and conn[2]: return 'I'
                if conn[1] and conn[3]: return 'I'
                return 'L'
            return 'E' 

        for r in range(self.rows):
            for c in range(self.cols):
                p_type = get_pipe_type(req_conns[r][c])
                node = Node(r, c, p_type)
                
                if (r, c) == (0, 0) or (r, c) == (self.rows-1, self.cols-1):
                    self.grid[r][c] = node
                    continue
                    
                for _ in range(4):
                    covers_all = True
                    for i in range(4):
                        if req_conns[r][c][i] and not node.connections[i]: covers_all = False
                    if covers_all: break
                    node.rotate()
                self.grid[r][c] = node

        in_node = self.grid[0][0]
        while not in_node.connections[1]: in_node.rotate() 
        in_node.angle = in_node.target_angle
        in_node.is_fixed = True
        
        out_node = self.grid[self.rows-1][self.cols-1]
        while not out_node.connections[3]: out_node.rotate() 
        out_node.angle = out_node.target_angle
        out_node.is_fixed = True
        
        for r in range(self.rows):
            for c in range(self.cols):
                if not getattr(self.grid[r][c], 'is_fixed', False):
                    for _ in range(random.randint(1, 3)): self.grid[r][c].rotate()
                    self.grid[r][c].angle = self.grid[r][c].target_angle

        # ========================================================
        # SINH ĐÁ TỰ ĐỘNG (CHỈ TỪ MÀN 2 TRỞ ĐI ĐỂ MÀN 1 CÀY TIỀN)
        # ========================================================
        if self.level_id > 1:
            if self.rows <= 5: num_rocks = random.randint(3, 5) 
            elif self.rows == 7: num_rocks = random.randint(10, 13) 
            elif self.rows >= 10: num_rocks = random.randint(15, 20) 
            else: num_rocks = 0

            placed = 0; attempts = 0
            while placed < num_rocks and attempts < 500:
                rr = random.randint(0, self.rows - 1); cc = random.randint(0, self.cols - 1)
                node = self.grid[rr][cc]
                if not getattr(node, 'is_fixed', False) and not getattr(node, 'is_rock', False):
                    node.is_rock = True
                    placed += 1
                attempts += 1
        random.seed() 

    def handle_click(self, mouse_x, mouse_y):
        offset_x = (WINDOW_WIDTH - (self.cols * TILE_SIZE)) // 2
        offset_y = (WINDOW_HEIGHT - (self.rows * TILE_SIZE)) // 2
        col = (mouse_x - offset_x) // TILE_SIZE
        row = (mouse_y - offset_y) // TILE_SIZE
        if 0 <= row < self.rows and 0 <= col < self.cols:
            self.grid[row][col].rotate()
            self.update_connectivity()

    def update_connectivity(self):
        for row in range(self.rows):
            for col in range(self.cols):
                self.grid[row][col].is_powered = False

        start_node = self.grid[0][0]
        # ---> CHẶN NƯỚC: Nếu ô nguồn bị đá đè thì tịt luôn <---
        if getattr(start_node, 'is_rock', False): return

        start_node.is_powered = True
        queue = [start_node]; visited = set([(0,0)])
        neighbor_offsets = [(-1, 0), (0, 1), (1, 0), (0, -1)]
        opposite_direction = {0: 2, 1: 3, 2: 0, 3: 1}

        while queue:
            current = queue.pop(0)
            if getattr(current, 'is_rock', False): continue # Safety check
            
            for direction in range(4):
                if not current.connections[direction]: continue
                dr, dc = neighbor_offsets[direction]
                n_row, n_col = current.row + dr, current.col + dc
                
                if not (0 <= n_row < self.rows and 0 <= n_col < self.cols): continue
                if (n_row, n_col) in visited: continue

                neighbor = self.grid[n_row][n_col]
                
                # ---> CHẶN NƯỚC: Không cho nước chảy vào ô có đá <---
                if getattr(neighbor, 'is_rock', False): continue
                
                opposite_dir = opposite_direction[direction]
                if neighbor.connections[opposite_dir]:
                    neighbor.is_powered = True
                    visited.add((n_row, n_col))
                    queue.append(neighbor)

    def draw(self, screen):
        offset_x = (WINDOW_WIDTH - (self.cols * TILE_SIZE)) // 2
        offset_y = (WINDOW_HEIGHT - (self.rows * TILE_SIZE)) // 2

        panel = pygame.Surface((self.cols * TILE_SIZE + 40, self.rows * TILE_SIZE + 40), pygame.SRCALPHA)
        pygame.draw.rect(panel, (30, 35, 45, 210), panel.get_rect(), border_radius=15) 
        pygame.draw.rect(panel, (100, 100, 100), panel.get_rect(), 3, border_radius=15) 
        screen.blit(panel, (offset_x - 20, offset_y - 20))

        for row in range(self.rows):
            for col in range(self.cols):
                x = offset_x + col * TILE_SIZE; y = offset_y + row * TILE_SIZE
                rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
                pygame.draw.rect(screen, (50, 50, 50), rect, 1)

                if row == 0 and col == 0: pygame.draw.rect(screen, (50, 60, 80), rect.inflate(-2, -2))
                elif row == self.rows - 1 and col == self.cols - 1: pygame.draw.rect(screen, (40, 40, 40), rect.inflate(-2, -2))

                node = self.grid[row][col]
                if abs(node.target_angle - node.angle) > 0.1: node.angle += (node.target_angle - node.angle) * 0.3
                else: node.angle = node.target_angle

                pipe_surface = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
                center = TILE_SIZE // 2
                outer_w = 24; metal_w = 18; water_w = 8; flange_w = 30; flange_t = 5  
                c_border = (30, 35, 40); c_metal = (140, 150, 160) 
                c_water = (0, 230, 255) if node.is_powered else (70, 80, 90) 
                c_brass = (210, 150, 50)  
                
                dirs = node.base_connections
                pygame.gfxdraw.aacircle(pipe_surface, center, center, outer_w // 2, c_border)
                pygame.gfxdraw.filled_circle(pipe_surface, center, center, outer_w // 2, c_border)
                for i, has_conn in enumerate(dirs):
                    if has_conn:
                        end_pos = [(center, 0), (TILE_SIZE, center), (center, TILE_SIZE), (0, center)][i]
                        pygame.draw.line(pipe_surface, c_border, (center, center), end_pos, outer_w)

                pygame.gfxdraw.aacircle(pipe_surface, center, center, metal_w // 2, c_metal)
                pygame.gfxdraw.filled_circle(pipe_surface, center, center, metal_w // 2, c_metal)
                for i, has_conn in enumerate(dirs):
                    if has_conn:
                        end_pos = [(center, 0), (TILE_SIZE, center), (center, TILE_SIZE), (0, center)][i]
                        pygame.draw.line(pipe_surface, c_metal, (center, center), end_pos, metal_w)

                pygame.gfxdraw.aacircle(pipe_surface, center, center, water_w // 2, c_water)
                pygame.gfxdraw.filled_circle(pipe_surface, center, center, water_w // 2, c_water)
                for i, has_conn in enumerate(dirs):
                    if has_conn:
                        end_pos = [(center, 0), (TILE_SIZE, center), (center, TILE_SIZE), (0, center)][i]
                        pygame.draw.line(pipe_surface, c_water, (center, center), end_pos, water_w)

                for i, has_conn in enumerate(dirs):
                    if has_conn:
                        if i == 0: pygame.draw.rect(pipe_surface, c_border, (center - flange_w//2, 0, flange_w, flange_t))
                        if i == 1: pygame.draw.rect(pipe_surface, c_border, (TILE_SIZE - flange_t, center - flange_w//2, flange_t, flange_w))
                        if i == 2: pygame.draw.rect(pipe_surface, c_border, (center - flange_w//2, TILE_SIZE - flange_t, flange_w, flange_t))
                        if i == 3: pygame.draw.rect(pipe_surface, c_border, (0, center - flange_w//2, flange_t, flange_w))

                if node.pipe_type in ['L', 'T', '+']:
                    pygame.gfxdraw.aacircle(pipe_surface, center, center, metal_w // 2 + 2, c_border)
                    pygame.gfxdraw.filled_circle(pipe_surface, center, center, metal_w // 2 + 2, c_border)
                    pygame.gfxdraw.aacircle(pipe_surface, center, center, metal_w // 2, c_brass)
                    pygame.gfxdraw.filled_circle(pipe_surface, center, center, metal_w // 2, c_brass)
                    pygame.gfxdraw.aacircle(pipe_surface, center, center, water_w // 2, c_water)
                    pygame.gfxdraw.filled_circle(pipe_surface, center, center, water_w // 2, c_water)

                rotated_surface = pygame.transform.rotozoom(pipe_surface, node.angle, 1.0)
                rot_rect = rotated_surface.get_rect(center=(x + center, y + center))
                screen.blit(rotated_surface, rot_rect)

                if row == 0 and col == 0:
                    cx, cy = x + TILE_SIZE // 2, y + TILE_SIZE // 2
                    pygame.draw.circle(screen, (200, 200, 255), (cx, cy), metal_w // 2 + 6, 2)
                    pygame.draw.circle(screen, (255, 100, 100), (cx, cy), metal_w // 2 + 3, 2)
                elif row == self.rows - 1 and col == self.cols - 1:
                    cx, cy = x + TILE_SIZE // 2, y + TILE_SIZE // 2
                    pygame.draw.circle(screen, (80, 80, 80), (cx, cy), TILE_SIZE // 2 - 8, 2)
                    pygame.draw.line(screen, (80, 80, 80), (cx, y + 5), (cx, y + TILE_SIZE - 5), 1)
                    pygame.draw.line(screen, (80, 80, 80), (x + 5, cy), (x + TILE_SIZE - 5, cy), 1)
                    
                # VẼ ĐÁ
                if getattr(node, 'is_rock', False):
                    cx, cy = x + TILE_SIZE // 2, y + TILE_SIZE // 2
                    pygame.draw.circle(screen, (100, 100, 100), (cx, cy), TILE_SIZE // 3)
                    pygame.draw.circle(screen, (60, 60, 60), (cx, cy), TILE_SIZE // 3, 3)