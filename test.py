# from server.amebo_server import *

# amebo_server = AmeboServer("localhost", 8000)
# AmeboObject.PRIME = 7

# print(f"AmeboServer started on ip={amebo_server.ip}, port={amebo_server.port}")

# EventLoop().run_until_complete(amebo_server)
# EventLoop().run_forever()


from server.sync_amebo_server import *

AmeboObject.PRIME = 7
amebo_server = AmeboServer(("localhost", 8000))

print(
    f"AmeboServer started on ip={amebo_server.server_address[0]}, port={amebo_server.server_address[1]}"
)
amebo_server.serve_forever(0)
