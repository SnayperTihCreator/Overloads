
class PolyMethod:
    def __init__(self, name='<lambda>'):
        self.impl = {}
        self.inst = None
        self.cls = None
        self.name = name
        self.empty = True
        self._init_cls = False

    def __get__(self, instance, cls):
        self.inst = instance
        self.cls = cls
        self._init_cls = True
        return self

    def _parse_args(self, args):
        raise NotImplementedError

    def _parse_func(self, func, state):
        raise NotImplementedError

    def _parse_res(self, key):
        raise NotImplementedError

    def _get_callable(self, impl):
        return getattr(impl, "__func__", impl)

    def add_impl(self, func, state=False):
        func = self._get_callable(func)
        key = self._parse_func(func, state)
        self.impl[key] = func
        if self.empty:
            self.empty = False
            self.__call__.__func__.__name__ = func.__name__
            self.__call__.__func__.__annotations__ = func.__annotations__
            self.__call__.__func__.__doc__ = func.__doc__

    def get(self, key):
        try:
            return self._parse_res(key)
        except KeyError as e:
            raise NotImplementedError(f"Current not implemented key {key}") from e

    def __call__(self, *args):
        impl = self.get(self._parse_args(args))
        funct = self._get_callable(impl)
        if self.cls and isinstance(impl, classmethod):
            return funct(self.cls, *args)
        elif self.inst:
            return funct(self.inst, *args)
        else:
            return funct(*args)


class PolyMethodCount(PolyMethod):
    def _parse_func(self, func, state):
        return func.__code__.co_argcount - (1 if state else 0)

    def _parse_args(self, args):
        return len(args)

    def _parse_res(self, key):
        return self.impl.get(key)


class PolyMethodType(PolyMethod):
    def _parse_func(self, func, state):
        l = func.__code__.co_argcount - (1 if state else 0)
        t = tuple(func.__annotations__.values())
        if len(t) == l: return t
        print(l, len(t), t)
        return (*t, *[type]*(l-len(t)))

    def _parse_args(self, args):
        return tuple(map(type, args))

    def _parse_res(self, key):
        for tss, v in self.impl.items():
            for k, ts in zip(key, tss):
                if not issubclass(k, ts):
                    break
            else:
                return v


class PolyMethodTypeCount(PolyMethod):
    def _parse_func(self, func, state):
        return func.__code__.co_argcount - (1 if state else 0), tuple(func.__annotations__.values())

    def _parse_args(self, args):
        return len(args), tuple(map(type, args))

    def _parse_res(self, key):
        l2, key2 = key
        for (l, tss), v in self.impl.items():
            for k, ts in zip(key2, tss):
                if not issubclass(k, ts):
                    break
            else:
                return v


class OverLoadBase:
    polyMethod = PolyMethod

    def __init__(self, func):
        self.base = self.polyMethod(func.__name__)
        self.registry(func)

    def __call__(self, *args):
        return self.base(*args)

    def registry(self, func):
        self.base.add_impl(func)
        return self


class OverLoadCount(OverLoadBase):
    polyMethod = PolyMethodCount


class OverLoadType(OverLoadBase):
    polyMethod = PolyMethodType


class OverLoadTypeCount(OverLoadBase):
    polyMethod = PolyMethodTypeCount


MethodBase = type("MethodBase", tuple(), {"__init__": (lambda self, func: setattr(self, "func", func))})
MethodType = type("MethodType", (MethodBase,), {})
MethodCount = type("MethodCount", (MethodBase,), {})
MethodTypeCount = type("MethodTypeCount", (MethodBase,), {})


class PolyDictMulti(dict):
    def __setitem__(self, key, value):
        if isinstance(value, MethodBase):
            func, poly = self._parse_method(value)
            if key not in self:
                super().__setitem__(key, poly)
            self[key].add_impl(func, True)
            return
        return super().__setitem__(key, value)

    def _parse_method(self, method):
        if isinstance(method, MethodType):
            poly = PolyMethodType(method.func.__name__)
        elif isinstance(method, MethodCount):
            poly = PolyMethodCount(method.func.__name__)
        elif isinstance(method, MethodTypeCount):
            poly = PolyMethodTypeCount(method.func.__name__)
        return method.func, poly


class MetaOverLoadMulti(type):
    @classmethod
    def __prepare__(metacls, name, bases, **kwds):
        return PolyDictMulti()
