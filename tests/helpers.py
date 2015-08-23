

class TestType(object):
    def __init__(self, *args, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    def __eq__(self, other):

        return isinstance(other, TestType) and self.__dict__ == other.__dict__
