from .details_view import *


class LabeledLabel(Labeled):
    def __init__(self, label: str):
        super().__init__(Label, label)


class ProfileDialog(RoundDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setMinimumWidth(250)
        self.setMaximumWidth(400)
        self.setWindowFlag(Qt.SubWindow)

        lay = self.windowLayout()

        self.view_frame = VFrame()
        lay.addWidget(self.view_frame)

        view_lay = self.view_frame.layout()
        view_lay.setSpacing(15)

        hlay = QHBoxLayout()
        view_lay.addLayout(hlay)

        self.avatar = ImageLabel()
        addShadow(self.avatar)
        hlay.addWidget(self.avatar, 1, Qt.AlignLeft)

        hlay.addStretch()

        vlay = QVBoxLayout()
        vlay.setSpacing(2)
        hlay.addLayout(vlay)

        edit = IconTextButton(icon="edit", icon_size=25)
        edit.clicked.connect(self.edit)
        vlay.addWidget(edit, 0, Qt.AlignRight)

        self.status = ColorfulTag()
        vlay.addWidget(self.status)

        view_form = QFormLayout()
        view_lay.addLayout(view_form)

        self.display_name = Label(name="form_label")
        view_form.addRow("Display Name: ", self.display_name)

        self.description = Label(name="form_label")
        view_form.addRow("Description: ", self.description)
        self.description.setWordWrap(True)

        self.edit_frame = VFrame(name="edit_frame")
        self.edit_frame.hide()
        lay.addWidget(self.edit_frame)

        edit_lay = self.edit_frame.layout()

        hlay = QHBoxLayout()
        edit_lay.addLayout(hlay)

        self.edit_avatar = ImageLabel()
        addShadow(self.edit_avatar)
        self.edit_avatar.mousePressEvent = lambda e: self.change_avatar()
        hlay.addWidget(self.edit_avatar, 0, Qt.AlignLeft)

        hlay.addStretch()

        check = IconTextButton(icon="check")
        check.clicked.connect(self.save)
        hlay.addWidget(check)

        self.edit_display_name = LabeledLineEdit(label="Display Name: ")
        self.edit_display_name.setMinimumWidth(200)
        edit_lay.addWidget(self.edit_display_name, 0, Qt.AlignLeft)

        self.edit_description = LabeledTextEdit(label="Description: ")
        edit_lay.addWidget(self.edit_description, 0, Qt.AlignLeft)

        m = 5
        for a in [self.edit_display_name, self.edit_description]:
            a.layout().setContentsMargins(m, m, m, m)

        self.changed_avatar: str = ""
        self.load()

    def change_avatar(self):
        print("change avatar")

    def load(self):
        user: AmeboUser = AmeboClientData.user()
        self.avatar.setImage(image=user.avatar)
        if user.status:
            text = "Online"
            name = "green"
        else:
            text = user.last_seen_string
            name = "red"
        self.status.setText(text)
        self.status.setObjectName(name)
        self.display_name.setText(user.display_name)
        self.description.setText(user.description)

    def edit(self):
        user: AmeboUser = AmeboClientData.user()
        self.edit_avatar.setPixmap(self.avatar.pixmap())
        self.edit_display_name.edit.setText(self.display_name.text())
        self.edit_description.edit.setText(user.description)
        self.view_frame.hide()
        self.edit_frame.show()

    def save(self):
        user: AmeboUser = AmeboClientData.user()
        display_name = self.edit_display_name.text()
        description = self.edit_description.text()

        json = Json()

        if display_name and display_name != user.display_name:
            json.display_name = display_name
        if description and description != user.description:
            json.description = description
        if self.changed_avatar:
            json.avatar = self.changed_avatar

        if json:
            AmeboUserClient.get_client().edit_user_profile_info(**json)

    def check(self):
        self.edit_frame.hide()
        self.view_frame.show()
        self.load()


class MyAccountButton(QPushButton):
    def __init__(self, title: str):
        super().__init__(title)


class PasswordLineEdit(HFrame):
    HIDE: QIcon = None
    SHOW: QIcon = None

    def __init__(
        self,
        show_first: bool = False,
        password_hidden: bool = False,
        color: COLORS = Qt.black,
        **kwargs,
    ):
        super().__init__(**kwargs)
        if not PasswordLineEdit.HIDE:
            PasswordLineEdit.HIDE = QSvgIcon(":/eye-off", color=color)
        if not PasswordLineEdit.SHOW:
            PasswordLineEdit.SHOW = QSvgIcon(":/eye", color=color)

        lay = self.layout()
        m = 0
        lay.setSpacing(m)
        lay.setContentsMargins(m, m, m, m)

        if show_first:
            self.hide_mode = QLineEdit.PasswordEchoOnEdit
        elif password_hidden:
            self.hide_mode = QLineEdit.NoEcho
        else:
            self.hide_mode = QLineEdit.Password

        self.line_edit = QLineEdit()
        lay.addWidget(self.line_edit)
        self.line_edit.setEchoMode(self.hide_mode)

        self.icon = IconTextButton(icon_size=20, icon=PasswordLineEdit.SHOW)
        self.icon.setCheckable(True)
        lay.addWidget(self.icon)
        self.icon.toggled.connect(self.change_echo_mode)

    def setText(self, text: str):
        self.line_edit.setText(text)

    def change_echo_mode(self, toggled):
        if toggled:
            self.line_edit.setEchoMode(QLineEdit.EchoMode.Normal)
            self.icon.setIcon(PasswordLineEdit.HIDE)
        else:
            self.line_edit.setEchoMode(self.hide_mode)
            self.icon.setIcon(PasswordLineEdit.SHOW)


class ChangePasswordDialog(RoundDialog):
    def __init__(self, user: Channel, *args, **kwargs):
        super().__init__(*args, **kwargs)

        lay = self.windowLayout()

        self.user = user

        form_lay = QFormLayout()
        lay.addLayout(form_lay)

        self.edit_password = PasswordLineEdit()
        self.edit_password.line_edit.textEdited.connect(self.password_edited)
        form_lay.addRow("Password: ", self.edit_password)

        self.confirm_password = PasswordLineEdit()
        self.confirm_password.line_edit.textEdited.connect(self.confirm_password_edited)
        form_lay.addRow("Confirm: ", self.confirm_password)

        self.notify_password = Label(name="notify_password")
        form_lay.addWidget(self.notify_password)

        change = MyAccountButton("Change")
        change.clicked.connect(self.change)
        form_lay.addWidget(change)

    def change(self):
        self.close()

    def password_edited(self, text: str):
        l = len(text)
        if l > 8:
            text_ = "Strong Password"
            color = "green"

        elif l > 5:
            text_ = "Mild Password"
            color = "orange"

        else:
            text_ = "Weak Password"
            color = "red"

        self.notify_password.setText(text_)
        self.notify_password.setStyleSheet(f"color: {color}")

    def confirm_password_edited(self, text: str):
        if text == self.edit_password.line_edit.text():
            color = "green"

        else:
            color = "red"

        self.notify_password.setStyleSheet(f"color: {color}")


class MyAccountDialog(RoundWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setWindowFlag(Qt.SubWindow)

        self.setMinimumWidth(250)
        self.setMaximumWidth(450)

        lay = self.windowLayout()

        self.user = DMS[0]

        self.view_frame = VFrame(name="my_account_view")
        lay.addWidget(self.view_frame)
        view_lay = self.view_frame.layout()
        view_lay.setSpacing(4)

        hlay = QHBoxLayout()
        view_lay.addLayout(hlay)

        info = Label("ACCOUNT INFORMATION")
        hlay.addWidget(info, 0, Qt.AlignLeft)

        hlay.addStretch()

        edit = IconTextButton(icon="edit")
        edit.clicked.connect(self.edit)
        hlay.addWidget(edit)

        form_lay = QFormLayout()
        view_lay.addLayout(form_lay)

        self.unique_id = Label(name="form_label")
        form_lay.addRow("Unique ID: ", self.unique_id)

        self.edit_frame = VFrame(name="my_account_edit_frame")
        lay.addWidget(self.edit_frame)
        self.edit_frame.hide()
        edit_lay = self.edit_frame.layout()

        hlay = QHBoxLayout()
        edit_lay.addLayout(hlay)

        info = Label("EDIT ACCOUNT INFORMATION")
        hlay.addWidget(info, 0, Qt.AlignLeft)

        hlay.addStretch()

        check = IconTextButton(icon="check")
        check.clicked.connect(self.check)
        hlay.addWidget(check)

        form_lay = QFormLayout()
        edit_lay.addLayout(form_lay)
        form_lay.setSpacing(2)

        self.edit_unique_id = QLineEdit()
        form_lay.addRow("Unique ID: ", self.edit_unique_id)

        self.change_password_dialog: ChangePasswordDialog = None

        change_password = MyAccountButton("Change Password")
        change_password.clicked.connect(self.toggle_change_password_dialog)
        lay.addWidget(change_password)

        disable = MyAccountButton("Disable Account")
        lay.addWidget(disable)

        delete = MyAccountButton("Delete Account")
        delete.setObjectName("red")
        lay.addWidget(delete)

        self.load()

    def toggle_change_password_dialog(self):
        if not self.change_password_dialog:
            self.change_password_dialog = ChangePasswordDialog(self.user, parent=self)
        MOVE_DIALOG_TO_CURSOR(self.change_password_dialog)

    def load(self):
        self.unique_id.setText(self.user.unique_id)

    def edit(self):
        self.edit_unique_id.setText(self.unique_id.text())
        self.view_frame.hide()
        self.edit_frame.show()

    def check(self):
        self.edit_frame.hide()
        self.view_frame.show()


class SearchedChannelItem(MemberItem):
    def __init__(self, channel: Channel, command):
        super().__init__(channel, None, command=command)

        self.sized = 0

    def showEvent(self, event: PySide6.QtGui.QShowEvent) -> None:
        if not self.sized:
            p = self.parent()
            m = p.contentsMargins()
            w = p.width() - 4
            self.setMinimumWidth(w)
            self.setMaximumWidth(w)
            self.sized = 1


class GlobalSearchDialog(RoundDialog):
    def __init__(self, menu: "_Menu"):
        super().__init__()

        self.menu = menu

        self.w = 300
        self.setMinimumSize(self.w, self.w + 200)
        self.setMaximumWidth(self.w)

        lay = self.windowLayout()

        top_lay = QHBoxLayout()
        lay.addLayout(top_lay)
        top_lay.setSpacing(10)

        self.search_line_edit = LineEdit(
            name="search_line_edit", placehoder="Search ..."
        )
        top_lay.addWidget(self.search_line_edit)

        self.search_button = IconTextButton(
            icon="search", tip="Search Globally", icon_size=25
        )
        self.search_button.clicked.connect(self.search)
        top_lay.addWidget(self.search_button)

        self.tab = QTabWidget()
        lay.addWidget(self.tab)

        self.users_list = SearchableList()
        self.tab.addTab(self.users_list, "Users")
        self.groups_list = SearchableList()
        self.tab.addTab(self.groups_list, "Groups")
        self.broadcasts_list = SearchableList()
        self.tab.addTab(self.broadcasts_list, "Broadcasts")

    def search(self):
        ...

    def current_list(self) -> SearchableList:
        return self.tab.currentWidget()

    def channel_selected(self):
        self.menu.home.channel_item_selected(self.sender())

    CHANNELS = list[Channel]

    def fill_list(self, channels: CHANNELS, s_list: SearchableList):
        channel_items = [
            SearchedChannelItem(channel, self.channel_selected) for channel in channels
        ]
        s_list.fillItems(channel_items)

    def fill_users(self, channels: CHANNELS):
        self.fill_list(channels, self.users_list)

    def fill_groups(self, channels: CHANNELS):
        self.fill_list(channels, self.groups_list)

    def fill_broadcasts(self, channels: CHANNELS):
        self.fill_list(channels, self.broadcasts_list)

    def showEvent(self, _: QShowEvent) -> None:
        if not self.users_list.items:
            for channels, method in zip(
                (DMS[:5], GROUPS[:3], BROADCASTS[:5]),
                (self.fill_users, self.fill_groups, self.fill_broadcasts),
            ):
                method(channels)


class _Menu:
    def __init__(self, home: IHome, layout: QBoxLayout):
        self.home = home
        m = 5
        layout.setContentsMargins(m, m, m, m)

        self.global_search_dialog: GlobalSearchDialog = None
        self.global_search_button = MenuButton(self, text="Global Search", icon="globe")
        self.global_search_button.clicked.connect(self.global_search)
        layout.addWidget((self.global_search_button))

        self.profile_dialog: ProfileDialog = None
        self.user_profile_button = MenuButton(self, text="User Profile", icon="user")
        self.user_profile_button.clicked.connect(self.user_profile)
        layout.addWidget((self.user_profile_button))

        self.dms_button = MenuButton(self, text="DMs", icon="message-2")
        self.dms_button.clicked.connect(self.dms)
        layout.addWidget((self.dms_button))

        self.groups_button = MenuButton(self, text="Groups", icon="messages")
        self.groups_button.clicked.connect(self.groups)
        layout.addWidget((self.groups_button))

        self.broadcasts_button = MenuButton(
            self, text="Broadcasts", icon="speakerphone"
        )
        self.broadcasts_button.clicked.connect(self.broadcasts)
        layout.addWidget((self.broadcasts_button))

        self.my_account_dialog: MyAccountDialog = None
        self.my_account_button = MenuButton(self, text="My Account", icon="id")
        self.my_account_button.clicked.connect(self.my_account)
        layout.addWidget((self.my_account_button))

        self.privacy_button = MenuButton(self, text="Privacy and Safety", icon="lock")
        self.privacy_button.clicked.connect(self.privacy)
        layout.addWidget((self.privacy_button))

        self.settings_button = MenuButton(self, text="Settings", icon="settings")
        self.settings_button.clicked.connect(self.settings)
        layout.addWidget((self.settings_button))

    def global_search(self):
        if not self.global_search_dialog:
            self.global_search_dialog = GlobalSearchDialog(self)

        MOVE_DIALOG_TO_CURSOR(self.global_search_dialog)

    def user_profile(self):
        if not self.profile_dialog:
            self.profile_dialog = ProfileDialog()

        MOVE_DIALOG_TO_CURSOR(self.profile_dialog)

    def dms(self):
        self.home.set_channels(DMS)

    def groups(self):
        self.home.set_channels(GROUPS)

    def broadcasts(self):
        self.home.set_channels(BROADCASTS)

    def my_account(self):
        self.my_account_dialog = MyAccountDialog()
        MOVE_DIALOG_TO_CURSOR(self.my_account_dialog)

    def privacy(self):
        ...

    def settings(self):
        ...


class MenuDrawer(_Menu, DrawerWindow):
    def __init__(self, *args, main_window: QWidget):
        DrawerWindow.__init__(
            self,
            main_window,
            220,
            parent=main_window,
            x=5,
            y=5,
            shadow_kwargs=dict(
                add_shadow=True,
            ),
            height_getter=self._height_getter,
        )
        _Menu.__init__(self, *args, self.windowLayout())

    def _height_getter(self) -> int:
        return self.home.height() - 10


class Menu(_Menu, Expandable, VFrame, Shadow):
    def __init__(self, *args):
        VFrame.__init__(self)
        Expandable.__init__(self, max_width=170, min_width=45)
        _Menu.__init__(self, *args, self.layout())
        Shadow.__init__(self)
