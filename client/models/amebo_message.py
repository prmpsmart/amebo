from .amebo_object import *


class AmeboMessageType:
    TEXT: int = 1
    IMAGE: int = 2
    AUDIO: int = 3
    VIDEO: int = 4


class AmeboMessage(AmeboObject):
    def __init__(
        self,
        *,
        type: AmeboMessageType,
        author: IUser,
        text: str,
        attachment: str,
        reply_message_id: Union[int, str] = "",
        forwarder: IUser = None,
        forwarded_at: datetime = None,
        forwarded_from: Union[IDirectMessage, IRoom] = None
    ):
        # whether this message is of type
        # [TEXT, IMAGE, AUDIO | VOICE, VIDEO].
        self.type = type

        # the author of the message.
        self.author = author

        # the text of the message.
        self.text = text

        # the [IMAGE, AUDIO | VOICE, VIDEO] data if type != TEXT.
        self.attachment = attachment

        # the list of mention users in the message
        # i.e ["<@natty>", "<@hakeem>"]
        self.mentions: list[str] = []

        # the id of the message this message is replying to.
        self.reply_message_id = reply_message_id

        # whether message is read or not.
        self.status: bool = None

        # describes whether message is forwarded
        self.forwarded: bool = bool(forwarder)
        if self.forwarded:
            assert forwarder and forwarded_at and forwarded_from

        # the user that forwarded this message
        self.forwarder = forwarder

        # the time that this message is forwarded last
        self.forwarded_at = forwarded_at

        # the dm or room that this message is forwarded from
        self.forwarded_from = forwarded_from

        # the members that the messages was delivered to.
        self.members_delivered_to: list[str, int] = []

        # the members that read the messages.
        self.members_read: list[str, int] = []


class AmeboDMMessage(AmeboMessage):
    def __init__(self, *, recipient: IUser, dm: IDirectMessage, **kwargs):
        super().__init__(**kwargs)

        # the recipient of the message.
        self.recipient = recipient

        # the dm that this message is sent.
        self.dm = dm


class AmeboRoomMessage(AmeboMessage):
    def __init__(self, *, room: IRoom, **kwargs):
        super().__init__(**kwargs)

        # the room that this message is sent or forwarded.
        self.room = room


class AmeboGroupMessage(AmeboMessage):
    def __init__(self, group: IGroup):

        self.group = group


class AmeboChannelMessage(AmeboMessage):
    def __init__(self, channel: IBroadcastChannel):

        self.channel: IBroadcastChannel = channel
