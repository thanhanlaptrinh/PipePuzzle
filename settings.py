# settings.py
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 600
FPS = 60

# Lưới đồ thị
ROWS = 10
COLS = 10
TILE_SIZE = 50

# Màu sắc
BG_COLOR = (30, 30, 30)
GRID_COLOR = (100, 100, 100)
PIPE_COLOR_OFF = (60, 60, 60)
PIPE_COLOR_ON = (0, 255, 255)
TEXT_COLOR = (255, 255, 255)
HIGHLIGHT_COLOR = (255, 255, 0)
INPUT_BOX_COLOR = (50, 50, 50)
BG_START_PATH = "assets/images/game_bg.png"
BG_GAME_PATH = "assets/images/game_bg.png"
IMG_MONEY_PATH = "assets/money_chip.png"

# Các trạng thái luồng game
STATE_MENU_NAME = 0
STATE_DASHBOARD = 1
STATE_LEVEL_SELECT = 2
STATE_GAME_PLAY = 3
STATE_SHOP = 4
STATE_QUESTS = 5
STATE_SKIN = 6

# ==========================================
# CẤU HÌNH NHIỆM VỤ (Đã Viết Có Dấu Tiếng Việt)
# ==========================================
QUEST_DEFINITIONS = [
    {
        "id": "FIRST_FLOW",
        "title": "Khai thông dòng chảy",
        "desc": "Hoàn thành 1 màn chơi",
        "metric": "levels_completed",
        "target": 1,
        "reward": 500,
    },
    {
        "id": "APPRENTICE_ENGINEER",
        "title": "Kỹ sư tập sự",
        "desc": "Hoàn thành 5 màn chơi",
        "metric": "levels_completed",
        "target": 5,
        "reward": 1800,
    },
    {
        "id": "COIN_HUNTER",
        "title": "Thợ săn Coin",
        "desc": "Kiếm được tổng cộng 10.000 xu",
        "metric": "total_coins_earned",
        "target": 10000,
        "reward": 2500,
    },
    {
        "id": "AI_ASSISTED",
        "title": "Trợ lý AI",
        "desc": "Sử dụng AI giải 3 lần",
        "metric": "ai_solves_used",
        "target": 3,
        "reward": 900,
    },
    {
        "id": "ACT_BREAKER",
        "title": "Phá đảo Act 1",
        "desc": "Mở khóa đến màn 12",
        "metric": "highest_unlocked_level",
        "target": 12,
        "reward": 2000,
    },
]

QUEST_STAT_DEFAULTS = {
    "levels_completed": 0,
    "total_coins_earned": 0,
    "ai_solves_used": 0,
    "replays_used": 0,
    "highest_unlocked_level": 1,
}