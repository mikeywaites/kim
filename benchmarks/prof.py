import cProfile

from data import serialize, test_object


def do_cprofile(func):
    def profiled_func(*args, **kwargs):
        profile = cProfile.Profile()
        try:
            profile.enable()
            result = func(*args, **kwargs)
            profile.disable()
            return result
        finally:
            profile.print_stats('cumulative')
    return profiled_func


@do_cprofile
def test_many(limit=1000):
    for i in range(0, limit):
        serialize([test_object, test_object], many=True)


@do_cprofile
def test_one(limit=1000):
    for i in range(0, limit):
        serialize(test_object)


def run():

    test_many()
    test_one()


if __name__ == '__main__':

    run()
