from bs4 import BeautifulSoup
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
caminho_html = BASE_DIR / "data" / "input" / "exemplo.html"

with open(caminho_html, "r", encoding="utf-8") as file:
    soup = BeautifulSoup(file, "html.parser")
    
articles = soup.find_all("article")

data = []

for article in articles:
    section = article.find_parent("section").find("h2").text.strip()

    title = article.find("h3").text.strip()
    content = article.find("p").text.strip()

    data.append({
        "Categoria": section,
        "Título": title,
        "Descrição": content
    })

df = pd.DataFrame(data)
print(df)
