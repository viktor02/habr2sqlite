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

    url = "https://m.habr.com/kek/v1/articles/{}/?fl=ru%2Cen&hl=ru".format(i)

    try:
        r = requests.get(url)
        if r.status_code == 503:
            logging.critical("503 Error")
            return 503
    except:
        with open("req_errors.txt") as file:
            file.write(i)
        return 2

    data = json.loads(r.text)

    if data['success']:
        article = data['data']['article']

        id = article['id']
        is_tutorial = article['is_tutorial']
        time_published = article['time_published']
        comments_count = article['comments_count']
        lang = article['lang']
        tags_string = article['tags_string']
        title = article['title']
        content = article['text_html']
        reading_count = article['reading_count']
        author = article['author']['login']
        score = article['voting']['score']

        data = (id, is_tutorial, time_published, title, content, comments_count, lang, tags_string, reading_count, author, score)
        with open(currentFile, "w") as write_file:
            json.dump(data, write_file)

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Необходимы параметры min и max. Использование: asyc.py 1 100")
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