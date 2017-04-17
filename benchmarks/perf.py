import time
from timeit import default_timer as timer
from data import serialize, test_object
from tabulate import tabulate


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


def report():
    """This function will run our performance benchmarking suite.  The Test will serialize
    1000 objects once using the many() API and also 1000 objects one at a time using
    serialize().

    We run the test three times to produce the avg, min and max of each test.  The
    data and mapper for the test can be found in benchmarks/data.py and represent a
    fairly typical set of requirements from a mapper.

    Usage::

        $ docker-compose run --rm py3 python benchmarks/perf.py
        Type                 Avg       Min       Max
        --------------  --------  --------  --------
        Serialize many  1.36577   1.3606    1.36849
        Serialize one   0.665721  0.659155  0.671596

        $ docker-compose run --rm py2 python benchmarks/perf.py
        Type                 Avg       Min       Max
        --------------  --------  --------  --------
        Serialize many  1.22495   1.20991   1.24298
        Serialize one   0.599094  0.589109  0.605523
    """

    results1 = run()
    results2 = run()
    results3 = run()

    many_results = [results1[0].elapsed, results2[0].elapsed, results3[0].elapsed]
    one_results = [results1[1].elapsed, results2[1].elapsed, results3[1].elapsed]

    many_avg = (many_results[0] + many_results[1] + many_results[2]) / 3
    one_avg = (one_results[0] + one_results[1] + one_results[2]) / 3

    def find_min(results):

        min_result = None
        for result in results:
            if min_result is None:
                min_result = result
            elif result < min_result:
                min_result = result

        return min_result

    def find_max(results):

        max_result = None
        for result in results:
            if max_result is None:
                max_result = result
            elif result > max_result:
                max_result = result

        return max_result

    many_min = find_min(many_results)
    one_min = find_min(one_results)
    many_max = find_max(many_results)
    one_max = find_max(one_results)

    table = []
    table.append(['Serialize Many', many_avg, many_min, many_max])
    table.append(['Serialize One', one_avg, one_min, one_max])

    print(tabulate(table, headers=['Test', 'Avg', 'Min', 'Max']))


if __name__ == "__main__":

    report()
