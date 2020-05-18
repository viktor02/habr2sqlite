import json
import sqlite3
import subprocess
import sys

import requests


def getLastPostOnHabr():
    """ Get last post on Habr """
    url = "https://m.habr.com/kek/v1/articles/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:76.0) Gecko/20100101 Firefox/76.0'
    }
    params = {
        "date": "day",
        "sort": "date"
    }

    r = requests.get(url, headers=headers, params=params)
    data = json.loads(r.text)
    lastPostOnHabr = data['articleIds'][0]

    return lastPostOnHabr


def getLastPostInBase():
    """ Get last post in database """
    query = "SELECT max(id) from articles"

    conn = sqlite3.connect('habr.db')
    c = conn.cursor()
    c.execute(query)
    lastPostInBase = c.fetchone()[0]

    return lastPostInBase


lastPostBase = getLastPostInBase()
lastPostHabr = getLastPostOnHabr()

print("min={} max={}".format(lastPostBase, lastPostHabr))

argsArticles = "{} articles.py --min {} --max {}".format(sys.executable, lastPostBase, lastPostHabr)
argsComments = "{} comments.py --min {} --max {}".format(sys.executable, lastPostBase, lastPostHabr)

subprocess.call(argsArticles)
print("Articles downloaded")
subprocess.call(argsComments)
print("Comments downloaded")
