import json
import sqlite3
import logging
from datetime import datetime

def parser(min, max):
    conn = sqlite3.connect('habr.db')
    c = conn.cursor()
    c.execute('PRAGMA encoding = "UTF-8"')
    c.execute('PRAGMA synchronous = 0') # Отключаем подтверждение записи, так скорость увеличивается в разы.
    c.execute("CREATE TABLE IF NOT EXISTS articles(id INTEGER, time_published TEXT, author TEXT, title TEXT, content TEXT, \
    lang TEXT, comments_count INTEGER, reading_count INTEGER, score INTEGER, is_tutorial INTEGER, tags_string TEXT)")
    try:
        for i in range(min, max):
            try:
                filename = "files\\{}.json".format(i)
                f = open(filename)
                data = json.load(f)

                (id, is_tutorial, time_published, title, content, comments_count, lang,
                 tags_string, reading_count, author, score) = data

                # Ради лучшей читаемости базы можно пренебречь читаемостью кода. Или нет?
                # Если вам так кажется, можно просто заменить кортеж аргументом data. Решать вам.

                c.execute('INSERT INTO articles VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (id, time_published, author,
                    title, content, lang, comments_count, reading_count, score, is_tutorial, tags_string))
                f.close()

            except IOError:
                logging.info('FileNotExists')
                continue

    finally:
        conn.commit()

start_time = datetime.now()
parser(490000, 490918)
print(datetime.now() - start_time)