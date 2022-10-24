import json, asyncio, functools
from websockets.legacy.server import (
    WebSocketServerProtocol,
    Serve,
    Union,
)
from websockets.exceptions import ConnectionClosed
from amebo import *


Data = Union[str, bytes]


def EventLoop() -> asyncio.AbstractEventLoop:
    return asyncio.get_event_loop()


class AmeboServer(Serve):
    def __init__(self, ip: str, port: int):
        super().__init__(self.handler, ip, port)

        self.amebo_clients: list[AmeboClient] = []
        self.websockets = self.ws_server.websockets
        self.ip = ip
        self.port = port

    async def handler(self, client: WebSocketServerProtocol, path: str):
        amebo_client = AmeboClient(client, self)
        self.amebo_clients.append(amebo_client)
        await amebo_client.start_session()
        # asyncio.create_task(amebo_client.start_session())

    def remove_client(self, client: "AmeboClient"):
        if client in self.amebo_clients:
            self.amebo_clients.remove(client)

    def broadcast(
        self,
    ):
        ...


class AmeboClient:
    def __init__(
        self, ws_handler: WebSocketServerProtocol, server: "AmeboServer"
    ) -> None:
        self.ws_handler = ws_handler
        self.server = server
        self.user: Union[AmeboUser, AmeboBot] = None
        self.signed_in = False
        self.stop = False

    @property
    def is_bot(self):
        return isinstance(self.user, AmeboBot)

    async def send(self, data: Union[str, bytes]):
        try:
            await self.ws_handler.send(data)
            return True
        except ConnectionClosed as cc:
            print(f"Send Error: Close(code={cc.rcvd.code}, reason={cc.rcvd.reason})")
            return False

    async def send_json(self, data: Json) -> Json:
        _json = data.to_str()
        return await self.send(_json)

    async def recv(self) -> Data:
        try:
            return await self.ws_handler.recv()
        except ConnectionClosed as cc:
            print(f"Recv Error: Close(code={cc.rcvd.code}, reason={cc.rcvd.reason})")
            return None

    async def recv_json(self) -> Json:
        recv = await self.recv()
        if recv:
            try:
                _json = Json.from_str(recv or "{}")
                return _json
            except json.JSONDecodeError as jde:
                print(f"Message Error, {recv}")
                return False

        else:
            return recv

    async def close(self, code: int = 1000, reason: str = ""):
        return await self.ws_handler.close(code, reason)

    def start_message_listener(self):
        print("Starting Message Listener")

        async def start():
            while not self.stop:
                if self.user:
                    if self.user.messages:
                        id = list(self.user.messages.keys())[0]
                        message = self.user.messages[id]
                        if await self.send_json(message):
                            del self.user.messages[id]
                print("running")

        asyncio.create_task(start())
        EventLoop().run_until_complete(start())
        # asyncio.run_coroutine_threadsafe(start(), asyncio.new_event_loop())

    async def start_session(self):
        print("Starting Session")

        # self.start_message_listener()
        # threading.Thread(target=self.start_message_listener).start()

        while not self.stop:
            json = await self.recv_json()
            if json and json.action:
                action = json.action.lower()
                action_handler = getattr(self, f"{action}_handler", None)

                if action == "signout":
                    await self.close(1000, "Signing Out")
                    self.server.remove_client(self)
                    self.stop = True
                    self.user.last_seen = time()
                    print("Client Signed Out")

                elif not action_handler:
                    if not await self.send_json(
                        Json(response=f"Action {action} is not supported.")
                    ):
                        print("Send : Client disconnected.")
                        break

                else:
                    response_json = Json(action=action)

                    if not action in ["signout", "signin", "signup"]:
                        if json.caller_id == self.user.id:
                            response_json.response = action_handler(json)
                        else:
                            response_json.response = 500
                    else:
                        response_json.response = action_handler(json)

                    if response_json.response:
                        await self.send_json(response_json)

            elif json == False:
                if not await self.send_json(Json(response=f"Invalid Data")):
                    print("Send : Client disconnected.")
                    break

            elif json == None:
                print("Recv : Client disconnected.")
                break

        self.signed_in = False

    # action handlers

    def signin_handler(self, json: Json):
        unique_id: str = json.unique_id
        password: str = json.password
        response = 400

        if unique_id and password:
            if "api_key" in json:
                get = functools.partial(Amebo.get_bot, api_key=json.api_key)
                response = 401
            else:
                get = Amebo.get_user

            user = get(unique_id=unique_id, password=password)
            if user:
                self.user = user
                self.signed_in = True
                response = 200

        return response

    def signup_handler(self, json: Json):
        unique_id = json.unique_id
        password = json.password

        response = 400

        if unique_id and password:
            if not Amebo.unique_id_exist(unique_id):
                create = Amebo.create_bot if json.is_bot else Amebo.create_user

                create(
                    unique_id=unique_id,
                    password=password,
                    display_name=json.display_name,
                    description=json.description,
                    avatar=json.avatar,
                )
                response = 200

            else:
                response = 401

        return response

    def set_role_handler(self, json: Json):
        role_name = json.role_name
        sub_room_name: int = json.sub_room_name
        caller_id = json.caller_id

        response = 0

        if room := Amebo.get_room(json):
            member: AmeboMember
            if member := GET(room.members, caller_id):
                if AmeboMemberPermissions.MANAGE_SUBROOMS in member.permissions:
                    if role := GET(room.roles, role_name):
                        if sub_room := GET(room.sub_rooms, sub_room_name):
                            sub_room.set_role(role)
                            response = 200
                        else:
                            response = 404
                    else:
                        response = 403
                else:
                    response = 402
            else:
                response = 401
        else:
            response = 400

        return response

    def set_visibility_handler(self, json: Json):
        sub_room_name: int = json.sub_room_name
        caller_id = json.caller_id
        hidden = json.hidden

        response = 0

        if room := Amebo.get_room(json):
            member: AmeboMember
            if member := GET(room.members, caller_id):
                if AmeboMemberPermissions.MANAGE_SUBROOMS in member.permissions:
                    if sub_room := GET(room.sub_rooms, sub_room_name):
                        sub_room.set_hidden(hidden)
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

    def create_room_handler(self, json: Json):
        caller_id = json.caller_id
        unique_id = json.unique_id
        room_name = json.room_name
        room_description = json.room_description
        room_avatar = json.room_avatar
        is_broadcast = json.is_broadcast
        is_sub_room = json.is_sub_room

        response = 0

        if is_sub_room:
            if room := Amebo.get_room(json):
                member: AmeboMember
                if member := GET(room.members, caller_id):
                    if room_name.lower() not in room.sub_rooms:
                        if AmeboMemberPermissions.MANAGE_SUBROOMS in member.permissions:
                            room.create_sub_room(
                                display_name=room_name,
                                description=room_description,
                                avatar=room_avatar,
                            )
                            response = 200
                        else:
                            response = 405
                    else:
                        response = 404
                else:
                    response = 403
            else:
                response = 4032

        elif not Amebo.unique_id_exist(unique_id):
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
        sub_room_id = json.sub_room_id
        display_name = json.display_name
        description = json.description
        avatar = json.avatar
        caller_id = json.caller_id

        response = 0

        if room := Amebo.get_room(json):
            member: AmeboMember
            if member := GET(room.members, caller_id):
                if sub_room_id:
                    if sub_room := GET(room.sub_rooms, sub_room_id):
                        if AmeboMemberPermissions.MANAGE_SUBROOMS in member.permissions:
                            sub_room.edit(
                                display_name=display_name,
                                description=description,
                                avatar=avatar,
                            )
                        else:
                            response = 404
                    else:
                        response = 403
                elif AmeboMemberPermissions.MANAGE_ROOM in member.permissions:
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
        sub_room_name = json.sub_room_name
        caller_id = json.caller_id
        is_broadcast = json.is_broadcast

        response = 0

        if room := Amebo.get_room(json):
            if sub_room_name:
                member: AmeboMember
                if member := GET(room.members, caller_id):
                    if sub_room := GET(room.sub_rooms, sub_room_name):
                        if AmeboMemberPermissions.MANAGE_SUBROOMS in member.permissions:
                            room.delete_sub_room(sub_room)
                            response = 200
                        else:
                            response = 404
                    else:
                        response = 403
                else:
                    response = 402
            else:
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
                if AmeboMemberPermissions.MANAGE_MEMBERS in member.permissions:
                    if GET(room.members, user_id):
                        response = 403
                    elif user := Amebo.user_or_bot(user_id):
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
                if AmeboMemberPermissions.MANAGE_MEMBERS in member.permissions:
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
            if user := Amebo.user_or_bot(user_id):
                rooms[room_id].banned_users.append(user.id)

        return response

    def add_role_handler(self, json: Json):
        role_name = json.role_name
        role_description = json.role_description
        role_avatar = json.role_avatar
        caller_id = json.caller_id

        response = 0

        if room := Amebo.get_room(json):
            member: AmeboMember
            if member := GET(room.members, caller_id):
                if AmeboMemberPermissions.MANAGE_ROLES in member.permissions:
                    if role_name.lower() not in room.roles:
                        room.add_role(
                            display_name=role_name,
                            description=role_description,
                            avatar=role_avatar,
                        )
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

    def remove_role_handler(self, json: Json):
        role_name = json.role_name
        caller_id = json.caller_id

        response = 0

        if room := Amebo.get_room(json):
            member: AmeboMember
            if member := GET(room.members, caller_id):
                if AmeboMemberPermissions.MANAGE_ROLES in member.permissions:
                    if role := GET(room.roles, role_name):
                        room.delete_role(role)
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

    def add_member_role_handler(self, json: Json):
        caller_id = json.caller_id
        member_id = json.member_id
        role_name = json.role_name

        response = 0

        if room := Amebo.get_room(json):
            member: AmeboMember
            if member := GET(room.members, caller_id):
                if AmeboMemberPermissions.MANAGE_ROLES in member.permissions:
                    member_to_add_role: AmeboMember
                    if member_to_add_role := GET(room.members, member_id):
                        if role := GET(room.roles, role_name):
                            member_to_add_role.add_role(role)
                            room.add_message(json)
                            response = 200
                        else:
                            response = 404
                    else:
                        response = 403
                else:
                    response = 402
            else:
                response = 401
        else:
            response = 400

        return response

    def remove_member_role_handler(self, json: Json):
        caller_id = json.caller_id
        member_id = json.member_id
        role_name = json.role_name

        response = 0

        if room := Amebo.get_room(json):
            member: AmeboMember
            if member := GET(room.members, caller_id):
                if AmeboMemberPermissions.MANAGE_ROLES in member.permissions:
                    member_to_add_role: AmeboMember
                    if member_to_add_role := GET(room.members, member_id):
                        if role := GET(room.roles, role_name):
                            member_to_add_role.delete_role(role)
                            room.add_message(json)
                            response = 200
                        else:
                            response = 404
                    else:
                        response = 403
                else:
                    response = 402
            else:
                response = 401
        else:
            response = 400

        return response

    def create_room_invite_link_handler(self, json: Json):
        caller_id = json.caller_id

        response = 0

        if room := Amebo.get_room(json):
            member: AmeboMember
            if member := GET(room.members, caller_id):
                if AmeboMemberPermissions.MANAGE_INVITES in member.permissions:
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
                if AmeboMemberPermissions.MANAGE_INVITES in member.permissions:
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
                if AmeboMemberPermissions.MANAGE_MESSAGES in member.permissions:
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
                if AmeboMemberPermissions.MANAGE_MESSAGES in member.permissions:
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
        sub_room_name = json.sub_room_name
        is_room = json.is_room

        forwarder = json.forwarder
        forwarded_to = json.forwarded_to

        response = 0

        if forwarder:
            if forwarder := Amebo.user_or_bot(forwarder):
                if forwarded_to:
                    if is_room:
                        if room := Amebo.get_room(Json(room_id=forwarded_to, **json)):
                            member: AmeboMember
                            if member := GET(room.members, forwarder.id):
                                if forwarder.id not in room.banned_users:
                                    sub_room: AmeboSubRoom
                                    if sub_room_name and (
                                        sub_room := GET(room.sub_rooms, sub_room_name)
                                    ):
                                        if sub_room.role.unique_name in member.roles:
                                            sub_room.add_message(json)
                                            response = 200
                                        else:
                                            response = 403
                                    elif (
                                        AmeboMemberPermissions.SEND_MESSAGES
                                        in member.permissions
                                    ):
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
                    elif user := Amebo.user_or_bot(forwarded_to):
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
            if Amebo.user_or_bot(author_id):
                if receiver_id:
                    if is_room:
                        if room := Amebo.get_room(Json(room_id=receiver_id, **json)):
                            member: AmeboMember
                            if member := GET(room.members, author_id):
                                if author_id not in room.banned_users:
                                    sub_room: AmeboSubRoom
                                    if sub_room_name and (
                                        sub_room := GET(room.sub_rooms, sub_room_name)
                                    ):
                                        if sub_room.role.unique_name in member.roles:
                                            sub_room.add_message(json)
                                            response = 200
                                        else:
                                            response = 403
                                    elif (
                                        AmeboMemberPermissions.SEND_MESSAGES
                                        in member.permissions
                                    ):
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
                    elif user := Amebo.user_or_bot(receiver_id):
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
                if AmeboMemberPermissions.MANAGE_MESSAGES in member.permissions:
                    sub_room: AmeboSubRoom
                    if sub_room_name and (
                        sub_room := GET(room.sub_rooms, sub_room_name)
                    ):
                        if sub_room.role.unique_name in member.roles:
                            sub_room.add_message(json)
                            response = 200
                        else:
                            response = 403
                    elif AmeboMemberPermissions.SEND_MESSAGES in member.permissions:
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
            if user := Amebo.user_or_bot(receiver_id):
                user.add_message(json)
            else:
                response = 400

            response = 400

        return response

    def message_state_handler(self, json: Json):
        caller_id = json.caller_id
        receiver_id = json.receiver_id
        sub_room_name = json.sub_room_name
        is_room = json.is_room

        response = 0

        if is_room:
            if room := Amebo.get_room(Json(room_id=receiver_id, **json)):
                if GET(room.members, caller_id):
                    sub_room: AmeboSubRoom
                    if sub_room_name and (
                        sub_room := GET(room.sub_rooms, sub_room_name)
                    ):
                        sub_room.add_message(json)
                    else:
                        room.add_message(json)
            else:
                response = 401
        else:
            if user := Amebo.user_or_bot(receiver_id):
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

        if user := Amebo.user_or_bot(caller_id):
            if is_room:
                if room := Amebo.get_room(json):
                    user.add_message(room.json())


if __name__ == "__main__":
    amebo_server = AmeboServer("localhost", 8000)

    print(f"AmeboServer started on ip={amebo_server.ip}, port={amebo_server.port}")
    EventLoop().run_until_complete(amebo_server)
    EventLoop().run_forever()
