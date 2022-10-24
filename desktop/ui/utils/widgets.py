from .model_datas import *
from .commons import *


DEFAULT_ICON_COLOR = QColor("#717171")


class IconButton(IconButton):
    def __init__(self, *args, **kwargs):
        if icon := kwargs.get("icon"):
            kwargs["icon"] = f":/{icon}"
        super().__init__(*args, **kwargs)


class IconTextButton(IconTextButton):
    def __init__(
        self, icon_size: int = 30, tip=None, iconColor: COLORS = None, **kwargs
    ):

        if icon := kwargs.get("icon"):
            kwargs["icon"] = f":/{icon}"
        super().__init__(
            icon_size=icon_size, iconColor=iconColor or DEFAULT_ICON_COLOR, **kwargs
        )

        if tip is True:
            self.setToolTip(self.text())
        elif tip:
            self.setToolTip(tip)


class AvatarButton(Button):
    def __init__(
        self, avatar: str = "", icon_size: int = 60, mask=50, icon=":/user-2", **kwargs
    ):
        super().__init__(icon_size=icon_size, **kwargs)
        self._icon = icon
        self._mask = mask
        self.setAvatar(avatar)

    def setAvatar(self, avatar: str):
        icon = ICON(avatar, self._icon, mask=self._mask)
        self.setIcon(icon)


class MenuButton(IconTextButton):
    def __init__(self, menu: QWidget, **kwargs):
        super().__init__(**kwargs)

        self._menu = menu
        self._menu.animation_group.finished.connect(self.toggle_tip)
        self.toggle_tip()

    def toggle_tip(self):
        self.setToolTip("" if self._menu.expanded else self.text())


class ImageLabel(ImageLabel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, default=":/photo-off", **kwargs)


class ChatIcon(IconButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, icon_size=15, border=False, clickable=False, **kwargs)

        self.setAttribute(Qt.WA_TransparentForMouseEvents)


class SearchableItem:
    def __init__(self):
        ...

    def search(self, text: str) -> bool:
        return False


SearchableItems = list[SearchableItem]


class SearchableList(Scrollable):
    def __init__(self, reverse: bool = False, **kwargs):
        super().__init__(VFrame, **kwargs)

        self.items: SearchableItems = []
        self.reverse = reverse

        m = 2
        self.widgetLayout().setContentsMargins(m, m, m, m)
        self.widgetLayout().setSpacing(m)
        self.widgetLayout().addStretch()

    @property
    def arranged_items(self) -> SearchableItems:
        return self.arrange_items(self.items)

    def add(
        self,
        item: SearchableItem,
        stretch: int = 0,
        alignment: Qt.Alignment = Qt.AlignCenter,
    ):
        assert isinstance(item, SearchableItem)

        lay = self.widgetLayout()

        if self.reverse:
            lay.insertWidget(lay.count() - 1, item, stretch, alignment)
        else:
            lay.addWidget(item, stretch, alignment)

    def addItem(self, item: SearchableItem, alignment: Qt.Alignment = Qt.AlignCenter):
        self.add(item)
        self.items.append(item)

    def remove(self, item: SearchableItem):
        assert isinstance(item, SearchableItem)
        self.widgetLayout().removeWidget(item)

    def removeItem(self, item: SearchableItem):
        self.remove(item)
        if item in self.items:
            self.items.remove(item)

    def deleteItem(self, item: SearchableItem):
        self.removeItem(item)
        item.deleteLater()

    def deleteItems(self):
        for item in self.widget().children():
            if isinstance(item, SearchableItem):
                self.deleteItem(item)

    def clear(self):
        for item in self.widget().children():
            if isinstance(item, SearchableItem):
                self.remove(item)

    def search(self, text: str):
        self.clear()

        item: QWidget
        for item in self.items:
            if text:
                valid = item.search(text)
            else:
                valid = True

            item.setVisible(valid)

        self.fill(self.items)

    def fill(self, items: SearchableItems):
        items = self.arrange_items(items)

        for item in reversed(items):
            self.widgetLayout().insertWidget(0, item)

    def fillItems(self, items: SearchableItems):
        self.fill(items)
        self.items = items

    def arrange_items(self, items: SearchableItems) -> SearchableItems:
        "A method to customized the order of the search, it can be override in subclasses"
        return items


class IHome(QWidget):
    def channel_item_selected(self, chat_item: QWidget):
        ...

    def toggle_details_view(self, room_view: QWidget):
        ...

    def set_channels(self, channels: list[Channel]):
        ...


class View(Shadow):
    def __init__(self, home: IHome, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.home = home


class ChatTypeButton(IconTextButton):
    CHAT_TYPE_ICONS = {}
    CHAT_TYPE_STRS = {}

    def __init__(self):
        super().__init__(clickable=False, icon_size=15)
        if not (ChatTypeButton.CHAT_TYPE_ICONS and ChatTypeButton.CHAT_TYPE_STRS):
            ChatTypeButton.CHAT_TYPE_ICONS = {
                ChatType.Image: QIcon(":/photo"),
                ChatType.Voice: QIcon(":/microphone"),
                ChatType.Audio: QIcon(":/headphones"),
            }
            ChatTypeButton.CHAT_TYPE_STRS = {
                ChatType.Image: "Photo",
                ChatType.Voice: "Voice Message",
                ChatType.Audio: "Audio",
            }
        self.setAttribute(Qt.WA_TransparentForMouseEvents)

    def load_chat(self, chat: Chat):
        text = ChatTypeButton.CHAT_TYPE_STRS.get(chat.chat_type)

        if chat.chat_type in [ChatType.Image, ChatType.Text]:
            text = chat.text or text

        self.setText(text)
        icon = ChatTypeButton.CHAT_TYPE_ICONS.get(chat.chat_type)

        if icon:
            self.setIcon(icon)


class VoiceWaveform(AudioWaveForm):
    def __init__(
        self,
        avgColor: COLORS = Qt.white,
        seekColor: COLORS = Qt.black,
        backgroundColor: COLORS = Qt.transparent,
        seekerColor: COLORS = None,
        seekerRadius: int = None,
        bytes: bytes = "",
    ) -> None:

        options = AudioWaveFormOptions(
            pixelSpacing=1,
            pixelWidth=3,
            avgColor=avgColor,
            seekColor=seekColor,
            showHLine=0,
            radius=3,
            gravity=AudioWaveFormGravity.Average,
            seekerRadius=seekerRadius,
            seekerColor=seekerColor,
        )

        if bytes:
            channel1 = AudioWaveFormChannel.from_bytes(bytes, options)
        else:
            channel1 = AudioWaveFormChannel(options=options)

        super().__init__(channel1, backgroundColor=backgroundColor, showHLine=False)


POLICY = QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Minimum)


class VoicePlayer(HFrame):
    def __init__(
        self,
        avgColor: COLORS = Qt.white,
        seekColor: COLORS = Qt.black,
        backgroundColor: COLORS = Qt.transparent,
        seekerColor: COLORS = None,
        bytes: bytes = "",
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)

        self.setContentsMargins(0, 0, 0, 0)
        self.setSizePolicy(POLICY)

        lay = self.layout()
        lay.setSpacing(2)
        o = 0
        lay.setContentsMargins(o, o, o, o)

        self.play = IconTextButton(icon="player-play", iconColor="black")
        lay.addWidget(self.play)
        self.play.clicked.connect(self.on_play)

        self.pause = IconTextButton(icon="player-pause", iconColor="black")
        lay.addWidget(self.pause)
        self.pause.hide()
        self.pause.clicked.connect(self.on_pause)

        options = AudioWaveFormOptions(
            seekerRadius=10,
            pixelSpacing=1,
            pixelWidth=3,
            avgColor=avgColor,
            seekColor=seekColor,
            showHLine=0,
            radius=3,
            gravity=AudioWaveFormGravity.Average,
            seekerColor=seekerColor,
        )

        if bytes:
            channel1 = AudioWaveFormChannel.from_bytes(bytes, options)
        else:
            channel1 = AudioWaveFormChannel(options=options)

        self.player = PlayingFixedAudioWaveForm(
            waveFormChannel1=channel1, backgroundColor=backgroundColor, bytes=bytes, channels=1
        )
        lay.addWidget(self.player)
        
        # aw = self.player.audiowave
        # aw.frame_rate = 44100
        # self.player.live.createAudio(rate=aw.frame_rate, sample)
        # self.player.setSeconds(self.audiowave.duration)

    def on_play(self):
        self.play.hide()
        self.pause.show()
        self.player.startLive()

    def on_pause(self):
        self.pause.hide()
        self.play.show()
        self.player.stopLive()


class Dialog(RoundDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.opened = False

    def showEvent(self, _: QShowEvent) -> None:
        self.opened = True


def MOVE_DIALOG_TO_CURSOR(dialog: Dialog, *args, **kwargs):
    opened = dialog.opened
    MOVE_TO_CURSOR(dialog, *args, **kwargs)

    if not opened:
        MOVE_TO_CURSOR(dialog, *args, **kwargs)
