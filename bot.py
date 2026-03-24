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
    return f"https://mod.gov.ua/news/bojovi-vtrati-voroga-na-{day}-{month}-{year}-roku"

def check_news(url):
    """Перевіряє, чи сторінка існує (HTTP 200)"""
    r = requests.get(url, headers=HEADERS)
    return r.status_code == 200

def parse_losses(url):
    """Парсить текст новини з конкретної сторінки"""
    r = requests.get(url, headers=HEADERS)
    if r.status_code != 200:
        return None

    soup = BeautifulSoup(r.text, "html.parser")

    # Шукаємо заголовок новини
    today = datetime.now()
    day = today.day
    month_name = MONTHS[today.month]
    year = today.year
    target_header = f"Бойові втрати ворога на {day} {month_name} {year} року"

    header_tag = soup.find(lambda tag: tag.name in ["h1", "h2"] and target_header in tag.get_text())
    if not header_tag:
        return None

    # Беремо всі наступні теги <p> і <ul><li> після заголовка до наступного заголовка
    result_lines = []
    for sibling in header_tag.find_next_siblings():
        if sibling.name in ["h1", "h2"]:
            break
        text = sibling.get_text(strip=True)
        if text:
            result_lines.append(text)

    return "\n".join(result_lines)

# =================== Головна функція ===================

def main():
    url = get_today_url()
    if check_news(url):
        text = parse_losses(url)
        if text:
            send_message("🔥 Втрати ворога:\n\n" + text)
        else:
            send_message("❌ Не вдалося розпарсити текст новини")
    else:
        send_message("❌ Сьогоднішня новина ще не опублікована")

if __name__ == "__main__":
    main()
