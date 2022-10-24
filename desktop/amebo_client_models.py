import pickle, os
from amebo_common import *


class AmeboObject:
    PRIME = 13

    def __init__(self, id: int, created_at: int = 0):
        # a unique value across all the server.
        assert id
        self.id = id
        # the time this user was created.
        self.created_at = created_at or TIME()

    @property
    def json(self) -> Json:
        return Json(id=self.id, created_at=self.created_at)

    def __bool__(self):
        return True


class AmeboProfile(AmeboObject):
    def __init__(
        self,
        *args,
        display_name: str,
        description: str,
        avatar: str,
        unique_id: str,
    ):
        AmeboObject.__init__(self, *args)

        # as the name implies.
        self.display_name = display_name
        self.description = description
        # the profile image maybe later we can add cover_image
        #  and slide_images like telegram.
        self.avatar = avatar
        assert unique_id
        self.unique_id = unique_id

    @property
    def unique_name(self):
        return self.display_name.lower()

    def edit(self, display_name: str = "", description: str = "", avatar: str = ""):
        if display_name:
            self.display_name = display_name
        if description:
            self.description = description
        if avatar:
            self.avatar = avatar

    @property
    def json(self) -> Json:
        return Json(
            unique_id=self.unique_id,
            display_name=self.display_name,
            description=self.description,
            avatar=self.avatar,
        )


class AmeboMessage(AmeboObject):
    TEXT: int = 0
    AUDIO: int = 1
    IMAGE: int = 2
    VIDEO: int = 3

    def __init__(
        self,
        author: int,
        type: int,
        text: str,
        attachment: str,
        attachment_type: str,
        reply_chat_id: str,
        status: bool,
        forwarded: bool,
        forwarder: str,
        forwarded_at: datetime,
        forwarded_from: int,
        members_seen: set[int],
        members_read: set[int],
    ) -> None:

        self.author = author
        self.type = type
        self.text = text
        self.attachment = attachment
        self.attachment_type = attachment_type
        self.reply_chat_id = reply_chat_id
        self.status = status
        self.forwarded = forwarded
        self.forwarder = forwarder
        self.forwarded_at = forwarded_at
        self.forwarded_from = forwarded_from

        self.members_seen = members_seen
        self.members_read = members_read


class AmeboChannel(AmeboProfile):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # chats | messages


class AmeboContact(AmeboChannel):
    ...


class AmeboGroup(AmeboChannel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # members, pinned messages, banned members, creator


class AmeboBroadcastChannel(AmeboGroup):
    ...


class AmeboUser(AmeboProfile):
    def __init__(self, *args, password: str, status: bool, **kwargs):
        super().__init__(*args, **kwargs)

        assert password
        self.password = password
        self.last_seen: int = 0

        # online if status_bool is True, offline if not.
        self.status: bool = status

        self.messages: dict[int, Json] = {}
        self.contacts: dict[int, AmeboContact] = {}
        self.groups: dict[int, AmeboGroup] = {}
        self.broadcast_channels: dict[int, AmeboBroadcastChannel] = {}

        self.banned_users: dict[int, AmeboContact] = {}

    @property
    def last_seen_string(self):
        return TIME2STRING(self.last_seen)
        string = "Offline"
        if self.last_seen:
            string = TIME2STRING(self.last_seen)
        return string

    def add_message(self, json: Json):
        self.messages[json.id] = json

    @property
    def json(self) -> Json:
        return Json(
            last_seen=self.last_seen, status=self.status, **AmeboProfile.json(self)
        )


class AmeboClientData:
    USER: AmeboUser = None
    DB_FILE = "amebo.dump"

    @classmethod
    def file(cls, mode: str):
        f = os.path.join(os.path.dirname(__file__), cls.DB_FILE)
        return open(f, mode)

    @classmethod
    def rfile(cls):
        return cls.file("rb")

    @classmethod
    def wfile(cls):
        return cls.file("wb")

    @classmethod
    def load(cls):
        try:
            json = pickle.load(cls.rfile())
            json = Json(json)
            cls.USER = json.user
        except Exception as e:
            print(e, "Data Read Error")

    @classmethod
    def save(cls):
        user = cls.user()
        status = user.status
        user.status = False
        user.status = status
        json = dict(
            user=user,
        )
        pickle.dump(json, cls.wfile())

    @classmethod
    def user(cls):
        if not cls.USER:
            cls.load()

        return cls.USER
