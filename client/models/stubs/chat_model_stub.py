from datetime import datetime
from ..amebo_utils import *

# I for interface

STR_INT = Union[str, int]
STR_BYTES = Union[str, bytes]


class IObject:
    # a unique value across all the server.
    id: STR_INT = ...
    # the time this user was created.
    created_at: datetime = ...


class IMiniProfile:
    # as the name implies.
    display_name: str = ...
    # the bio of the profile
    description: str = ...
    # the profile image maybe later we can add cover_image
    #  and slide_images like telegram.
    avatar: STR_BYTES = ...


class IProfile(IObject, IMiniProfile):
    unique_id: STR_INT = ...


class IMemberPermissions:
    # Manage room details and everyother thing in the room, the highest permission. Manage
    # everyother permissions in this room.
    MANAGE_ROOM: int = 0
    # Manage the roles in the room, add or delete roles, add or remove members to or from a role. Also manage the permissions of each roles.
    MANAGE_ROLES: int = 1
    # Manage messages in the room, delete messages or pin message.
    MANAGE_MESSAGES: int = 2
    # Manage members in the room, add or delete members to or from the room.
    MANAGE_MEMBERS: int = 3
    # Manage subgroups, add or delete subgroups, change avatar, name and description of subgroups
    MANAGE_SUBROOMS: int = 4
    # Have access to the room invite link, and can add members to the room, but can’t delete them from the room.
    MANAGE_INVITES: int = 5
    # Able to send messages in the room
    SEND_MESSAGES: int = 6
    # Make links send into the room clickable, when a member without this permission send a message that has a link in it, the link won’t be clickable from the app.
    EMBED_LINKS: int = 7
    # Able to send files into the room (images, audio, pdf, doc etc)
    ATTACH_FILES: int = 8


class IMemberRole(IMiniProfile):
    # permissions that this message has in a room,
    # whether, to message, edit room info, etc
    permissions: list[IMemberPermissions]


class IUser(IProfile):
    password: str = ...
    last_seen: datetime = ...
    # online if status_bool is True, offline if not.
    status: str = ...
    messages: dict[int] = ...
    messages: list[int] = ...
    contacts: list[int] = ...
    groups: list[int] = ...
    broadcast_channels: list[int] = ...
    banned_users: list[int] = ...


class IBot(IUser):
    api_key: str = ...


class IMember:
    joined_at: int = ...  # created_at
    user: IUser = ...
    # list of roles this member has, a member has the
    # IMemberRole.MEMBER role by default so far the member is a
    # member of the room
    roles: list[IMemberRole] = ...
    # the room that this member belongs to, whether a group or
    # channel.
    room: "IRoom" = ...
    # value that specify the type of room.
    is_broadcast: bool = ...


class IRoomType:
    GROUP = 0
    SUB_GROUP = 1
    BROADCAST_CHANNEL = 2


class IRoom(IMiniProfile):
    # the messages sent in this room.
    messages: dict[int, "IRoomMessage"] = ...
    pinned_message: "IRoomMessage" = ...
    members: list[IMember] = ...


class ISubRoom(IRoom):
    # the type of users that can access this subgroup are those with roles listed here.
    role: IMemberRole = ...
    # whether to hide from other roles except the assigned role
    hidden: bool = ...


class IGroup(IRoom):
    creator: Union[IUser, IMember] = ...
    # list of the roles in this room.
    roles: dict[int, IMemberRole] = ...
    members: list[IMember]
    # list of the sub rooms in this room.
    sub_rooms: dict[int, ISubRoom] = ...
    invite_link: str = ...
    banned_users: list[int] = ...


class IBroadcastChannel(IGroup):
    ...


class IMessageType:
    TEXT: int = 0
    AUDIO: int = 1
    IMAGE: int = 2
    VIDEO: int = 3


class IMessage(IObject):
    # the author of the message.
    author: IUser = ...
    # whether this message is of type
    # [TEXT, IMAGE, AUDIO | VOICE, VIDEO].
    type: IMessageType = ...
    # the text of the message.
    text: str = ...
    # the [IMAGE, AUDIO | VOICE, VIDEO] data if type != TEXT.
    attachment: STR_BYTES = ...
    attachment_type: str = ...
    # the list of users this message is mentioning
    # i.e ["<@natty>", "<@hakeem>"]
    reply_message_id: str = ...
    # whether message is read or not.
    status: bool = ...
    # describes whether message is forwarded
    forwarded: bool = ...
    # the user that forwarded this message
    forwarder: IUser = ...
    # the time that this message is forwarded last
    forwarded_at: datetime = ...
    # the dm or room that this message is forwarded from
    forwarded_from: Union["IDirectMessage", "IRoom"] = ...
    # the members that the messages was delivered to.
    members_seen: set[int] = ...
    # the members that read the messages.
    members_read: set[int] = ...


class IDirectMessage(IMessage):
    # the recipient of the message.
    recipient: IUser = ...


class IRoomMessage(IMessage):

    # the room that this message is sent or forwarded to.
    room: IRoom = ...
    is_broadcast: bool = ...


class ISubRoomMessage(IRoomMessage):
    sub_room: ISubRoom = ...
    main_room: Union[IGroup, IBroadcastChannel] = ...
