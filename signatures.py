import inspect
from dataclasses import dataclass

from base import Spec, AnyTypeInfo

__all__ = ["BaseSignature", "ArgsSignature", "KwArgsSignature", "PositionSignature", "KeyWordSignature",
           "KwPosSignature", "EmptySignature", "DataSet"]


class BaseSignature:
    def hashable(self, **kwargs):
        pass


class EmptySignature:
    @property
    def type_data(self):
        return AnyTypeInfo

    @property
    def count(self):
        return 0


class ArgsSignature(BaseSignature):
    def __init__(self, code, spec: Spec):
        self.name = spec.varargs
        self.type_data = spec.annotations.get(self.name, AnyTypeInfo)

    @property
    def count(self):
        return self.type_data.count


class KwArgsSignature(BaseSignature):
    def __init__(self, code, spec: Spec):
        self.name = spec.varkw
        self.type_data = spec.annotations.get(self.name, AnyTypeInfo)

    @property
    def count(self):
        return self.type_data.count


class PositionSignature(BaseSignature):
    def __init__(self, code, spec: Spec):
        self.names = spec.args[:code.co_posonlyargcount + 1]
        self.type_datas = [spec.annotations.get(nm, AnyTypeInfo) for nm in self.names]
        self.default = {k: v for k, v in spec.defaults.items() if k in self.names}

    @property
    def count(self):
        return len(self.names)


class KeyWordSignature(BaseSignature):
    def __init__(self, code, spec: Spec):
        self.names = spec.kwonlyargs
        self.type_datas = {nm: spec.annotations.get(nm, AnyTypeInfo) for nm in self.names}
        self.default = spec.kwonlydefaults

    @property
    def count(self):
        return len(self.names)


class KwPosSignature(BaseSignature):
    def __init__(self, code, spec: Spec):
        self.names = spec.args[code.co_posonlyargcount:]
        self.type_datas = [spec.annotations.get(nm, AnyTypeInfo) for nm in self.names]
        self.default = {k: v for k, v in spec.defaults.items() if k in self.names}

    @property
    def count(self):
        return len(self.names)


@dataclass
class DataSet:
    pos: PositionSignature
    kwpos: KwPosSignature
    kw: KeyWordSignature
    args: ArgsSignature
    kwargs: KwArgsSignature

    @classmethod
    def from_code_or_spec(cls, code, spec):
        return cls(PositionSignature(code, spec), KwPosSignature(code, spec), KeyWordSignature(code, spec),
                   ArgsSignature(code, spec) if code.co_flags & inspect.CO_VARARGS else EmptySignature(),
                   KwArgsSignature(code, spec) if code.co_flags & inspect.CO_VARKEYWORDS else EmptySignature())
