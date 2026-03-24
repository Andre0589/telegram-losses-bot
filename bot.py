import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime
import os

# Дані для доступу 
TOKEN = os.getenv("API_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def get_ukr_month_name(month):
    months = {
        1: "sichnya", 2: "lyutogo", 3: "bereznya", 4: "kvitnya",
        5: "travnya", 6: "chervnya", 7: "lypnya", 8: "serpnya",
        9: "veresnya", 10: "zhovtnya", 11: "lystopada", 12: "grudnya"
    }
    return months.get(month)

def fetch_image_url():
    now = datetime.now()
    day = now.day
    month_name = get_ukr_month_name(now.month)
    year = now.year
    
    # Формуємо URL новини
    url = f"https://mod.gov.ua/news/bojovi-vtrati-voroga-na-{day}-{month_name}-{year}-roku"
    print(f"Шукаю картинку на: {url}")
    
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            # Шукаємо блок новини, де зазвичай лежить інфографіка
            content_div = soup.find('div', class_='news-content') or soup.find('article')
            
            if content_div:
                img_tag = content_div.find('img')
                if img_tag and img_tag.get('src'):
                    image_url = img_tag.get('src')
                    # Перетворюємо відносне посилання на повне
                    if not image_url.startswith('http'):
                        image_url = "https://mod.gov.ua" + image_url
                    return image_url
        return None
    except Exception as e:
        print(f"Помилка при пошуку фото: {e}")
        return None

def send_photo_only(image_url):
    url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"
    payload = {
        "chat_id": CHAT_ID,
        "photo": image_url,
        "caption": "📊 Офіційна інфографіка втрат ворога"
    }
    try:
        r = requests.post(url, json=payload)
        return r.status_code == 200
    except Exception as e:
        print(f"Помилка відправки в Telegram: {e}")
        return False

def main():
    print("Бот запущений (Тільки Фото). Очікую новину...")
    max_attempts = 24 
    attempt = 0
    
    while attempt < max_attempts:
        image_url = fetch_image_url()
        
        if image_url:
            if send_photo_only(image_url):
                print("Фото успішно надіслано!")
                return 
        
        attempt += 1
        if attempt < max_attempts:
            print(f"Спроба {attempt}: Картинки ще немає. Чекаю 15 хв...")
            time.sleep(900)

if __name__ == "__main__":
    main()
