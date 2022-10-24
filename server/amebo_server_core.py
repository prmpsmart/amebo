from .amebo_server_models import *


class AmeboClientHandlerBase:
    def __init__(self) -> None:
        self.user: AmeboUser = None

    # action handlers

    def signup_handler(self, json: Json):
        unique_id = json.unique_id
        password = json.password

        response = 400

        if unique_id and password:
            if not Amebo.unique_id_exist(unique_id):
                user = Amebo.create_user(
                    unique_id=unique_id,
                    password=password,
                    display_name=json.display_name,
                    description=json.description,
                    avatar=json.avatar,
                )
                response = Json(id=user.id, response=200)
                self.user = None
            else:
                response = 401
        return response

    def signin_handler(self, json: Json):
        unique_id: str = json.unique_id
        password: str = json.password
        response = 400

        if not self.user:
            if unique_id and password:
                user = Amebo.get_user(unique_id=unique_id, password=password)
                if user:
                    user.status = True
                    self.user = user
                    response = 200
                    response = Json(response=200, **user.json)
        else:
            response = 401

        return response

    def create_room_handler(self, json: Json):
        caller_id = json.caller_id
        unique_id = json.unique_id
        room_name = json.room_name
        room_description = json.room_description
        room_avatar = json.room_avatar
        is_broadcast = json.is_broadcast

        response = 0

        if Amebo.unique_id_exist(unique_id):
            if user := GET(Amebo.amebo_users, caller_id):
                create = (
                    Amebo.create_broadcast_channel
                    if is_broadcast
                    else Amebo.create_group
                )
                create(
                    creator=user,
                    unique_id=unique_id,
                    display_name=room_name,
                    description=room_description,
                    avatar=room_avatar,
                )
                response = 200
            else:
                response = 401
        else:
            response = 400

        return response

    def edit_room_info_handler(self, json: Json):
        display_name = json.display_name
        description = json.description
        avatar = json.avatar
        caller_id = json.caller_id

        response = 0

        if room := Amebo.get_room(json):
            member: AmeboMember
            if member := GET(room.members, caller_id):
                if member.is_admin:
                    room.edit(
                        display_name=display_name,
                        description=description,
                        avatar=avatar,
                    )
                else:
                    response = 402
            else:
                response = 401
        else:
            response = 400

        return response

    def delete_room_handler(self, json: Json):
        caller_id = json.caller_id
        is_broadcast = json.is_broadcast

        response = 0

        if room := Amebo.get_room(json):
            if caller_id == room.creator.id:
                delete = (
                    Amebo.delete_group
                    if not is_broadcast
                    else Amebo.delete_broadcast_channel
                )
                delete(room)
                response = 200
            else:
                response = 401
        else:
            response = 400

        return response

    def join_room_handler(self, json: Json):
        caller_id = json.caller_id
        invite_link = json.invite_link

        response = 0

        if user := GET(Amebo.amebo_users, caller_id):
            if room := Amebo.get_room(json):
                if invite_link == room.invite_link and user.id not in room.banned_users:
                    room.add_user(user)
                    response = 200
                else:
                    response = 402
            else:
                response = 401
        else:
            response = 400

        return response

    def leave_room_handler(self, json: Json):
        caller_id = json.caller_id

        response = 0

        if user := GET(Amebo.amebo_users, caller_id):
            if room := Amebo.get_room(json):
                room.delete_user(user)
                response = 200
            else:
                response = 401
        else:
            response = 400

        return response

    def add_member_handler(self, json: Json):
        caller_id = json.caller_id
        user_id = json.user_id

        response = 0

        if room := Amebo.get_room(json):
            member: AmeboMember
            if member := GET(room.members, caller_id):
                if member.is_admin:
                    if GET(room.members, user_id):
                        response = 403
                    elif user := Amebo.get_user(user_id):
                        room.add_user(user)
                        room.add_message(
                            Json(
                                display_name=user.display_name,
                                unique_id=user.unique_id,
                                description=user.description,
                                last_seen=user.last_seen,
                                **json,
                            )
                        )
                        response = 200
                    else:
                        response = 404
                else:
                    response = 402
            else:
                response = 401
        else:
            response = 400

        return response

    def delete_member_handler(self, json: Json):
        caller_id = json.caller_id
        user_id = json.user_id

        response = 0

        if room := Amebo.get_room(json):
            member: AmeboMember
            if member := GET(room.members, caller_id):
                if member.is_admin:
                    if member_to_delete := GET(room.members, user_id):
                        if member_to_delete.user != room.creator:
                            room.delete_user(member_to_delete)
                            room.add_message(json)
                            response = 200
                        else:
                            response = 402
                    else:
                        response = 403
                else:
                    response = 402
            else:
                response = 401
        else:
            response = 400

        return response

    def ban_member_handler(self, json: Json):
        room_id = json.room_id
        user_id = json.user_id
        is_broadcast = json.is_broadcast

        response = self.delete_member_handler(json)
        if response == 200:
            rooms = (
                Amebo.amebo_groups
                if not is_broadcast
                else Amebo.amebo_broadcast_channels
            )
            if user := Amebo.get_user(user_id):
                rooms[room_id].banned_users.append(user.id)

        return response

    def create_room_invite_link_handler(self, json: Json):
        caller_id = json.caller_id

        response = 0

        if room := Amebo.get_room(json):
            member: AmeboMember
            if member := GET(room.members, caller_id):
                if member.is_admin:
                    if not room.invite_link:
                        room.generate_invite_link()
                        room.add_message(json)
                    response = 200
                else:
                    response = 402
            else:
                response = 401
        else:
            response = 400

        return response

    def revoke_room_invite_link_handler(self, json: Json):
        caller_id = json.caller_id

        response = 0

        if room := Amebo.get_room(json):
            member: AmeboMember
            if member := GET(room.members, caller_id):
                if member.is_admin:
                    room.revoke_invite_link()
                    room.add_message(json)
                    response = 200
                else:
                    response = 402
            else:
                response = 401
        else:
            response = 400

        return response

    def set_pinned_message_handler(self, json: Json):
        caller_id = json.caller_id
        id = json.id

        response = 0

        if room := Amebo.get_room(json):
            member: AmeboMember
            if member := GET(room.members, caller_id):
                if member.is_admin:
                    if id in room.messages:
                        room.set_pinned_message(id)
                        room.add_message(json)
                        response = 200
                    else:
                        response = 403
                else:
                    response = 402
            else:
                response = 401
        else:
            response = 400

        return response

    def remove_pinned_message_handler(self, json: Json):
        caller_id = json.caller_id
        id = json.id

        response = 0

        if room := Amebo.get_room(json):
            member: AmeboMember
            if member := GET(room.members, caller_id):
                if member.is_admin:
                    if id in room.messages:
                        room.remove_pinned_message(id)
                        room.add_message(json)
                        response = 200
                    else:
                        response = 403
                else:
                    response = 402
            else:
                response = 401
        else:
            response = 400

        return response

    def send_message_handler(self, json: Json):
        author_id = json.author_id
        receiver_id = json.receiver_id
        is_room = json.is_room

        forwarder = json.forwarder
        forwarded_to = json.forwarded_to

        response = 0

        if forwarder:
            if forwarder := Amebo.get_user(forwarder):
                if forwarded_to:
                    if is_room:
                        if room := Amebo.get_room(Json(room_id=forwarded_to, **json)):
                            member: AmeboMember
                            if member := GET(room.members, forwarder.id):
                                if forwarder.id not in room.banned_users:
                                    if member.is_admin:
                                        room.add_message(json)
                                        response = 200
                                    else:
                                        response = 403
                                else:
                                    response = 403
                            else:
                                response = 404
                        else:
                            response = 402
                    elif user := Amebo.get_user(forwarded_to):
                        if author_id not in user.banned_users:
                            user.add_message(json)
                        else:
                            response = 403
                    else:
                        response = 402
                else:
                    response = 401
            else:
                response = 400
        else:
            if Amebo.get_user(author_id):
                if receiver_id:
                    if is_room:
                        if room := Amebo.get_room(Json(room_id=receiver_id, **json)):
                            member: AmeboMember
                            if member := GET(room.members, author_id):
                                if author_id not in room.banned_users:
                                    if member.is_admin:
                                        room.add_message(json)
                                        response = 200
                                    else:
                                        response = 403
                                else:
                                    response = 403
                            else:
                                response = 404
                        else:
                            response = 402
                    elif user := Amebo.get_user(receiver_id):
                        if author_id not in user.banned_users:
                            user.add_message(json)
                            response = 200
                        else:
                            response = 403
                    else:
                        response = 402
                else:
                    response = 401
            else:
                response = 400

        return response

    def delete_message_handler(self, json: Json):
        receiver_id = json.receiver_id
        id = json.id
        caller_id = json.caller_id
        sub_room_name = json.sub_room_name
        is_room = json.is_room

        response = 0

        if is_room and (room := Amebo.get_room(Json(room_id=receiver_id, **json))):
            member: AmeboMember
            if member := GET(room.members, caller_id):
                if member.is_admin:
                    if member.is_admin:
                        room.add_message(json)
                        response = 200
                    else:
                        response = 403
                    if id in room.messages:
                        room.delete_message(id)
                        response = 200
                    else:
                        response = 402
                else:
                    response = 402
            else:
                response = 401
        else:
            if user := Amebo.get_user(receiver_id):
                user.add_message(json)
            else:
                response = 400

            response = 400

        return response

    def message_state_handler(self, json: Json):
        caller_id = json.caller_id
        receiver_id = json.receiver_id
        is_room = json.is_room

        response = 0

        if is_room:
            if room := Amebo.get_room(Json(room_id=receiver_id, **json)):
                if GET(room.members, caller_id):
                    room.add_message(json)
            else:
                response = 401
        else:
            if user := Amebo.get_user(receiver_id):
                user.add_message(json)
            else:
                response = 400

        return response

    def edit_user_info_handler(self, json: Json):
        ...

    def delete_user_handler(self, json: Json):
        ...

    def info_handler(self, json: Json):
        caller_id = json.id
        id = json.id
        is_room = json.is_room
        is_broadcast = json.is_broadcast
        sub_room_name = json.sub_room_name
        role_name = json.role_name

        if user := Amebo.get_user(caller_id):
            if is_room:
                if room := Amebo.get_room(json):
                    user.add_message(room.json())
