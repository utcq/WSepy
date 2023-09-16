import wsepy

socket = wsepy.Server(port=5005)

@socket.command("echo")
async def echo(client, cipher, message:str):
    print(f"Client: {cipher.decrypt(message)}")
    await client.send(f"/echo '{cipher.encrypt('Hello Client')}'")

    await client.send(f"/disconnect")

socket.run()