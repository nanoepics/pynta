import os


def from_here(*args):
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), *args)
