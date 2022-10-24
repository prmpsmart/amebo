from .room_view import *


class DetailsButton(QPushButton):
    def __init__(self, icon: str, text: str, red: bool = False, command=None):
        super().__init__()
        if command:
            self.clicked.connect(command)

        lay = QHBoxLayout(self)
        lay.setSpacing(10)

        if red:
            color = Qt.red
            name = "red_text"
        else:
            color = Qt.black
            name = "text"

        self._icon = Label(name="icon")
        self._icon.setPixmap(QSvgPixmap(f":/{icon}", color=color))
        self._icon.setScaledContents(True)
        lay.addWidget(self._icon)

        self._text = Label(text, name=name)
        lay.addWidget(self._text)


class MemberItem(QPushButton, SearchableItem):
    def __init__(
        self, channel: Channel, user_unique_id: str, admin: bool = False, command=None
    ):
        QPushButton.__init__(self)
        SearchableItem.__init__(self)

        self.channel = channel
        self.user_unique_id = user_unique_id
        self.is_admin = admin

        lay = QHBoxLayout(self)
        lay.setSpacing(4)
        m = 0
        lay.setContentsMargins(m, m, 15, m)

        self.avatar = AvatarButton(mask=41)
        lay.addWidget(self.avatar)

        col = QVBoxLayout()
        col.setSpacing(0)
        c = 5
        col.setContentsMargins(0, c, 0, c)
        lay.addLayout(col)

        self.row_1 = QHBoxLayout()
        col.addLayout(self.row_1)

        self.display_name = Label(name="display_name")
        self.row_1.addWidget(self.display_name)

        self.row_1.addStretch()

        self.admin = Label("Group Admin", name="admin")
        self.admin.hide()
        self.row_1.addWidget(self.admin)

        row_2 = QHBoxLayout()
        row_2.setSpacing(0)
        col.addLayout(row_2)

        self.description = Label(name="member_description")
        row_2.addWidget(self.description)

        row_2.addStretch()

        self.unique_id = Label(name="member_unique_id")
        row_2.addWidget(self.unique_id)

        if command:
            self.clicked.connect(command)

        h = 40
        self.setMaximumHeight(h)

        self.avatar_timer_id = self.startTimer(10)

        self.load()

    def load(self):
        display_name = self.channel.display_name or self.channel.unique_id
        if self.user_unique_id == self.channel.unique_id:
            display_name = "You"

        self.display_name.setText(display_name)
        self.description.setText(self.channel.description)
        self.unique_id.setText(self.channel.unique_id)
        self.admin.setVisible(bool(self.is_admin))

    def search(self, text: str) -> bool:
        text = text.lower()

        searchables = [
            self.channel.description,
            self.channel.display_name,
            str(self.channel.unique_id),
        ]

        for searchable in searchables:
            if text in searchable.lower():
                return True

        return False

    def timerEvent(self, e: QTimerEvent) -> None:
        if e.timerId() == self.avatar_timer_id:
            self.avatar.setAvatar(self.channel.avatar)
            self.killTimer(self.avatar_timer_id)

    def showEvent(self, event: PySide6.QtGui.QShowEvent) -> None:
        w = self.parent().width()
        self.setMinimumWidth(w)
        self.setMaximumWidth(w)


class MembersList(SearchableList):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def arrange_items(self, items: list[MemberItem]) -> list[MemberItem]:

        admin_items = []
        user_item = None
        for member_item in items:
            if member_item.is_admin:
                admin_items.append(member_item)

            if member_item.channel.unique_id == member_item.user_unique_id:
                user_item = member_item

        if user_item:
            admin_items.insert(0, user_item)
        items = [member_item for member_item in items if member_item not in admin_items]

        return admin_items + items


class MediaDialog(RoundDialog):
    def __init__(self, **kwargs):
        super().__init__(add_shadow=1, **kwargs)

        self.setMinimumSize(440, 350)
        # self.setMaximumSize(500, 350)

        lay = self.windowLayout()
        self.windowFrame().setStyleSheet("background: white;")

        peachy = PIXMAP(PEACHY, None)
        mimi = PIXMAP(MIMI, None)
        eye = PIXMAP(EYE, None)

        self.pixmaps = [
            peachy,
            mimi,
            eye,
            peachy,
            mimi,
            eye,
            peachy,
            mimi,
            eye,
            peachy,
            mimi,
            eye,
            peachy,
            mimi,
            eye,
            peachy,
            mimi,
            eye,
            peachy,
            mimi,
            eye,
        ]

        tab = QTabWidget()
        lay.addWidget(tab)

        self.media = Scrollable(Frame)
        self.media._widget.setStyleSheet("background: #e1e1e1;")
        m = 2
        self.media._widget.setLayout(QGridLayout())
        self.media.widgetLayout().setContentsMargins(m, m, m, m)
        self.media.widgetLayout().setSpacing(m)
        tab.addTab(self.media, QSvgIcon(":/photo"), "Media")

        self.docs = Frame()
        tab.addTab(self.docs, QSvgIcon(":/book"), "Docs")

    def showEvent(self, _: QShowEvent) -> None:
        lay: QGridLayout = self.media._widget.layout()
        row = 0
        col = 0
        for pixmap in self.pixmaps:
            media_image = ImageLabel(pixmap=pixmap)
            count = lay.count()
            if col and not count % 4:
                row += 1
                col = 0
            lay.addWidget(media_image, row, col)
            col += 1


class MemberSearchDialog(RoundDialog):
    def __init__(self, textEdited: Callable[[str], None], **kwargs):
        super().__init__(add_shadow=1, **kwargs)

        lay = self.windowLayout()
        self.windowFrame().setStyleSheet("background: white;")

        self.search = QLineEdit()
        self.search.setObjectName("search_dialog_search")
        self.search.setPlaceholderText("Search ...")
        self.search.textEdited.connect(textEdited)
        lay.addWidget(self.search)


class MembersListFrame(VFrame):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.members = []

        lay = self.layout()
        m = 0
        lay.setSpacing(m)
        m = 5
        lay.setContentsMargins(m, m, m, m)

        user = CHANNELS[3]
        self.user_unique_id = user.unique_id

        self.member_search_dialog: MemberSearchDialog = None

        hlay = QHBoxLayout()
        lay.addLayout((hlay))

        self.count_label = Label(f"{len(CHANNELS)} members", name="members_count")
        hlay.addWidget(self.count_label)

        hlay.addStretch()

        search = IconTextButton(icon="search", icon_size=20, name="members_search")
        search.clicked.connect(self.on_search)
        hlay.addWidget(search)
        search.clicked.connect(self.toggle_member_search_dialog)

        self.user_item = MemberItem(user, self.user_unique_id)

        self.members_list = MembersList()
        lay.addWidget(self.members_list)

        h = 45 * 11
        self.members_list.setMinimumHeight(h)
        self.members_list.setMaximumHeight(h)

        # self.members_list.addItem(self.user_item)

        self.fillMembers(CHANNELS)

    def toggle_member_search_dialog(self):
        if not self.member_search_dialog:
            self.member_search_dialog = ChatSearchDialog(
                self.members_list.search, parent=self.window()
            )

        MOVE_DIALOG_TO_CURSOR(self.member_search_dialog, True)

    def fillMembers(self, members: list[Channel]):
        if members == self.members:
            return

        self.members = members
        self.members_list.deleteItems()
        self.members_list.fillItems(
            [
                MemberItem(member, self.user_unique_id, index % 3)
                for index, member in enumerate(members)
            ]
        )

    def on_search(self):
        ...

    def resizeEvent(self, event: PySide6.QtGui.QResizeEvent) -> None:
        width = self.width()
        self.members_list.setMaximumWidth(width)
        self.members_list._widget.setMaximumWidth(width)


class DetailsView(View, VFrame):
    def __init__(self, *args):
        VFrame.__init__(self)
        View.__init__(self, *args)

        h = 300
        self.setMinimumWidth(h)
        self.setMaximumWidth(h)

        lay = self.layout()
        m = 0
        lay.setSpacing(0)
        lay.setContentsMargins(m, m, m, 3)

        # top buttons
        hlay = QHBoxLayout()
        lay.addLayout(hlay)

        self.details_scrollable = Scrollable(
            VFrame, widgetKwargs=dict(name="details_scrollable")
        )
        lay.addWidget(self.details_scrollable)

        lay = self.details_scrollable.widgetLayout()
        # lay.setSpacing()

        close_button = IconTextButton(icon="arrow-left", icon_size=25)
        close_button.clicked.connect(self.hide)
        hlay.addWidget(close_button)
        hlay.addStretch()

        edit = IconTextButton(icon="edit", icon_size=25)
        edit.clicked.connect(self.edit)
        hlay.addWidget(edit)

        # avatar, display_name, type, users count
        details_frame = VFrame(name="details_frame")
        # addShadow(details_frame)
        lay.addWidget(details_frame)
        lay.setSpacing(7)
        m = 0
        lay.setContentsMargins(m, m, m, m)

        details_lay = details_frame.layout()

        self.avatar = Label()
        self.avatar.setPixmap(PIXMAP(PEACHY, ":/user"))
        self.avatar.setScaledContents(True)
        # self.avatar.setMaximumHeight(200)
        details_lay.addWidget(self.avatar)

        self.details = Label("Group ~ 271 members", name="details")
        self.details.setAlignment(Qt.AlignCenter)
        details_lay.addWidget(self.details)

        description_frame = VFrame()
        description_lay = description_frame.layout()
        lay.addWidget(description_frame)

        self.description = Label(
            """DetailsView, ChannelItem, RoomView, QScrollBar:vertical, IconTextButton:hover {
            background: #e1e1e1;}""",
            name="description",
        )
        self.description.setWordWrap(True)
        description_lay.addWidget(self.description)

        self.creator = Label("Created by @prmpsmart, 23/09/2022", name="creator")
        description_lay.addWidget(self.creator)

        self.media_dialog: MediaDialog = None
        self.media = DetailsButton("photo", "Media, Docs", command=self.toggle_media)
        lay.addWidget(self.media)

        self.starred = DetailsButton("star", "Starred Messages")
        lay.addWidget(self.starred)
        self.starred_count = Label("23")
        self.starred.layout().addStretch()
        self.starred.layout().addWidget(self.starred_count)

        self.members_list_frame = MembersListFrame()
        lay.addWidget(self.members_list_frame)

        red_lay = QVBoxLayout()
        lay.addLayout(red_lay)

        m = 0
        red_lay.setSpacing(m)
        red_lay.setContentsMargins(m, m, m, m)

        self.exit = DetailsButton("logout", "Exit group", red=True)
        red_lay.addWidget(self.exit)

        self.report = DetailsButton("thumb-down", "Report group", red=True)
        red_lay.addWidget(self.report)

    def edit(self):
        ...

    def toggle_media(self):
        if not self.media_dialog:
            self.media_dialog = MediaDialog(parent=self.window())

        MOVE_DIALOG_TO_CURSOR(self.media_dialog, True)

    def resizeEvent(self, event: PySide6.QtGui.QResizeEvent) -> None:
        width = self.width()
        self.details_scrollable.setMaximumWidth(width)
        self.details_scrollable._widget.setMaximumWidth(width)

    def load(self, room_view: RoomView):
        ...
