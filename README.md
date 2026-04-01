🧩 PIPE PUZZLE 

 Bậc Thầy Đường Ống Là một tựa game giải đố trí tuệ (Puzzle Game) được xây dựng hoàn toàn bằng ngôn ngữ Python (thư viện Pygame). Nhiệm vụ của bạn là xoay các đoạn ống để dẫn nước từ điểm xuất phát đến đích đến một cách thông minh nhất


🎓 Mục tiêu học thuật

Dự án này minh họa các khái niệm cốt lõi trong AI và Khoa học máy tính:
* Biểu diễn đồ thị: Sử dụng lưới 2D (Grid) và cấu trúc đối tượng (Node) làm dữ liệu chính.
* Trí tuệ nhân tạo (AI): Ứng dụng thuật toán leo đồi (Hill Climbing) và hàm Heuristic để tự động    giải quyết bài toán tìm đường.
* Thuật toán tìm kiếm: Kiểm tra tính kết nối và tìm đường đi ngắn nhất bằng logic duyệt đồ thị (BFS / Priority Queue).
* Quản lý trạng thái: Theo dõi luồng màn hình (State Machine), quản lý góc xoay và loại ống của từng ô lưới.
* Hệ thống luật:Xác định tính hợp lệ của dòng chảy dựa trên các quy tắc khớp nối đường ống.


✨ Tính Năng Nổi Bật

Trò chơi không chỉ dừng lại ở việc xoay ống nước, còn được tích hợp thuật toán nâng cao:
* 🌌 60 Màn Chơi Thử Thách (5 Chapter): Bản đồ được mở rộng độ khó liên tục từ lưới 3x3 lên đến 10x10.
* ⛏️ Hệ thống Vật cản & Phá Đá: Game tự động sinh ra các viên đá ngẫu nhiên cản đường nước. Bạn có thể tích trữ tối đa 9 cây cuốc trong túi đồ để đập vỡ chúng.
* 🤖 Trợ Lý AI (Auto-Solve): Tích hợp thuật toán Hill Climbing kết hợp tìm kiếm đường đi ngắn nhất. AI có thể tự động quét bản đồ, tìm góc xoay tối ưu, và tự động tính toán đập viên đá nào cản đường gần nhất.
* 🛒 Cửa Hàng & Nhiệm Vụ: Hoàn thành các nhiệm vụ như "Thợ săn Coin", "Trợ lý AI" để nhận thưởng Xu.
* Dùng Xu để mua thêm Cuốc hoặc Mở khóa các Chapter cấp cao và có thể dùng để mua skin.
* 🎨 Giao Diện: UI/UX được thiết kế với hiệu ứng Glow, âm thanh sống động.


📁 Cấu Trúc Dự Án

Dự án được phân chia module rõ ràng theo tư duy lập trình hướng đối tượng (OOP):
PipePuzzle/
├── assets/                 # Chứa toàn bộ hình ảnh, âm thanh
├── board.py                # Xử lý logic lưới đồ thị (Node), thuật toán nối ống và sinh đá
├── hill_climbing.py        # Não bộ AI: Heuristic, tính điểm, dự đoán góc xoay
├── main.py                 # Game Loop chính, quản lý vòng đời và sự kiện
├── screens.py              # Xử lý toàn bộ giao diện UI (Menu, Shop, Quests, Popups)
├── settings.py             # Khai báo các hằng số cấu hình, màu sắc và dữ liệu Quest
└── save_data.json          # File database cục bộ lưu tiến trình người chơi


🎁 Giftcode Bí Mật

Bật mí một chút, ở màn hình Dashboard -> Options -> Giftcode, bạn có thể nhập các mã sau để test game nhanh hơn:
Nhập UNPIPE: Mở khóa toàn bộ 60 màn chơi.
Nhập PIPEGOLD: Nhận ngay 10.000 Xu để thỏa sức mua sắm.
