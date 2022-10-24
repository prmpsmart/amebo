from ..utils import *


class ChannelItem(QPushButton, SearchableItem):
    def __init__(self, channel_view: "ChannelsView", channel: Channel):
        QPushButton.__init__(self)
        SearchableItem.__init__(self)

        self.channel = channel
        self.channel_view = channel_view
        self.clicked.connect(channel_view.channel_item_selected)

        self.setMinimumWidth(self.channel_view.w - 50)
        self.setMaximumWidth(self.channel_view.w)

        m = 2

        lay = QHBoxLayout(self)

        self.avatar = AvatarButton(mask=51)
        self.avatar.setAttribute(Qt.WA_TransparentForMouseEvents)
        lay.addWidget(self.avatar)

        col = QVBoxLayout()
        lay.addLayout(col)

        row_1 = QHBoxLayout()
        col.addLayout(row_1)

        self.display_name = Label(name="display_name")
        row_1.addWidget(self.display_name)

        row_1.addStretch()

        self.time = Label(name="time")
        row_1.addWidget(self.time)

        row_2 = QHBoxLayout()
        row_2.setSpacing(3)
        col.addLayout(row_2)

        self.status = IconButton(
            icon="clock",
            icon_size=15,
            border=False,
            clickable=False,
        )
        row_2.addWidget(self.status)

        self.author = Label("You:", name="author")
        row_2.addWidget(self.author)

        self.last_chat = ChatTypeButton()
        row_2.addWidget(self.last_chat)

        row_2.addStretch()

        self.unreads = ColorfulTag(name="blue")
        self.unreads.setAlignment(Qt.AlignCenter)
        row_2.addWidget(self.unreads)

        self.pin = IconButton(
            icon="pin", icon_size=20, name="pin", border=False, clickable=False
        )
        row_2.addWidget(self.pin)

        for a in (self.status, self.pin):
            a.setAttribute((Qt.WA_TransparentForMouseEvents))

        for l in (lay, row_2, row_2, col):
            l.setContentsMargins(m, m, m, m)

        for l in (
            self.unreads,
            self.pin,
            self.time,
            self.author,
            self.last_chat,
            self.status,
        ):
            l.hide()

        self.load()
        self.avatar_timer_id = self.startTimer(10)

    def load(self):
        self.display_name.setText(self.channel.display_name or self.channel.unique_id)

        if unreads := self.channel.unreads:
            self.unreads.setText(str(unreads) if unreads < 100 else "99+")
            self.unreads.show()
        else:
            self.unreads.hide()

        if self.channel.pin:
            self.pin.show()
        else:
            self.pin.hide()

        if last_chat := self.channel.last_chat:
            if last_chat.isMe:
                self.status.setIcon(
                    ":/check" if last_chat.sent else ":/clock",
                )
                self.status.show()
                author = "You"
            else:
                self.status.hide()
                author = (
                    last_chat.author
                    if self.channel.channel_type == ChannelType.Group
                    else ""
                )

            if author:
                self.author.setText(f"{author}:")
            self.author.setVisible(bool(author))

            self.last_chat.load_chat(last_chat)
            self.last_chat.show()

            self.time.setText(last_chat.day_str)
            self.time.show()
        else:
            self.status.hide()
            self.author.hide()
            self.last_chat.hide()
            self.time.hide()

    def search(self, text: str) -> bool:
        text = text.lower()

        searchables = [
            self.channel.description,
            self.channel.display_name,
            str(self.channel.unique_id),
            self.channel.last_chat.text,
        ]

        for searchable in searchables:
            if text in searchable.lower():
                return True

        return False

    def timerEvent(self, e: QTimerEvent) -> None:
        if e.timerId() == self.avatar_timer_id:
            self.avatar.setAvatar(self.channel.avatar)
            self.killTimer(self.avatar_timer_id)


class ChannelsList(SearchableList):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def arrange_items(self, items: list[ChannelItem]) -> list[ChannelItem]:
        pinned = [chat_item for chat_item in items if chat_item.channel.pin]
        pinned.sort(key=lambda item: item.channel.pin)
        items = [chat_item for chat_item in items if chat_item not in pinned]
        return pinned + items


class ChannelsView(View, VFrame):
    def __init__(self, *args, **kwargs):
        VFrame.__init__(self, **kwargs)
        View.__init__(self, *args)

        self.w = 300
        self.setMinimumWidth(self.w)
        self.setMaximumWidth(self.w)

        lay = self.layout()
        m = 5
        lay.setContentsMargins(m, m, m, m)

        top_lay = QHBoxLayout()
        lay.addLayout(top_lay)

        self.menu_button = IconTextButton(icon="menu")
        self.menu_button.clicked.connect(self.open_menu)
        top_lay.addWidget(self.menu_button)

        self.search_line_edit = LineEdit(
            name="search_line_edit", placehoder="Search ..."
        )
        top_lay.addWidget(self.search_line_edit)

        self.hide_button = IconTextButton(icon="device-desktop-off")
        self.hide_button.clicked.connect(self.home.toggle_channels_view)
        top_lay.addWidget(self.hide_button)

        self.channels_list = ChannelsList()
        lay.addWidget(self.channels_list)
        self.search_line_edit.textEdited.connect(self.channels_list.search)

        self.channels = []

        self.fillChannels(DMS)

    def fillChannels(self, channels: list[Channel]):
        if channels == self.channels:
            return

        self.channels = channels
        self.channels_list.deleteItems()
        self.channels_list.fillItems(
            [ChannelItem(self, channel) for channel in channels]
        )

    def open_menu(self):
        self.home.open_menu()

    def channel_item_selected(self):
        chat_item: ChannelItem = self.sender()
        self.home.channel_item_selected(chat_item)

    def showEvent(self, event: PySide6.QtGui.QShowEvent) -> None:
        # self.home.channel_item_selected(self.channels_list.arranged_items[0])
        ...
