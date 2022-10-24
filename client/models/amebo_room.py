from .amebo_user import *
from .amebo_roles import *


class AmeboMember(IMember):
    def __init__(
        self,
        user: AmeboUser,
        room: "AmeboRoom",
        is_broadcast: bool,
    ) -> None:
        self.joined_at = time()
        self.user: AmeboUser = user
        self.roles: dict[str, AmeboMemberRole] = {}
        self.room: AmeboRoom = room
        self.is_broadcast = is_broadcast

    @property
    def permissions(self) -> set:
        perms = set()
        for role in self.roles:
            for permission in role.permissions:
                perms.add(permission)
        return perms

    def add_role(self, role: AmeboMemberRole):
        self.roles[role.unique_name] = role

    def delete_role(self, role: AmeboMemberRole):
        self.roles.pop(role.unique_name)

    def add_message(self, json: Json):
        self.user.add_message(json)

    @property
    def json(self) -> Json:
        return Json(id=self.id, created_at=self.created_at)


class AmeboRoomType(IRoomType):
    GROUP = 0
    SUB_GROUP = 1
    BROADCAST_CHANNEL = 2


class AmeboRoom(AmeboMiniProfile, IRoom):
    def __init__(self, display_name: str, description: str, avatar: str):
        AmeboMiniProfile.__init__(
            self, display_name=display_name, description=description, avatar=avatar
        )
        # the messages sent in this room.
        self.messages: dict[int, Json] = {}
        self.pinned_message: int = None
        self.members: list[AmeboMember]

    def set_pinned_message(self, message_id: int):
        self.pinned_message = GET(self.messages, message_id)

    def remove_pinned_message(self, message_id: int):
        self.pinned_message = None

    def add_message(self, json: Json):
        for member in self.members:
            member.add_message(json)

    def delete_message(self, message_id: int):
        self.messages.pop(message_id, None)


class AmeboSubRoom(AmeboRoom, ISubRoom):
    def __init__(
        self,
        room: "AmeboGroup",
        display_name: str,
        description: str,
        avatar: str,
        hidden: bool = False,
    ):
        AmeboRoom.__init__(
            self, display_name=display_name, description=description, avatar=avatar
        )

        self.room = room
        self.role: AmeboMemberRole = None
        self.hidden = hidden

    def set_role(self, role: AmeboMemberRole):
        self.role = role

    def set_hidden(self, hidden: bool):
        self.hidden = hidden

    @property
    def members(self) -> list[AmeboMember]:
        members: list[AmeboMember] = []
        for member in self.room.members.values():
            if self.role.unique_name in member.roles:
                members.append(member)

        return members


class AmeboGroup(AmeboRoom, IGroup):
    def __init__(
        self, creator: AmeboUser, display_name: str, description: str, avatar: str
    ):
        AmeboRoom.__init__(
            self, display_name=display_name, description=description, avatar=avatar
        )
        # list of the administators in this room.
        self.creator = creator
        # list of the roles in this room.
        self.roles: dict[str, AmeboMemberRole] = {MEMBER_ROLE.unique_name: MEMBER_ROLE}
        self.members: dict[int, AmeboMember] = {}
        # list of the sub rooms in this room.
        self.sub_rooms: dict[str, AmeboSubRoom] = {}
        self.invite_link: str = None
        self.banned_users: list[int] = []

    def generate_invite_link(self):
        ...

    def revoke_invite_link(self):
        if self.invite_link:
            ...

    @property
    def bots(self) -> dict:
        return {
            id: user for id, user in self.members.items() if isinstance(user, AmeboBot)
        }

    def create_sub_room(self, display_name: str, description: str, avatar: str):
        sub_room = AmeboSubRoom(
            display_name=display_name, description=description, avatar=avatar
        )
        self.sub_rooms[sub_room.unique_name] = sub_room

    def delete_sub_room(self, sub_room: AmeboSubRoom):
        self.sub_rooms.pop(sub_room.unique_name, None)
        # if sub_room_name in self.sub_rooms:
        #     del self.sub_rooms[sub_room_name]

    def add_user(self, user: Union[AmeboUser, AmeboBot]):
        self.members[user.id] = AmeboMember(
            user, self, isinstance(AmeboBroadcastChannel)
        )

    def delete_user(self, user: Union[AmeboUser, AmeboBot]):
        ...

    def add_role(self, display_name: str, description: str, avatar: str):
        role = AmeboMemberRole(
            display_name=display_name,
            description=description,
            avatar=avatar,
        )
        self.roles[role.unique_name] = role

    def delete_role(self, role: AmeboMemberRole):
        self.roles.pop(role.unique_name, None)


class AmeboBroadcastChannel(AmeboGroup, IBroadcastChannel):
    ...
