from sqlite3worker import Sqlite3Worker
from multiprocessing.dummy import Pool as ThreadPool
from datetime import datetime
import json
import requests
import logging
import argparse

sql_worker = Sqlite3Worker("habr.db")
sql_worker.execute(
    """
CREATE TABLE IF NOT EXISTS "articles" (
                           "id"	            INTEGER,
                           "time_published"	TEXT,
                           "author"	        TEXT,
                           "title"	        TEXT,
                           "content"	    TEXT,
                           "lang"	        TEXT,
                           "comment_count"	INTEGER,
                           "reading_count"	INTEGER,
                           "score"	        INTEGER,
                           "is_tutorial"	INTEGER,
                           "tags_string"	TEXT)
    """)


def worker(i):
    url = "https://m.habr.com/kek/v2/articles/{}/?fl=ru%2Cen&hl=ru".format(i)

    try:
        r = requests.get(url)
        if r.status_code == 503:
            logging.critical("503 Error")
            raise SystemExit
        if r.status_code != 200:
            logging.info("Not found or in drafts")
            return 404
    except requests.exceptions.HTTPError as err:
        raise SystemExit(err)

    article = json.loads(r.text)

    id = article['id']
    is_tutorial = True if 'tutorial' in article['postLabels'] else False
    time_published = article['timePublished']
    comments_count = article['statistics']['commentsCount']
    lang = article['lang']
    tags_string = ','.join(tuple(tag['titleHtml'] for tag in article['tags']))
    title = article['titleHtml']
    content = article['textHtml']
    reading_count = article['statistics']['readingCount']
    author = article['author']['login']
    score = article['statistics']['score']

    try:
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
    except:
        data = (None, None, None, None, None,
                None, None, None, None, None, None)

    sql_worker.execute(
        "INSERT INTO articles VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", data)

    logging.info("Comments on article {} were parsed".format(i))


parser = argparse.ArgumentParser(
    description='Habr articles parser. Specify the maximum and minimum number of articles.')

parser.add_argument('--min',
                    action="store",
                    dest="min",
                    required=True,
                    type=int)
parser.add_argument('--max', 
                    action="store",
                    dest="max", 
                    required=True, 
                    type=int)
parser.add_argument('--threads', '-t', 
                    action="store", 
                    dest="threads_count",
                    help="number of threads", 
                    default=3, 
                    type=int)

args = parser.parse_args()

pool = ThreadPool(args.threads_count)

start_time = datetime.now()
results = pool.map(worker, range(args.min, args.max))

pool.close()
pool.join()
sql_worker.close()
print(datetime.now() - start_time)
