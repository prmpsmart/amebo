from .amebo_profile import *


class AmeboMessageType(IMessageType):
    TEXT: int = 0
    AUDIO: int = 1
    IMAGE: int = 2
    VIDEO: int = 3


class AmeboMessage(IMessage):
    def __init__(
        self,
        author: "AmeboUser",
        type: AmeboMessageType,
        text: str,
        attachment: STR_BYTES,
        attachment_type: str,
        reply_chat_id: str,
        status: bool,
        forwarded: bool,
        forwarder: IUser,
        forwarded_at: datetime,
        forwarded_from: Union["IDirectMessage", "IRoom"],
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


class AmeboUser(AmeboProfile, IUser):
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
        self.messages[json.message_id] = json

    def json(self) -> Json:
        return Json(
            last_seen=self.last_seen, status=self.status, **AmeboProfile.json(self)
        )


class AmeboBot(AmeboUser, IBot):
    def __init__(self, *args, api_key: str, **kwargs):
        super().__init__(*args, **kwargs)

        self.api_key = api_key
