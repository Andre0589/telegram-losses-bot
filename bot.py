import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import time

TOKEN = "8389604591:AAFv_X9LSdIt7EX-X0CmOiixDYhQN50Tioc"
CHAT_ID = "1886501853"

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept-Language": "uk-UA,uk;q=0.9,en-US;q=0.8,en;q=0.7"
}

MONTHS = {
    1: "sichnya", 2: "lyutogo", 3: "bereznya", 4: "kvitnya",
    5: "travnya", 6: "chervnya", 7: "lypnya", 8: "serpnya",
    9: "veresnya", 10: "zhovtnya", 11: "lystopada", 12: "hrudnya"
}


def send_message(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": text})


def get_today_url():
    today = datetime.now() + timedelta(hours=0)  # часова зона Київ +2
    day = today.day
    month = MONTHS[today.month]
    year = today.year

    url = f"https://mod.gov.ua/news/bojovi-vtrati-voroga-na-{day}-{month}-{year}-roku"
    return url


def check_news(url):
    r = requests.get(url, headers=HEADERS)
    if r.status_code == 200:
        return True
    return False


def parse_losses(url):
    r = requests.get(url, headers=HEADERS)
    if r.status_code != 200:
        return None

    soup = BeautifulSoup(r.text, "html.parser")
    text = soup.get_text("\n")
    lines = [line.strip() for line in text.split("\n") if line.strip()]

    result = []
    start = False

    for line in lines:
        lower = line.lower()
        if "втрат" in lower:
            result.append("📊 " + line)
            start = True
            continue

        if start:
            clean = line.replace("–", "-").replace("—", "-").replace("−", "-")
            if "-" in clean:
                parts = clean.split("-")
                if len(parts) >= 2:
                    name = parts[0].strip()
                    value = parts[1].strip()
                    if "(+0)" in value:
                        value = value.replace("(+0)", "").strip()
                    result.append(f"• {name} — {value}")

        if len(result) >= 20:
            break

    return "\n".join(result)


def wait_until_5am():
    now = datetime.now()
    next_run = now.replace(hour=5, minute=0, second=0, microsecond=0)
    if now >= next_run:
        next_run += timedelta(days=1)
    wait_seconds = (next_run - now).total_seconds()
    print(f"Чекаємо до 5:00 наступного ранку: {wait_seconds/3600:.2f} годин")
    time.sleep(wait_seconds)


def main():
    while True:
        wait_until_5am()
        print("Старт перевірки новини про втрати ворога")

        news_found = False
        url = get_today_url()

        while not news_found:
            print(f"Перевіряємо URL: {url}")
            if check_news(url):
                print("Новина знайдена! Парсимо...")
                losses_text = parse_losses(url)
                if losses_text:
                    send_message("🔥 Втрати ворога:\n\n" + losses_text)
                else:
                    send_message("❌ Новина з’явилась, але не вдалося розпарсити втрати")
                news_found = True
            else:
                print("Новина ще не опублікована. Чекаємо 15 хвилин...")
                time.sleep(15 * 60)  # 15 хвилин

        print("Повідомлення відправлено. Чекаємо до 5:00 наступного дня...")


if __name__ == "__main__":
    main()
