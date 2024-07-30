import typing as tpi
from itertools import repeat


class BaseOverLoad:
    _message_error = ""

    def __init__(self, func):
        self.impls = {}
        self.status_method = False
        self.instance = None
        self.cls = None
        self._register(func)

    def __call__(self, *args):
        impl = self._get_internal(args)
        if impl is None:
            raise NotImplementedError(self._message_error)

        match int(self.status_method):
            case 0:
                return impl(*args)
            case 1:
                return impl(self.instance, *args)
            case 2:
                return impl(self.cls, *args)

    def __set_name__(self, owner, name):
        self.status_method = self.status_method if self.status_method else True

    def __get__(self, instance, owner):
        self.instance = instance
        self.cls = owner
        return self

    def _register(self, func):
        if hasattr(func, "__func__"):
            self.status_method = 2 if isinstance(func, classmethod) else self.status_method
            self.status_method = False if isinstance(func, staticmethod) else self.status_method
            return self.register(func.__func__)
        self._add_internal(func)

    def register(self, func):
        self._register(func)
        return self

    def _add_internal(self, func):
        pass

    def _get_internal(self, args) -> tpi.Callable:
        pass


class OverloadCount(BaseOverLoad):
    _message_error = "couldn't find an implementation with the given number of arguments"

    def _add_internal(self, func):
        argcount = func.__code__.co_argcount
        self.impls[argcount] = func

    def _get_internal(self, args):
        return self.impls.get(len(args) + bool(self.status_method))


class _OverLoadType(BaseOverLoad):
    _message_error = "couldn't find an implementation with the given types of arguments"

    def __init__(self, func, *types):
        self._temp_var = types
        super().__init__(func)

    def register(self, *types):
        self._temp_var = types
        return super().register

    def _add_internal(self, func):
        self.impls[self._temp_var] = func
        self._temp_var = None


class _OverLoadTypeStatic(_OverLoadType):
    def _get_internal(self, args):
        return self.impls.get(tuple(type(el) for el in args))


class _OverLoadTypeMro(_OverLoadType):
    def _get_internal(self, args):
        hasble = filter(lambda x: len(x[0]) == len(args), self.impls.items())
        if not hasble: return None
        for source, (wait, impl) in zip(repeat(tuple(type(el) for el in args)), hasble):
            if self._cross(source, wait):
                return impl

    def _cross(self, tps1, tps2):
        for tp1, tp2 in zip(tps1, tps2):
            if not issubclass(tp1, tp2):
                return False
        return True


def OverLoadTypeStatic(*types):
    def inner(func):
        return _OverLoadTypeStatic(func, *types)

    return inner


def OverLoadTypeMro(*types):
    def inner(func):
        return _OverLoadTypeMro(func, *types)

    return inner