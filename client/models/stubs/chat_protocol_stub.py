from typing import Union
from prmp_hash import PRMP_Hash, time

print(PRMP_Hash.gen_id())
print(time.time())
{500: "caller_id is not the same as the current client user."}


class SIGN:
    SIGN_IN = {
        "request": {"action": "signin", "unique_id": "", "password": ""},
        "response": {
            200: "successful",
            400: "invalid username or password",
            401: "invalid username or password or api_key",
        },
    }
    SIGN_UP = {
        "request": {
            "action": "signup",
            "unique_id": Union[str, int],
            "password": str,
            "display_name": str,
            "description": str,
            "avatar": str,
            "is_bot": bool,
        },
        "response": {
            200: "successful",
            400: "invalid username or password",
            401: "unique_id already exists",
            402: "signup error",
        },
    }
    SIGN_OUT = {
        "request": {
            "action": "signout",
            "caller_id": int,
        },
        "response": {},
    }


class SUB_ROOM:
    # Role that can be in this room. People with this role in the main room will be able to
    # interact in this subroom.
    # Whether to hide this subroom from people without the assigned role.
    SET_ROLE = {
        "request": {
            "action": "set_role",
            "role_name": int,
            "room_id": int,
            "sub_room_name": int,
            "caller_id": int,
            "is_broadcast": bool,
        },
        "response": {
            200: "successful",
            400: "room doesn't exist",
            401: "caller doesn't exist",
            402: "not authorized",
            403: "sub_room doesn't exist",
            404: "role doesn't exist",
        },
    }
    SET_VISIBILITY = {
        "request": {
            "action": "set_visibility",
            "room_id": int,
            "sub_room_name": int,
            "caller_id": int,
            "hidden": bool,
            "is_broadcast": bool,
        },
        "response": {
            200: "successful",
            400: "room doesn't exist",
            401: "caller doesn't exist",
            402: "not authorized",
            403: "sub_room doesn't exist",
        },
    }


class ROOM:
    # BROADCAST also has its own by replacing ROOM with BROADCAST in the following actions.
    CREATE_ROOM = {
        "request": {
            "action": "create_room",
            "unique_id": str,
            "room_name": str,
            "room_description": str,
            "room_avatar": str,
            "is_broadcast": bool,
            "is_sub_room": bool,
            "room_id": int,
            "caller_id": int,
        },
        "response": {
            200: "successful",
            400: "room already exist",
            401: "user doesn't exist",
            402: "room doesn't exist",
            403: "member doesn't exist",
            404: "sub_room already exist",
            405: "not authorized",
        },
    }
    EDIT_ROOM_INFO = {
        "request": {
            "action": "edit_room_info",
            "room_id": int,
            "sub_room_id": int,
            "display_name": str,
            "description": str,
            "avatar": str,
            "caller_id": int,
            "is_broadcast": bool,
        },
        "response": {
            200: "successful",
            400: "room doesn't exist",
            401: "caller doesn't exist",
            402: "room not authorized",
            403: "sub_room doesn't exist",
            404: "sub_room not authorized",
        },
    }
    DELETE_ROOM = {
        "request": {
            "action": "delete_room",
            "room_id": int,
            "sub_room_name": str,
            "caller_id": int,
            "is_broadcast": bool,
        },
        "response": {
            200: "successful",
            400: "room doesn't exist",
            401: "not authorized",
            402: "caller doesn't exist",
            403: "sub_room doesn't exist",
            404: "sub_room not authorized",
        },
    }
    JOIN_ROOM = {
        "request": {
            "action": "join_room",
            "room_id": int,
            "caller_id": int,
            "is_broadcast": bool,
            "invite_link": str,
        },
        "response": {
            200: "successful",
            400: "user doesn't exist",
            401: "room doesn't exist",
            402: "not authorized",
        },
    }
    LEAVE_ROOM = {
        "request": {
            "action": "leave_room",
            "room_id": int,
            "caller_id": int,
            "is_broadcast": bool,
        },
        "response": {
            200: "successful",
            400: "user doesn't exist",
            401: "room doesn't exist",
        },
    }
    ADD_MEMBER = {
        "request": {
            "action": "add_member",
            "room_id": int,
            "caller_id": int,
            "user_id": int,
            "is_broadcast": bool,
        },
        "response": {
            200: "successful",
            400: "room doesn't exist",
            401: "caller doesn't exist",
            402: "not authorized",
            403: "user already in room",
            404: "user doesn't exist",
        },
    }
    DELETE_MEMBER = {
        "request": {
            "action": "delete_member",
            "room_id": int,
            "is_broadcast": bool,
            "user_id": int,
            "caller_id": int,
            "is_bot": bool,
        },
        "response": {
            200: "successful",
            400: "room doesn't exist",
            401: "caller doesn't exist",
            402: "not authorized",
            403: "user doesn't exist",
        },
    }
    BAN_MEMBER = {
        "request": {
            "action": "ban_member",
            "room_id": int,
            "caller_id": int,
            "user_id": int,
            "is_broadcast": bool,
        },
        "response": DELETE_MEMBER["response"],
    }
    ADD_ROLE = {
        "request": {
            "action": "add_role",
            "role_name": str,
            "role_description": str,
            "role_avatar": str,
            "room_id": int,
            "is_broadcast": bool,
            "caller_id": int,
        },
        "response": {
            200: "successful",
            400: "room doesn't exist",
            401: "caller doesn't exist",
            402: "not authorized",
            403: "role already exist",
        },
    }
    REMOVE_ROLE = {
        "request": {
            "action": "remove_role",
            "role_name": int,
            "room_id": int,
            "is_broadcast": bool,
            "caller_id": int,
        },
        "response": {
            200: "successful",
            400: "room doesn't exist",
            401: "caller doesn't exist",
            402: "not authorized",
            403: "role doesn't exist",
        },
    }
    ADD_MEMBER_ROLE = {
        "request": {
            "action": "add_member_role",
            "room_id": int,
            "is_broadcast": bool,
            "caller_id": int,
            "member_id": int,
            "role_name": int,
        },
        "response": {
            200: "successful",
            400: "room doesn't exist",
            401: "caller doesn't exist",
            402: "not authorized",
            403: "member doesn't exist",
            404: "role doesn't exist",
        },
    }
    REMOVE_MEMBER_ROLE = {
        "request": {
            "action": "remove_member_role",
            "role_name": int,
            "member_id": int,
            "room_id": int,
            "is_broadcast": bool,
            "caller_id": int,
            "is_bot": bool,
        },
        "response": {
            200: "successful",
            400: "room doesn't exist",
            401: "caller doesn't exist",
            402: "not authorized",
            403: "member doesn't exist",
            404: "role doesn't exist",
        },
    }
    CREATE_ROOM_INVITE_LINK = {
        "request": {
            "action": "create_room_invite_link",
            "room_id": int,
            "is_broadcast": bool,
            "caller_id": int,
        },
        "response": {
            200: "successful",
            400: "room doesn't exist",
            401: "caller doesn't exist",
            402: "not authorized",
        },
    }
    REVOKE_ROOM_INVITE_LINK = {
        "request": {
            "action": "revoke_room_invite_link",
            "room_id": int,
            "is_broadcast": bool,
            "caller_id": int,
        },
        "response": {
            200: "successful",
            400: "room doesn't exist",
            401: "caller doesn't exist",
            402: "not authorized",
        },
    }
    SET_PINNED_MESSAGE = {
        "request": {
            "action": "set_pinned_message",
            "room_id": int,
            "is_broadcast": bool,
            "caller_id": int,
            "message_id": int,
        },
        "response": {
            200: "successful",
            400: "room doesn't exist",
            401: "caller doesn't exist",
            402: "not authorized",
            403: "message doesn't exist",
        },
    }
    REMOVE_PINNED_MESSAGE = {
        "request": {
            "action": "remove_pinned_message",
            "room_id": int,
            "is_broadcast": bool,
            "caller_id": int,
            "message_id": int,
        },
        "response": {
            200: "successful",
            400: "room doesn't exist",
            401: "caller doesn't exist",
            402: "not authorized",
            403: "message doesn't exist",
        },
    }


class MESSAGE:
    SEND_MESSAGE = {
        "request": {
            "action": "send_message",
            "message_id": int,
            "receiver_id": int,
            "sub_room_name": str,
            "is_room": bool,
            "is_broadcast": bool,
            "author_id": int,
            "is_bot": bool,
            "type": int,
            "text": str,
            "attachment": str,
            "attachment_type": str,
            "reply_message_id": int,
            "forwarder": int,
            "forwarder_at": int,
            "forwarded_to": int,
            "forwarded_from": int,
        },
        "response": {
            200: "successful",
            400: "author doesn't exists",
            401: "receiver not provided",
            402: "receiver doesn't exist",
            403: "not authorized",
            404: "member doesn't exists",
        },
    }
    DELETE_MESSAGE = {
        "request": {
            "action": "delete_message",
            "message_id": int,
            "caller_id": int,
            "receiver_id": int,
            "is_room": bool,
            "sub_room_name": str,
            "is_broadcast": bool,
        },
        "response": {
            200: "successful",
            400: "room doesn't exists",
            401: "caller doesn't exists",
            402: "not authorized",
            403: "message doesn't exists",
        },
    }
    # Whether message is sent, read, or seen.
    MESSAGE_STATE = {
        "request": {
            "action": "message_state",
            "message_id": int,
            "caller_id": int,
            "receiver_id": int,
            "sub_room_name": str,
            "is_broadcast": bool,
            "is_room": bool,
            "state": int,  # {0=seen, 1=read}
        },
        "response": {
            200: "successful",
            400: "user doesn't exists",
            401: "room doesn't exists",
        },
    }


class USER:
    EDIT_USER_INFO = {
        "request": {
            "action": "edit_user_info",
            "unique_id": Union[str, int],
            "password": str,
            "display_name": str,
            "description": str,
            "avatar": str,
            "caller_id": int,
            "is_bot": bool,
        },
        "response": {
            "action": "edit_user_info",
            "unique_id": Union[str, int],
            "password": str,
            "display_name": str,
            "description": str,
            "avatar": str,
            "caller_id": int,
            "is_bot": bool,
        },
    }
    DELETE_USER = {
        "request": {
            "action": "delete_user",
            "caller_id": int,
            "is_bot": bool,
        },
        "response": {
            "action": "delete_user",
            "caller_id": int,
            "is_bot": bool,
        },
    }
    INFO = {
        "action": "info",
        "caller_id": int,
        "id": int,
        "is_room": bool,
        "is_broadcast": bool,
        "sub_room_name": str,
        "role_name": str,
    }
