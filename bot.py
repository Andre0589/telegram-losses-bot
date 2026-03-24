import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime
import os

# Ваші актуальні дані для перевірки
TOKEN = "8389604591:AAFv_X9LSdIt7EX-X0CmOiixDYhQN50Tioc"
CHAT_ID = "1886501853"

def get_ukr_month_name(month):
    months = {
        1: "sichnya", 2: "lyutogo", 3: "bereznya", 4: "kvitnya",
        5: "travnya", 6: "chervnya", 7: "lypnya", 8: "serpnya",
        9: "veresnya", 10: "zhovtnya", 11: "lystopada", 12: "grudnya"
    }
    return months.get(month)

def fetch_losses():
    now = datetime.now()
    day = now.day
    month_name = get_ukr_month_name(now.month)
    year = now.year
    
    # Формуємо посилання: https://mod.gov.ua/news/bojovi-vtrati-voroga-na-24-bereznya-2026-roku
    url = f"https://mod.gov.ua/news/bojovi-vtrati-voroga-na-{day}-{month_name}-{year}-roku"
    print(f"Перевіряю адресу: {url}")
    
    try:
        # Додаємо User-Agent, щоб сайт не блокував запити від бота
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            # Шукаємо статтю або основний блок новин
            content = soup.find('div', class_='news-content') or soup.find('article')
            if content:
                # Очищаємо текст від зайвих пробілів та скриптів
                return content.get_text(separator='\n', strip=True)
        return None
    except Exception as e:
        print(f"Помилка при запиті до сайту: {e}")
        return None

def send_telegram(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    # Обрізаємо текст, якщо він занадто довгий для одного повідомлення Telegram
    clean_text = text[:4000]
    payload = {
        "chat_id": CHAT_ID,
        "text": f"📊 *ОФІЦІЙНО: ВТРАТИ ВОРОГА*\n\n{clean_text}",
        "parse_mode": "Markdown"
    }
    try:
        r = requests.post(url, json=payload)
        return r.status_code == 200
    except Exception as e:
        print(f"Помилка відправки в Telegram: {e}")
        return False

def main():
    print("Бот запущений. Очікую публікацію новини...")
    
    # Спроби: кожні 15 хвилин протягом 6 годин (24 спроби)
    max_attempts = 24 
    attempt = 0
    
    while attempt < max_attempts:
        news_text = fetch_losses()
        
        if news_text:
            if send_telegram(news_text):
                print("Успіх! Новину відправлено.")
                return # Завершуємо роботу до наступного дня
            else:
                print("Помилка відправки в Telegram, спробую знову через 15 хв.")
        
        attempt += 1
        if attempt < max_attempts:
            print(f"Спроба {attempt}: Новини ще немає. Наступна перевірка через 15 хвилин...")
            time.sleep(900) # 15 хвилин

if __name__ == "__main__":
    main()
