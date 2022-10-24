from .chat import *
from .channels_view import *
import random


class HF:
    def __init__(self, room_view: "RoomView", h=50):
        self.h = h
        self.room_view = room_view
        self.set_h(h)

    def set_h(self: QWidget, h):
        self.setMinimumHeight(h)
        self.setMaximumHeight(h)


class ChatSearchDialog(Dialog):
    def __init__(self, textEdited: Callable[[str], None], **kwargs):
        super().__init__(add_shadow=1, **kwargs)

        lay = self.windowLayout()
        self.windowFrame().setStyleSheet("background: white;")

        self.search = LineEdit(name="search_dialog_search", placehoder="Search ...")
        self.search.textEdited.connect(textEdited)
        lay.addWidget(self.search)


class RoomMenuDialog(Dialog):
    def __init__(self, room_view: "RoomView", **kwargs):
        super().__init__(add_shadow=1, **kwargs)

        self.room_view = room_view

        lay = self.windowLayout()
        m = 2
        lay.setContentsMargins(m, m, m, m)
        self.windowFrame().setStyleSheet("VFrame{background: white;}")

        self.pinned_chats = IconTextButton(icon="pinned", text="Pinned Chats")
        lay.addWidget(self.pinned_chats)

        self.starred_chats = IconTextButton(icon="star", text="Starred Chats")
        lay.addWidget(self.starred_chats)

        self.clear_channels = IconTextButton(icon="trash", text="Clear Chats")
        lay.addWidget(self.clear_channels)

        self.block_user = IconTextButton(icon="user-off", text="Block User")
        lay.addWidget(self.block_user)

        self.leave_room = IconTextButton(icon="logout", text="Leave Room")
        lay.addWidget(self.leave_room)


class Header(HF, QPushButton):
    def __init__(self, *args, **kwargs):
        QPushButton.__init__(self, **kwargs)
        HF.__init__(self, *args, h=65)

        self.clicked.connect(self.room_view.toggle_details_view)

        lay = QHBoxLayout(self)

        m = 0
        lay.setContentsMargins(5, m, 5, m)
        lay.setSpacing(10)

        self.chat_search_dialog: ChatSearchDialog = None
        self.room_menu_dialog: RoomMenuDialog = None

        self.avatar = AvatarButton(mask=45)
        self.avatar.clicked.connect(self.room_view.home.toggle_room_view)
        lay.addWidget(self.avatar)

        col = QVBoxLayout()
        col.setContentsMargins(5, 10, 5, 10)
        col.setSpacing(2)
        lay.addLayout(col)

        self.display_name = Label(name="display_name")
        col.addWidget(self.display_name)

        self.status = Label(name="status")
        col.addWidget(self.status)

        lay.addStretch()

        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(2)
        lay.addLayout(row)

        self.notification = IconTextButton(icon="bell-off")
        self.notification.setCheckable(True)
        self.notification.toggle()
        self.notification.toggled.connect(self.toggle_notification)
        row.addWidget(self.notification)

        self.search = IconTextButton(icon="search")
        self.search.clicked.connect(self.toggle_chat_search_dialog)

        row.addWidget(self.search)

        self.room_menu = IconTextButton(icon="dots-vertical")
        self.room_menu.clicked.connect(self.toggle_room_menu_dialog)
        row.addWidget(self.room_menu)

    def load(self):
        if channel_item := self.room_view.channel_item:
            channel = channel_item.channel
            if channel.avatar:
                self.avatar.setIcon(channel_item.avatar.icon())

            self.display_name.setText(channel.display_name)
            if channel.channel_type == ChannelType.Broadcast:
                subs = random.randint(300, 12000)
                status = f"{subs} subscribers"
            elif channel.channel_type == ChannelType.Group:
                mems = random.randint(60, 300)
                status = f"{mems} members"
            elif channel.channel_type == ChannelType.DM:

                if random.randint(0, 1):
                    days = random.randint(1, 60)
                    last_login = datetime.datetime.now() - datetime.timedelta(days=days)
                    status = f'last login {last_login.strftime("%b %d")} members'
                else:
                    status = "Online"

            self.status.setText(status)

    def toggle_notification(self, toggled: bool):
        self.notification.setIcon("bell-off" if toggled else "bell")

    def toggle_room_menu_dialog(self):
        if not self.room_menu_dialog:
            self.room_menu_dialog = RoomMenuDialog(self, parent=self.window())

        MOVE_DIALOG_TO_CURSOR(self.room_menu_dialog, True)

    def toggle_chat_search_dialog(self):
        if not self.chat_search_dialog:
            self.chat_search_dialog = ChatSearchDialog(
                self.room_view.chats_list.search, parent=self.window()
            )

        MOVE_DIALOG_TO_CURSOR(self.chat_search_dialog, True)


class FooterReply(HF):
    def __init__(self: Union["FooterReply", QWidget], *args, chat: Chat = None):
        super().__init__(*args, h=60)

        self.room_view: RoomView

        self.cancel_button = IconTextButton(icon="x")
        self.cancel_button.clicked.connect(self.hide_footer)

        self.reply_chat = ReplyChat(chat=chat)
        m = 0
        self.reply_chat.clicked.connect(self.locate)
        self.layout().setContentsMargins(m, m, m, m)
        self.min_height = 0

    @property
    def chat(self):
        return self.reply_chat.chat

    def load_chat(self, chat: Chat):
        self.reply_chat.load_chat(chat)
        self.show()

    def locate(self):
        ...

    def hide_footer(self: Union["FooterReply", QWidget]):
        self.close()
        footer = self.room_view.footer
        lay = footer.layout()

        f = self.height()

        h = footer.height() - f
        m = lay.contentsMargins()
        m.setTop(5)
        lay.setContentsMargins(m)
        h += 5

        footer.set_h(h)

        footer.text_input.min_height = self.min_height
        footer.text_input.max_height -= f

    def showEvent(self, _):
        footer = self.room_view.footer
        lay = footer.layout()
        m = lay.contentsMargins()
        m.setTop(0)
        lay.setContentsMargins(m)

        self.min_height = footer.text_input.min_height
        h = self.height()
        footer.text_input.min_height += h
        footer.text_input.max_height += h

        footer.set_h(footer.height() + h)


class TelegramFooterReply(FooterReply, HFrame):
    def __init__(self, *args):
        HFrame.__init__(self)
        FooterReply.__init__(self, *args)

        lay = self.layout()
        self.locate_button = IconTextButton(icon="arrow-forward-up")
        self.locate_button.clicked.connect(self.locate)
        lay.addWidget(self.locate_button)
        lay.addWidget(self.reply_chat)
        lay.addWidget(self.cancel_button)


class WhatsAppFooterReply(FooterReply, VFrame):
    def __init__(self, *args):
        VFrame.__init__(self)
        FooterReply.__init__(self, *args)

        self.reply_chat.setObjectName("WhatsApp")
        lay = self.layout()
        lay.addWidget(self.reply_chat)
        self.cancel_button.setParent(self.reply_chat)
        self.cancel_button.setIconSize(QSize(15, 15))
        self.cancel_button.setObjectName("WhatsApp_cancel")

        self.m = None

    def hide_footer(self):
        self.room_view.footer.vframe.setObjectName("WhatsApp_frame")
        if self.m:
            self.room_view.footer.vframe.layout().setContentsMargins(self.m)
        return super().hide_footer()

    def showEvent(self, e):
        self.room_view.footer.vframe.setObjectName("WhatsApp_frame_reply")
        self.m = self.room_view.footer.vframe.layout().contentsMargins()

        m = QMargins(self.m)
        m.setTop(0)
        self.room_view.footer.vframe.layout().setContentsMargins(m)

        return super().showEvent(e)

    def resizeEvent(self, event: PySide6.QtGui.QResizeEvent) -> None:
        size = self.reply_chat.size()
        i = self.cancel_button.iconSize()
        x = size.width() - i.width() - 2
        self.cancel_button.setGeometry(x, 2, i.width(), i.height())


class CameraPhotoDialog(Dialog):
    def __init__(self, footer: "Footer", **kwargs):
        super().__init__(add_shadow=1, **kwargs)

        self.footer = footer

        lay = self.windowLayout()
        m = 2
        lay.setContentsMargins(m, m, m, m)
        self.windowFrame().setStyleSheet("VFrame{background: white;}")

        self.photo = IconTextButton(icon="photo", text="Pictures")
        lay.addWidget(self.photo)

        self.camera = IconTextButton(icon="camera", text="Camera Capture")
        lay.addWidget(self.camera)


class Footer(HF, VFrame):
    def __init__(self, *args, **kwargs):
        VFrame.__init__(self, **kwargs)
        HF.__init__(self, *args)

        lay = self.layout()
        m = 5
        m = 0
        lay.setSpacing(m)
        lay.setContentsMargins(m, m, m, m)

        self.text_frame = VFrame(name="text_frame")
        text_lay = self.text_frame.layout()

        m = 5
        text_lay.setSpacing(m)
        text_lay.setContentsMargins(m, m, m, m)
        lay.addWidget(self.text_frame)

        self.smile = IconTextButton(icon="mood-smile")
        self.text_input = TextInput(
            self,
            min_height=50,
            max_height=200,
        )
        self.link = IconTextButton(icon="link")
        self.link.clicked.connect(self.on_link)

        self.microphone = IconTextButton(icon="microphone")
        self.microphone.clicked.connect(self.on_microphone)

        self.send = IconTextButton(icon="send")
        self.send.hide()
        self.send.clicked.connect(self.on_send)

        self.camera_photo_dialog: CameraPhotoDialog = None
        self.photo = IconTextButton(icon="photo")
        self.photo.clicked.connect(self.toggle_camera_photo_dialog)
        self.photo.hide()

        self.footer_reply: Union[TelegramFooterReply, WhatsAppFooterReply] = None

        self.text_bottom_lay = QHBoxLayout()
        self.text_bottom_lay.addWidget(self.smile)
        self.text_bottom_lay.addWidget(self.text_input)
        self.text_bottom_lay.addWidget(self.link)
        self.text_bottom_lay.addWidget(self.photo)
        self.text_bottom_lay.addWidget(self.microphone)
        self.text_bottom_lay.addWidget(self.send)

        self.voice_frame = VFrame(name="voice_frame")
        lay.addWidget(self.voice_frame)
        self.voice_frame.hide()
        self.voice_frame.setMaximumHeight(120)

        voice_lay = self.voice_frame.layout()
        m = 5
        voice_lay.setSpacing(m * 2)
        voice_lay.setContentsMargins(m, m, m, m)

        top_lay = QHBoxLayout()
        voice_lay.addLayout(top_lay)

        self.recording_frame = HFrame(name="recording_frame")
        top_lay.addWidget(self.recording_frame)
        recording_lay = self.recording_frame.layout()

        self.recording_time = Label("0:28", name="voice_time")
        recording_lay.addWidget(self.recording_time)

        self.recording_waveform = VoiceWaveform(
            bytes=CHATS[-2].data,
            avgColor=Qt.black,
        )
        recording_lay.addWidget(self.recording_waveform)

        self.voice_player = VoicePlayer(bytes=CHATS[-2].data)
        self.voice_player.hide()
        top_lay.addWidget(self.voice_player)

        self.playing_time = Label("0:47", name="voice_time")
        self.voice_player.layout().addWidget(self.playing_time)

        for lay in (recording_lay,):
            lay.setSpacing(m)
            lay.setContentsMargins(m, m, m, m)

        self.voice_bottom_lay = QHBoxLayout()
        voice_lay.addLayout(self.voice_bottom_lay)

        self.delete_recorded = IconTextButton(
            icon="trash", name="recording_control_button"
        )
        self.delete_recorded.clicked.connect(self.on_delete_recorded)
        self.voice_bottom_lay.addWidget(self.delete_recorded)

        self.record = IconTextButton(
            icon="microphone", iconColor=Qt.red, name="recording_control_button"
        )
        self.record.clicked.connect(self.on_record)
        self.voice_bottom_lay.addWidget(self.record)

        self.stop_record = IconTextButton(
            icon="pause", iconColor=Qt.red, name="recording_control_button"
        )
        self.stop_record.hide()
        self.stop_record.clicked.connect(self.on_stop_record)
        self.voice_bottom_lay.addWidget(self.stop_record)

        # self.setupTelegram()
        self.setupWhatsApp()

        if self.footer_reply:
            self.footer_reply.hide()

    def on_link(self):
        ...

    def on_microphone(self):
        self.voice_bottom_lay.addWidget(self.send)
        self.send.show()
        self.text_frame.hide()
        self.voice_frame.show()
        self.setMaximumHeight(self.voice_frame.maximumHeight() + 5)

    def on_send(self):
        if text := self.text_input.text:
            chat = CHATS[0]
            chat.text = text
            reply_chat: Chat = None
            if self.footer_reply.isVisible():
                reply_chat = self.footer_reply.reply_chat.chat
            self.room_view.chats_list.add_chat(chat, reply_chat)
            self.text_input.clear()

    def toggle_camera_photo_dialog(self):
        if not self.camera_photo_dialog:
            self.camera_photo_dialog = CameraPhotoDialog(self, parent=self.window())

        MOVE_DIALOG_TO_CURSOR(self.camera_photo_dialog, x=1, y=1, cx=1, ty=1)

    def on_play_recorded(self):
        self.play_recorded.hide()
        self.pause_recorded.show()

    def on_pause_recorded(self):
        self.pause_recorded.hide()
        self.play_recorded.show()

    def on_delete_recorded(self):
        self.voice_frame.hide()
        self.text_frame.show()
        self.setMaximumHeight(self.text_frame.height())

    def on_record(self):
        self.record.hide()
        self.stop_record.show()
        self.voice_player.hide()
        self.recording_frame.show()

    def on_stop_record(self):
        self.stop_record.hide()
        self.record.show()
        self.recording_frame.hide()
        self.voice_player.show()

    def set_reply_chat(self, chat: Chat):
        self.footer_reply.load_chat(chat)

    def setupTelegram(self):
        self.footer_reply = TelegramFooterReply(self.room_view)
        self.text_input.textChanged.connect(self.telegramTextChanged)

        lay = self.layout()
        lay = self.text_frame.layout()
        lay.setSpacing(2)
        lay.addWidget(self.footer_reply)
        lay.addLayout(self.text_bottom_lay)

    def setupWhatsApp(self):
        self.setObjectName("WhatsApp")
        self.footer_reply = WhatsAppFooterReply(self.room_view)
        self.text_input.textChanged.connect(self.whatsAppTextChanged)

        lay = self.layout()
        lay = self.text_frame.layout()

        self.blay = QHBoxLayout()
        self.blay.setSpacing(5)
        lay.addLayout(self.blay)

        self.vframe = VFrame(name="WhatsApp_frame")
        vlay = self.vframe.layout()
        self.blay.addWidget(self.vframe)
        m = 5
        vlay.setSpacing(m)
        vlay.setContentsMargins(m, m, m, m)

        self.text_input.min_height = 60

        vlay.addWidget(self.footer_reply)
        vlay.addLayout(self.text_bottom_lay)

        s = 30
        for btn in (self.send, self.microphone):
            btn.setIconColor(Qt.white)
            btn.setObjectName("WhatsApp_button")
            self.blay.addWidget(btn, 1, Qt.AlignBottom)

    def telegramTextChanged(self):
        value = bool(self.text_input.text)
        self.send.setVisible(value)
        self.link.setHidden(value)
        self.microphone.setHidden(value)
        self.text_bottom_lay.addWidget(self.send)

    def whatsAppTextChanged(self):
        value = bool(self.text_input.text)
        self.send.setVisible(value)
        self.photo.setHidden(value)
        self.microphone.setHidden(value)
        self.blay.addWidget(self.send)

    def resizeEvent(self, event: PySide6.QtGui.QResizeEvent) -> None:
        self.setStyleSheet(
            """
            VFrame#WhatsApp_frame, VFrame#WhatsApp_frame_reply {
                border-radius: 25px;
            }
            VFrame#WhatsApp_frame_reply {
                padding: 0px;
                border-top-left-radius: 10px;
                border-top-right-radius: 10px;
            }
            """
        )

    def showEvent(self, event: PySide6.QtGui.QShowEvent) -> None:
        self.text_input.setTextInputSize()
        if self.objectName() == "WhatsApp":
            self.photo.show()


class RoomView(View, VFrame):
    def __init__(self, *args, **kwargs):
        VFrame.__init__(self, **kwargs)
        View.__init__(self, *args)

        self.channel_item: SearchableItem = None
        self.setMinimumWidth(400)

        lay = self.layout()
        lay.setSpacing(0)

        m = 0
        lay.setContentsMargins(m, m, m, m)

        self.header = Header(self)
        lay.addWidget(self.header)

        self.chats_list = ChatsList(self, widgetKwargs=dict(name="chats_list_widget"))
        lay.addWidget(self.chats_list)

        self.footer = Footer(self)
        lay.addWidget(self.footer)

    @property
    def channel(self) -> Chat:
        if self.channel_item:
            return self.channel_item.channel

    def channel_item_selected(self, channel_item: SearchableItem):
        if channel_item == self.channel_item:
            return

        self.channel_item = channel_item
        self.header.load()

        self.chats_list.deleteItems()

        # self.chats_list.add_chat(self, CHATS[-3])
        self.chats_list.add_chat(channel_item.channel.last_chat)
        self.chats_list.add_chat(CHATS[-2])
        # self.chats_list.add_chat(self, CHATS[-1])
        if self.footer.footer_reply.isVisible():
            self.footer.footer_reply.hide_footer()

    def toggle_details_view(self):
        self.home.toggle_details_view()

    def set_footer_reply_chat(self, chat: Chat):
        self.footer.set_reply_chat(chat)

    def closeEvent(self, _):
        self.home.toggle_details_view()
        w = 5
        for wid in (self.home.menu, self.home.channels_view):
            w += wid.width() + 5

        self.home.setMaximumWidth(w)
        self.home.update()
        self.home.hide()
        self.home.show()
