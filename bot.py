import requests
from bs4 import BeautifulSoup
import re

TOKEN = "8389604591:AAFv_X9LSdIt7EX-X0CmOiixDYhQN50Tioc"
CHAT_ID = "1886501853"

BASE_URL = "https://mod.gov.ua/news"


def send_message(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": text})


def get_today_post():
    r = requests.get(BASE_URL)
    html = r.text

    matches = re.findall(r'/news/bojovi-vtrati-voroga[^"]+', html)

    if matches:
        return "https://mod.gov.ua" + matches[0]

    return None


def parse_losses(url):
    r = requests.get(url)
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
                    value = parts[1].strip()

                    if "(+0)" in value:
                        value = value.replace("(+0)", "").strip()

                    result.append(f"• {name} — {value}")

            if len(result) >= 15:
                break

    return "\n".join(result)


def main():
    latest = get_today_post()

    if latest:
        text = parse_losses(latest)
        send_message("🔥 Втрати ворога:\n\n" + text)
    else:
        send_message("❌ Новину не знайдено")


if __name__ == "__main__":
    main()
