from dataclasses import dataclass, make_dataclass, InitVar, field
from typing import Callable
from types import FunctionType
from copy import copy
from itertools import repeat

import inspect

from pprint import pp

from base import Spec, Range
from signatures import *


def vars(obj):
    return {n: getattr(obj, n, "Null") for n in dir(obj)}


def parseType(inst: object, type_info: Spec.TypeInfo):
    if type_info.fixed:
        return type(inst) is type_info.type
    else:
        return isinstance(inst, type_info.type)


class Signature(BaseSignature):
    class ArgumentParse:
        def __init__(self, dataset):
            self.dataset: DataSet = dataset

        def parse(self, *args, **kwargs):
            pos = args[:self.dataset.pos.count + 1]
            kw = {k: v for k, v in kwargs.items() if k in self.dataset.kw.names}
            kwpos, args, kwargs = self.parseKwPos(args[self.dataset.pos.count:],
                                                  {k: v for k, v in kwargs.items() if k not in kw})
            return pos, kwpos, kw, args, kwargs

        def parseKwPos(self, args, kwargs):
            kwpos = {k: v for k, v in kwargs.items() if k in self.dataset.kwpos.names}
            kwargs = {k: v for k, v in kwargs.items() if k not in self.dataset.kwpos.names}
            lks = self.dataset.kwpos.count - len(kwpos)
            kwpos = [*args[:lks + 1], *kwpos.values()]
            args = args[lks:]
            return kwpos, args, kwargs

    def __init__(self, func: FunctionType):
        code = func.__code__
        spec = Spec(inspect.getfullargspec(func))
        self.signs = DataSet.from_code_or_spec(code, spec)
        self.args = self.ArgumentParse(self.signs)

    def hashable(self, **kwargs):
        if not self.parseCount(kwargs["args"], kwargs["kwargs"]):
            return False
        return self.parseTypes(kwargs["args"], kwargs["kwargs"])

    def parseCount(self, args, kwargs):
        scount = len(args) + len(kwargs)
        res = Range(self.signs.pos.count + self.signs.kwpos.count + self.signs.kw.count)
        res.stop = res.stop + self.signs.args.count
        res.stop = res.stop + self.signs.kwargs.count
        return scount in res

    def parseTypes(self, args, kwargs):
        pos, kwpos, kw, vargs, vkwargs = self.args.parse(*args, **kwargs)
        posres = self.correctiveType(pos, self.signs.pos.type_datas)
        kwposres = self.correctiveType(kwpos, self.signs.kwpos.type_datas)
        kwres = self.correctiveType(kw, self.signs.kw.type_datas)
        argsres = self.parseOneType(vargs, self.signs.args.type_data)
        kwargsres = self.parseOneType(vkwargs, self.signs.kwargs.type_data)
        return posres and kwposres and kwres and argsres and kwargsres

    def correctiveType(self, insts, types):
        if isinstance(insts, dict):
            return all(parseType(insts[nm], types[nm]) for nm in insts.keys())
        return all(parseType(inst, tpinfo) for inst, tpinfo in zip(insts, types))

    def parseOneType(self, insts, tp):
        return all(parseType(inst, tp) for inst in insts)


class BaseOverLoad:
    _message_error = ""

    def __init__(self, func):
        self.impls = {}
        self.status_method = False
        self.instance = None
        self.cls = None
        self._register(func)

    def __call__(self, *args, **kwargs):
        impl: Callable = self._get_internal(args, kwargs)
        if impl is None:
            raise NotImplementedError(self._message_error)

        match int(self.status_method):
            case 0:
                return impl(*args, **kwargs)
            case 1:
                return impl(self.instance, *args, **kwargs)
            case 2:
                return impl(self.cls, *args, **kwargs)

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

    def _get_internal(self, args, kwargs):
        pass


class OverLoad(BaseOverLoad):
    def _add_internal(self, func):
        self.impls[Signature(func)] = func

    def _get_internal(self, args, kwargs):
        signs = [sign for sign in self.impls.keys() if sign.hashable(args=args, kwargs=kwargs)]

        return self.impls[signs[0]] if signs else None


if __name__ == "__main__":
    @OverLoad
    def func(a:int, b, **kwargs):
        print(1)


    @func.register
    def func(a):
        print(2)


    func("", b=6, c=7)
