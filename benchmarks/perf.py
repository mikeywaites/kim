import time
from timeit import default_timer as timer
from data import serialize, test_object


class timer():
    def __init__(self, name=''):
        self.name = name

    def __enter__(self):
        self.start = time.time()
        return self

    def __exit__(self, type, value, traceback):
        self.elapsed = time.time() - self.start


def test_many(limit=1000):
    for i in range(0, limit):
        serialize([test_object, test_object], many=True)


def test_one(limit=1000):
    for i in range(0, limit):
        serialize(test_object)


def run():

    results = []
    with timer('many') as result:
        test_many()
        results.append(result)

    with timer('one') as result:
        test_one()
        results.append(result)

    return results
