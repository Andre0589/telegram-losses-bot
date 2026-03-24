import requests
from bs4 import BeautifulSoup
from datetime import datetime

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
    return f"{BASE_URL}/bojovi-vtrati-voroga-na-{day}-{month}-{year}-roku"

def check_news(url):
    """Перевіряє, чи сторінка існує (HTTP 200)"""
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        return r.status_code == 200
    except requests.RequestException:
        return False

def parse_losses(url):
    """Парсить текст новини з сайту МО за сьогоднішню дату"""
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        if r.status_code != 200:
            return None

        soup = BeautifulSoup(r.text, "html.parser")

        # Беремо заголовок новини для підтвердження, що це сторінка з втратами
        header_tag = soup.find("h1", class_="news-title")
        if not header_tag or "Бойові втрати ворога" not in header_tag.get_text():
            return None

        # Беремо весь текст новини з блоку <div class="news-detail">
        article = soup.find("div", class_="news-detail")
        if not article:
            return None

        # Збираємо всі абзаци і пункти списків
        result_lines = [p.get_text(strip=True) for p in article.find_all(["p", "li"]) if p.get_text(strip=True)]

        return "\n".join(result_lines) if result_lines else None

    except requests.RequestException:
        return None

# =================== Головна функція ===================

def main():
    url = get_today_url()
    print(f"Перевірка новини за URL: {url}")

    if check_news(url):
        text = parse_losses(url)
        if text:
            send_message(f"🔥 Втрати ворога на сьогодні ({datetime.now().strftime('%d.%m.%Y')}):\n\n{text}")
            print("Новина відправлена у Telegram!")
        else:
            print("Сторінка доступна, але не вдалося розпарсити текст.")
    else:
        print("Сьогоднішня новина ще не опублікована.")

if __name__ == "__main__":
    main()
