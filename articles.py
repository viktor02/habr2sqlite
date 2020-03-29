from sqlite3worker import Sqlite3Worker
from multiprocessing.dummy import Pool as ThreadPool
from datetime import datetime
import json
import requests
import logging

sql_worker = Sqlite3Worker("habr.db")
sql_worker.execute(
"""
CREATE TABLE "articles" (
	"id"	INTEGER,
	"time_published"	TEXT,
	"author"	TEXT,
	"title"	TEXT,
	"content"	TEXT,
	"lang"	TEXT,
	"comment_count"	INTEGER,
	"reading_count"	INTEGER,
	"score"	INTEGER,
	"is_tutorial"	INTEGER,
	"tags_string"	TEXT
)
""")


def worker(i):
    url = "https://m.habr.com/kek/v1/articles/{}/?fl=ru%2Cen&hl=ru".format(i)

    try:
        r = requests.get(url)
        if r.status_code == 503:
            logging.critical("503 Error")
            raise SystemExit
    except:
        with open("req_errors.txt", "a") as file:
            logging.critical("requests error")
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

        data = (id,
                time_published,
                author,
                title,
                content,
                lang,
                comments_count,
                reading_count,
                score,
                is_tutorial,
                tags_string)

        sql_worker.execute("INSERT INTO articles VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", data)

    logging.info("Comments on article {} were parsed".format(i))


min = 490406
max = 494452

pool = ThreadPool(3)

start_time = datetime.now()
results = pool.map(worker, range(min, max))

pool.close()
pool.join()
sql_worker.close()
print(datetime.now() - start_time)
