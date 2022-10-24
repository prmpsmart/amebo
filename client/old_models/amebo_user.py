from .amebo_profile import *


class AmeboMessageType:
    TEXT: int = 0
    AUDIO: int = 1
    IMAGE: int = 2
    VIDEO: int = 3


class AmeboUser(AmeboProfile):
    def __init__(
        self,
        id: int,
        created_at: int,
        display_name: str,
        description: str,
        avatar: str,
        unique_id: str,
        password: str,
    ):
        super().__init__(
            id, created_at, display_name, description, avatar, unique_id=unique_id
        )

        self.password = password
        self.last_seen: int = None

        # online if status_bool is True, offline if not.
        self.status: bool = False

        self.messages: dict[int, Json] = {}
        self.contacts: list[int] = []
        self.groups: list[int] = []
        self.broadcast_channels: list[int] = []

        self.banned_users: list[int] = []

    def add_message(self, json: Json):
        self.messages[json.id] = json

    def json(self) -> Json:
        return Json(
            last_seen=self.last_seen, status=self.status, **AmeboProfile.json(self)
        )

    def full_json(self) -> Json:
        from ..amebo import Amebo, AmeboGroup, AmeboBroadcastChannel

        contacts: list[AmeboUser] = []
        for contact in self.contacts:
            contact = Amebo.amebo_users[contact]
            contacts.append(contact.json())

        groups: list[AmeboGroup] = []
        for group in self.groups:
            group = Amebo.amebo_users[group]
            groups.append(group.json())

        broadcast_channels: list[AmeboBroadcastChannel] = []
        for broadcast_channel in self.broadcast_channels:
            broadcast_channel = Amebo.amebo_users[broadcast_channel]
            broadcast_channels.append(broadcast_channel.json())

        return Json(
            contacts=self.contacts,
            groups=self.groups,
            broadcast_channels=self.broadcast_channels,
            **self.json()
        )
