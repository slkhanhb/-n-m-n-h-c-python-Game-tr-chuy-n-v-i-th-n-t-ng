import ollama
import os
import random

# Biến lưu trữ số lượng tin nhắn đã trao đổi với từng idol
msg_counts = {}


def get_idol_response(idol_name, user_message, base_path):
    # Khởi tạo bộ đếm nếu chưa có
    if idol_name not in msg_counts:
        msg_counts[idol_name] = 0
    msg_counts[idol_name] += 1

    # Profile chi tiết dựa trên dữ liệu bạn cung cấp
    idol_profiles = {
        "Matsumoto Momona": "MBTI: INFP, 'living doll'. Color: Light Pink.",
        "Tachibana Miku": "MBTI: ESFJ, Sweet and professional. Group: Karen na Ivory.",
        "Momiyama Himeri": "MBTI: ISTJ, Leader, reliable. Color: Blue.",
        "Haruno Riri": "Gentle, diligent, Green color.",
        "Hoshino Sarasa": "Charm Poche member, bright personality."
    }

    profile = idol_profiles.get(idol_name, "A lovely Japanese idol.")

    try:
        response = ollama.chat(model='llama3.2', messages=[
            {'role': 'system', 'content': f"You are {idol_name}. {profile} Speak English, max 2 sentences."},
            {'role': 'user', 'content': user_message},
        ])
        bot_reply = response['message']['content'].strip()
    except Exception as e:
        return f"Ollama Error: {e}"

    # --- LOGIC TỰ ĐỘNG GỬI ẢNH/VIDEO SAU 2-3 TIN NHẮN ---
    # Đường dẫn: F:\ĐATT tro chuyen voi than tuong\Member\Conten\[Tên Idol]
    content_folder = os.path.join(base_path, "Member", "Conten", idol_name)

    # Nếu đã chat được 2 hoặc 3 tin, hoặc ngẫu nhiên 30%
    if os.path.exists(content_folder) and (msg_counts[idol_name] >= random.randint(2, 3) or random.random() < 0.3):
        files = [f for f in os.listdir(content_folder) if f.lower().endswith(('.jpg', '.png', '.mp4'))]
        if files:
            chosen = random.choice(files)
            full_path = os.path.join(content_folder, chosen)
            tag = "VIDEO" if chosen.lower().endswith('.mp4') else "IMAGE"
            bot_reply += f"\n[{tag}:{full_path}]"
            msg_counts[idol_name] = 0  # Reset bộ đếm sau khi gửi media

    return bot_reply