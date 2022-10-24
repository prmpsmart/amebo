from ..utils import *


class ChatWidget:
    def __init__(self: QWidget, chat: Chat):
        self.chat = chat
        self.setSizePolicy(POLICY)
        self.setContentsMargins(0, 0, 0, 0)


class TextChat(ChatWidget, Label):
    def __init__(self, *args) -> None:
        Label.__init__(self)
        ChatWidget.__init__(self, *args)

        self.setText(self.chat.text)
        # self.setText(
        #     f"{self.chat.text}{self.chat.text}{self.chat.text} {self.chat.text}\n"
        # )
        self.setWordWrap(True)
        self.setTextFormat(Qt.RichText)
        self.setTextInteractionFlags(
            Qt.LinksAccessibleByMouse | Qt.TextSelectableByMouse
        )


class ImageChat(ChatWidget, VFrame):
    def __init__(self, *args) -> None:
        VFrame.__init__(self)
        ChatWidget.__init__(self, *args)

        lay = self.layout()
        lay.setSpacing(0)
        m = 2
        lay.setContentsMargins(m, m, m, m)
        h = 0

        if self.chat.data:
            self.image = Label(name="image")
            w = 300
            self.image.setMaximumWidth(w)
            lay.addWidget(self.image)

            pixmap = PIXMAP(
                image_data=self.chat.data,
                icon=":/photo-off",
            ).scaledToWidth(w, Qt.SmoothTransformation)
            self.image.setScaledContents(True)

            self.image.setPixmap(pixmap)
            h = pixmap.height()

        if self.chat.text:
            self.text = TextChat(self.chat)
            lay.addWidget(self.text)
            h += self.text.minimumHeight()


class VoiceChat(ChatWidget, VoicePlayer):
    def __init__(self, chat: Chat) -> None:
        VoicePlayer.__init__(
            self,
            seekerColor=QColor("#4c4c71" if chat.isMe else "#96694e"),
            bytes=chat.data,
        )
        ChatWidget.__init__(self, chat)


class AudioChat(VoiceChat):
    ...


ChatWidgets = {
    ChatType.Text: TextChat,
    ChatType.Image: ImageChat,
    ChatType.Voice: VoiceChat,
    ChatType.Audio: AudioChat,
}


class ReplyChat(Button):
    def __init__(self, chat: Chat = None, **kwargs):
        super().__init__(**kwargs)

        self.chat: Chat = chat
        self.h = 45
        self.setMinimumHeight(self.h)
        self.setMaximumHeight(self.h)

        lay = QHBoxLayout(self)
        lay.setSpacing(0)
        lay.setContentsMargins(0, 0, 0, 0)

        details_lay = QVBoxLayout()
        details_lay.setSpacing(0)
        details_lay.setContentsMargins(5, 0, 0, 0)
        lay.addLayout(details_lay)

        self.author = Label(name="reply_author")
        details_lay.addWidget(self.author)

        self.chat_type_button = ChatTypeButton()
        details_lay.addWidget(self.chat_type_button)
        details_lay.addStretch()

        self.photo = IconTextButton(self.h, clickable=False, name="photo")
        lay.addWidget(self.photo)

        if chat:
            self.load_chat(chat)

    def load_chat(self, chat: Chat):
        self.author.setText("You" if chat.isMe else chat.author)
        self.chat_type_button.load_chat(chat)
        self.photo.setVisible(chat.chat_type == ChatType.Image)

        if chat.chat_type == ChatType.Image:
            pixmap = PIXMAP(chat.data, "photo-off")
            pixmap = pixmap.scaled(
                QSize(50, self.height()), Qt.IgnoreAspectRatio, Qt.SmoothTransformation
            )
            self.photo.setIcon(QIcon(pixmap))
        self.chat = chat


class ChatItem(SearchableItem, VFrame):

    STATUS_ICONS = {}

    def __init__(self, chats_list: "ChatsList", chat: Chat, reply_chat: Chat = None):
        SearchableItem.__init__(self)
        VFrame.__init__(self, name="right" if chat.isMe else "left")
        self.chats_list = chats_list

        if not ChatItem.STATUS_ICONS:
            ChatItem.STATUS_ICONS = {
                "sending": QIcon(":/clock"),
                "sent": QIcon(":/check"),
                "delivered": QIcon(":/checks"),
                "seen": QSvgIcon(":/eye-check", color=Qt.blue),
            }

        self.chat = chat
        lay = self.layout()
        lay.setSpacing(0)
        lay.setContentsMargins(0, 0, 0, 0)

        self.name = None

        if chat.channel_type == ChannelType.Group and not chat.isMe:
            name_lay = QHBoxLayout()
            name_lay.setSpacing(0)
            name_lay.setContentsMargins(0, 0, 0, 0)
            lay.addLayout(name_lay)

            self.name = Label(text=chat.author, name="author")
            name_lay.addWidget(self.name)

            name_lay.addStretch()
            lay.addSpacing(10)

        self.reply_chat: ReplyChat = None
        if reply_chat:
            self.reply_chat = ReplyChat(reply_chat)
            lay.addWidget(self.reply_chat)

        self.chat_widget: ChatWidget = ChatWidgets[chat.chat_type](chat)
        lay.addWidget(self.chat_widget)

        bottom = HFrame(name="bottom")
        lay.addWidget(bottom)

        bottom_lay = bottom.layout()
        m = 0
        bottom_lay.setContentsMargins(m * 2, 0, m * 2, m * 2)
        bottom_lay.setSpacing(m)

        bottom_lay.addStretch()

        self.starred = ChatIcon(icon="star", name="starred")
        bottom_lay.addWidget(self.starred)

        self.date_time = Label(text=chat.date_time, name="date_time")
        bottom_lay.addWidget(self.date_time)

        if chat.isMe:
            self.status = ChatIcon(self.STATUS_ICONS[chat.status], name="status")
            bottom_lay.addWidget(self.status)

        self.load()

        misi = lay.minimumSize()
        width, height = misi.toTuple()

        if chat.chat_type == ChatType.Audio:
            height = 70

        if chat.chat_type == ChatType.Text:
            height += 10
            width += 10

        self.setMinimumWidth(width)
        self.setMaximumHeight(height)

        chats_list.resized.connect(self.on_chats_list_resized)

    def load(self):
        self.starred.setVisible(self.chat.starred)
        if self.chat.isMe:
            self.status.setIcon(self.STATUS_ICONS[self.chat.status])

    def on_chats_list_resized(self):
        width = self.chats_list._widget.width() * 0.8
        self.setMaximumWidth(width)

        if self.chat.chat_type in [ChatType.Audio, ChatType.Voice]:
            self.setMinimumWidth(width)

    def mouseDoubleClickEvent(self, event: PySide6.QtGui.QMouseEvent) -> None:
        self.chats_list.room_view.set_footer_reply_chat(self.chat)

    def showEvent(self, event: PySide6.QtGui.QShowEvent) -> None:
        self.on_chats_list_resized()

    def search(self, text: str) -> bool:
        text = text.lower()

        searchables = [
            self.chat.author,
            self.chat.date_time,
            self.chat.text,
        ]

        for searchable in searchables:
            if text in searchable.lower():
                return True

        return False


class _RoomView(QWidget):
    def set_footer_reply_chat(self, chat: Chat):
        ...


class ChatsList(SearchableList):
    resized = Signal()

    def __init__(self, room_view: _RoomView, **kwargs):
        super().__init__(reverse=0, **kwargs)

        self.room_view = room_view
        self.hide_hbar()
        self.widgetLayout().setAlignment(Qt.AlignBottom)

    def add(self, item: ChatItem):
        super().add(
            item, stretch=1, alignment=Qt.AlignRight if item.chat.isMe else Qt.AlignLeft
        )

    def add_chat(self, chat: Chat, reply_chat: Chat = None):
        self.addItem(ChatItem(self, chat, reply_chat))

        QTimer.singleShot(100, lambda: self.scroll_down(0, self.maximumHeight()))

    def resizeEvent(self, arg__1: PySide6.QtGui.QResizeEvent) -> None:
        self._widget.setMaximumWidth(self.width())
        self.resized.emit()

    def fill(self, items: list[ChatItem]):
        items = self.arrange_items(items)

        for item in items:
            self.widgetLayout().addWidget(
                item,
                1,
                Qt.AlignBottom | (Qt.AlignRight if item.chat.isMe else Qt.AlignLeft),
            )
