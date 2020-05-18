# habr2sqlite

 Парсер Хабрахабра в базу данных SQLite3
### Требования
* python >= 3.7.6
* requests >= 2.22.0
* sqlite3worker >= 1.1.7

### Использование
#### Создаем базу
 1. ```python articles.py --min 490000 --max 500000```
 2. ```python comments.py --min 490000 --max 500000```

#### Обновляем базу
 * ```python updateDB.py```


[Статья на Хабре](https://m.habr.com/ru/post/490820/)

[Статья про habramirror](https://habr.com/ru/post/496892/)