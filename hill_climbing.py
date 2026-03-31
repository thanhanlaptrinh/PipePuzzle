import random

def get_out_network(board):
    ROWS, COLS = len(board.grid), len(board.grid[0])
    out_r, out_c = ROWS - 1, COLS - 1
    
    visited = set([(out_r, out_c)])
    queue = [(out_r, out_c)]
    
    while queue:
        r, c = queue.pop(0)
        node = board.grid[r][c]
        if r > 0 and node.connections[0] and board.grid[r-1][c].connections[2] and (r-1, c) not in visited:
            visited.add((r-1, c)); queue.append((r-1, c))
        if c < COLS - 1 and node.connections[1] and board.grid[r][c+1].connections[3] and (r, c+1) not in visited:
            visited.add((r, c+1)); queue.append((r, c+1))
        if r < ROWS - 1 and node.connections[2] and board.grid[r+1][c].connections[0] and (r+1, c) not in visited:
            visited.add((r+1, c)); queue.append((r+1, c))
        if c > 0 and node.connections[3] and board.grid[r][c-1].connections[1] and (r, c-1) not in visited:
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
                
    # --- ĐÃ XÓA ĐIỂM DỌN ĐƯỜNG RÂU RIA ---
    # Chỉ tập trung vào 2 mục tiêu tối thượng: Rút ngắn khoảng cách & Mở rộng mạng lưới
    score = - (min_dist * 10000) 
    score += len(in_network) * 100
    score += len(out_network) * 100
        
    return score

def get_best_single_rotation(board):
    if board.check_win(): return None 

    current_score = calculate_score(board)
    best_score = current_score
    best_move = None
    ROWS, COLS = len(board.grid), len(board.grid[0])
    
    # =========================================================
    # TỐI ƯU HÓA: KHOANH VÙNG CHIẾN SỰ (ACTIVE ZONES)
    # =========================================================
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
                        
    # THAY VÌ QUÉT 100 Ô, BÂY GIỜ AI CHỈ QUÉT NHỮNG Ô TRONG VÙNG CHIẾN SỰ!
    for r, c in active_zones:
        node = board.grid[r][c]
        if getattr(node, 'is_fixed', False): continue
        
        original = node.connections.copy()
        for i in range(1, 4): 
            node.connections = [node.connections[-1]] + node.connections[:-1]
            test_score = calculate_score(board)
            if test_score > best_score:
                best_score = test_score
                best_move = (r, c, i) 
        node.connections = original
            
    # NẾU KẸT: Chỉ xoay bừa (Random Kick) ở ngay tại vùng chiến sự
    if best_move is None:
        unfixed_active = [(r, c) for r, c in active_zones if not getattr(board.grid[r][c], 'is_fixed', False)]
        if unfixed_active:
            rand_r, rand_c = random.choice(unfixed_active)
            return (rand_r, rand_c, random.randint(1, 3))
            
    return best_move