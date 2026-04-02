import requests
from bs4 import BeautifulSoup
import os
import sys
from datetime import datetime

# Дані для доступу 
TOKEN = os.getenv("API_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
HISTORY_FILE = "last_news.txt"

def get_ukr_month_name(month):
    months = {
        1: "sichnya", 2: "lyutogo", 3: "bereznya", 4: "kvitnia",
        5: "travnya", 6: "chervnya", 7: "lypnya", 8: "serpnya",
        9: "veresnya", 10: "zhovtnya", 11: "lystopada", 12: "grudnya"
    }
    return months.get(month)

def fetch_image_url():
    now = datetime.now()
    day = now.day
    month_name = get_ukr_month_name(now.month)
    year = now.year
    
    url = f"https://mod.gov.ua/news/bojovi-vtrati-voroga-na-{day}-{month_name}-{year}-roku"
    print(f"Перевіряю сайт: {url}")
    
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            content_div = soup.find('div', class_='news-content') or soup.find('article')
            
            if content_div:
                img_tag = content_div.find('img')
                if img_tag and img_tag.get('src'):
                    image_url = img_tag.get('src')
                    if not image_url.startswith('http'):
                        image_url = "https://mod.gov.ua" + image_url
                    return image_url
        return None
    except Exception as e:
        print(f"Помилка при пошуку фото: {e}")
        return None

def send_photo_only(image_url):
    now = datetime.now().strftime("%d.%m.%Y")
    url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"
    # Оновлений текст підпису з датою
    caption_text = f"📊 Офіційна інфографіка втрат ворога на {now}"
    
    payload = {
        "chat_id": CHAT_ID,
        "photo": image_url,
        "caption": caption_text
    }
    try:
        r = requests.post(url, json=payload)
        return r.status_code == 200
    except Exception as e:
        print(f"Помилка відправки в Telegram: {e}")
        return False

def main():
    today = datetime.now().date().isoformat()

    # Перевірка: чи не надсилали ми вже сьогодні?
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            if f.read().strip() == today:
                print(f"Сьогодні ({today}) новина вже була надіслана. Вихід.")
                return

    image_url = fetch_image_url()
    
    if image_url:
        if send_photo_only(image_url):
            print("Фото успішно надіслано!")
            # Записуємо дату успішної відправки
            with open(HISTORY_FILE, "w") as f:
                f.write(today)
        else:
            print("Помилка відправки фото.")
    else:
        print("Картинки ще немає на сайті. Спробуємо пізніше.")

if __name__ == "__main__":
    main()
