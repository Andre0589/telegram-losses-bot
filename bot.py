import requests
from bs4 import BeautifulSoup
import os
from datetime import datetime

# Дані для доступу
TOKEN = os.getenv("API_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
HISTORY_FILE = "last_news.txt"

def get_month_variants(month_num):
    """Повертає список можливих варіантів написання місяця латиницею"""
    variants = {
        1: ["sichnia", "sichnya"],
        2: ["liutoho", "lyutogo"],
        3: ["bereznia", "bereznya"],
        4: ["kvitnia", "kvitnya"],
        5: ["travnia", "travnya"],
        6: ["chervnia", "chervnya"],
        7: ["lypnia", "lypnya"],
        8: ["serpnia", "serpnya"],
        9: ["veresnia", "veresnya"],
        10: ["zhovtnia", "zhovtnya"],
        11: ["lystopada"],
        12: ["hrudnia", "grudnya"]
    }
    return variants.get(month_num, [])

def fetch_image_url():
    now = datetime.now()
    day = now.day
    year = now.year
    
    # Варіанти написання основної частини посилання
    slug_variants = [
        "boiovi-vtraty-voroha",  # Новий варіант (квітень 2026)
        "bojovi-vtrati-voroga"   # Старий варіант
    ]
    
    month_variants = get_month_variants(now.month)
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

    # Перебираємо всі комбінації
    for slug in slug_variants:
        for m_name in month_variants:
            url = f"https://mod.gov.ua/news/{slug}-na-{day}-{m_name}-{year}-roku"
            print(f"Пробую посилання: {url}")
            
            try:
                response = requests.get(url, headers=headers, timeout=10)
                if response.status_code == 200:
                    print(f"Знайдено робоче посилання! Скрапимо...")
                    soup = BeautifulSoup(response.text, 'html.parser')
                    content_div = soup.find('div', class_='news-content') or soup.find('article')
                    
                    if content_div:
                        img_tag = content_div.find('img')
                        if img_tag and img_tag.get('src'):
                            image_url = img_tag.get('src')
                            if not image_url.startswith('http'):
                                image_url = "https://mod.gov.ua" + image_url
                            return image_url
            except Exception as e:
                print(f"Помилка при перевірці {url}: {e}")
                continue
                
    return None

def send_photo_only(image_url):
    now_date = datetime.now().strftime("%d.%m.%Y")
    url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"
    caption_text = f"📊 Офіційна інфографіка втрат ворога на {now_date}"
    
    payload = {"chat_id": CHAT_ID, "photo": image_url, "caption": caption_text}
    try:
        r = requests.post(url, json=payload)
        return r.status_code == 200
    except:
        return False

def main():
    today = datetime.now().date().isoformat()

    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            if f.read().strip() == today:
                print(f"Сьогодні ({today}) вже відправлено. Вихід.")
                return

    image_url = fetch_image_url()
    
    if image_url:
        if send_photo_only(image_url):
            print("Успіх!")
            with open(HISTORY_FILE, "w") as f:
                f.write(today)
    else:
        print("Жоден з варіантів посилань не спрацював. Можливо, новину ще не опублікували.")

if __name__ == "__main__":
    main()
    
