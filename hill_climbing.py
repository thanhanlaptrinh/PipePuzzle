import random

def get_out_network(board):
    ROWS, COLS = len(board.grid), len(board.grid[0])
    out_r, out_c = ROWS - 1, COLS - 1
    
    visited = set([(out_r, out_c)])
    queue = [(out_r, out_c)]
    
    while queue:
        r, c = queue.pop(0)
        node = board.grid[r][c]
        if r > 0 and node.conns[0] == 1 and board.grid[r-1][c].conns[2] == 1 and (r-1, c) not in visited:
            visited.add((r-1, c)); queue.append((r-1, c))
        if c < COLS - 1 and node.conns[1] == 1 and board.grid[r][c+1].conns[3] == 1 and (r, c+1) not in visited:
            visited.add((r, c+1)); queue.append((r, c+1))
        if r < ROWS - 1 and node.conns[2] == 1 and board.grid[r+1][c].conns[0] == 1 and (r+1, c) not in visited:
            visited.add((r+1, c)); queue.append((r+1, c))
        if c > 0 and node.conns[3] == 1 and board.grid[r][c-1].conns[1] == 1 and (r, c-1) not in visited:
            visited.add((r, c-1)); queue.append((r, c-1))
            
    return visited

def calculate_score(board):
    board.update_connectivity()
    if board.check_win():
        return 99999999

    ROWS, COLS = len(board.grid), len(board.grid[0])
    in_network = [(r, c) for r in range(ROWS) for c in range(COLS) if board.grid[r][c].is_powered]
    out_network = get_out_network(board)
    
    min_dist = 999
    for r1, c1 in in_network:
        for r2, c2 in out_network:
            dist = abs(r1 - r2) + abs(c1 - c2)
            if dist < min_dist: 
                min_dist = dist
                
    # =========================================================
    # CÔNG THỨC ĐIỂM CHUẨN: Khuyến khích AI mạnh dạn bung lụa
    # =========================================================
    score = - (min_dist * 10000)   # Rút ngắn khoảng cách đến đích là ưu tiên số 1
    score += len(in_network) * 100 # Phải để +100 để AI dám đi đường vòng/đi ngang
    score += len(out_network) * 100
        
    return score

def get_best_single_rotation(board):
    if board.check_win(): return None 

    current_score = calculate_score(board)
    best_score = current_score
    best_move = None
    ROWS, COLS = len(board.grid), len(board.grid[0])
    active_zones = set()
    out_net = get_out_network(board)
    
    for r in range(ROWS):
        for c in range(COLS):
            # Nếu ống đang có nước HOẶC đang nối với đích
            if board.grid[r][c].is_powered or (r, c) in out_net:
                active_zones.add((r, c)) # Thêm chính nó
                # Thêm cả 4 ô hàng xóm xung quanh nó vào vùng chiến sự
                for dr, dc in [(-1,0), (1,0), (0,-1), (0,1)]:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < ROWS and 0 <= nc < COLS:
                        active_zones.add((nr, nc))
                        
    for r, c in active_zones:
        node = board.grid[r][c]
        if node.is_fixed or node.is_rock: continue
        
        original = node.conns.copy() # Đổi tên
        for i in range(1, 4): 
            node.conns = [node.conns[-1]] + node.conns[:-1]
            test_score = calculate_score(board)
            if test_score > best_score:
                best_score = test_score
                best_move = (r, c, i) 
        node.conns = original # Phục hồi
            
    if best_move is None:
        blocking_rocks = [(r, c) for r, c in active_zones if board.grid[r][c].is_rock]        
        if blocking_rocks:
            return None 
            
        unfixed_active = [(r, c) for r, c in active_zones if not board.grid[r][c].is_fixed and not board.grid[r][c].is_rock]
        if unfixed_active:
            rand_r, rand_c = random.choice(unfixed_active)
            return (rand_r, rand_c, random.randint(1, 3))
            
    return best_move