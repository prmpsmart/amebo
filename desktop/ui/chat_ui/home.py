from .menu import *
from .details_view import *


class Home(BaseWindow_, HFrame):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.setWindowTitle("Amebo Chat")
        self.setWindowIcon(QSvgIcon(":/message-2", color=Qt.blue))

        self.lay = self.layout()
        self.lay.setContentsMargins(5, 5, 5, 5)

        self.drawer: MenuDrawer = None

        self.menu: Menu = Menu(self)
        self.lay.addWidget(self.menu)

        self._finished: Callable[[], None] = None
        self.menu.animation_group.finished.connect(self.animation_finished)

        self.setMinimumWidth(self.menu.width())

        self.channels_view = ChannelsView(self)
        # self.channels_view.hide()
        self.lay.addWidget(self.channels_view)

        self.room_view = RoomView(self)
        # self.room_view.hide()
        self.lay.addWidget(self.room_view)

        self.details_view = DetailsView(self)
        self.details_view.hide()
        self.lay.addWidget(self.details_view)

        self.setMinimumHeight(700)
        self.reset_maximum_width_timer_id = 0

    def animation_finished(self):
        if self._finished:
            self._finished()
            self._finished = None

    def set_channels(self, channels: list[Channel]):
        m = self.lay.contentsMargins()

        if self.all_true(
            self.menu.expanded,
            self.channels_view.isHidden(),
            self.room_view.isHidden(),
        ):
            self._finished = lambda: self.set_channels(channels)
            self.menu.toggle()

        else:
            self.channels_view.fillChannels(channels)
            if self.channels_view.isHidden():
                self.toggle_channels_view()

    def toggle_menu(self):
        if self.all_true(
            not self.menu.expanded,
            self.channels_view.isHidden(),
            self.room_view.isHidden(),
        ):
            m = self.lay.contentsMargins()
            self._finished = lambda: self.reset_width(
                self.menu.width() + m.left() + m.right(), 0
            )
            self.menu.toggle()

    def toggle_channels_view(self):
        m = self.lay.contentsMargins()
        s = self.lay.spacing()
        w = m.left() + m.right()
        mw = self.menu.width()

        if self.room_view.isVisible():
            mw = self.menu.width()
            w += self.room_view.width() + s

            if self.details_view.isVisible():
                w += self.details_view.width() + s

        if self.channels_view.isVisible():
            self.reset_width(mw + w)
            self.channels_view.hide()

            if self.room_view.isHidden() and not self.menu.expanded:
                self.toggle_menu()

        else:
            self.reset_width(mw + w + self.channels_view.width() + s)
            self.channels_view.show()

    def channel_item_selected(self, channel_item: ChannelItem):
        self.room_view.channel_item_selected(channel_item)
        if self.room_view.isHidden():
            self.toggle_room_view()

    def toggle_room_view(self):
        m = self.lay.contentsMargins()
        w = self.channels_view.width() if self.channels_view.isVisible() else 0
        s = self.lay.spacing()
        w += m.left() + m.right() + self.menu.width() + s

        if self.room_view.isHidden():
            m = self.lay.contentsMargins()
            self.reset_width(w + self.room_view.minimumWidth() + s)
            self.room_view.show()
        else:
            self.reset_width(w)
            self.room_view.hide()
            if self.details_view.isVisible():
                self.details_view.hide()
            self.toggle_menu()

    def toggle_details_view(self):
        m = self.lay.contentsMargins()
        w = self.channels_view.width() if self.channels_view.isVisible() else 0
        s = self.lay.spacing()
        w += (
            m.left()
            + m.right()
            + self.menu.width()
            + s * 2
            + self.room_view.minimumWidth()
        )

        if self.details_view.isHidden():
            self.details_view.load(self.room_view)
            self.reset_width(w + self.details_view.minimumWidth() + s)
            self.details_view.show()
        else:
            self.reset_width(w)
            self.details_view.hide()

    def toggle_drawer(self):
        if not self.drawer:
            self.drawer = MenuDrawer(self, main_window=self.window())
        self.drawer.toggle_drawer()

    def open_menu(self):
        details_width = (
            0 if self.details_view.isHidden() else self.details_view.minimumWidth()
        )

        width = (
            self.menu.max_width
            + self.channels_view.minimumWidth()
            + self.room_view.minimumWidth()
            + details_width
        )

        if self.width() < width:
            self.toggle_drawer()
        else:
            self.menu.toggle()

    def reset_width(self, width: int, r=True):
        if width <= 120:
            return

        self.setMinimumWidth(width)
        self.setMaximumWidth(width)

        if r:
            self.reset_maximum_width_timer_id = self.startTimer(10)

    def timerEvent(self, event: QTimerEvent) -> None:
        if event.timerId() == self.reset_maximum_width_timer_id:
            self.setMaximumWidth(QApplication.primaryScreen().availableSize().width())
            self.killTimer(self.reset_maximum_width_timer_id)

    def showEvent(self, _: QShowEvent) -> None:
        self.toggle_menu()
        self.setMinimumWidth(self.width())

    def resizeEvent(self, _: QResizeEvent) -> None:
        if self.drawer:
            self.drawer._height = self.height() - 15
        self.resized.emit()

    def all_true(self, *bools: list[bool]) -> bool:
        for bool in bools:
            if not bool:
                return False

        return True

    def set_default_width(self):
        s = self.lay.spacing()
        ws = self.menu, self.channels_view, self.room_view, self.details_view

        wd = 0

        for w in ws:
            if w.isVisible():
                wd += w.minimumWidth() + s

        self.reset_width(wd)
