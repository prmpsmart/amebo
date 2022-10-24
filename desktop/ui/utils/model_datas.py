import datetime, enum
from typing import Union
from .images import *
from .commons import AudioWave


class ChatType(enum.Enum):
    Text = enum.auto()
    Image = enum.auto()
    Voice = enum.auto()
    Audio = enum.auto()
    File = enum.auto()


class ChannelType(enum.Enum):
    DM = enum.auto()
    Group = enum.auto()
    Broadcast = enum.auto()


class Chat:
    def __init__(
        self,
        chat_type=ChatType.Text,
        channel_type=ChannelType.DM,
        sent=False,
        author="Test Author",
        seen=False,
        delivered=False,
        text="",
        data="",
        isMe=False,
        time: datetime = None,
        starred=False,
    ) -> None:

        self.chat_type: ChatType = chat_type
        self.channel_type: ChannelType = channel_type
        self.sent: bool = sent
        self.author: str = author
        self.seen: bool = seen
        self.delivered: bool = delivered
        self.text: str = text
        self.data: str = data
        self.isMe: bool = isMe
        self.time = time or datetime.datetime.now()
        self.starred: bool = starred
        self.reply_chat_id = None

    @property
    def time_str(self):
        return self.time.strftime("%H:%M %p")

    @property
    def day_str(self):
        return self.time.strftime("%b %d")

    @property
    def date_time(self):
        return self.time.strftime("%d/%m/%Y ... %H:%M %p")

    @property
    def status(self) -> str:
        if not self.sent:
            return "sending"
        elif self.seen:
            return "seen"
        elif self.delivered:
            return "delivered"
        return "sent"


class Channel:
    def __init__(
        self,
        channel_type: ChannelType,
        display_name: str,
        unique_id: Union[str, int],
        password: str,
        description: str,
        avatar: str,
        last_chat: Chat,
        unreads: int = 0,
        pin: int = 0,
    ) -> None:

        self.channel_type: ChannelType = channel_type
        self.display_name: str = display_name
        self.unique_id: Union[str, int] = unique_id
        self.password: str = password
        self.description: str = description
        self.avatar: str = avatar
        self.last_chat: Chat = last_chat
        self.unreads: int = unreads
        self.pin: int = pin


test_mono = r"C:\Users\Administrator\Desktop\GITHUB_PROJECTS\audiowave\tests\assets\test_mono.wav"
test = r"C:\Users\Administrator\Desktop\GITHUB_PROJECTS\audiowave\tests\assets\test.wav"

CHATS: list[Chat] = [
    #    dm
    Chat(
        chat_type=ChatType.Text,
        channel_type=ChannelType.DM,
        sent=False,
        text="This is a text chat in a DM, sent by the user itself., not yet sent",
        data="",
        isMe=True,
    ),
    Chat(
        chat_type=ChatType.Image,
        channel_type=ChannelType.DM,
        sent=True,
        seen=True,
        text="This is an image chat in a DM, sent by the user itself, sent.",
        data=PEACHY,
        isMe=True,
    ),
    Chat(
        chat_type=ChatType.Text,
        channel_type=ChannelType.DM,
        sent=False,
        text="This is a text chat in a DM, sent by the contact.",
        data="",
        isMe=False,
    ),
    Chat(
        chat_type=ChatType.Image,
        channel_type=ChannelType.DM,
        sent=False,
        text="This is an image chat in a DM, sent by the contact.",
        data=PEACHY,
        isMe=False,
    ),
    Chat(
        chat_type=ChatType.Image,
        channel_type=ChannelType.DM,
        sent=False,
        text="This is an image with a text chat in a DM, sent by the user itself.",
        data=EYE,
        isMe=True,
    ),
    Chat(
        chat_type=ChatType.Voice,
        channel_type=ChannelType.DM,
        sent=False,
        data=AudioWave(file=test_mono).bytes,
        isMe=True,
    ),
    Chat(
        chat_type=ChatType.Voice,
        channel_type=ChannelType.DM,
        sent=False,
        data=AudioWave(file=test).bytes,
        isMe=False,
    ),
    #    group
    Chat(
        chat_type=ChatType.Text,
        channel_type=ChannelType.Group,
        sent=True,
        text="This is a text chat in a GROUP, sent by the user itself., not yet sent here",
        data="",
        isMe=True,
    ),
    Chat(
        chat_type=ChatType.Image,
        channel_type=ChannelType.Group,
        sent=True,
        text="This is an image chat in a GROUP, sent by the user itself, sent.",
        data=MIMI,
        isMe=True,
    ),
    Chat(
        chat_type=ChatType.Text,
        channel_type=ChannelType.Group,
        sent=False,
        text="This is a text chat in a GROUP, sent by the contact.",
        data="",
        isMe=False,
    ),
    Chat(
        chat_type=ChatType.Image,
        channel_type=ChannelType.Group,
        sent=False,
        text="This is an image 67",
        data=PEACHY,
        isMe=False,
    ),
    Chat(
        chat_type=ChatType.Image,
        channel_type=ChannelType.Group,
        sent=False,
        text="This is an image 90",
        data=EYE,
        isMe=True,
    ),
    # all features
    Chat(
        chat_type=ChatType.Image,
        channel_type=ChannelType.Group,
        sent=False,
        delivered=True,
        seen=True,
        text="This is an image with a text chat in a GROUP, sent by the user itself.",
        data=EYE,
        isMe=True,
    ),
    Chat(
        chat_type=ChatType.Voice,
        channel_type=ChannelType.Group,
        sent=True,
        delivered=True,
        data=AudioWave(file=test_mono).bytes,
        isMe=True,
    ),
    Chat(
        chat_type=ChatType.Text,
        channel_type=ChannelType.DM,
        sent=True,
        delivered=True,
        seen=True,
        text="This is an image with a text chat in a GROUP, sent by the user itself.",
        data=EYE,
        isMe=True,
        starred=True,
    ),
]

MIMI = EYE
CHANNELS: list[Channel] = [
    Channel(
        channel_type=ChannelType.DM,
        display_name="Prince",
        unique_id="prmpsmart",
        password="@prmpsmart",
        description="I love Aina",
        avatar=EYE,
        last_chat=CHATS[0],
        unreads=9,
    ),
    Channel(
        channel_type=ChannelType.DM,
        display_name="Miracy",
        unique_id="miracy",
        password="@miracy",
        description="It's just a crush",
        avatar=EYE,
        last_chat=CHATS[7],
        unreads=50,
        pin=2,
    ),
    Channel(
        channel_type=ChannelType.DM,
        display_name="Rocky",
        unique_id="rocky_m",
        password="@rockymiracy",
        description="I love Aina",
        avatar=PEACHY,
        last_chat=CHATS[2],
        unreads=9000,
        pin=4,
    ),
    Channel(
        channel_type=ChannelType.Group,
        display_name="Segun",
        unique_id="emasvp",
        password="unfanthomable",
        description="The beautifier, sweet voice.",
        avatar=MIMI,
        last_chat=CHATS[4],
    ),
    Channel(
        channel_type=ChannelType.Group,
        display_name="Lekan",
        unique_id="barrister",
        password="lekans",
        description="A barrister of a kind.",
        avatar=EYE,
        last_chat=CHATS[-7],
    ),
    Channel(
        channel_type=ChannelType.Group,
        display_name="Salvage",
        unique_id="salvie",
        password="mimi_crush",
        description="I love You.",
        avatar=PEACHY,
        last_chat=CHATS[7],
    ),
    Channel(
        channel_type=ChannelType.Broadcast,
        display_name="Prinzo",
        unique_id="prinzo",
        password="princy_jay",
        description="I think he likes Kemi, until later",
        avatar=EYE,
        last_chat=CHATS[5],
        pin=3,
    ),
    Channel(
        channel_type=ChannelType.Broadcast,
        display_name="Aina",
        unique_id="kemi_aina",
        password="kanai",
        description="A new babe I crush on.",
        avatar=MIMI,
        last_chat=CHATS[8],
        pin=1,
    ),
    Channel(
        channel_type=ChannelType.Broadcast,
        display_name="Adewale",
        unique_id="warrior",
        password="1906",
        description="A father figure.",
        avatar=EYE,
        last_chat=CHATS[5],
    ),
    Channel(
        channel_type=ChannelType.Group,
        display_name="Beatrice",
        unique_id="adbeakok",
        password="money_mum",
        description="My first love.",
        avatar=MIMI,
        last_chat=CHATS[5],
    ),
    # ?
    Channel(
        channel_type=ChannelType.DM,
        display_name="Kiki",
        unique_id="okiki",
        password="1906",
        description="A cousin bro.",
        avatar=EYE,
        last_chat=CHATS[6],
    ),
    Channel(
        channel_type=ChannelType.DM,
        display_name="Lola",
        unique_id="lollybabe",
        password="lolo_love",
        description="Someone that I should've known first.",
        avatar=PEACHY,
        last_chat=CHATS[1],
    ),
]

DMS = [channel for channel in CHANNELS if channel.channel_type == ChannelType.DM]
GROUPS = [channel for channel in CHANNELS if channel.channel_type == ChannelType.Group]
BROADCASTS = [
    channel for channel in CHANNELS if channel.channel_type == ChannelType.Broadcast
]
