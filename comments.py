from sqlite3worker import Sqlite3Worker
from multiprocessing.dummy import Pool as ThreadPool
from datetime import datetime
import json
import requests
import logging
import argparse

sql_worker = Sqlite3Worker("habr.db")
sql_worker.execute("CREATE TABLE IF NOT EXISTS comments("
                   "id              INTEGER,"
                   "parent_id       INTEGER,"
                   "article         INTEGER,"
                   "level           INTEGER,"
                   "timePublished   TEXT,"
                   "score           INTEGER,"
                   "message         TEXT,"
                   "children        TEXT,"
                   "author          TEXT)"
                   )


def worker(i):
    url = "https://m.habr.com/kek/v2/articles/{}/comments/?fl=ru%2Cen&hl=ru".format(i)

    try:
        r = requests.get(url)
        if r.status_code == 503:
            logging.critical("503 Error")
            raise SystemExit
        if r.status_code == 404:
            logging.info("Not found")
            return 404
    except requests.exceptions.HTTPError as err:
        raise SystemExit(err)

    data = json.loads(r.text)

    if data['comments']:
        comments = data['comments']
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

            try:
                data = (id,
                        parent_id,
                        article,
                        level,
                        time_published,
                        score,
                        message,
                        str(children),
                        str(author['login']))
            except:
                data = (None, None, None, None, None, None, None, None, None)

            sql_worker.execute("INSERT INTO comments VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", data)

            logging.info("Comments on article {} were parsed".format(i))


parser = argparse.ArgumentParser(description='Habr comments parser')
parser.add_argument('--min', action="store", dest="min", default=1, type=int)
parser.add_argument('--max', action="store", dest="max", default=1000, type=int)
parser.add_argument('--threads', action="store", dest="threads_count", default=3, type=int)
args = parser.parse_args()

pool = ThreadPool(args.threads_count)

start_time = datetime.now()
results = pool.map(worker, range(args.min, args.max))

pool.close()
pool.join()
sql_worker.close()
print(datetime.now() - start_time)
