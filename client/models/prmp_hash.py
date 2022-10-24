import secrets, time


class PRMP_Hash:
    MAX_64_INT = 2 ** 63 - 1
    MAX_32_INT = 2 ** 31 - 1

    def __init__(
        self, prime: int, inverse: int = None, random: int = None, bitlength: int = 64
    ) -> "PRMP_Hash":

        assert bitlength in (32, 64), "bitlength can only be 32 or 64"

        self.max_int = bitlength == 32 and self.MAX_32_INT or self.MAX_64_INT
        self.prime = prime
        self.inverse = inverse or self.mod_inverse(prime, self.max_int)
        self.random = random or self.rand_n(self.max_int - 1)

    def encode(self, n: int) -> int:
        return ((int(n) * self.prime) & self.max_int) ^ self.random

    def decode(self, n: int) -> int:
        return ((int(n) ^ self.random) * self.inverse) & self.max_int

    def mod_inverse(self, n: int, p: int) -> int:
        return pow(n, -1, p + 1)

    def rand_n(self, n: int) -> int:
        return secrets.randbelow(n) + 1

    @classmethod
    def gen_id(cls, prime: int = 7, trunc=False):
        c = cls(prime)
        t = time.time()
        if not trunc:
            t = int(str(t).replace(".", ""))
        return c.encode(t)
