# main.py
import pygame
import sys
from settings import *

def draw_grid(screen):
    """Vẽ khung lưới 5x5 lên giữa màn hình"""
    # Căn giữa lưới
    offset_x = (WINDOW_WIDTH - (COLS * TILE_SIZE)) // 2
    offset_y = (WINDOW_HEIGHT - (ROWS * TILE_SIZE)) // 2

    for row in range(ROWS):
        for col in range(COLS):
            rect = pygame.Rect(offset_x + col * TILE_SIZE, offset_y + row * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(screen, GRID_COLOR, rect, 1) # Số 1 là độ dày viền

def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Pipe Puzzle AI - Hill Climbing")
    clock = pygame.time.Clock()

    running = True
    while running:
        # Xử lý sự kiện (Click chuột, tắt cửa sổ...)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Vẽ lên màn hình
        screen.fill(BG_COLOR)  # Xóa màn hình cũ bằng màu xám đen
        draw_grid(screen)      # Vẽ lại lưới 5x5

        pygame.display.flip()  # Cập nhật hiển thị
        clock.tick(FPS)        # Giới hạn tốc độ khung hình

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()