import pygame
import datetime
import os
import threading
import ollama

# --- KHỞI TẠO HỆ THỐNG ĐỒ HỌA ---
pygame.init()
WIDTH, HEIGHT = 1366, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Gemini AI - Chat với Hashimoto Momoko 🌸")
clock = pygame.time.Clock()

# --- ĐƯỜNG DẪN TÀI NGUYÊN THỰC TẾ TRÊN MÁY KHÁNH ---
# Tự động chọn ổ đĩa F:\ hoặc G:\ tùy thuộc vào sự tồn tại của thư mục
if os.path.exists(r"F:\ĐAMH tro chuyen voi than tuong"):
    BASE_PATH = r"F:\ĐAMH tro chuyen voi than tuong"
else:
    BASE_PATH = r"G:\ĐAMH tro chuyen voi than tuong"

CARD_INFO_PATH = os.path.join(BASE_PATH, "Takaneko_member")

# --- HỆ THỐNG MÀU SẮC MODERN (GEMINI SOFT THEME) ---
COLOR_BG_MAIN = (255, 255, 255)  # Nền trắng tinh khôi của Gemini
COLOR_TEXT_MAIN = (31, 31, 31)  # Chữ đen xám cao cấp, dịu mắt
COLOR_TEXT_MUTED = (117, 117, 117)  # Chữ xám ghi phụ cho thời gian, gợi ý
COLOR_PRIMARY_PINK = (255, 90, 150)  # Hồng đậm Pastel (Màu chủ đạo của Momoko)
COLOR_BORDER_GEMINI = (218, 220, 224)  # Đường viền xám mỏng chuẩn Google
COLOR_BUBBLE_USER = (240, 244, 252)  # Bong bóng chat của Khánh (Xanh nhạt phong cách Google)
COLOR_BUBBLE_MOMOKO = (255, 240, 245)  # Bong bóng chat của Momoko (Hồng phấn dịu dàng)


# --- NẠP FONT CHỮ CHỐNG LỖI UNICODE TIẾNG VIỆT ---
def get_safe_font(size, bold=False):
    font_paths = [
        r"C:\Windows\Fonts\SegoeUI.ttf" if not bold else r"C:\Windows\Fonts\SegoeUIb.ttf",
        r"C:\Windows\Fonts\calibri.ttf" if not bold else r"C:\Windows\Fonts\calibrib.ttf",
        r"C:\Windows\Fonts\Arial.ttf" if not bold else r"C:\Windows\Fonts\Arialbd.ttf"
    ]
    for path in font_paths:
        if os.path.exists(path):
            try:
                return pygame.font.Font(path, size)
            except:
                continue
    return pygame.font.SysFont("Segoe UI", size, bold)


font_title = get_safe_font(20, bold=True)
font_chat = get_safe_font(16, bold=False)
font_hint = get_safe_font(14, bold=False)

# --- BIẾN TOÀN CỤC QUẢN LÝ DỮ LIỆU CHAT ---
user_input_text = ""
chat_history = [
    {
        "sender": "Momoko",
        "text": "Chào Khánh yêu quý! Mình là Hashimoto Momoko đây~ ♥ Thật vui vì hôm nay được trò chuyện riêng với bạn trong không gian Gemini mượt mà này đó nha! ✨",
        "time": datetime.datetime.now().strftime("%H:%M")
    }
]
chat_scroll_y = 0
max_chat_scroll = 0
momoko_avatar = None


# --- NẠP ĐỒ HỌA AVATAR CHỊ MOMOKO ---
def load_momoko_graphics():
    global momoko_avatar
    # Nạp tệp ảnh thẻ từ thư mục Takaneko_member của em
    momoko_img_path = os.path.join(CARD_INFO_PATH, "F:\ĐAMH tro chuyen voi than tuong\Member\TAKANE NO NADESHIKO\Hashimoto Momoko.jpg")
    if os.path.exists(momoko_img_path):
        try:
            raw_img = pygame.image.load(momoko_img_path).convert_alpha()
            # Cắt và bo tỉ lệ avatar nhỏ xinh xắn 45x45 cho top-bar chat
            momoko_avatar = pygame.transform.smoothscale(raw_img, (45, 45))
        except:
            momoko_avatar = None


# --- THUẬT TOÁN TỰ ĐỘNG XUỐNG DÒNG CHỮ CHAT MƯỢT MÀ ---
def wrap_text(text, font, max_width):
    words = text.split(' ')
    lines = []
    current_line = ""
    for word in words:
        test_line = current_line + " " + word if current_line else word
        if font.size(test_line)[0] <= max_width:
            current_line = test_line
        else:
            if current_line: lines.append(current_line)
            current_line = word
    if current_line: lines.append(current_line)
    return lines


# --- PROMPT AI ĐẶC THỦ CHO CHỊ MOMOKO (DỰA TRÊN AI_ENGINE CỦA EM) ---
def get_momoko_system_prompt():
    return (
        "You are roleplaying as Hashimoto Momoko from the J-Pop group 'Takane no Nadeshiko'.\n"
        "Your chatter is Khánh, a 19-year-old IT student in Hanoi.\n"
        "Your Profile: Color Pink, Birthday 28/06/2003, Hometown Yamaguchi.\n"
        "Your Personality: Lively, energetic, honest, cute, making people happy.\n"
        "Instructions: Speak 100% in Vietnamese. Be extremely affectionate, cute, use 'mình'/'tớ' and call him 'Khánh'. "
        "Incorporate pink hearts (♥, ♡) naturally. Keep answers relatively brief like a real chat app message."
    )


# --- THREAD XỬ LÝ OLLAMA CHỐNG ĐƠ GIAO DIỆN ---
def ask_momoko_ai_async(message):
    def task():
        sys_prompt = get_momoko_system_prompt()
        try:
            response = ollama.chat(
                model='llama3.2',
                messages=[
                    {'role': 'system', 'content': sys_prompt},
                    {'role': 'user', 'content': message}
                ]
            )
            reply = response['message']['content'].strip()
        except:
            reply = "Khánh ơi, tớ vừa hoàn thành buổi tổng duyệt cho concert xong nè! Nhớ nhắn tin tiếp cho tớ nha~ ♥"

        chat_history.append({
            "sender": "Momoko",
            "text": reply,
            "time": datetime.datetime.now().strftime("%H:%M")
        })

    threading.Thread(target=task, daemon=True).start()


# --- HÀM VẼ GIAO DIỆN CHÍNH (GEMINI STYLE) ---
def draw_gemini_ui(surface, mouse_pos):
    global max_chat_scroll
    w, h = surface.get_size()
    surface.fill(COLOR_BG_MAIN)

    # 1. THANH TIÊU ĐỀ TRÊN CÙNG (TOP-BAR) - ĐƠN GIẢN VÀ TINH TẾ
    pygame.draw.rect(surface, COLOR_BG_MAIN, (0, 0, w, 65))
    pygame.draw.line(surface, COLOR_BORDER_GEMINI, (0, 65), (w, 65), 1)

    # Vẽ ảnh đại diện nhỏ của Momoko nếu nạp thành công
    avatar_x = 30
    if momoko_avatar:
        surface.blit(momoko_avatar, (avatar_x, 10))
        text_offset_x = avatar_x + 60
    else:
        text_offset_x = avatar_x

    surface.blit(font_title.render("Hashimoto Momoko 🌸", True, COLOR_TEXT_MAIN), (text_offset_x, 12))
    surface.blit(font_hint.render("Mô hình Llama 3.2 cục bộ • Sẵn sàng", True, COLOR_TEXT_MUTED), (text_offset_x, 38))

    # 2. KHUNG HIỂN THỊ NỘI DUNG TIN NHẮN CHAT (VÙNG GIỮA)
    chat_zone_rect = pygame.Rect(30, 80, w - 60, h - 200)
    surface.set_clip(chat_zone_rect)

    current_y = 95 - chat_scroll_y
    bubble_max_w = 600
    _, line_h = font_chat.size("A")

    for msg in chat_history:
        is_user = (msg["sender"] == "User")
        wrapped_lines = wrap_text(msg["text"], font_chat, bubble_max_w - 30)

        # Tính toán kích thước bong bóng chat linh hoạt
        box_w = bubble_max_w if len(wrapped_lines) > 1 else font_chat.size(wrapped_lines[0])[0] + 30
        box_h = (len(wrapped_lines) * (line_h + 6)) + 20

        # Căn lề phải cho User (Khánh), lề trái cho Momoko
        box_x = chat_zone_rect.right - box_w - 10 if is_user else chat_zone_rect.x + 10

        if current_y + box_h > 70 and current_y < h - 110:
            # Vẽ bong bóng chat phong cách bo góc tròn mềm mịn
            pygame.draw.rect(
                surface,
                COLOR_BUBBLE_USER if is_user else COLOR_BUBBLE_MOMOKO,
                (box_x, current_y, box_w, box_h),
                border_radius=16
            )

            # Đổ chữ vào lòng bong bóng chat
            print_y = current_y + 10
            for line in wrapped_lines:
                surface.blit(font_chat.render(line, True, COLOR_TEXT_MAIN), (box_x + 15, print_y))
                print_y += line_h + 6

            # Vẽ mốc thời gian mờ nhỏ dưới mỗi bong bóng
            time_x = box_x + box_w - 45 if is_user else box_x + 15
            surface.blit(font_hint.render(msg["time"], True, COLOR_TEXT_MUTED), (box_x + 5, current_y + box_h + 2))

        current_y += box_h + 22

    surface.set_clip(None)
    max_chat_scroll = max(0, (current_y + chat_scroll_y) - (h - 200))

    # 3. KHUNG GÕ TIN NHẮN PHÍA DƯỚI (MÔ PHỎNG THANH NHẬP LIỆU GEMINI TRUNG TÂM)
    input_box_w = min(800, w - 80)  # Căn chỉnh chiều rộng tối đa 800px giống Google Web
    input_box_x = (w - input_box_w) // 2
    input_box_y = h - 85
    input_rect = pygame.Rect(input_box_x, input_box_y, input_box_w, 48)

    # Khung bo góc hình viên thuốc cực mượt (border_radius=24)
    pygame.draw.rect(surface, (240, 244, 252), input_rect, border_radius=24)
    pygame.draw.rect(surface, COLOR_PRIMARY_PINK, input_rect, 1, border_radius=24)

    # Hiển thị chữ đang nhập hoặc chữ gợi ý mờ
    if user_input_text == "":
        surface.blit(
            font_chat.render("Nhập tin nhắn gửi chị Momoko... (Bấm Enter để gửi)", True, COLOR_TEXT_MUTED),
            (input_rect.x + 20, input_rect.y + 13)
        )
    else:
        surface.blit(font_chat.render(user_input_text, True, COLOR_TEXT_MAIN), (input_rect.x + 20, input_rect.y + 13))

    return input_rect


# --- VÒNG LẶP ĐIỀU HƯỚNG CHƯƠNG TRÌNH ---
def main():
    global user_input_text, chat_scroll_y, max_chat_scroll

    load_momoko_graphics()
    app_running = True

    while app_running:
        current_mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                app_running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4:  # Lăn chuột lên
                    chat_scroll_y = max(0, chat_scroll_y - 30)
                elif event.button == 5:  # Lăn chuột xuống
                    chat_scroll_y = min(max_chat_scroll, chat_scroll_y + 30)

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    user_input_text = user_input_text[:-1]
                elif event.key == pygame.K_RETURN:
                    if user_input_text.strip():
                        cleaned_msg = user_input_text.strip()
                        # Đẩy tin nhắn của Khánh vào giao diện
                        chat_history.append({
                            "sender": "User",
                            "text": cleaned_msg,
                            "time": datetime.datetime.now().strftime("%H:%M")
                        })
                        user_input_text = ""
                        # Gọi AI phản hồi bất đồng bộ chống đơ game
                        ask_momoko_ai_async(cleaned_msg)
                        chat_scroll_y = max_chat_scroll
                else:
                    if event.unicode.isprintable():
                        user_input_text += event.unicode

        # Vẽ toàn bộ giao diện lên màn hình
        draw_gemini_ui(screen, current_mouse_pos)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()