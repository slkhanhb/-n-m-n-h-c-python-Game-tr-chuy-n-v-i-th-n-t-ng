import pygame
import pandas as pd
import datetime
import os
import ai_engine
import tkinter as tk
from tkinter import filedialog

# --- KHỞI TẠO ---
pygame.init()
WIDTH, HEIGHT = 1366, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Trò chuyện với thần tượng")

# --- ĐƯỜNG DẪN MỚI ---
BASE_PATH = r"F:\ĐAMH tro chuyen voi than tuong"
MEMBER_PATH = os.path.join(BASE_PATH, "Member")
chat_file = os.path.join(BASE_PATH, "chat_history.csv")

# --- MÀU SẮC & FONT ---
COLOR_BG = (240, 242, 245)
COLOR_SIDEBAR = (255, 255, 255)
COLOR_ACTIVE = (231, 243, 255)
font_main = pygame.font.SysFont("timesnewroman", 19)
font_bold = pygame.font.SysFont("timesnewroman", 19, bold=True)
font_small = pygame.font.SysFont("timesnewroman", 15)


# --- HÀM HỖ TRỢ ---
def get_circle_avatar(image_path, size):
    """Tạo avatar tròn và Khử răng cưa (Anti-aliasing) bằng Supersampling"""
    try:
        img = pygame.image.load(image_path).convert_alpha()
        big_size = size * 2  # Vẽ to gấp đôi để khử răng cưa
        img = pygame.transform.smoothscale(img, (big_size, big_size))

        mask = pygame.Surface((big_size, big_size), pygame.SRCALPHA)
        pygame.draw.circle(mask, (255, 255, 255), (big_size // 2, big_size // 2), big_size // 2)

        output = pygame.Surface((big_size, big_size), pygame.SRCALPHA)
        output.blit(img, (0, 0))
        output.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)

        # Thu nhỏ lại kích thước chuẩn
        return pygame.transform.smoothscale(output, (size, size))
    except:
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(surf, (200, 200, 200), (size // 2, size // 2), size // 2)
        return surf


def load_all_members(base_folder):
    members_dict = {}
    if not os.path.exists(base_folder): return members_dict

    for root, dirs, files in os.walk(base_folder):
        if "Conten" in root: continue
        for file in files:
            if file.lower().endswith(('.jpg', '.png')):
                name = os.path.splitext(file)[0]
                path = os.path.join(root, file)
                members_dict[name] = {"img": get_circle_avatar(path, 55), "history": [], "path": path}
    return members_dict


def open_file_picker():
    """Mở hộp thoại chọn file của Windows"""
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    file_path = filedialog.askopenfilename(
        title="Chọn Ảnh hoặc Video",
        filetypes=[("Media Files", "*.png;*.jpg;*.jpeg;*.mp4")]
    )
    root.destroy()
    return file_path


# --- LOAD DATA ---
members = load_all_members(MEMBER_PATH)
members_list = list(members.keys())

if os.path.exists(chat_file):
    df_history = pd.read_csv(chat_file)
    for name in members:
        members[name]["history"] = df_history[df_history['target'] == name].to_dict('records')
else:
    df_history = pd.DataFrame(columns=['target', 'sender', 'message', 'time'])

# --- BIẾN TRẠNG THÁI ---
current_member = members_list[0] if members_list else "None"
input_text = ""
sidebar_w = 330
sidebar_scroll = 0
chat_scroll = 0
clock = pygame.time.Clock()
chat_image_cache = {}

# --- VÒNG LẶP CHÍNH ---
running = True
while running:
    curr_w, curr_h = screen.get_size()
    screen.fill(COLOR_BG)
    mouse_pos = pygame.mouse.get_pos()
    click = False

    # 1. XỬ LÝ SỰ KIỆN
    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1: click = True
            if event.button == 4:  # Scroll Up
                if mouse_pos[0] < sidebar_w:
                    sidebar_scroll = min(0, sidebar_scroll + 40)
                else:
                    chat_scroll = min(0, chat_scroll + 40)
            if event.button == 5:  # Scroll Down
                if mouse_pos[0] < sidebar_w:
                    sidebar_scroll -= 40
                else:
                    chat_scroll -= 40

            # Click chuyển Idol
            if event.pos[0] < sidebar_w and click:
                idx = (event.pos[1] - 70 - sidebar_scroll) // 75
                if 0 <= idx < len(members_list):
                    current_member = members_list[idx]
                    chat_scroll = 0

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN and input_text.strip() and current_member != "None":
                now = datetime.datetime.now().strftime("%H:%M")
                user_msg_text = input_text

                new_chat = {'target': current_member, 'sender': 'User', 'message': user_msg_text, 'time': now}
                members[current_member]["history"].append(new_chat)
                input_text = ""

                ai_reply = ai_engine.get_idol_response(current_member, user_msg_text, BASE_PATH)
                bot_chat = {'target': current_member, 'sender': current_member, 'message': ai_reply, 'time': now}
                members[current_member]["history"].append(bot_chat)

                df_history = pd.concat([df_history, pd.DataFrame([new_chat, bot_chat])], ignore_index=True)
                df_history.to_csv(chat_file, index=False)
                chat_scroll = 0  # Tự động cuộn xuống cuối

            elif event.key == pygame.K_BACKSPACE:
                input_text = input_text[:-1]
            else:
                input_text += event.unicode

    # Rect của Nút đính kèm (Nằm dưới phần Input)
    btn_attach_rect = pygame.Rect(sidebar_w + 15, curr_h - 65, 40, 40)

    # Xử lý sự kiện bấm Nút Gửi File (Thực hiện ngoài vòng lặp event để không block)
    if click and btn_attach_rect.collidepoint(mouse_pos) and current_member != "None":
        selected_file = open_file_picker()
        if selected_file:
            ext = selected_file.lower().split('.')[-1]
            now = datetime.datetime.now().strftime("%H:%M")
            msg_format = f"[VIDEO:{selected_file}]" if ext == 'mp4' else f"[IMAGE:{selected_file}]"

            # Gửi file với tư cách User
            media_chat = {'target': current_member, 'sender': 'User', 'message': msg_format, 'time': now}
            members[current_member]["history"].append(media_chat)
            df_history = pd.concat([df_history, pd.DataFrame([media_chat])], ignore_index=True)
            df_history.to_csv(chat_file, index=False)
            chat_scroll = 0

    # 2. VẼ SIDEBAR
    pygame.draw.rect(screen, COLOR_SIDEBAR, (0, 0, sidebar_w, curr_h))
    for i, name in enumerate(members_list):
        y = 70 + (i * 75) + sidebar_scroll
        if y < -75 or y > curr_h: continue

        if name == current_member:
            pygame.draw.rect(screen, COLOR_ACTIVE, (8, y - 5, sidebar_w - 16, 68), border_radius=12)
        screen.blit(members[name]["img"], (20, y))
        screen.blit(font_bold.render(name, True, (0, 0, 0)), (90, y + 5))
        screen.blit(font_small.render("Online", True, (0, 150, 0)), (90, y + 32))

    # 3. VẼ CHAT AREA
    if current_member != "None":
        y_chat = 100 + chat_scroll
        for msg in members[current_member]["history"][-20:]:
            is_user = msg['sender'] == 'User'
            raw_text = str(msg['message'])

            display_text = raw_text
            media_path = None
            media_type = None

            if "[IMAGE:" in raw_text:
                display_text = raw_text.split("[IMAGE:")[0].strip()
                media_path = raw_text.split("[IMAGE:")[1].split("]")[0]
                media_type = "IMAGE"
            elif "[VIDEO:" in raw_text:
                display_text = raw_text.split("[VIDEO:")[0].strip()
                media_path = raw_text.split("[VIDEO:")[1].split("]")[0]
                media_type = "VIDEO"

            # Vẽ Text
            if display_text:
                txt_surf = font_main.render(display_text, True, (0, 0, 0))
                box_w = min(txt_surf.get_width() + 30, curr_w - sidebar_w - 100)
                x_msg = curr_w - box_w - 30 if is_user else sidebar_w + 80

                color = (220, 245, 198) if is_user else (255, 255, 255)
                pygame.draw.rect(screen, color, (x_msg, y_chat, box_w, 45), border_radius=15)
                screen.blit(txt_surf, (x_msg + 15, y_chat + 10))

                if not is_user: screen.blit(members[current_member]["img"], (sidebar_w + 15, y_chat - 5))
                y_chat += 55

            # Vẽ Media (Ảnh/Video)
            if media_path and os.path.exists(media_path):
                if media_type == "IMAGE":
                    if media_path not in chat_image_cache:
                        img = pygame.image.load(media_path).convert_alpha()
                        ratio = 280 / img.get_width()  # Max width 280px
                        new_h = int(img.get_height() * ratio)
                        chat_image_cache[media_path] = pygame.transform.smoothscale(img, (280, new_h))

                    cached_img = chat_image_cache[media_path]
                    img_w = cached_img.get_width()
                    # Căn phải cho User, căn trái cho AI
                    img_x = curr_w - img_w - 30 if is_user else sidebar_w + 80

                    pygame.draw.rect(screen, (255, 255, 255),
                                     (img_x - 5, y_chat - 5, img_w + 10, cached_img.get_height() + 10),
                                     border_radius=10)
                    screen.blit(cached_img, (img_x, y_chat))
                    if not is_user: screen.blit(members[current_member]["img"], (sidebar_w + 15, y_chat - 5))
                    y_chat += cached_img.get_height() + 20

                elif media_type == "VIDEO":
                    vid_x = curr_w - 230 if is_user else sidebar_w + 80
                    vid_rect = pygame.Rect(vid_x, y_chat, 200, 55)

                    btn_color = (180, 210, 255) if vid_rect.collidepoint(mouse_pos) else (210, 230, 255)
                    pygame.draw.rect(screen, btn_color, vid_rect, border_radius=12)
                    pygame.draw.rect(screen, (100, 150, 255), vid_rect, 2, border_radius=12)
                    screen.blit(font_bold.render("▶ Xem Video", True, (0, 50, 150)), (vid_x + 45, y_chat + 15))
                    if not is_user: screen.blit(members[current_member]["img"], (sidebar_w + 15, y_chat - 5))

                    if click and vid_rect.collidepoint(mouse_pos):
                        os.startfile(media_path)
                    y_chat += 70

    # 4. Vẽ HEADER & INPUT LAYER
    pygame.draw.rect(screen, (255, 255, 255), (sidebar_w, 0, curr_w, 70))
    if current_member != "None":
        screen.blit(font_bold.render(current_member, True, (0, 0, 0)), (sidebar_w + 25, 20))

    pygame.draw.rect(screen, (255, 255, 255), (sidebar_w, curr_h - 90, curr_w, 90))

    # Nút đính kèm [+]
    attach_color = (200, 200, 200) if btn_attach_rect.collidepoint(mouse_pos) else (230, 230, 230)
    pygame.draw.rect(screen, attach_color, btn_attach_rect, border_radius=20)
    screen.blit(font_bold.render("+", True, (100, 100, 100)), (sidebar_w + 28, curr_h - 55))

    # Ô nhập Text
    pygame.draw.rect(screen, (240, 242, 245), (sidebar_w + 65, curr_h - 70, curr_w - sidebar_w - 90, 50),
                     border_radius=25)
    screen.blit(font_main.render(input_text + "|", True, (0, 0, 0)), (sidebar_w + 80, curr_h - 57))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()