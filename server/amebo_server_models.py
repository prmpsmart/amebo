from .amebo_common import *


class AmeboObject:
    PRIME = 13

    def __init__(self):
        # a unique value across all the server.
        self.id = PRMP_Hash.gen_id(AmeboObject.PRIME, True)
        # the time this user was created.
        self.created_at = TIME()

    @property
    def json(self) -> Json:
        return Json(id=self.id, created_at=self.created_at)

    def __bool__(self):
        return True


class AmeboProfile(AmeboObject):
    def __init__(
        self,
        display_name: str,
        description: str,
        avatar: str,
        unique_id: str,
    ):
        AmeboObject.__init__(self)

        # as the name implies.
        self.display_name = display_name
        self.description = description
        # the profile image maybe later we can add cover_image
        #  and slide_images like telegram.
        self.avatar = avatar
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
            **super().json
        )


class AmeboUser(AmeboProfile):
    def __init__(
        self,
        display_name: str,
        description: str,
        avatar: str,
        unique_id: str,
        password: str,
    ):
        super().__init__(display_name, description, avatar, unique_id=unique_id)

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

    @property
    def json(self) -> Json:
        return Json(
            last_seen=self.last_seen,
            status=self.status,
            **super().json,
            password=self.password
        )

    @property
    def full_json(self) -> Json:
        contacts: list[AmeboUser] = []
        for contact in self.contacts:
            contact = Amebo.amebo_users[contact]
            contacts.append(contact.json)

        groups: list[AmeboGroup] = []
        for group in self.groups:
            group = Amebo.amebo_users[group]
            groups.append(group.json)

        broadcast_channels: list[AmeboBroadcastChannel] = []
        for broadcast_channel in self.broadcast_channels:
            broadcast_channel = Amebo.amebo_users[broadcast_channel]
            broadcast_channels.append(broadcast_channel.json)

        return Json(
            contacts=self.contacts,
            groups=self.groups,
            broadcast_channels=self.broadcast_channels,
            **self.json
        )


class AmeboChat(AmeboObject):
    def __init__(self, json: Json):
        super().__init__(json.id)

        self._json = json

        # the members that the messages was delivered to.
        self.members_delivered_to: list[str] = []

        # the members that read the messages.
        self.members_read: list[str] = []


class AmeboGroup(AmeboProfile):
    def __init__(
        self, creator: AmeboUser, display_name: str, description: str, avatar: str
    ):
        AmeboProfile.__init__(
            self, display_name=display_name, description=description, avatar=avatar
        )
        # the messages sent in this room.
        self.messages: dict[int, Json] = {}
        self.creator = creator
        self.chats: list[AmeboChat] = []
        self.pinned_message: int = None

        self.members: dict[str, AmeboMember] = {
            creator.id: AmeboMember(creator, self, True)
        }
        self.invite_link: str = None
        self.banned_users: list[str] = []

    def set_pinned_message(self, message_id: int):
        self.pinned_message = GET(self.messages, message_id)

    def remove_pinned_message(self, message_id: int):
        self.pinned_message = None

    def add_message(self, json: Json):
        for member in self.members:
            member.add_message(json)

    def delete_message(self, message_id: int):
        self.messages.pop(message_id, None)

    @property
    def admins(self):
        return {member.id: member for member in self.members if member.is_admin}

    def generate_invite_link(self):
        ...

    def revoke_invite_link(self):
        if self.invite_link:
            ...

    def add_user(self, user: AmeboUser):
        self.members[user.id] = AmeboMember(
            user, self, isinstance(self, AmeboBroadcastChannel)
        )

    def delete_user(self, user: AmeboUser):
        ...


class AmeboBroadcastChannel(AmeboGroup):
    ...


class AmeboMember:
    def __init__(
        self,
        user: AmeboUser,
        room: "AmeboGroup",
        is_broadcast: bool,
    ) -> None:
        self.joined_at = time()
        self.user: AmeboUser = user
        self.room: AmeboGroup = room
        self.is_broadcast = is_broadcast
        self.is_admin = False

    def add_message(self, json: Json):
        self.user.add_message(json)

    @property
    def json(self) -> Json:
        return Json(id=self.id, created_at=self.created_at, **self.user.json)


class Amebo:
    amebo_users: dict[int, AmeboUser] = {}
    amebo_groups: dict[int, AmeboGroup] = {}
    amebo_broadcast_channels: dict[int, AmeboBroadcastChannel] = {}

    @classmethod
    def create_user(cls, **kwargs) -> AmeboUser:
        user = AmeboUser(**kwargs)
        cls.amebo_users[user.id] = user
        return user

    @classmethod
    def create_group(cls, creator: AmeboUser, **kwargs):
        ...

    @classmethod
    def create_broadcast_channel(cls, creator: AmeboUser, **kwargs):
        ...

    @classmethod
    def delete_user(cls, user: AmeboUser):
        ...

    @classmethod
    def delete_group(cls, group: AmeboGroup):
        ...

    @classmethod
    def delete_broadcast_channel(cls, broadcast_channel: AmeboBroadcastChannel):
        ...

    @classmethod
    def unique_id_exist(cls, unique_id: str):
        user = GET_BY_ATTR(
            cls.amebo_users, validator=LOWER_VALIDATOR, unique_id=unique_id.lower()
        )
        if user:
            return user

        group = GET_BY_ATTR(
            cls.amebo_groups, validator=LOWER_VALIDATOR, unique_id=unique_id.lower()
        )
        if group:
            return group

        broadcast_channel = GET_BY_ATTR(
            cls.amebo_broadcast_channels,
            validator=LOWER_VALIDATOR,
            unique_id=unique_id.lower(),
        )
        if broadcast_channel:
            return broadcast_channel

        return False

    @classmethod
    def get_user(cls, validator=None, **attrs_values: dict[str, Any]) -> AmeboUser:
        return GET_BY_ATTR(cls.amebo_users, validator=validator, **attrs_values)

    @classmethod
    def get_group(cls, validator=None, **attrs_values: dict[str, Any]):
        return GET_BY_ATTR(cls.amebo_groups, validator=validator, **attrs_values)

    @classmethod
    def get_broadcast_channel(cls, validator=None, **attrs_values: dict[str, Any]):
        return GET_BY_ATTR(
            cls.amebo_broadcast_channels, validator=validator, **attrs_values
        )

    @classmethod
    def get_room(self, json: Json) -> Union[AmeboGroup, AmeboBroadcastChannel]:
        room_id = json.room_id
        is_broadcast = json.is_broadcast
        if room_id and is_broadcast:
            rooms = (
                Amebo.amebo_groups
                if not is_broadcast
                else Amebo.amebo_broadcast_channels
            )
            return GET(rooms, room_id)
