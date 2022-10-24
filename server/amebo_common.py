import datetime, time, json
from typing import Union, Any, Callable

try:
    from .prmp_hash import PRMP_Hash
except:
    from prmp_hash import PRMP_Hash


def GET_BY_ATTR(
    sequence: Union[list, dict],
    validator: Callable[[Any], Any] = None,
    **attrs_values: dict[str, Any]
):
    if isinstance(sequence, dict):
        sequence = sequence.values()

    l = len(attrs_values)
    for obj in sequence:
        count = 0
        for attr, value in attrs_values.items():
            val = getattr(obj, attr, None)
            if val and validator:
                val = validator(val)

            if val == value:
                count += 1
            else:
                break

        if count == l:
            return obj


def GET(dict: dict, key: str):
    if isinstance(key, str):
        key = key.lower()
    return dict.get(key, None)


def TIME():
    return int(time.time())


def TIME2STRING(time: int):
    return datetime.datetime.fromtimestamp(time).strftime("%d/%m/%Y ... %H:%M %p")


class Json(dict):
    response: int

    def __getattr__(self, attr):
        return self.get(attr)

    def __setattr__(self, attr, value):
        self[attr] = value

    @classmethod
    def from_str(self, string: str):
        return json.loads(string or "{}", object_hook=Json)

    def to_str(self):
        return json.dumps(self)


LOWER_VALIDATOR = lambda dn: str(dn).lower()
