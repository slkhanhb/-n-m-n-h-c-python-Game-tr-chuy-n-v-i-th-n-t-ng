# api_services.py
import requests
import threading
from config import WEATHER_API_KEY, VIRUSTOTAL_API_KEY

class BackgroundAPI:
    def __init__(self):
        self.weather_data = None
        self.vt_result = None

    def fetch_weather(self, city="Hanoi"):
        def task():
            url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
            try:
                res = requests.get(url).json()
                self.weather_data = f"{res['main']['temp']}°C - {res['weather'][0]['description']}"
            except:
                self.weather_data = "Lỗi thời tiết"
        threading.Thread(target=task, daemon=True).start()

    def scan_file_vt(self, file_path):
        def task():
            # Tích hợp logic upload file từ file Virus total.py cũ của bạn vào đây
            # Đảm bảo gán kết quả vào self.vt_result
            pass
        threading.Thread(target=task, daemon=True).start()