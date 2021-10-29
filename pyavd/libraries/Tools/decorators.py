'''Some decorators for PyAVD - no AVD theory here!'''

import logging


def stub(func):
    """Decorator to mark a function as stub - returns 1 """
    def wrapper(*args, **kwargs):
        return 1
    return wrapper


def debug(fn):
    """Debug wrapper - logs basically everything"""
    def wrapper(*args, **kwargs):
        logging.debug(f"Invoking {fn.__name__}")
        logging.debug(f"  args: {args}")
        logging.debug(f"  kwargs: {kwargs}")
        result = fn(*args, **kwargs)
        logging.debug(f"  returned {result}")
        return result
    return wrapper