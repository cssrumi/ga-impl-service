from time import clock


def print_generator(func):
    def wrapper(*args, **kwargs):
        for rv in func(*args, **kwargs):
            print(rv)

    return wrapper


def logger(func):
    def wrapper(*args, **kwargs):
        rv = func(*args, **kwargs)
        print(rv)
        return rv

    return wrapper


def timer(func):
    def wrapper(*args, **kwargs):
        before = clock()
        rv = func(*args, **kwargs)
        after = clock()
        # print(func.__name__, 'elapsed', after - before)
        print('%s elapsed %.7f' % (func.__name__, after - before))
        return rv

    return wrapper


def not_implemented(func):
    def wrapper(*_, **__):
        raise TypeError('Not implemented : {}'.format(func.__name__))

    return wrapper


def until_not_none(func):
    def wrapper(*args, **kwargs):
        rv = func(*args, **kwargs)
        while not rv:
            rv = func(*args, **kwargs)
        return rv

    return wrapper
