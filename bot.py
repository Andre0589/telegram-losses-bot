import requests
from bs4 import BeautifulSoup

TOKEN = "8389604591:AAFv_X9LSdIt7EX-X0CmOiixDYhQN50Tioc"
CHAT_ID = "1886501853"

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept-Language": "uk-UA,uk;q=0.9,en-US;q=0.8,en;q=0.7"
}


def send_message(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": text})


def get_latest_losses_url():
    url = "https://mod.gov.ua/news"
    r = requests.get(url, headers=HEADERS)

    if r.status_code != 200:
        print("Не вдалося відкрити сторінку новин")
        return None

    soup = BeautifulSoup(r.text, "html.parser")

    for a in soup.find_all("a", href=True):
        href = a["href"]

        if "vtrati-voroga" in href:
            print("Знайдено новину:", href)
            return href

    print("Новину не знайдено на сторінці")
    return None


def parse_losses(url):
    r = requests.get(url, headers=HEADERS)

    if r.status_code != 200:
        print("Помилка відкриття новини")
        return None

    soup = BeautifulSoup(r.text, "html.parser")

    text = soup.get_text("\n")
    lines = [line.strip() for line in text.split("\n") if line.strip()]

    result = []
    start = False

    for line in lines:
        if "втрат" in line.lower():
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

        if len(result) >= 15:
            break

    return "\n".join(result)


def main():
    url = get_latest_losses_url()

    if not url:
        send_message("❌ Не вдалося знайти новину про втрати")
        return

    text = parse_losses(url)

    if text:
        send_message("🔥 Втрати ворога:\n\n" + text)
    else:
        send_message("❌ Не вдалося розпарсити новину")


if __name__ == "__main__":
    main()
