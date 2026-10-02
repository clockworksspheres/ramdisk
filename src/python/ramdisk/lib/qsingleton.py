from PySide6.QtCore import QObject

class QSingleton(type):
    """Metaclass implementing a QObject-based singleton."""

    def __init__(cls, name, bases, attrs):
        super().__init__(name, bases, attrs)
        cls._instance = None

    def __call__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__call__(*args, **kwargs)
        return cls._instance

'''
from PySide6.QtCore import QObject

# Extract the QObject metaclass once
QObjectMeta = type(QObject)

class QSingleton(QObjectMeta):
    """Metaclass implementing a QObject-based singleton."""

    def __init__(cls, name, bases, attrs):
        super().__init__(name, bases, attrs)
        cls._instance = None

    def __call__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__call__(*args, **kwargs)
        return cls._instance


from PySide6.QtCore import QObject

QObjectMeta = type(QObject)

class QSingleton(QObjectMeta):
    def __init__(cls, *args, **kwargs):
        super().__init__(*args, **kwargs)
        cls.instance = None

    def __call__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__call__(*args, **kwargs)
        return cls.instance

##########

from PySide6.QtCore import QObject

class QSingleton(type(QObject), type):
    def __init__(cls, *args, **kwargs):
        super().__init__(*args, **kwargs)
        cls.instance = None
    def __call__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__call__(*args, **kwargs)
        return cls.instance
'''

