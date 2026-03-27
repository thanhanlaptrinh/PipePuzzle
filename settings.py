# settings.py
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 60
ROWS = 5
COLS = 5
TILE_SIZE = 100

BG_COLOR = (30, 30, 30)
GRID_COLOR = (100, 100, 100)
PIPE_COLOR_OFF = (60, 60, 60)
PIPE_COLOR_ON = (0, 255, 255)
TEXT_COLOR = (255, 255, 255)
HIGHLIGHT_COLOR = (255, 255, 0)
INPUT_BOX_COLOR = (50, 50, 50)

# ========================================================
# --- ĐỊNH NGHĨA LẠI CÁC TRẠNG THÁI GAME MỚI CỰC CHUẨN ---
# ========================================================
STATE_MENU_NAME = 0     # Nhập tên
STATE_DASHBOARD = 1     # Menu chính (PIPEMASTER PRO)
STATE_LEVEL_SELECT = 2  # Chọn 10 màn
STATE_GAME_PLAY = 3     # Đang chơi game
STATE_SHOP = 4          # Cửa hàng
STATE_QUESTS = 5        # Nhiệm vụ