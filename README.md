# Đồ án: Game Pipe Puzzle - AI Hill Climbing

Đây là dự án game nối đường ống nước, sử dụng Pygame để tạo giao diện và áp dụng thuật toán trí tuệ nhân tạo Leo Đồi (Hill Climbing) để tự động tìm đường đi từ điểm A đến điểm B trên đồ thị.

## Trạng thái hiện tại
- Đã thiết lập xong môi trường ảo và thư viện (`pygame-ce`).
- Đã tạo khung lưới hiển thị 5x5 (25 nodes) trên Pygame.
- Đang chuẩn bị viết logic tạo bảng (`board.py`) và thuật toán (`hill_climbing.py`).

## Cấu trúc file Logic
- `settings.py`: Chứa các hằng số cài đặt (kích thước màn hình, FPS, màu sắc, số dòng/cột).
- `node.py`: Class định nghĩa cấu trúc dữ liệu của một đỉnh trong đồ thị (loại ống, góc xoay).
- `main.py`: File khởi chạy chính, chứa vòng lặp game và vẽ giao diện.

## Hướng dẫn cài đặt cho thành viên nhóm
Sau khi clone code về máy, các bạn làm theo các bước sau để chạy game:

1. Mở terminal tại thư mục dự án và tạo môi trường ảo:
   python -m venv venv

2. Kích hoạt môi trường ảo:
   - Trên Windows: `venv\Scripts\activate`
   - Trên Mac/Linux: `source venv/bin/activate`

3. Cài đặt các thư viện cần thiết:
   pip install -r requirements.txt

4. Chạy game:
   python main.py