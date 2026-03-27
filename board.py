# board.py
import pygame
import random
from settings import *
from node import Node

class Board:
    def __init__(self):
        self.grid = []
        self.pipe_types = ['I', 'L', 'T', '+']
        self.generate_board()
        # Chạy kiểm tra kết nối lần đầu ngay khi tạo bảng
        self.update_connectivity()

    def generate_board(self):
        self.grid = []
        for row in range(ROWS):
            grid_row = []
            for col in range(COLS):
                node = Node(row, col, random.choice(self.pipe_types))
                for _ in range(random.randint(0, 3)):
                    node.rotate()
                grid_row.append(node)
            self.grid.append(grid_row)

    def handle_click(self, mouse_x, mouse_y):
        offset_x = (WINDOW_WIDTH - (COLS * TILE_SIZE)) // 2
        offset_y = (WINDOW_HEIGHT - (ROWS * TILE_SIZE)) // 2
        col = (mouse_x - offset_x) // TILE_SIZE
        row = (mouse_y - offset_y) // TILE_SIZE
        
        if 0 <= row < ROWS and 0 <= col < COLS:
            self.grid[row][col].rotate()
            # CỰC KỲ QUAN TRỌNG: Xoay xong phải kiểm tra kết nối lại ngay
            self.update_connectivity()

    # ========================================================
    # --- THUẬT TOÁN CỐT LÕI: KIỂM TRA KẾT NỐI (BFS) ---
    # ========================================================
    def update_connectivity(self):
        """
        Dùng BFS duyệt từ ô [0,0] để đánh dấu các ô có nước chảy tới.
        """
        # 1. Reset trạng thái nước của toàn bộ bảng
        for row in range(ROWS):
            for col in range(COLS):
                self.grid[row][col].is_powered = False

        # 2. Định nghĩa Nguồn Nước (Góc trên bên trái)
        start_node = self.grid[0][0]
        
        # Tạm thời coi như nguồn [0,0] luôn có nước. 
        # (Nếu bạn muốn điểm đầu vào từ bên Trái hoặc phía Trên, 
        #  hãy thêm logic kiểm tra connections[3] hoặc connections[0] của ô [0,0] tại đây).
        start_node.is_powered = True
        
        # Hàng đợi (Queue) cho BFS
        queue = [start_node]
        visited = set([(0,0)]) # Tập hợp các ô đã duyệt qua để tránh lặp vô hạn

        # Quy ước hướng: 0=Trên, 1=Phải, 2=Dưới, 3=Trái
        # Vị trí láng giềng tương ứng: (d_row, d_col)
        neighbor_offsets = [(-1, 0), (0, 1), (1, 0), (0, -1)]
        
        # Ánh xạ cổng đối diện (Ví dụ: cổng Phải(1) đối diện với cổng Trái(3))
        opposite_direction = {0: 2, 1: 3, 2: 0, 3: 1}

        while queue:
            # Lấy ô hiện tại ra khỏi hàng đợi
            current_node = queue.pop(0)
            
            # Duyệt qua 4 láng giềng (Trên, Phải, Dưới, Trái)
            for direction in range(4):
                # 1. Kiểm tra xem ô hiện tại có đầu mở về hướng này không
                if not current_node.connections[direction]:
                    continue # Không có đường ra hướng này, bỏ qua

                # 2. Tính tọa độ ô láng giềng
                dr, dc = neighbor_offsets[direction]
                n_row, n_col = current_node.row + dr, current_node.col + dc
                
                # 3. Kiểm tra ô láng giềng có nằm trong bảng không
                if not (0 <= n_row < ROWS and 0 <= n_col < COLS):
                    continue # Nằm ngoài bảng, bỏ qua

                # 4. Kiểm tra ô láng giềng đã được duyệt chưa
                if (n_row, n_col) in visited:
                    continue # Đã duyệt rồi, bỏ qua

                # 5. Lấy đối tượng Node láng giềng
                neighbor_node = self.grid[n_row][n_col]
                
                # 6. KIỂM TRA KHỚP CỔNG: Ống láng giềng có cổng mở ngược lại không?
                opposite_dir = opposite_direction[direction]
                if neighbor_node.connections[opposite_dir]:
                    # THÀNH CÔNG: Cổng khớp nhau, nước chảy qua được
                    neighbor_node.is_powered = True
                    visited.add((n_row, n_col))
                    queue.append(neighbor_node) # Đưa ô này vào queue để chảy tiếp

    # ========================================================
    # --- CẬP NHẬT HÀM VẼ ĐỂ CÓ HIỆU ỨNG SÁNG LÊN ---
    # ========================================================
    def draw(self, screen):
        offset_x = (WINDOW_WIDTH - (COLS * TILE_SIZE)) // 2
        offset_y = (WINDOW_HEIGHT - (ROWS * TILE_SIZE)) // 2

        for row in range(ROWS):
            for col in range(COLS):
                x = offset_x + col * TILE_SIZE
                y = offset_y + row * TILE_SIZE
                
                pygame.draw.rect(screen, GRID_COLOR, pygame.Rect(x, y, TILE_SIZE, TILE_SIZE), 1)
                
                node = self.grid[row][col]
                center_x = x + TILE_SIZE // 2
                center_y = y + TILE_SIZE // 2
                thickness = 20
                
                # --- CHỌN MÀU DỰA TRÊN TRẠNG THÁI CẤP NƯỚC ---
                # Nếu ô này có nước (is_powered=True) thì dùng màu sáng rực PIPE_COLOR_ON
                draw_color = PIPE_COLOR_ON if node.is_powered else PIPE_COLOR_OFF
                
                # Cục nối giữa (Hơi to hơn một chút khi sáng để tạo cảm giác "glow")
                circle_radius = thickness // 2 + 2 if node.is_powered else thickness // 2
                pygame.draw.circle(screen, draw_color, (center_x, center_y), circle_radius)
                
                # Nhánh
                if node.connections[0]: # Trên
                    pygame.draw.line(screen, draw_color, (center_x, center_y), (center_x, y), thickness)
                if node.connections[1]: # Phải
                    pygame.draw.line(screen, draw_color, (center_x, center_y), (x + TILE_SIZE, center_y), thickness)
                if node.connections[2]: # Dưới
                    pygame.draw.line(screen, draw_color, (center_x, center_y), (center_x, y + TILE_SIZE), thickness)
                if node.connections[3]: # Trái
                    pygame.draw.line(screen, draw_color, (center_x, center_y), (x, center_y), thickness)