from enum import IntEnum


class Const:
    class ConstError(TypeError):
        pass  # base error class

    class ConstCaseError(ConstError):
        pass

    def __setattr__(self, name, value):
        if name in self.__dict__:
            raise self.ConstError("Can't change const.%s" % name)
        if not name.isupper():
            raise self.ConstCaseError("const name %r is not all uppercase" % name)
        self.__dict__[name] = value


class SupportEnv(IntEnum):
    LOCALHOST = 1
    PROD = 2
