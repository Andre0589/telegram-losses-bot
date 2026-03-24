import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time

# =================== Налаштування ===================
TOKEN = "8389604591:AAFv_X9LSdIt7EX-X0CmOiixDYhQN50Tioc"
CHAT_ID = "1886501853"

HEADERS = {"User-Agent": "Mozilla/5.0"}

MONTHS = {
    1: "sichnya", 2: "lyutogo", 3: "bereznya", 4: "kvitnya",
    5: "travnya", 6: "chervnya", 7: "lypnya", 8: "serpnya",
    9: "veresnya", 10: "zhovtnya", 11: "lystopada", 12: "hrudnya"
}

BASE_URL = "https://mod.gov.ua/news"

# =================== Функції ===================

def send_message(text):
    """Відправка повідомлення в Telegram"""
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": text})

def get_today_url():
    """Формує URL новини за сьогоднішньою датою"""
    today = datetime.now()
    day = today.day
    month = MONTHS[today.month]
    year = today.year
    # Формуємо URL сторінки за шаблоном сайту МО
    return f"{BASE_URL}/bojovi-vtrati-voroga-na-{day}-{month}-{year}-roku"

def check_news(url):
    """Перевіряє, чи сторінка існує (HTTP 200)"""
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        return r.status_code == 200
    except requests.RequestException:
        return False

def parse_losses(url):
    """Парсить текст новини з конкретної сторінки"""
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        if r.status_code != 200:
            return None

        soup = BeautifulSoup(r.text, "html.parser")

        # Шукаємо заголовок з "Бойові втрати ворога"
        header_tag = soup.find(lambda tag: tag.name in ["h1", "h2"] and "Бойові втрати ворога" in tag.get_text())
        if not header_tag:
            return None

        # Беремо текст усіх <p> і <li> після заголовка до наступного <h1>/<h2>
        result_lines = []
        for sibling in header_tag.find_next_siblings():
            if sibling.name in ["h1", "h2"]:
                break
            if sibling.name in ["p", "li"]:
                text = sibling.get_text(strip=True)
                if text:
                    result_lines.append(text)

        # Якщо нічого не знайшли, пробуємо весь блок статті
        if not result_lines:
            article = soup.find("div", class_="news-detail")
            if article:
                result_lines = [p.get_text(strip=True) for p in article.find_all(["p", "li"]) if p.get_text(strip=True)]

        return "\n".join(result_lines) if result_lines else None

    except requests.RequestException:
        return None

# =================== Головна функція ===================

def main():
    url = get_today_url()
    print(f"Перевірка новини за URL: {url}")

    while True:
        if check_news(url):
            text = parse_losses(url)
            if text:
                send_message(f"🔥 Втрати ворога на сьогодні ({datetime.now().strftime('%d.%m.%Y')}):\n\n{text}")
                print("Новина відправлена у Telegram!")
                break
            else:
                print("Сторінка доступна, але не вдалося розпарсити текст. Спробуємо знову через 15 хв.")
        else:
            print("Сьогоднішня новина ще не опублікована. Чекаємо 15 хв.")

        time.sleep(900)  # 15 хвилин

if __name__ == "__main__":
    main()
