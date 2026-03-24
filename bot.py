import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime

# Налаштування
TOKEN = "8389604591:AAFv_X9LSdIt7EX-X0CmOiixDYhQN50Tioc"
CHAT_ID = "1886501853"
BASE_URL = "https://mod.gov.ua/news"

def send_message(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    try:
        requests.post(url, data={"chat_id": CHAT_ID, "text": text}, timeout=10)
    except Exception as e:
        print(f"Помилка відправки: {e}")

def get_latest_post():
    try:
        # Отримуємо число сьогоднішнього дня (наприклад, '24')
        day_now = datetime.now().strftime("%d")
        # Якщо число починається з нуля (01, 02...), прибираємо його для пошуку в URL
        day_now_clean = day_now.lstrip('0') 

        r = requests.get(BASE_URL, timeout=15)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        
        for link in soup.find_all("a"):
            href = link.get("href", "")
            # Перевіряємо, чи це новина про втрати І чи є там сьогоднішнє число
            if "bojovi-vtrati-voroga" in href and f"-{day_now_clean}-" in href:
                return "https://mod.gov.ua" + href
    except Exception as e:
        print(f"Помилка парсингу: {e}")
    return None

def parse_losses(url):
    try:
        r = requests.get(url, timeout=15)
        soup = BeautifulSoup(r.text, "html.parser")
        text = soup.get_text("\n")
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        
        result = []
        start = False
        for line in lines:
            if "втратила" in line.lower():
                result.append("📊 " + line)
                start = True
                continue
            if start:
                if "—" in line or "-" in line:
                    clean = line.replace("–", "-").replace("—", "-")
                    parts = clean.split("-")
                    if len(parts) >= 2:
                        name = parts[0].strip()
                        value = parts[1].strip().replace('(+0)', '').strip()
                        result.append(f"• {name} — {value}")
                if len(result) >= 15: break
        return "\n".join(result)
    except:
        return "Не вдалося отримати деталі втрат."

def main():
    print(f"Моніторинг запущено. Шукаємо новину за {datetime.now().strftime('%d-%m-%Y')}...")

    # 12 спроб по 15 хвилин (разом 3 години)
    for attempt in range(12):
        latest_link = get_latest_post()
        
        if latest_link:
            print(f"Знайдено сьогоднішню новину: {latest_link}")
            text = parse_losses(latest_link)
            send_message(f"🔥 Втрати ворога (оновлено):\n\n" + text)
            return # Успіх, виходимо
        
        print(f"Спроба {attempt + 1}: Новини ще немає на сайті. Чекаємо 15 хв...")
        time.sleep(900)

    print("Час очікування вичерпано. Сьогоднішньої новини не знайдено.")

if __name__ == "__main__":
    main()
