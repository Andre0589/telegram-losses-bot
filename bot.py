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
        r = requests.get(BASE_URL, timeout=15)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        for link in soup.find_all("a"):
            href = link.get("href", "")
            # Шукаємо саме новину про втрати
            if "bojovi-vtrati-voroga" in href:
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
                        result.append(f"• {parts[0].strip()} — {parts[1].strip().replace('(+0)', '').strip()}")
                if len(result) >= 15: break
        return "\n".join(result)
    except:
        return "Не вдалося розпарсити текст новини."

def main():
    # Отримуємо сьогоднішню дату у форматі посилання (напр. 24-03-2026)
    # Перевірте формат на сайті, зазвичай там dd-mm-yyyy або yyyy-mm-dd
    today_str = datetime.now().strftime("%d-%m-%Y") 
    
    print(f"Починаємо моніторинг. Шукаємо дату: {today_str}")

    # Цикл: 12 перевірок по 15 хвилин = 3 години очікування
    for attempt in range(12):
        latest_link = get_latest_post()
        
        if latest_link and today_str in latest_link:
            print(f"Знайдено нову новину: {latest_link}")
            text = parse_losses(latest_link)
            send_message(f"🔥 Втрати ворога за {today_str}:\n\n" + text)
            return # ВИХІД: Новина знайдена і надіслана
        
        print(f"Спроба {attempt + 1}: Новини ще немає. Чекаємо 15 хв...")
        time.sleep(900) # 900 секунд = 15 хвилин

    print("Час очікування вичерпано. Сьогоднішньої новини поки немає.")

if __name__ == "__main__":
    main()
