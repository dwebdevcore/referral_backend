import re
from copy import deepcopy
from datetime import datetime
from types import GeneratorType

from testfixtures import compare


class Comparator:

    def pytest_diff(self, other):
        raise NotImplementedError


class ReprMixin:

    def __init__(self, *args, **kwargs):

        self.last_repr = None
        super().__init__(*args, **kwargs)

    def __eq__(self, other):

        result = super().__eq__(other)
        if result is True:
            self.last_repr = repr(other)
        return result

    def __repr__(self):

        if self.last_repr is not None:
            return self.last_repr

        else:
            return super().__repr__()


class AnyIntegerMixin:

    def __eq__(self, other):

        if isinstance(other, int):
            return True

        else:
            return NotImplemented


class AnyInteger(ReprMixin, AnyIntegerMixin, Comparator):
    pass


class AnyBoolMixin:

    def __eq__(self, other):

        if isinstance(other, bool):
            return True

        else:
            return NotImplemented


class AnyBool(ReprMixin, AnyBoolMixin, Comparator):
    pass


class AnyStrMixin:

    def __eq__(self, other):

        if isinstance(other, str):
            return True

        else:
            return NotImplemented


class AnyStr(ReprMixin, AnyStrMixin, Comparator):
    pass


class AnyDictMixin:

    def __init__(self, **kwargs):

        self.failed_comparison = None
        self.kwargs = kwargs

    def __eq__(self, other):

        if isinstance(other, dict):
            for k, v in self.kwargs.items():
                if not (k in other and v == other[k]):
                    self.failed_comparison = other
                    return False

            return True

        else:
            return NotImplemented

    def __repr__(self):

        classname = self.__class__.__name__
        args = ", ".join(f"{k}={v!r}" for k, v in self.kwargs.items())
        return f"{classname}({args})"

    def pytest_diff(self, other):

        tmp = deepcopy(self.failed_comparison)
        tmp.update(self.kwargs)
        return compare(tmp, other, raises=False).splitlines()


class AnyDict(ReprMixin, AnyDictMixin, Comparator):
    pass


class AnyISODateTimeMixin:

    def __eq__(self, other):

        if isinstance(other, str):
            try:
                datetime.strptime(other, "%Y-%m-%dT%H:%M:%S.%fZ")
            except ValueError:
                return False

            else:
                return True

        else:
            return NotImplemented


class AnyISODateTime(ReprMixin, AnyISODateTimeMixin, Comparator):
    pass


class ListItemsMixin:

    def __init__(self, *items):

        if len(items) == 1 and isinstance(items[0], GeneratorType):
            self.items = list(items[0])
        else:
            self.items = items

    def __eq__(self, other):

        return (
                   isinstance(other, list)
                   and len(self.items) == len(other)
                   and all(item in other for item in self.items)
               ) or NotImplemented

    def pytest_diff(self, other):

        return compare(self.items, other, raises=False).splitlines()


class ListItems(ReprMixin, ListItemsMixin, Comparator):
    pass


class AnyListMixin:

    def __init__(self):

        self.undefined = object()
        self.expected_length = self.undefined
        self.expected_item = self.undefined
        self.expected_type = self.undefined
        self.failure_message = self.undefined

    def length(self, num):

        self.expected_length = num
        return self

    def of(self, item):

        self.expected_item = item
        return self

    def of_type(self, t):

        self.expected_type = t
        return self

    def __eq__(self, other):

        if isinstance(other, list):
            if self.expected_length is not self.undefined:
                actual_length = len(other)
                if self.expected_length != actual_length:
                    self.failure_message = f"Should be a list of {self.expected_length} items (has {actual_length} instead)"
                    return False

            if self.expected_item is not self.undefined:
                for x in other:
                    if not self.expected_item == x:
                        if hasattr(self.expected_item, "pytest_diff"):
                            self.failure_message = "List item is different:\n\n"
                            self.failure_message += "\n".join(
                                self.expected_item.pytest_diff(x)
                            )
                        else:
                            self.failure_message = f"{x!r} in list did not equal {self.expected_item!r}"
                        return False

            if self.expected_type is not self.undefined:
                for x in other:
                    if not isinstance(x, self.expected_type):
                        self.failure_message = f"{x!r} is not of type {self.expected_type!r}"
                        return False

            return True

        else:
            return NotImplemented

    def pytest_diff(self, other):

        if self.failure_message is not self.undefined:
            return self.failure_message.splitlines()

        else:
            super().pytest_diff(other)


class AnyList(ReprMixin, AnyListMixin, Comparator):
    pass


class MemberOfMixin:

    def __init__(self, *items):

        if len(items) == 1 and isinstance(items[0], GeneratorType):
            self.items = list(items[0])
        else:
            self.items = list(items)

    def __eq__(self, other):

        return other in self.items


class MemberOf(ReprMixin, MemberOfMixin, Comparator):
    pass


class RegexMixin:
    substitutions = {
        "uuid4": r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"
    }
    subscriptions_re = re.compile(r"\|".join(f"{{{sub}}}" for sub in substitutions))

    def __init__(self, regex):

        self.flags = 0
        if self.subscriptions_re.search(regex):
            self.formatted = regex.format_map(self.substitutions)
        else:
            self.formatted = regex
        self.compiled = re.compile(self.formatted)
        self.match()

    def match(self):

        self.method = self.compiled.match
        return self

    def search(self):

        self.method = self.compiled.search
        return self

    def ignorecase(self):

        self.flags |= re.I
        self.compiled = re.compile(self.formatted, self.flags)
        return self

    def __eq__(self, other):

        return bool(self.method(other))

    def __repr__(self):

        return f"{self.__class__.__name__}({self.formatted!r})"


class Regex(ReprMixin, RegexMixin, Comparator):
    pass
