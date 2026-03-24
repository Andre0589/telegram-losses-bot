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
    """Робить заголовки ЖИРНИМИ ТА ПРОПИСНИМИ"""
    keywords = [
        "Особовий склад:", 
        "Бронетехніка і автомобілі:", 
        "Артилерія і ППО:", 
        "Повітряні цілі:", 
        "Флот:"
    ]
    
    formatted_text = text
    for word in keywords:
        # Шукаємо слово в будь-якому регістрі та замінюємо на ВЕЛИКІ ЛІТЕРИ + жирний
        pattern = re.compile(re.escape(word), re.IGNORECASE)
        replacement = f"<b>{word.upper()}</b>"
        formatted_text = pattern.sub(replacement, formatted_text)
            
    return formatted_text

def fetch_losses():
    now = datetime.now()
    day = now.day
    month_name = get_ukr_month_name(now.month)
    year = now.year
    
    url = f"https://mod.gov.ua/news/bojovi-vtrati-voroga-na-{day}-{month_name}-{year}-roku"
    
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            content = soup.find('div', class_='news-content') or soup.find('article')
            if content:
                raw_text = content.get_text(separator='\n', strip=True)
                return format_text_html(raw_text)
        return None
    except Exception as e:
        print(f"Помилка: {e}")
        return None

def send_telegram(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": f"<b>📊 ОФІЦІЙНО: ВТРАТИ ВОРОГА</b>\n\n{text}",
        "parse_mode": "HTML" # Використовуємо HTML для надійності
    }
    try:
        r = requests.post(url, json=payload)
        return r.status_code == 200
    except Exception as e:
        print(f"Помилка відправки: {e}")
        return False

def main():
    print("Бот запущений (UPPERCASE mode). Перевіряю...")
    max_attempts = 24 
    attempt = 0
    
    while attempt < max_attempts:
        news_text = fetch_losses()
        
        if news_text:
            if send_telegram(news_text):
                print("Готово! Повідомлення надіслано з новим стилем.")
                return 
        
        attempt += 1
        time.sleep(900)

if __name__ == "__main__":
    main()
