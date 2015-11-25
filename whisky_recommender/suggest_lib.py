import sqlite3


def get_reviewers(name):
    """
    Get the drink's reviewers
    :param name:
    :return:
    """
    conn = sqlite3.connect('reviews.sqlite3')
    cursor = conn.cursor()
    ratings = []
    for row in cursor.execute("select * from reviews where name=?", (name,)):
        ratings.append((row[4], row[2]))
    return ratings


def find_favorites(reviewers):
    """
    Find the reviewer's favorite drinks
    :param reviewers:
    :return:
    """
    conn = sqlite3.connect('reviews.sqlite3')
    cursor = conn.cursor()
    results = {}
    for user in reviewers:
        for row in cursor.execute("select * from reviews where user=?", (user[1],)):
            drink_name = row[1]
            if not row[4].isdigit():
                continue
            drink_review = int(row[4]) * (float(user[0]) / 100)
            if drink_name in results:
                results[drink_name].append(drink_review)
            else:
                results[drink_name] = [drink_review]
    choices = [(r, average(results[r])) for r in results]
    choices = sorted(choices, key=lambda x: x[1], reverse=True)
    return choices[:5]


def average(n):
    """
    Average some values
    :param n:
    :return:
    """
    total = 0
    for i in n:
        total += i
    return float(total) / float(len(n))