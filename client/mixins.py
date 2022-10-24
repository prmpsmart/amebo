from typing import *
import os, re


class ClassMixins:
    containers = list, set, tuple

    def propertize(self, name: str):
        return name.lower().replace(" ", "_")

    @property
    def AlphabetsSwitch(self):
        d = {}
        for n in range(65, 91):
            d[chr(n)] = chr(n + 32)
            d[chr(n + 32)] = chr(n)
        return d

    def __bool__(self):
        return True

    @property
    def mroStr(self):
        return [s.__name__ for s in self.mro]

    @property
    def mro(self):
        return self.__class__.__mro__

    @property
    def class_(self):
        return self.__class__

    def attrError(self, attr):
        raise AttributeError('"{}" does not exist in {}'.format(attr, self))

    @property
    def className(self):
        return self.__class__.__name__

    def get_from_self(self, name, unget=None):
        ret = self.__dict__.get(name, unget)
        if ret != unget:
            return ret
        else:
            for cl in self.mro:
                ret = cl.__dict__.get(name, unget)
                if ret != unget:
                    return ret.__get__(self)
        return unget

    def __len__(self):
        return len(self[:])

    def __getitem__(self, item):
        if isinstance(item, str):
            return self.get_from_self(self.propertize(item))

        elif isinstance(item, self.containers):
            res = []
            for it in item:
                res.append(self[it])
            return res

        elif isinstance(item, dict):
            res = []
            for k, v in item.items():
                head = self[k]
                if isinstance(v, dict):
                    tail = []
                    tail_props = [(g, h) for g, h in v.items()]
                    last = tail_props[-1]
                    count = 0
                    length_of_tail_props = len(tail_props)
                    while count < length_of_tail_props:
                        tail_prop = tail_props[count]
                        try:
                            tail_1 = head[tail_prop[0]]
                        except:
                            tail_1 = getattr(head, tail_prop[0])

                        try:
                            tail_2 = tail_1[tail_prop[1]]
                        except:
                            tail_2 = getattr(tail_1, tail_prop[1])

                        tail.append(tail_2)
                        count += 1
                else:
                    if head:
                        try:
                            tail = head[v]
                        except:
                            tail = getattr(head, v)
                    else:
                        self.attrError(k)
                res.append(tail)
            return res if len(res) > 1 else res[0]

        if hasattr(self, "subs"):
            return self.subs[item]
        else:
            return None
