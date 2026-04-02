import requests
from bs4 import BeautifulSoup
import os
import sys
from datetime import datetime

# Дані для доступу (беруться з Secrets вашого репозиторію)
TOKEN = os.getenv("API_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
HISTORY_FILE = "last_news.txt"

def get_ukr_month_name(month):
    """
    Оновлена транслітерація місяців згідно з новим форматом сайту mod.gov.ua
    (Використовується 'ia' замість 'ya' та 'h' замість 'g')
    """
    months = {
        1: "sichnia", 2: "liutoho", 3: "bereznia", 4: "kvitnia",
        5: "travnia", 6: "chervnia", 7: "lypnia", 8: "serpnia",
        9: "veresnia", 10: "zhovtnia", 11: "lystopada", 12: "hrudnia"
    }
    return months.get(month)

def fetch_image_url():
    now = datetime.now()
    day = now.day
    month_name = get_ukr_month_name(now.month)
    year = now.year
    
    # Оновлений шаблон посилання: boiovi-vtraty-voroha (замість bojovi-vtrati-voroga)
    url = f"https://mod.gov.ua/news/boiovi-vtraty-voroha-na-{day}-{month_name}-{year}-roku"
    print(f"Перевіряю сайт: {url}")
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            # Шукаємо контейнер з новиною
            content_div = soup.find('div', class_='news-content') or soup.find('article')
            
            if content_div:
                img_tag = content_div.find('img')
                if img_tag and img_tag.get('src'):
                    image_url = img_tag.get('src')
                    # Якщо посилання відносне, додаємо домен
                    if not image_url.startswith('http'):
                        image_url = "https://mod.gov.ua" + image_url
                    return image_url
            else:
                print("Контейнер з контентом не знайдено на сторінці.")
        else:
            print(f"Сайт повернув статус: {response.status_code}")
        return None
    except Exception as e:
        print(f"Помилка при пошуку фото: {e}")
        return None

def send_photo_only(image_url):
    now_date = datetime.now().strftime("%d.%m.%Y")
    url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"
    
    caption_text = f"📊 Офіційна інфографіка втрат ворога на {now_date}"
    
    payload = {
        "chat_id": CHAT_ID,
        "photo": image_url,
        "caption": caption_text
    }
    try:
        r = requests.post(url, json=payload)
        if r.status_code != 200:
            print(f"Помилка Telegram API: {r.text}")
        return r.status_code == 200
    except Exception as e:
        print(f"Помилка відправки в Telegram: {e}")
        return False

def main():
    # Отримуємо поточну дату для перевірки дублікатів
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
            print(f"Фото успішно надіслано! URL: {image_url}")
            # Записуємо дату успішної відправки у файл
            with open(HISTORY_FILE, "w") as f:
                f.write(today)
        else:
            print("Помилка відправки фото в Telegram.")
    else:
        print("Картинку за сьогодні ще не знайдено. Перевірте посилання вище.")

if __name__ == "__main__":
    main()
    
