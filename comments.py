from sqlite3worker import Sqlite3Worker
from multiprocessing.dummy import Pool as ThreadPool
from datetime import datetime
import json
import requests
import logging

sql_worker = Sqlite3Worker("test.db")
sql_worker.execute("CREATE TABLE IF NOT EXISTS comments(id INTEGER,"
                   "parent_id INTEGER,"
                   "article INTEGER,"
                   "level INTEGER,"
                   "timePublished TEXT,"
                   "score INTEGER,"
                   "message TEXT,"
                   "children TEXT,"
                   "author TEXT)")


def worker(i):
    url = "https://m.habr.com/kek/v2/articles/{}/comments/?fl=ru%2Cen&hl=ru".format(i)

    try:
        r = requests.get(url)
        if r.status_code == 503:
            logging.critical("503 Error")
            raise SystemExit
    except:
        with open("req_errors.txt") as file:
            file.write(i)
        return 2

    data = json.loads(r.text)

    if data['success']:
        comments = data['data']['comments']

        for comment in comments:
            current = comments[comment]

            id = current['id']
            parent_id = current['parentId']
            article = i
            level = current['level']
            time_published = current['timePublished']
            score = current['score']
            message = current['message']
            children = [children for children in current['children']]
            author = current['author']

            data = (id,
                    parent_id,
                    article,
                    level,
                    time_published,
                    score,
                    message,
                    str(children),
                    str(author))

            sql_worker.execute("INSERT INTO comments VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", data)

        logging.info("Comments on article {} were parsed".format(i))


min = 1
max = 1000

pool = ThreadPool(3)

start_time = datetime.now()
results = pool.map(worker, range(min, max))

pool.close()
pool.join()
sql_worker.close()
print(datetime.now() - start_time)
