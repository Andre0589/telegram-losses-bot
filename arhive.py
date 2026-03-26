import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime, timedelta
import os

# Дані для доступу (беруться з секретів GitHub)
TOKEN = os.getenv("API_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def get_ukr_month_name(month):
    months = {
        1: "sichnya", 2: "lyutogo", 3: "bereznya", 4: "kvitnya",
        5: "travnya", 6: "chervnya", 7: "lypnya", 8: "serpnya",
        9: "veresnya", 10: "zhovtnya", 11: "lystopada", 12: "grudnya"
    }
    return months.get(month)

def fetch_image_for_date(target_date):
    day = target_date.day
    month_name = get_ukr_month_name(target_date.month)
    year = target_date.year
    
    url = f"https://mod.gov.ua/news/bojovi-vtrati-voroga-na-{day}-{month_name}-{year}-roku"
    
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        response = requests.get(url, headers=headers, timeout=10)
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
    except Exception:
        return None

def send_to_telegram(image_url, date_str):
    url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"
    # Підпис ідентичний до щоденного бота
    caption_text = f"📊 Офіційна інфографіка втрат ворога на {date_str}"
    
    payload = {
        "chat_id": CHAT_ID,
        "photo": image_url,
        "caption": caption_text
    }
    try:
        requests.post(url, json=payload, timeout=20)
    except Exception as e:
        print(f"Помилка відправки за {date_str}: {e}")

def main():
    # Початкова дата: 1 січня 2026
    current_date = datetime(2026, 1, 1)
    # Кінцева дата: сьогодні
    end_date = datetime.now()

    print(f"--- Починаю збір архіву з 01.01.2026 по {end_date.strftime('%d.%m.%Y')} ---")

    while current_date <= end_date:
        date_str = current_date.strftime("%d.%m.%Y")
        img = fetch_image_for_date(current_date)
        
        if img:
            print(f"[{date_str}] Знайдено, надсилаю...")
            send_to_telegram(img, date_str)
            # Затримка 3 секунди, щоб Telegram не заблокував за спам (Flood Limit)
            time.sleep(3) 
        else:
            print(f"[{date_str}] Новини не знайдено на сайті.")
        
        current_date += timedelta(days=1)

    print("--- Збір архіву успішно завершено! ---")

if __name__ == "__main__":
    main()
