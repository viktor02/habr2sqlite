from bs4 import BeautifulSoup
import sqlite3
import requests
from datetime import datetime

def main(min, max):
    conn = sqlite3.connect('habr.db')
    c = conn.cursor()
    c.execute('PRAGMA encoding = "UTF-8"')
    c.execute("CREATE TABLE IF NOT EXISTS habr(id INT, author VARCHAR(255), title VARCHAR(255), content  TEXT, tags TEXT)")

    start_time = datetime.now()
    c.execute("begin")
    for i in range(min, max):
        url = "https://m.habr.com/post/{}".format(i)
        try:
            r = requests.get(url)
        except:
            with open("req_errors.txt") as file:
                file.write(i)
            continue
        if(r.status_code != 200):
            print("{} - {}".format(i, r.status_code))
            continue

        html_doc = r.text
        soup = BeautifulSoup(html_doc, 'html.parser')

        try:
            author = soup.find(class_="tm-user-info__username").get_text()
            content = soup.find(id="post-content-body")
            content = str(content)
            title = soup.find(class_="tm-article-title__text").get_text()
            tags = soup.find(class_="tm-article__tags").get_text()
            tags = tags[5:]
        except:
            author,title,tags = "Error", "Error {}".format(r.status_code), "Error"
            content = "При парсинге этой странице произошла ошибка."

        c.execute('INSERT INTO habr VALUES (?, ?, ?, ?, ?)', (i, author, title, content, tags))
        print(i)
    c.execute("commit")
    print(datetime.now() - start_time)

main(1, 490406)