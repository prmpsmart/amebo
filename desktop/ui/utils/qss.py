AMEBO_QSS = """

VFrame {
    background-color: white;
    border-radius: 5px;
}

IconTextButton {
    background: transparent;
    border: 1px solid transparent;
    border-radius: 18px;
    padding: 5px;
}


IconTextButton:pressed {
    background: #cecece;
}

VFrame#details_scrollable, ChannelItem, RoomView, QScrollBar:vertical {
    background: #e1e1e1;
}

IconTextButton:hover {
    background: #e1e1e1;
    background: #f2f2f2;
}


IconTextButton:pressed {
    background: #b3b3b3;
}

QScrollBar:vertical {
    width: 8px;
}

QScrollBar::handle:vertical{
    background: white;
    margin: 3px;
    margin-right: 2px;
}

ChannelItem {
    border: none;
    border-radius: 10px;
    min-height: 60px;
    max-height: 60px;
}

ChannelItem:hover {
    background: #62a6ff;
}

ChannelItem:pressed {
    background: #448aff;
}

AvatarButton {
    border: none;
    padding: 5px;
    border-radius: 25px;
    background: #e1e1e1;
    max-width: 40px;
    max-height: 40px;
}

ChannelItem > Label {
    background: transparent;
}

Label#display_name {
    font-weight: bold;
    font-size: 15px;
}

Header > Label#display_name {
    font-size: 20px;
}

ChannelItem > Label#time {
    color: #646464;
    font-weight: bold;
    font-size: 12px;
}

ChannelItem > Label#author {
    font-weight: bold;
}

ColorfulTag#blue {
    padding: 2px;
}

ChannelItem > ColorfulTag#blue {
    min-width: 1.5em;
}

IconTextButton {
    text-align: center;
}

Header IconTextButton, Footer IconTextButton {
    border-radius: 20px;
    max-width: 30px;
    max-height: 30px;
}

RoomMenuDialog IconTextButton {
    font-size: 13px;
}

MenuButton {
    text-align: left;
    font-size: 15px;
    font-weight: bold;
    font-family: Times New Roman;
    border-radius: 15px;
}

LineEdit#search_line_edit {
    padding: 5px;
    border-bottom: 1px solid black;
    border-bottom: 1px solid #c1c1c1;
    border-radius: 10px;
}

Scrollable {
    border: none;
    border-radius: 5px;
}

#details_view_frame {
    border-radius: 5px;
}

#chats_list_widget, #chats_list {
    background:  #e1e1e1;
    border-radius: 0px;
}

MenuDrawer > VFrame#window_frame {
    background: white;
}

Header, Footer {
    border: none;
    background: white;
}

Header {
    border-top-left-radius: 5px;
    border-top-right-radius: 5px;
}

Header:pressed {
    background: #f3f3f3;
}

Footer {
    border-radius: 0px;
    border-bottom-left-radius: 5px;
    border-bottom-right-radius: 5px;
}

VoicePlayer > IconTextButton, Footer > VFrame#voice_frame > IconTextButton {
    max-width: 30px;
    border-radius: 20px;
}

Footer > VFrame#voice_frame > VoicePlayer { 
    background: #e1e1e1;
    background: #8c8c8c;
    border-radius: 10px;
    padding: 5px;
}

Label#voice_time {
    max-width: 30px;
    font-size: 13px;
    font-weight: bold;
    padding: 5px;
}

Footer, Footer#WhatsApp > VFrame#text_frame {
    background: transparent;
}

IconTextButton#WhatsApp_button {
    background: #00a884;
    border-radius: 25px;
    min-height: 40px;
    min-width: 40px;
    max-height: 40px;
    max-width: 40px;
}

IconTextButton#WhatsApp_cancel:hover {
    background: #e1e1e1;
    background: #f2f2f2;
    border-radius: 5px;
}

IconTextButton#WhatsApp_button:pressed {
    background: #00755c;
}

SearchDialog > VFrame, RoomMenuDialog > VFrame {
    padding: 5px;
}

LineEdit#search_dialog_search {
    padding: 5px;
    border: none;
    border-bottom: 2px solid #e1e1e1;
    border-radius: 5px;
}

RoomMenuDialog > VFrame#window_frame {
    background: white;
}

RoomMenuDialog > VFrame > IconTextButton {
    text-align: left;
}

TextInput {
    border: none;
    font-size: 14px;
    padding-top: 5px;
}

ChatItem {
    background: #73ff78;
    border-radius: 10px;
    padding: 5px;
    padding-bottom: 0px;
    
}

ChatItem#right {
    background: white;
    background: #9090d6;
    background: #aaaafc;
}

ChatItem#left {
    background: white;
    background: #ffb285;
}

TextChat {
    font-size: 13px;
    font-weight: 510;
    border-radius: 5px;
    background: yellow;
    background: transparent;
    padding: 1px;
}

ImageChat {
    background: transparent;
    border-radius: 10px;
    padding: 0px;
}

ImageChat > Label#image {
    border-radius: 10px;
    padding: 0px;
    background: grey;
}

HFrame#bottom {
    max-height: 20px;
}

Label#date_time {
    font-weight: bold;
    font-size: 11px;
    padding: 2px;
}

Label#author, Label#reply_author {
    font-size: 14px;
    font-weight: 600;
    text-align: left;
}

VoiceChat {
    background: red;
    background: transparent;
}

AudioWaveForm {
    border-radius: 5px;
    min-height: 30px;
    background: red;
    background: transparent;
}

VoiceChat > IconTextButton {
    max-height: 25;
    min-height: 25;
    min-width: 25;
    max-width: 25;
    border-radius: 15px;
    text-align: center;
}

VoiceChat > IconTextButton:hover, VoiceChat > IconTextButton:pressed {
    background: transparent;
}

Label#reply_author {
    font-weight: bold;
    font-size: 13px;
}

ReplyChat {
    background: transparent;
    background: #e6e6e6;
    border-radius: 5px;
}

ReplyChat#WhatsApp {
    background: #eeeeee;
    border-left: 2px solid black;
}

ReplyChat > IconTextButton, ChatTypeButton {
    padding: 0px;
    text-align: left;
    background: transparent;
    font-size: 11px;
}

ReplyChat > IconTextButton#photo {
    text-align: right;
    margin-right: 2px;
}

ReplyChat > IconTextButton:hover, ChatTypeButton:hover {
    text-align: left;
    background: transparent;
}

TelegramFooterReply > IconTextButton {
    max-height: 15px;
    max-width: 15px;
    border-radius: 8px;
}

DetailsView VFrame {
    border-radius: 3px;
}

Label#description, DetailsView VFrame > Label#description {
    font-size: 13px;
    font-weight: bold;
}

DetailsView VFrame#details_frame {
    min-height: 210px;
    max-height: 210px;
}

DetailsView VFrame > Label#details, DetailsView VFrame > Label#creator 
, DetailsView VFrame > Label#members_count {
    font-size: 11px;
    font-weight: bold;
    color: #515151;
}

DetailsButton, MemberItem {
    padding: 5px;
    min-height: 45px;
    max-height: 45px;
    background: white;
    border: none;
}

MemberItem {
    padding: 2px;
}

MemberItem > AvatarButton {
    background: transparent;
}

MemberItem > Label#admin {
    font-size: 8px;
    border: 1px solid green;
    color: green;
    border-radius: 5px;
}

MemberItem > Label#member_description, MemberItem > Label#member_unique_id {
    font-size: 12px;
    font-weight: 600;
    color: #a3a3a3;
}

MembersList > IconTextButton#members_search {
    border-radius: 15px;
}

DetailsButton:pressed, MemberItem:pressed {
    background: #f2f2f2;
}

DetailsButton > Label#icon {
    min-height: 20px;
    max-height: 20px;
    min-width: 20px;
    max-width: 20px;
}

ImageLabel {
    min-height: 100px;
    max-height: 100px;
    min-width: 100px;
    max-width: 100px;
    border-radius: 10px;
}

DetailsButton > Label#text, DetailsButton > Label#red_text {
    font-size: 13px;
    font-weight: bold;
}


DetailsButton > Label#red_text {
    color: red;
}

DetailsView  Scrollable QScrollBar:vertical {
    width: 3px;
}

DetailsView  Scrollable QScrollBar::handle:vertical{
    margin: 0px;
}

QTabWidget::pane {
    border-radius: 5px;
}

QTabBar::tab {
    border-top-left-radius: 5px;
    border-top-right-radius: 5px;
    padding: 5px;
    font-size: 15px;
    font-weight: bold;
    margin: 5px;
    border-bottom-color: black;
}

QTabWidget::tab-bar {
    alignment: center;
}

QTabBar::tab:hover {
    background: #f2f2f2;
}

QTabBar::tab:selected {
    background: #e1e1e1;
    border-bottom: 2px solid black;
}

ProfileDialog VFrame {
    border-radius: 10px;
}

ProfileDialog VFrame#edit_frame {
    background: #e1e1e1;
}

#labeled_edit {
    border-radius: 5px;
    border: 1px solid #f2f2f2;
    font-size: 14px;
    font-weight: 600;
    background: #f2f2f2;
}

QLabel#bold {
    font-size: 10px;

}

LabeledLabel Label#display_name, LabeledLabel Label#description {
    background: #f2f2f2;
    border-radius: 5px;
    padding: 5px;
}

QGroupBox {
    border: 0px;
    border-top: 2px solid #e1e1e1;
    border-radius: 5px;
    margin-top: 8px;
    background: white;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top center;
    padding: 0 3px;
}

MyAccountButton {
    min-height: 40px;
    border: none;
    background: white;
    border-radius: 5px;
    font-size: 14px;
    font-weight: 600;
    text-align: left;
    padding-left: 10px;
}

MyAccountButton:hover {
    background: #f2f2f2;
}

MyAccountButton:pressed {
    background: #e1e1e1;
}

MyAccountButton#red {
    color: red;
}

VFrame QLabel {
    font-size: 12px;
    font-weight: 600;
}

VFrame > Label#form_label {
    padding: 1px;
    border-radius: 5px;
    background: #e2e2e2;
    font-size: 14px;
    font-weight: 600;
}

VFrame#my_account_edit_frame QLineEdit {
    border: 2px solid #e1e1e1;
    border-radius: 5px;
}

PasswordLineEdit IconTextButton, PasswordLineEdit IconTextButton:hover, PasswordLineEdit IconTextButton:pressed {
    background: transparent;
}

VFrame#my_account_edit_frame Label#notify_password {
    font-size: 10px;
}

QToolTip {
    border-radius: 5px;
}

SearchedChannelItem {
    border-radius: 5px;
}


SearchedChannelItem:hover {
    background: #f2f2f2;
}

SearchedChannelItem:pressed {
    background: #e1e1e1;
}

Sign QLineEdit {
    min-height: 30px;
    background: #e1e1e1;
}

Sign Labeled Label#bold, Sign Labeled Label#required {
    font-size: 13px;
}

CameraPhotoDialog IconTextButton {
    text-align: left;
}









"""
# AMEBO_QSS = ""
