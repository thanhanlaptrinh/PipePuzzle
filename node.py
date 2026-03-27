# node.py

class Node:
    def __init__(self, row, col, pipe_type=None):
        self.row = row
        self.col = col
        self.pipe_type = pipe_type  # 'I' (thẳng), 'L' (góc), 'T' (ngã 3), '+' (ngã 4)
        self.rotation = 0           # Góc xoay: 0, 90, 180, 270 độ
        
        # Mảng logic: [Trên, Phải, Dưới, Trái]
        # True = đầu ống mở để nước chảy qua
        self.connections = [False, False, False, False] 

    def rotate(self):
        """Xoay ống 90 độ theo chiều kim đồng hồ"""
        self.rotation = (self.rotation + 90) % 360
        # Xoay mảng logic sang phải 1 bậc để cập nhật hướng nước chảy
        self.connections = [self.connections[-1]] + self.connections[:-1]