import asyncio
import threading
from websockets.legacy.server import (
    WebSocketServerProtocol,
    Serve,
    Union,
)
from websockets.exceptions import ConnectionClosed

from .amebo_server_core import *


Data = Union[str, bytes]


def EventLoop() -> asyncio.AbstractEventLoop:
    return asyncio.get_event_loop()


class AmeboServer(Serve):
    def __init__(self, ip: str, port: int):
        super().__init__(self.handler, ip, port, reuse_address=True)

        self.amebo_clients: list[AmeboClientHandler] = []
        self.websockets = self.ws_server.websockets
        self.ip = ip
        self.port = port

    async def handler(self, client: WebSocketServerProtocol, path: str):
        amebo_client = AmeboClientHandler(client, self)
        self.amebo_clients.append(amebo_client)
        await amebo_client.start_session()
        # asyncio.create_task(amebo_client.start_session())

    def remove_client(self, client: "AmeboClientHandler"):
        if client in self.amebo_clients:
            self.amebo_clients.remove(client)

    def broadcast(
        self,
    ):
        ...


class AmeboClientHandler(AmeboClientHandlerBase):
    def __init__(
        self, ws_handler: WebSocketServerProtocol, server: "AmeboServer"
    ) -> None:
        super().__init__()

        self.ws_handler = ws_handler
        self.server = server
        self.user: AmeboUser = None
        self.stop = False

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
            if cc.rcvd:
                print(
                    f"Recv Error: Close(code={cc.rcvd.code}, reason={cc.rcvd.reason})"
                )
            return None

    async def recv_json(self) -> Json:
        recv = await self.recv()
        if recv:
            try:
                _json = Json.from_str(recv or "{}")
                print(_json)
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
            print("Started")
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
        threading.Thread(target=self.start_message_listener).start()

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
                    if not action in ["signout", "signin", "signup"]:
                        if json.caller_id == self.user.id:
                            response = action_handler(json)
                        else:
                            response = 500
                    else:
                        response = action_handler(json)

                    response_json = Json(action=action)

                    if not isinstance(response, int):
                        response_json.update(response)
                    else:
                        response_json.response = response

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
