# node.py
class Node:
    BASE_PIPES = {
        'I': [True, False, True, False],  # [Trên, Phải, Dưới, Trái]
        'L': [True, True, False, False],  
        'T': [True, True, True, False],   
        '+': [True, True, True, True]     
    }

    def __init__(self, row, col, pipe_type):
        self.row = row
        self.col = col
        self.pipe_type = pipe_type
        self.connections = self.BASE_PIPES[pipe_type].copy()
        
        # --- THÊM TRẠNG THÁI MỚI Ở ĐÂY ---
        self.is_powered = False # Mặc định ban đầu là không có nước

    def rotate(self):
        self.connections = [self.connections[-1]] + self.connections[:-1]