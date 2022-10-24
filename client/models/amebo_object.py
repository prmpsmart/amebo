from .stubs.chat_model_stub import *
from time import time


class AmeboObject(IObject):
    def __init__(self, id: Union[int, str]):

        # a unique value across all the server.
        self.id = id

        # the time this user was created.
        self.created_at = time()

    def json(self) -> Json:
        return Json(id=self.id, created_at=self.created_at)
