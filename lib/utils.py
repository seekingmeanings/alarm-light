
def locked(func):
    def wrapper(*args, **kwargs):
        s = args[0]
        with s._lock:
            return func(*args, **kwargs)
    return wrapper


# user395760 on stackowerflow
def for_all_methods(decorator):
    def decorate(cls):
        for attr in cls.__dict__:
            if callable(getattr(cls, attr)) and not attr.startswith("__"):
                setattr(cls, attr, decorator(getattr(cls, attr)))
        return cls
    return decorate