# idol_manager.py
import os
import pygame
from config import TAKA_MEMBER_PATH, KAREN_MEMBER_PATH


def load_idols(group_path):
    """
    Quét thư mục và trả về dictionary chứa thông tin Idol.
    Yêu cầu: Trong thư mục mỗi nhóm, tạo thư mục con mang tên Idol (VD: 'Momoko_Hashimoto').
    Trong đó chứa: avatar.png và info.txt
    """
    idols = {}
    if not os.path.exists(group_path):
        return idols

    for idol_name in os.listdir(group_path):
        idol_dir = os.path.join(group_path, idol_name)
        if os.path.isdir(idol_dir):
            avatar_path = os.path.join(idol_dir, "avatar.png")
            info_path = os.path.join(idol_dir, "info.txt")

            # Nạp ảnh mượt mà
            try:
                img = pygame.image.load(avatar_path).convert_alpha()
                img = pygame.transform.smoothscale(img, (120, 120))  # Tỉ lệ thẻ ảnh
            except:
                img = None  # Xử lý ảnh mặc định nếu thiếu

            # Đọc thông tin cá nhân (Photocard info)
            info = "Đang cập nhật..."
            if os.path.exists(info_path):
                with open(info_path, 'r', encoding='utf-8') as f:
                    info = f.read()

            idols[idol_name] = {
                "avatar": img,
                "info": info
            }
    return idols

# Sử dụng:
# taka_idols = load_idols(TAKA_MEMBER_PATH)
# karen_idols = load_idols(KAREN_MEMBER_PATH)