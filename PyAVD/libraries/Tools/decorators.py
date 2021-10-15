
'''Some decorators for PyAVD - no AVD theory here!'''

def stub(func):
    """Decorator to mark a function as stub - returns 1 """
    def wrapper(*args, **kwargs):
        return 1
    return wrapper
    