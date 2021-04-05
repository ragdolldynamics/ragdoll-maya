import time
import logging
import functools

log = logging.getLogger("ragdoll")


def with_timing(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        t0 = time.time()

        try:
            return func(*args, **kwargs)
        finally:
            t1 = time.time()
            duration = t1 - t0
            log.info("%s in %.2fms" % (func.__name__, duration * 1000))

    return wrapper
