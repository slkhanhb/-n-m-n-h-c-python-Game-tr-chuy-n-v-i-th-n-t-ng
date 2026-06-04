# app.py
from flask import Flask, render_template, request, jsonify
import ollama
import datetime

app = Flask(__name__, template_folder='.')

# Thông tin bản sắc của Momoko từ ai_engine của bạn
MOMOKO_PROFILE = {
    "name": "Hashimoto Momoko",
    "traits": "Sôi nổi, hoạt bát, trung thực. Luôn tràn đầy năng lượng và có khả năng làm bừng sáng bầu không khí của nhóm.",
    "color": "Hồng đậm",
    "birthday": "28/06/2003",
    "hometown": "Yamaguchi",
    "message": "Mình sẽ cố gắng hết sức để đem đến thật nhiều hạnh phúc cho mọi người!"
}

def get_momoko_system_prompt():
    return (
        f"You are roleplaying as {MOMOKO_PROFILE['name']} from the J-Pop group 'Takane no Nadeshiko'.\n"
        f"Your chatter is Khánh, a 19-year-old IT student in Hanoi.\n"
        f"Profile: Color {MOMOKO_PROFILE['color']}, Birthday {MOMOKO_PROFILE['birthday']}, Hometown {MOMOKO_PROFILE['hometown']}.\n"
        f"Personality: {MOMOKO_PROFILE['traits']}\n"
        f"Instructions: Speak 100% in Vietnamese. Be extremely affectionate, cute, use 'mình'/'tớ' and call him 'Khánh'. "
        f"Incorporate pink hearts (♥, ♡) naturally. Keep answers relatively brief like a real chat app message."
    )

@app.route('/')
def home():
    # Trả về giao diện HTML
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message', '').strip()
    if not user_message:
        return jsonify({"status": "error", "message": "Tin nhắn trống"}), 400

    sys_prompt = get_momoko_system_prompt()
    time_now = datetime.datetime.now().strftime("%H:%M")

    try:
        # Kết nối với mô hình Ollama Llama 3.2 chạy local
        response = ollama.chat(
            model='llama3.2',
            messages=[
                {'role': 'system', 'content': sys_prompt},
                {'role': 'user', 'content': user_message}
            ]
        )
        reply = response['message']['content'].strip()
    except Exception as e:
        # Fallback giống file cũ khi lỗi kết nối
        reply = "Khánh ơi, tớ vừa hoàn thành buổi tổng duyệt cho concert xong nè! Nhớ nhắn tin tiếp cho tớ nha~ ♥"

    return jsonify({
        "status": "success",
        "reply": reply,
        "time": time_now
    })

if __name__ == '__main__':
    # Chạy ứng dụng tại chế độ Debug
    app.run(debug=True, port=5000)