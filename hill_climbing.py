import random

def get_out_network(board):
    ROWS, COLS = board.rows, board.cols
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

def calculate_score(board, out_network_cached):
    board.update_connectivity()
    if board.check_win(): return 99999999

    ROWS, COLS = board.rows, board.cols
    in_network = [(r, c) for r in range(ROWS) for c in range(COLS) if board.grid[r][c].is_powered]
    
    min_dist = 999
    for r1, c1 in in_network:
        for r2, c2 in out_network_cached:
            dist = abs(r1 - r2) + abs(c1 - c2)
            if dist < min_dist: min_dist = dist
                
    score = -(min_dist * 10000)   
    score += len(in_network) * 100 
    score += len(out_network_cached) * 100
    return score

def get_best_single_rotation(board):
    if board.check_win(): return None 

    ROWS, COLS = board.rows, board.cols
    # TỐI ƯU 1: CACHE ĐÍCH ĐẾN, KHÔNG TÍNH LẠI TRONG VÒNG LẶP NỮA!
    out_net_cached = get_out_network(board)
    current_score = calculate_score(board, out_net_cached)
    
    best_score = current_score
    best_move = None
    active_zones = set()
    
    for r in range(ROWS):
        for c in range(COLS):
            if board.grid[r][c].is_powered or (r, c) in out_net_cached:
                active_zones.add((r, c)) 
                for dr, dc in [(-1,0), (1,0), (0,-1), (0,1)]:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < ROWS and 0 <= nc < COLS:
                        active_zones.add((nr, nc))
                        
    # TỐI ƯU 2: Trộn ngẫu nhiên để AI không bị dính vòng lặp chết
    zones_list = list(active_zones)
    random.shuffle(zones_list)

    for r, c in zones_list:
        node = board.grid[r][c]
        if node.is_fixed or node.is_rock or node.pipe_type in ['+', 'X']: continue
        
        original = node.conns.copy() 
        for i in range(1, 4): 
            node.conns = [node.conns[-1]] + node.conns[:-1]
            test_score = calculate_score(board, out_net_cached)
            
            if test_score > best_score:
                best_score = test_score
                best_move = (r, c, i) 
                
                # TỐI ƯU 3: CHỐT ĐƠN SỚM (SHORT-CIRCUIT)
                # Nếu xoay phát mà nước chảy được thêm 1 ô (tăng > 50 điểm), lấy luôn không cần tìm nữa!
                if test_score > current_score + 50:
                    node.conns = original 
                    return best_move
                    
        node.conns = original 
            
    if best_move is None:
        blocking_rocks = [(r, c) for r, c in active_zones if board.grid[r][c].is_rock]        
        if blocking_rocks: return None 
            
        unfixed_active = [(r, c) for r, c in active_zones if not board.grid[r][c].is_fixed and not board.grid[r][c].is_rock and board.grid[r][c].pipe_type not in ['+', 'X']]
        if unfixed_active:
            rand_r, rand_c = random.choice(unfixed_active)
            return (rand_r, rand_c, random.randint(1, 3))
            
    return best_move