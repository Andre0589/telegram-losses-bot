import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime
import os
import re

# Ваші дані для доступу
TOKEN = "8389604591:AAFv_X9LSdIt7EX-X0CmOiixDYhQN50Tioc"
CHAT_ID = "1886501853"

def get_ukr_month_name(month):
    months = {
        1: "sichnya", 2: "lyutogo", 3: "bereznya", 4: "kvitnya",
        5: "travnya", 6: "chervnya", 7: "lypnya", 8: "serpnya",
        9: "veresnya", 10: "zhovtnya", 11: "lystopada", 12: "grudnya"
    }
    return months.get(month)

def format_text_html(text):
    """Виділяє заголовки жирним через HTML-теги <b>"""
    keywords = [
        "Особовий склад:", 
        "Бронетехніка і автомобілі:", 
        "Артилерія і ППО:", 
        "Повітряні цілі:", 
        "Флот:"
    ]
    
    formatted_text = text
    for word in keywords:
        # Регістронезалежна заміна на HTML-тег <b>
        pattern = re.compile(re.escape(word), re.IGNORECASE)
        formatted_text = pattern.sub(f"<b>{word}</b>", formatted_text)
            
    return formatted_text

def fetch_losses():
    now = datetime.now()
    day = now.day
    month_name = get_ukr_month_name(now.month)
    year = now.year
    
    url = f"https://mod.gov.ua/news/bojovi-vtrati-voroga-na-{day}-{month_name}-{year}-roku"
    print(f"Запит до сайту: {url}")
    
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            # Витягуємо контент
            content = soup.find('div', class_='news-content') or soup.find('article')
            if content:
                raw_text = content.get_text(separator='\n', strip=True)
                return format_text_html(raw_text)
        return None
    except Exception as e:
        print(f"Помилка зчитування: {e}")
        return None

def send_telegram(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    # Використовуємо <b> для головного заголовка
    payload = {
        "chat_id": CHAT_ID,
        "text": f"<b>📊 ОФІЦІЙНО: ВТРАТИ ВОРОГА</b>\n\n{text}",
        "parse_mode": "HTML" # Змінено з Markdown на HTML для надійності
    }
    try:
        r = requests.post(url, json=payload)
        if r.status_code != 200:
            print(f"Telegram помилка: {r.text}")
        return r.status_code == 200
    except Exception as e:
        print(f"Помилка відправки: {e}")
        return False

def main():
    print("Бот запущений (HTML mode). Перевіряю новину...")
    max_attempts = 24 
    attempt = 0
    
    while attempt < max_attempts:
        news_text = fetch_losses()
        
        if news_text:
            if send_telegram(news_text):
                print("Успішно відправлено з HTML-форматуванням!")
                return 
        
        attempt += 1
        if attempt < max_attempts:
            print(f"Спроба {attempt}: Новина ще не оновлена. Чекаю 15 хв...")
            time.sleep(900)

if __name__ == "__main__":
    main()
