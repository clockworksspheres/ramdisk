from PySide6.QtCore import QObject

class QSingleton(type(QObject), type):
    def __init__(cls, *args, **kwargs):
        super().__init__(*args, **kwargs)
        cls.instance = None
    def __call__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__call__(*args, **kwargs)
        return cls.instance


