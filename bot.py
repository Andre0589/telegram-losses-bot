import requests
from bs4 import BeautifulSoup
from datetime import datetime

TOKEN = "8389604591:AAFv_X9LSdIt7EX-X0CmOiixDYhQN50Tioc"
CHAT_ID = "1886501853"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


def send_message(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": text})


def get_today_url():
    today = datetime.now()

    months = {
        1: "sichnya", 2: "lyutogo", 3: "bereznya", 4: "kvitnya",
        5: "travnya", 6: "chervnya", 7: "lypnya", 8: "serpnya",
        9: "veresnya", 10: "zhovtnya", 11: "lystopada", 12: "hrudnya"
    }

    day = today.day
    month = months[today.month]
    year = today.year

    return f"https://mod.gov.ua/news/bojovi-vtrati-voroga-na-{day}-{month}-{year}-roku"


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
    url = get_today_url()
    text = parse_losses(url)

    if text:
        send_message("🔥 Втрати ворога:\n\n" + text)
    else:
        send_message("❌ Сьогоднішня новина ще не опублікована")


if __name__ == "__main__":
    main()
