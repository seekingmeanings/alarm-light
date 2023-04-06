from subprocess import run as sprun


def termux_api_toast(msg: str,
                     position: str = "bottom",
                     background_color: str = "white",
                     text_color: str = "black"):
    sprun(['termux-toast',
           '-g', str(position),
           '-b', str(background_color),
           '-c', str(text_color),
           str(msg)],
          check=True)


def locked(func):
    def wrapper(*args, **kwargs):
        s = args[0]
        with s._lock:
            return func(*args, **kwargs)
    return wrapper


# user395760 on stackowerflow
# https://stackoverflow.com/questions/6307761/how-to-decorate-all-functions-of-a-class-without-typing-it-over-and-over-for-eac
def for_all_methods(decorator):
    def decorate(cls):
        for attr in cls.__dict__:
            if callable(getattr(cls, attr)) and not attr.startswith("__"):
                setattr(cls, attr, decorator(getattr(cls, attr)))
        return cls
    return decorate
