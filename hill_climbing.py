# hill_climbing.py
"""
File này sẽ chứa bộ não AI.
Nhiệm vụ: Nhận vào một đối tượng Board, dùng thuật toán Leo Đồi để tính toán
hướng xoay ống sao cho nước kết nối được từ [0,0] đến [ROWS-1, COLS-1].
"""

class AI_Solver:
    def __init__(self, board):
        self.board = board
    
    # Sẽ code hàm Heuristic và hàm tìm kiếm tại đây sau.