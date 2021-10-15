
'''
Some decorators for PyAVD - not aero related!
'''

def stub(func):
    """Decorator to mark a function as stub - return 1 """

    def wrapper(*args, **kwargs):
        return 1
    return wrapper
    