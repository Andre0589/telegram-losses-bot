import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime
import os

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

def format_text(text):
    """Виділяє жирним заголовки розділів згідно зі скріншотом"""
    # Список фраз для жирного виділення
    keywords = [
        "Особовий склад:", 
        "Бронетехніка і автомобілі:", 
        "Артилерія і ППО:", 
        "Повітряні цілі:", 
        "Флот:"
    ]
    
    formatted_text = text
    for word in keywords:
        # Додаємо зірочки для Markdown
        if word in formatted_text:
            formatted_text = formatted_text.replace(word, f"**{word}**")
            
    return formatted_text

def fetch_losses():
    now = datetime.now()
    day = now.day
    month_name = get_ukr_month_name(now.month)
    year = now.year
    
    url = f"https://mod.gov.ua/news/bojovi-vtrati-voroga-na-{day}-{month_name}-{year}-roku"
    
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            # Витягуємо текст новини
            content = soup.find('div', class_='news-content') or soup.find('article')
            if content:
                raw_text = content.get_text(separator='\n', strip=True)
                # Застосовуємо форматування
                return format_text(raw_text)
        return None
    except Exception as e:
        print(f"Помилка: {e}")
        return None

def send_telegram(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": f"📊 *ОФІЦІЙНО: ВТРАТИ ВОРОГА*\n\n{text}",
        "parse_mode": "Markdown" # Активує жирний шрифт
    }
    try:
        r = requests.post(url, json=payload)
        return r.status_code == 200
    except Exception as e:
        print(f"Помилка відправки: {e}")
        return False

def main():
    max_attempts = 24 
    attempt = 0
    
    while attempt < max_attempts:
        news_text = fetch_losses()
        
        if news_text:
            if send_telegram(news_text):
                print("Новину відправлено з новим виділенням!")
                return 
        
        attempt += 1
        time.sleep(900)

if __name__ == "__main__":
    main()
