class TerrapynException(BaseException):
    pass

class DependencyNotFound(RuntimeError, TerrapynException):
    pass
