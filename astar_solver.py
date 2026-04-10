import heapq

def can_pipe_fit(pipe_type, dir_in, dir_out):
    """Kiểm tra xem loại ống này có thể xoay để nối dir_in và dir_out không"""
    if pipe_type in ['+', 'X', 'T']: return True # Các loại này nối được hầu hết hướng
    if pipe_type == 'I' or pipe_type == 'O': # Ống thẳng hoặc 1 chiều: in/out phải đối diện
        return (dir_in - dir_out) % 2 == 0
    if pipe_type == 'L': # Ống góc: in/out phải vuông góc
        return (dir_in - dir_out) % 2 != 0
    if pipe_type == 'C' or pipe_type == 'P': return True # Cổng hoặc ống cụt linh hoạt hơn
    return False

def get_best_rotation_astar(board):
    if board.check_win(): return None
    rows, cols = board.rows, board.cols
    target = (rows - 1, cols - 1)
    
    # Priority Queue: (f, g, (r, c), path, in_direction)
    pq = [(0, 0, (0, 0), [], -1)] 
    visited = {} 
    
    while pq:
        f, g, (r, c), path, last_dir = heapq.heappop(pq)
        
        if (r, c) == target:
            full_path = path + [(r, c)]
            for i in range(1, len(full_path)):
                curr_r, curr_c = full_path[i]
                prev_r, prev_c = full_path[i-1]
                node = board.grid[curr_r][curr_c]
                if node.is_powered or node.is_rock or node.is_fixed or node.pipe_type in ['+', 'X']: continue
                
                # Xác định hướng cần nối về ô trước
                needed_dir = 0 if prev_r < curr_r else 1 if prev_c > curr_c else 2 if prev_r > curr_r else 3
                if node.conns[needed_dir] == 0:
                    temp_conns = list(node.conns)
                    for rot in range(1, 4):
                        temp_conns = [temp_conns[-1]] + temp_conns[:-1]
                        if temp_conns[needed_dir] == 1: return (curr_r, curr_c, rot)
            return None

        state = (r, c, last_dir)
        if state in visited and visited[state] <= g: continue
        visited[state] = g

        for dr, dc, d_idx in [(-1, 0, 0), (0, 1, 1), (1, 0, 2), (0, -1, 3)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols:
                neighbor = board.grid[nr][nc]
                if neighbor.is_rock: continue # A* né đá tuyệt đối
                
                # KIỂM TRA TÍNH TƯƠNG THÍCH CỦA ỐNG
                if last_dir != -1: # Nếu không phải ô đầu tiên
                    if not can_pipe_fit(board.grid[r][c].pipe_type, (last_dir+2)%4, d_idx): continue
                
                weight = 1
                if neighbor.is_fixed: weight = 5
                new_g = g + weight
                h = abs(nr - target[0]) + abs(nc - target[1])
                heapq.heappush(pq, (new_g + h, new_g, (nr, nc), path + [(r, c)], d_idx))
    return None