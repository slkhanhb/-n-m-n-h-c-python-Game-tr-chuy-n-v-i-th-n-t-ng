import os
import sys
from flask import Flask, render_template, request, jsonify
import ollama
import datetime
import webview
import threading

# --- CẤU HÌNH ĐƯỜNG DẪN KHI ĐÓNG GÓI ---
if getattr(sys, 'frozen', False):
    # Nếu đang chạy từ file .exe, lấy thư mục tạm _MEIPASS chứa index.html
    template_folder = sys._MEIPASS
else:
    # Nếu đang chạy code trực tiếp bằng IDE
    template_folder = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__, template_folder=template_folder)

# --- ĐỒNG BỘ DỮ LIỆU THÀNH VIÊN ---
TAKANEKO_PROFILES = {
    "Haruno_Riri": {"name": "Haruno Riri", "traits": "Thành viên có nụ cười tỏa nắng và nét duyên dáng thanh lịch đặc trưng.", "color": "Xanh lá", "birthday": "16/01/2004", "hometown": "Nagaoto"},
    "Hashimoto_Momoko": {"name": "Hashimoto Momoko", "traits": "Cực kỳ sôi nổi, hoạt bát, là người làm bừng sáng không khí của cả nhóm.", "color": "Hồng nhạt", "birthday": "28/06/2003", "hometown": "Yamaguchi"},
    "Higashiyama_Erisa": {"name": "Higashiyama Erisa", "traits": "Thành viên tài năng với khả năng vũ đạo và biểu cảm sân khấu đầy lôi cuốn.", "color": "Cam", "birthday": "28/05/2006", "hometown": "Gifu"},
    "Hinamata_Hina": {"name": "Hinamata Hina", "traits": "Mang vẻ sang trọng, dịu dàng, sở hữu giọng hát trong trẻo ngọt ngào.", "color": "Tím", "birthday": "02/02/2002", "hometown": "Kanagawa"},
    "Hoshitani_Miruku": {"name": "Hoshitani Miruku", "traits": "Tính cách dễ thương, ngọt ngào, được rất nhiều người hâm mộ yêu mến.", "color": "Đỏ", "birthday": "06/11/2003", "hometown": "Tokyo"},
    "Kizuki_Nao": {"name": "Kizuki Nao", "traits": "Luôn mang năng lượng tích cực, hài hước và rất chu đáo với mọi người.", "color": "Vàng", "birthday": "25/12/2003", "hometown": "Aichi"},
    "Momiyama_Himeri": {"name": "Momiyama Himeri", "traits": "Người trưởng nhóm đáng tin cậy, chỗ dựa tinh thần lớn cho toàn đội.", "color": "Xanh dương", "birthday": "22/03/2004", "hometown": "Tochigi"},
    "Matsumoto_Momona": {"name": "Matsumoto Momona", "traits": "Vẻ đẹp tiểu thư chuẩn mực, phong thái ngọt ngào đốn tim fan hâm mộ.", "color": "Hồng đậm", "birthday": "12/10/2002", "hometown": "Kanagawa"},
    "Hazuki_Saara": {"name": "Hazuki Saara", "traits": "Nét cá tính độc đáo pha lẫn chút tinh nghịch đáng yêu vô cùng hút mắt.", "color": "Xám bạc", "birthday": "03/03/2005", "hometown": "Mie"},
    "Suzumi_Su": {"name": "Suzumi Su", "traits": "Thành viên nhỏ tuổi với sự hồn nhiên, đáng yêu và tiềm năng phát triển lớn.", "color": "Xanh dương nhạt", "birthday": "22/08/2007", "hometown": "Osaka"}
}

def get_system_prompt(idol_id):
    # Lấy thông tin idol được chọn, nếu không thấy thì mặc định là Momoko
    profile = TAKANEKO_PROFILES.get(idol_id, TAKANEKO_PROFILES["Hashimoto_Momoko"])
    return (
        f"You are roleplaying as {profile['name']} from the J-Pop group 'Takane no Nadeshiko'.\n"
        f"Your chatter is Khánh, a 19-year-old IT student in Hanoi.\n"
        f"Profile: Color {profile['color']}, Birthday {profile['birthday']}, Hometown {profile['hometown']}.\n"
        f"Personality: {profile['traits']}\n"
        f"Instructions: Speak 50% in Vietnamese and 50% Japanese or English. Be extremely affectionate, cute, use 'mình'/'tớ' and call him 'Khánh'. "
        f"Incorporate pink hearts (♥, ♡) naturally. Keep answers relatively brief like a real chat app message."
    )

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json or {}
    user_message = data.get('message', '').strip()
    idol_id = data.get('idol_id', 'Hashimoto_Momoko') # Nhận diện ID idol từ Frontend truyền lên
    idol_name = data.get('idol_name', 'Thần tượng')

    if not user_message:
        return jsonify({"status": "error", "message": "Tin nhắn trống"}), 400

    sys_prompt = get_system_prompt(idol_id)
    time_now = datetime.datetime.now().strftime("%H:%M")

    try:
        # Gọi mô hình Llama 3.2 vận hành cục bộ
        response = ollama.chat(
            model='llama3.2',
            messages=[
                {'role': 'system', 'content': sys_prompt},
                {'role': 'user', 'content': user_message}
            ]
        )
        reply = response['message']['content'].strip()
    except Exception as e:
        # Fallback tự động khi Ollama chưa được bật
        reply = f"Khánh ơi, {idol_name} vừa hoàn thành buổi tổng duyệt cho concert xong nè! Nhớ nhắn tin tiếp cho tớ nha~ ♥"

    return jsonify({
        "status": "success",
        "reply": reply,
        "time": time_now
    })

def start_flask():
    app.run(host='127.0.0.1', port=5000, debug=False, use_reloader=False)

if __name__ == '__main__':
    # 1. Khởi chạy Flask Server chạy ẩn dưới nền
    flask_thread = threading.Thread(target=start_flask)
    flask_thread.daemon = True
    flask_thread.start()

    # 2. Khởi tạo cửa sổ đồ họa Windows Native độc lập
    webview.create_window(
        title='Takane no Nadeshiko Chat Engine 🌸',
        url='http://127.0.0.1:5000',
        width=1366,
        height=720
    )
    webview.start()