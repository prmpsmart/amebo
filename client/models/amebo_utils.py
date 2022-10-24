from typing import Union, Any, Callable


class Json(dict):
    response: int

    def __getattr__(self, attr):
        return self.get(attr, self.__class__())

    def __setattr__(self, attr, value):
        self[attr] = value


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
        for attr, value in attrs_values.values():
            val = getattr(obj, attr, None)
            if val and validator:
                val = validator(val)

            if val == value:
                count += 1
            else:
                break

        if count == l:
            return obj


def GET(dict: dict, key: Union[int, str]):
    if isinstance(key, str):
        key = key.lower()

    return dict.get(key, None)


LOWER_VALIDATOR = lambda dn: str(dn).lower()
