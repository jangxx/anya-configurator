import json
from urllib.parse import urljoin
import re

from bs4 import BeautifulSoup
import requests

URL_BASE = "https://www.anyaimbiss.de/"

resp = requests.get("https://www.anyaimbiss.de/irakischer-schawarma-imbiss-koeln.html")

soup = BeautifulSoup(resp.content, "html.parser")

menu = []

for entry in soup.select(".gerichte"):
    img = entry.select_one(".bild > img")
    name = entry.select_one(".name")

    if not img or not name:
        continue

    product_name = name.find_all(string=True)[0]
    product_type = "other"

    if "Sandwich" in product_name:
        product_type = "sandwich"
    if "Teller" in product_name:
        product_type = "plate"

    content = entry.select_one(".beschreibung").find_all(string=True)[0].strip()
    price = entry.select_one(".preislabel").text.strip()

    if product_type != "other":
        contents = list(c.strip() for c in content.split(","))
        notes = ""
    else:
        contents = []
        notes = content.strip()

    prices = {}

    for p in price.split("|"):
        p = p.strip()
        p_split = list(part for part in p.split(" ") if len(part) > 0)

        if len(p_split) == 2:
            prices["base"] = float(p_split[0].replace(",", "."))
        elif len(p_split) == 3:
            prices[p_split[0]] = float(p_split[1].replace(",", "."))
        else:
            print(f"Unknown price format: {p}")

    menu.append({
        "name": product_name,
        "image": urljoin(URL_BASE, img["src"]),
        "type": product_type,
        "contents": contents,
        "notes": notes,
        "prices": prices,
    })

with open("menu.json", "w") as f:
    json.dump(menu, f, indent=2)