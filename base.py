import inspect
from dataclasses import make_dataclass, InitVar, field, dataclass

Null = make_dataclass("Null", [])


class _AnyMeta(type):
    def __instancecheck__(self, obj):
        return True

    def __repr__(self):
        if self is Any:
            return "typing.Any"
        return super().__repr__()


class Any(metaclass=_AnyMeta):
    def __new__(cls, *args, **kwargs):
        if cls is Any:
            raise TypeError("Any cannot be instantiated")
        return super().__new__(cls)


class StaticType:
    def __init__(self, type):
        self.type = type

    @classmethod
    def __class_getitem__(cls, item):
        return StaticType(item)

    def __repr__(self):
        return f"StaticType(tp={self.type})"


class Fixed:
    def __init__(self, count, type):
        self.count = count
        self.type = type

    @classmethod
    def __class_getitem__(cls, item):
        return Fixed(*item)

    def __repr__(self):
        return f"Fixed(count={self.count}, tp={self.type})"


@dataclass
class Range:
    start: int | float
    stop: int | float = None

    def __post_init__(self):
        if self.stop is None:
            self.stop = self.start

    def __contains__(self, item):
        return self.stop >= item >= self.start


@dataclass
class Spec:
    spec: InitVar[inspect.FullArgSpec]
    args: list = field(init=False)
    varargs: str | None = field(init=False)
    varkw: str | None = field(init=False)
    annotations: dict = field(init=False)
    defaults: dict = field(init=False)
    kwonlyargs: list = field(init=False)
    kwonlydefaults: dict = field(init=False)

    @dataclass
    class TypeInfo:
        type: type
        fixed: bool
        count: float

    def __post_init__(self, spec: inspect.FullArgSpec):
        self.args = spec.args
        self.varargs = spec.varargs
        self.varkw = spec.varkw
        self.annotations = self._parse_annotation(spec.annotations)
        if spec.defaults is not None:
            nulls = [Null()] * (len(spec.args) - len(spec.defaults))
            self.defaults = dict(zip(spec.args, [*nulls, *spec.defaults]))
        else:
            self.defaults = {}
        self.kwonlyargs = spec.kwonlyargs
        self.kwonlydefaults = spec.kwonlydefaults or {}

    def _parse_annotation(self, annotations):
        return {k: self._getTopData(v) for k, v in annotations.items()}

    def _getTopData(self, tp, raised=False, memory={}):
        if isinstance(tp, StaticType):
            return self._getTopData(tp.type, raised, memory | {"StaticType": True})
        if isinstance(tp, Fixed) and raised:
            raise TypeError("type is not fixed")
        if isinstance(tp, Fixed):
            return self._getTopData(tp.type, raised, memory | {"Fixed": tp.count})
        return self.TypeInfo(tp, memory.get("StaticType", False), memory.get("Fixed", float("inf")))


AnyTypeInfo = Spec.TypeInfo(Any, False, float("inf"))
