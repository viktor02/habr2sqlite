from bs4 import BeautifulSoup
import requests
import os, sys
import json
from multiprocessing.dummy import Pool as ThreadPool
from datetime import datetime
import logging

def worker(i):
    currentFile = "files\\{}.json".format(i)

    if os.path.isfile(currentFile):
        logging.info("{} - File exists".format(i))
        return 1

    url = "https://m.habr.com/post/{}".format(i)

    try: r = requests.get(url)
    except:
        with open("req_errors.txt") as file:
            file.write(i)
        return 2

    # Запись заблокированных запросов на сервер
    if (r.status_code == 503):
        with open("Error503.txt", "a") as write_file:
            write_file.write(str(i) + "\n")
            logging.warning('{} / 503 Error'.format(i))

    # Если поста не существует или он был скрыт
    if (r.status_code != 200):
        logging.info("{} / {} Code".format(i, r.status_code))
        return r.status_code

    html_doc = r.text
    soup = BeautifulSoup(html_doc, 'html5lib')

    try:
        author = soup.find(class_="tm-user-info__username").get_text()

        timestamp = soup.find(class_='tm-user-meta__date')
        timestamp = timestamp['title']

        content = soup.find(id="post-content-body")
        content = str(content)
        title = soup.find(class_="tm-article-title__text").get_text()
        tags = soup.find(class_="tm-article__tags").get_text()
        tags = tags[5:]

        # Метка, что пост является переводом или туториалом.
        tm_tag = soup.find(class_="tm-tags tm-tags_post").get_text()

        rating = soup.find(class_="tm-votes-score").get_text()
    except:
        author = title = tags = timestamp = tm_tag = rating = "Error" 
        content = "При парсинге этой странице произошла ошибка."
        logging.warning("Error parsing - {}".format(i))
        with open("Errors.txt", "a") as write_file:
            write_file.write(str(i) + "\n")

    # Записываем статью в json
    try:
        article = [i, timestamp, author, title, content, tm_tag, rating, tags]
        with open(currentFile, "w") as write_file:
            json.dump(article, write_file)
    except:
        print(i)
        raise

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Необходимы параметры min и max. Использование: async_v1.py 1 100")
        sys.exit(1)
    min = int(sys.argv[1])
    max = int(sys.argv[2])

    # Если потоков >3
    # то хабр банит ipшник на время
    pool = ThreadPool(3)

    # Отсчет времени, запуск потоков
    start_time = datetime.now()
    results = pool.map(worker, range(min, max))

    # После закрытия всех потоков печатаем время
    pool.close()
    pool.join()
    print(datetime.now() - start_time)