import site

site.addsitedir(
    r"C:\Users\Administrator\Desktop\GITHUB_PROJECTS\Amebo\test\websockets\prmp_websockets"
)
from prmp_websockets import *
from .amebo_server_core import *
from json import JSONDecodeError


class AmeboServer(PRMP_WebSocketServer):
    def __init__(self, server_address: tuple[str, int], **kwargs) -> None:
        super().__init__(server_address, AmeboClientHandler, **kwargs)

    def on_start(self):
        print(f"\nServer started at {time.time(): .0f}")

    def on_new_client(self, client):
        print(f"New Client {client.client_address[0]} Connected")

    def on_client_left(self, client):
        print(f"Client {client.client_address[0]} left")

    def on_accept(self, sock, addr):
        print(f"Client {addr} Accepted")


class AmeboClientHandler(AmeboClientHandlerBase, PRMP_WebSocketHandler):
    def __init__(self, socket, addr, server: "PRMP_WebSocketServer"):
        AmeboClientHandlerBase.__init__(self)
        PRMP_WebSocketHandler.__init__(self, socket, addr, server)

    def setup(self):
        return super().setup()

    def on_connected(self):
        ...

    def on_message(self):
        data = self.data

        try:
            json = Json.from_str(data)
        except JSONDecodeError as jde:
            print(f"Message Error, {data}")

        if json and json.action:
            action = json.action.lower()
            action_handler = getattr(self, f"{action}_handler", None)

            if action == "signout":
                self.send_close(1000, "Signing Out")
                self.server.remove_client(self)
                self.user.last_seen = time()
                print("Client Signed Out")

            elif not action_handler:
                print(f"Action {action} is not supported.")
                if not self.send_json(
                    Json(response=f"Action {action} is not supported.")
                ):
                    print("Send : Client disconnected.")
                    self.keep_alive = False

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
                    self.send_json(response_json)

        elif json == False:
            if not self.send_json(Json(response=f"Invalid Data")):
                print("Send : Client disconnected.")
                self.keep_alive = False

        elif json == None:
            print("Recv : Client disconnected.")
            self.keep_alive = False

    def on_ping(self):
        ...

    def on_pong(self):
        ...

    def on_closed(self):
        if self.user:
            self.user.status = False

    def send_json(self, data: Json) -> Json:
        _json = data.to_str()
        return self.send_message(_json)
