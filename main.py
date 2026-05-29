import pygame
import pandas as pd
import datetime
import os
import random
import threading
import requests
import ollama
import tkinter as t
from tkinter import filedialog, messagebox

# --- KHỞI TẠO HỆ THỐNG ĐỒ HỌA HOÀN CHỈNH ---
pygame.init()
WIDTH, HEIGHT = 1366, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Idol Chat")
clock = pygame.time.Clock()

# --- ĐƯỜNG DẪN TÀI NGUYÊN HỆ THỐNG (Ổ G:\) ---
BASE_PATH = r"G:\ĐAMH tro chuyen voi than tuong"
TAKA_MEMBER_PATH = os.path.join(BASE_PATH, r"Member\\TAKANE NO NADESHIKO")
CARD_INFO_PATH = os.path.join(BASE_PATH, "Takaneko_member")
ICON_PATH = os.path.join(BASE_PATH, "Icon")

# --- HỆ THỐNG MÀU SẮC PREMIUM (SOFT UI THEME) ---
COLOR_BG_MAIN = (255, 255, 255)  # Nền trắng tinh khôi
COLOR_SIDEBAR = (245, 247, 250)  # Nền sidebar xám xanh dịu mát
COLOR_CARD_BG = (248, 249, 250)  # Nền thẻ thông tin
COLOR_PRIMARY = (255, 90, 150)  # Hồng đậm Pastel (Màu chủ đạo)
COLOR_PRIMARY_HOVER = (255, 120, 170)  # Hồng sáng khi di chuột qua
COLOR_TEXT_MAIN = (43, 45, 66)  # Chữ đen than cao cấp
COLOR_TEXT_MUTED = (141, 153, 174)  # Chữ xám ghi phụ
COLOR_BUBBLE_USER = (255, 225, 235)  # Bong bóng chat của Khánh (Hồng nhạt)
COLOR_BUBBLE_BOT = (235, 238, 243)  # Bong bóng chat của Thần tượng (Xám sáng)
COLOR_BORDER = (226, 232, 240)  # Đường viền phân cách mỏng thanh lịch


# --- SỬA LỖI FONT UNICODE TIẾNG VIỆT TRIỆT ĐỂ ---
def get_safe_font(size, bold=False):
    """Nạp trực tiếp font hệ thống Windows đảm bảo không bao giờ bị lỗi ô vuông"""
    font_files = [
        r"C:\Windows\Fonts\calibri.ttf" if not bold else r"C:\Windows\Fonts\calibrib.ttf",
        r"C:\Windows\Fonts\SegoeUI.ttf" if not bold else r"C:\Windows\Fonts\SegoeUIb.ttf",
        r"C:\Windows\Fonts\Arial.ttf" if not bold else r"C:\Windows\Fonts\Arialbd.ttf"
    ]
    for path in font_files:
        if os.path.exists(path):
            try:
                return pygame.font.Font(path, size)
            except:
                continue
    return pygame.font.SysFont("Calibri", size, bold)


# Khởi tạo các kích cỡ font dùng trong app
font_name_list = get_safe_font(16, bold=True)
font_chat_text = get_safe_font(16, bold=False)
font_title = get_safe_font(18, bold=True)
font_desc = get_safe_font(13, bold=False)

# --- BIẾN ĐIỀU HƯỚNG VÀ DỮ LIỆU ---
idols_data = {}
current_selected_idol = None
user_chat_input = ""
search_input = ""
active_input_box = "chat"  # 'chat' hoặc 'search'
chat_history = []
chat_scroll_y = 0
max_chat_scroll = 0
icons = {}


# --- NẠP BIỂU TƯỢNG HỆ THỐNG ---
def load_system_icons():
    global icons
    for key, name in [("search", "search.png")]:
        p = os.path.join(ICON_PATH, name)
        if os.path.exists(p):
            try:
                img = pygame.image.load(p).convert_alpha()
                icons[key] = pygame.transform.smoothscale(img, (18, 18))
            except:
                icons[key] = None


# --- NẠP VÀ XỬ LÝ ẢNH CHUẨN TỈ LỆ (IDOL MANAGER TÍCH HỢP) ---
def load_all_idols_graphics():
    global idols_data
    idols_data.clear()

    taka_names = [
    taka_names = [
        "Momiyama Himeri", "Matsumoto Momona", "Hashimoto Momoko", "Hoshitani Mikuru",
        "Hinahata Hina", "Kizuki Nao", "Suzumi Suu", "Haruno Riri", "Hazuki Saara", "Higashiyama Erisa"
    ]

    for name in taka_names:
        idols_data[name] = {
            "group": "Takane no Nadeshiko",
            "avatar": None,
            "photocard": None,
            "info": "Thành viên chính thức của nhóm Takane no Nadeshiko.\nTiểu sử đang được đồng bộ..."
        }

    # 1. Quét nạp Avatar nhỏ hình đại diện (Vòng tròn danh sách)
    if os.path.exists(TAKA_MEMBER_PATH):
        for f in os.listdir(TAKA_MEMBER_PATH):
            c_name = f.replace("_", " ").split(".")[0]
            for id_name in idols_data:
                if c_name.lower() in id_name.lower():
                    try:
                        p = os.path.join(TAKA_MEMBER_PATH, f)
                        raw_img = pygame.image.load(p).convert_alpha()
                        idols_data[id_name]["avatar"] = pygame.transform.smoothscale(raw_img, (48, 48))
                    except:
                        pass

    # 2. Quét nạp Ảnh thẻ Photocard đứng cao cấp (250x350) không bóp méo hình
    if os.path.exists(CARD_INFO_PATH):
        for f in os.listdir(CARD_INFO_PATH):
            f_lower = f.lower()
            for id_name in idols_data.keys():
                keyword = id_name.split()[-1].lower()
                if keyword in f_lower:
                    full_p = os.path.join(CARD_INFO_PATH, f)
                    if f_lower.endswith(('.png', '.jpg', '.jpeg')):
                        try:
                            card_img = pygame.image.load(full_p).convert_alpha()
                            idols_data[id_name]["photocard"] = pygame.transform.smoothscale(card_img, (331, 180))
                        except:
                            pass
                    elif f_lower.endswith('.txt'):
                        try:
                            with open(full_p, "r", encoding="utf-8") as file_txt:
                                idols_data[id_name]["info"] = file_txt.read()
                        except:
                            pass


# --- LOGIC TỰ ĐỘNG XUỐNG DÒNG CHỮ CHAT ---
def split_text_to_wrapped_lines(text, font, max_w):
    words = text.split(' ')
    lines = []
    curr_line = ""
    for w in words:
        test_line = curr_line + " " + w if curr_line else w
        w_size, _ = font.size(test_line)
        if w_size <= max_w:
            curr_line = test_line
        else:
            if curr_line: lines.append(curr_line)
            curr_line = w
    if curr_line: lines.append(curr_line)
    return lines


def draw_wrapped_info_text(surf, text, color, rect, font):
    raw_lines = text.split('\n')
    all_lines = []
    for rl in raw_lines:
        all_lines.extend(split_text_to_wrapped_lines(rl, font, rect.width))
    x, y = rect.topleft
    _, h_space = font.size("A")
    for line in all_lines:
        if y + h_space > rect.bottom: break
        surf.blit(font.render(line, True, color), (x, y))
        y += h_space + 5


# --- THREAD KẾT NỐI CHAT AI OLLAMA CHỐNG ĐƠ MÀN HÌNH ---
def send_chat_to_ollama_async(idol_name, message):
    from ai_engine import generate_system_prompt
    def task():
        sys_p = generate_system_prompt(idol_name)
        try:
            res = ollama.chat(model='llama3.2', messages=[
                {'role': 'system', 'content': sys_p},
                {'role': 'user', 'content': message}
            ])
            reply = res['message']['content'].strip()
        except:
            reply = f"Khánh ơi, tớ vừa hoàn thành lịch trình ghi hình xong nè! Nhớ nhắn tin cho tớ tiếp nha~ ♥"
        chat_history.append({"sender": idol_name, "text": reply, "time": datetime.datetime.now().strftime("%H:%M")})

    threading.Thread(target=task, daemon=True).start()


# --- HÀM VẼ TOÀN BỘ GIAO DIỆN CHÍNH ---
def draw_dashboard_ui(surface, mouse_pos):
    global max_chat_scroll
    w, h = surface.get_size()
    surface.fill(COLOR_BG_MAIN)

    # -----------------------------------------------------------------
    # COLUMN 1: SIDEBAR TRÁI (DANH SÁCH THẦN TƯỢNG)
    # -----------------------------------------------------------------
    sidebar_w = 320
    pygame.draw.rect(surface, COLOR_SIDEBAR, (0, 0, sidebar_w, h))
    pygame.draw.line(surface, COLOR_BORDER, (sidebar_w, 0), (sidebar_w, h), 1)

    # Tiêu đề Sidebar
    surface.blit(font_title.render("TAKANE NO NADESHIKO", True, COLOR_PRIMARY), (20, 20))

    # Ô Tìm kiếm bo góc phong cách Modern UI
    search_rect = pygame.Rect(15, 55, sidebar_w - 30, 36)
    pygame.draw.rect(surface, COLOR_BG_MAIN, search_rect, border_radius=8)
    is_search_focus = (active_input_box == "search")
    pygame.draw.rect(surface, COLOR_PRIMARY if is_search_focus else COLOR_BORDER, search_rect, 1, border_radius=8)

    # Vẽ icon kính lúp tìm kiếm
    offset_x = 15
    if icons.get("search"):
        surface.blit(icons["search"], (search_rect.x + 10, search_rect.y + 9))
        offset_x = 35

    if search_input == "":
        surface.blit(font_desc.render("Tìm kiếm thành viên...", True, COLOR_TEXT_MUTED),
                     (search_rect.x + offset_x, search_rect.y + 9))
    else:
        surface.blit(font_chat_text.render(search_input, True, COLOR_TEXT_MAIN),
                     (search_rect.x + offset_x, search_rect.y + 7))

    # Danh sách các thành viên (Vẽ thẻ có hiệu ứng Hover đổi màu)
    y_start = 105
    idol_click_zones = {}
    for name, data in idols_data.items():
        if search_input.lower() not in name.lower(): continue

        item_box = pygame.Rect(10, y_start, sidebar_w - 20, 64)
        is_hovered = item_box.collidepoint(mouse_pos)
        is_selected = (current_selected_idol == name)

        # Đổ màu nền linh hoạt theo trạng thái di chuột hoặc click chọn
        if is_selected:
            pygame.draw.rect(surface, (255, 235, 242), item_box, border_radius=10)
            pygame.draw.rect(surface, COLOR_PRIMARY, item_box, 1, border_radius=10)
        elif is_hovered:
            pygame.draw.rect(surface, (235, 240, 247), item_box, border_radius=10)
        else:
            pygame.draw.rect(surface, COLOR_BG_MAIN, item_box, border_radius=10)
            pygame.draw.rect(surface, (240, 242, 245), item_box, 1, border_radius=10)

        # Vẽ ảnh đại diện tròn/vuông mượt
        if data["avatar"]:
            surface.blit(data["avatar"], (item_box.x + 8, item_box.y + 8))

        # Hiển thị text tên và nhóm
        surface.blit(font_name_list.render(name, True, COLOR_PRIMARY if is_selected else COLOR_TEXT_MAIN),
                     (item_box.x + 68, item_box.y + 12))
        surface.blit(font_desc.render(data["group"], True, COLOR_TEXT_MUTED), (item_box.x + 68, item_box.y + 36))

        idol_click_zones[name] = item_box
        y_start += 72

    # -----------------------------------------------------------------
    # COLUMN 2: TIÊU ĐỀ CHAT & KHUNG CHAT GIỮA
    # -----------------------------------------------------------------
    chat_area_x = sidebar_w
    chat_area_w = w - sidebar_w - 290

    # Thanh tiêu đề top-bar
    pygame.draw.rect(surface, COLOR_BG_MAIN, (chat_area_x, 0, chat_area_w, 60))
    pygame.draw.line(surface, COLOR_BORDER, (chat_area_x, 60), (chat_area_x + chat_area_w, 60), 1)

    if current_selected_idol:
        surface.blit(font_title.render(f"🌸 {current_selected_idol} • Online", True, COLOR_TEXT_MAIN),
                     (chat_area_x + 25, 18))
    else:
        surface.blit(font_name_list.render("Hãy chọn một idol ở danh sách bên trái để kết nối nha Khánh!", True,
                                           COLOR_TEXT_MUTED), (chat_area_x + 40, h // 2))
        return idol_click_zones, search_rect, None

    # Khung hiển thị nội dung các dòng chat nhắn tin độc lập
    chat_zone_h = h - 145
    clip_chat_window = pygame.Rect(chat_area_x + 10, 70, chat_area_w - 20, chat_zone_h)

    surface.set_clip(clip_chat_window)
    chat_render_y = 85 - chat_scroll_y
    bubble_limit_width = 440
    _, font_h = font_chat_text.size("A")

    for bubble in chat_history:
        from_user = (bubble["sender"] == "User")
        lines_wrapped = split_text_to_wrapped_lines(bubble["text"], font_chat_text, bubble_limit_width - 24)

        box_w = bubble_limit_width if len(lines_wrapped) > 1 else font_chat_text.size(lines_wrapped[0])[0] + 26
        box_h = (len(lines_wrapped) * (font_h + 5)) + 16

        box_x = clip_chat_window.right - box_w - 15 if from_user else clip_chat_window.x + 15

        if chat_render_y + box_h > 65 and chat_render_y < h - 75:
            # Vẽ khối bong bóng chat bo góc cực mượt
            pygame.draw.rect(surface, COLOR_BUBBLE_USER if from_user else COLOR_BUBBLE_BOT,
                             (box_x, chat_render_y, box_w, box_h), border_radius=12)
            t_y = chat_render_y + 8
            for line in lines_wrapped:
                surface.blit(font_chat_text.render(line, True, COLOR_TEXT_MAIN), (box_x + 13, t_y))
                t_y += font_h + 5

        chat_render_y += box_h + 12

    surface.set_clip(None)
    max_chat_scroll = max(0, (chat_render_y + chat_scroll_y) - (h - 180))

    # Khung gõ nhập dữ liệu tin nhắn ở đáy màn hình
    panel_input_y = h - 68
    pygame.draw.line(surface, COLOR_BORDER, (chat_area_x, panel_input_y), (chat_area_x + chat_area_w, panel_input_y), 1)

    box_input_chat = pygame.Rect(chat_area_x + 20, panel_input_y + 12, chat_area_w - 40, 42)
    pygame.draw.rect(surface, (242, 244, 247), box_input_chat, border_radius=22)
    if active_input_box == "chat":
        pygame.draw.rect(surface, COLOR_PRIMARY, box_input_chat, 1, border_radius=22)

    if user_chat_input == "":
        surface.blit(
            font_chat_text.render("Nhắn tin gửi thần tượng của bạn... (Bấm Enter để gửi)", True, COLOR_TEXT_MUTED),
            (box_input_chat.x + 18, box_input_chat.y + 10))
    else:
        surface.blit(font_chat_text.render(user_chat_input, True, COLOR_TEXT_MAIN),
                     (box_input_chat.x + 18, box_input_chat.y + 10))

    # -----------------------------------------------------------------
    # COLUMN 3: PANEL BÊN PHẢI (ẢNH THẺ PHOTOCARD ĐỨNG CAO CẤP)
    # -----------------------------------------------------------------
    panel_right_x = w - 290
    panel_right_w = 290
    pygame.draw.rect(surface, COLOR_SIDEBAR, (panel_right_x, 0, panel_right_w, h))
    pygame.draw.line(surface, COLOR_BORDER, (panel_right_x, 0), (panel_right_x, h), 1)

    selected_info = idols_data[current_selected_idol]
    pc_w, pc_h = 250, 350
    pc_draw_x = panel_right_x + (panel_right_w - pc_w) // 2
    pc_draw_y = 20

    if selected_info["photocard"]:
        # Hiển thị ảnh chân dung đứng chuẩn tỉ lệ Photocard J-pop siêu sang
        surface.blit(selected_info["photocard"], (pc_draw_x, pc_draw_y))
    else:
        empty_rect = pygame.Rect(pc_draw_x, pc_draw_y, pc_w, pc_h)
        pygame.draw.rect(surface, COLOR_CARD_BG, empty_rect, border_radius=12)
        pygame.draw.rect(surface, COLOR_BORDER, empty_rect, 1, border_radius=12)
        surface.blit(font_name_list.render("[ No Photocard ]", True, COLOR_TEXT_MUTED),
                     (empty_rect.x + 65, empty_rect.y + pc_h // 2 - 10))

    # Hộp chứa thông tin tiểu sử cá nhân bo viền mờ dưới photocard
    text_info_box = pygame.Rect(pc_draw_x, pc_draw_y + pc_h + 15, pc_w, h - pc_h - 55)
    pygame.draw.rect(surface, COLOR_BG_MAIN, text_info_box, border_radius=12)
    pygame.draw.rect(surface, COLOR_BORDER, text_info_box, 1, border_radius=12)

    # Đẩy vị trí đệm chữ vào trong lòng khung
    inner_text_rect = pygame.Rect(text_info_box.x + 12, text_info_box.y + 12, text_info_box.width - 24,
                                  text_info_box.height - 24)
    draw_wrapped_info_text(surface, selected_info["info"], COLOR_TEXT_MAIN, inner_text_rect, font_desc)

    return idol_click_zones, search_rect, box_input_chat


# --- HÀM ĐIỀU HƯỚNG VÒNG LẶP CHÍNH ---
def main():
    global active_input_box, current_selected_idol, user_chat_input, search_input, chat_history, chat_scroll_y, max_chat_scroll

    load_system_icons()
    load_all_idols_graphics()

    app_running = True
    while app_running:
        is_mouse_click = False
        current_mouse_xy = pygame.mouse.get_pos()

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                app_running = False

            elif ev.type == pygame.MOUSEBUTTONDOWN:
                if ev.button == 1:
                    is_mouse_click = True
                elif ev.button == 4:  # Lăn bánh xe chuột lên trên
                    chat_scroll_y = max(0, chat_scroll_y - 25)
                elif ev.button == 5:  # Lăn bánh xe chuột xuống dưới
                    chat_scroll_y = min(max_chat_scroll, chat_scroll_y + 25)

            elif ev.type == pygame.KEYDOWN:
                if active_input_box == "chat" and current_selected_idol:
                    if ev.key == pygame.K_BACKSPACE:
                        user_chat_input = user_chat_input[:-1]
                    elif ev.key == pygame.K_RETURN:
                        if user_chat_input.strip():
                            cleaned_msg = user_chat_input.strip()
                            chat_history.append({"sender": "User", "text": cleaned_msg,
                                                 "time": datetime.datetime.now().strftime("%H:%M")})
                            user_chat_input = ""
                            send_chat_to_ollama_async(current_selected_idol, cleaned_msg)
                            chat_scroll_y = max_chat_scroll
                    else:
                        if ev.unicode.isprintable(): user_chat_input += ev.unicode

                elif active_input_box == "search":
                    if ev.key == pygame.K_BACKSPACE:
                        search_input = search_input[:-1]
                    elif ev.key == pygame.K_ESCAPE or ev.key == pygame.K_RETURN:
                        active_input_box = "chat"
                    else:
                        if ev.unicode.isprintable(): search_input += ev.unicode

        # --- VẼ ĐỒ HỌA RA CỬA SỔ ---
        idol_zones, s_bar, i_bar = draw_dashboard_ui(screen, current_mouse_xy)

        # Xử lý click chuột định vị hộp thoại tập trung (Focus)
        if is_mouse_click:
            if s_bar and s_bar.collidepoint(current_mouse_xy):
                active_input_box = "search"
            elif i_bar and i_bar.collidepoint(current_mouse_xy):
                active_input_box = "chat"
            else:
                for target_name, click_rect in idol_zones.items():
                    if click_rect.collidepoint(current_mouse_xy):
                        current_selected_idol = target_name
                        chat_history = [{"sender": target_name,
                                         "text": f"Chào Khánh yêu quý! Mình là {target_name} nè. Rất vui được trò chuyện cùng bạn hôm nay nha! ✨",
                                         "time": ""}]
                        chat_scroll_y = 0
                        active_input_box = "chat"
                        break

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()