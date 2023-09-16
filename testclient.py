import wsepy
import asyncio
import os

socket = wsepy.Client(host="localhost", port="5005")

@socket.command("echo")
async def echo(message:str):
    print(f"Server: {message}")
    print(f"Server: {socket.cipher.decrypt(message)}")

@socket.command("disconnect")
async def disconnect():
    if socket.is_connected():
        await socket.disconnect()

async def main():
    await socket.connect()
    await socket.handshake()
    await socket.send(f"/echo '{socket.cipher.encrypt('Hello Server')}'")
    #await socket.send(f"/echo '{os.urandom(2**26).hex()}'")
    await socket.handle()
    await socket.disconnect()
    return 0

asyncio.run(main())