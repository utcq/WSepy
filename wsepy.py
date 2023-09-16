import asyncio
from websockets.server import serve
import websockets
import inspect
import uks256

class Server():
    def __init__(self, port:int):
        self.port = port
        self.commands = {}
        self.clients = set()

    async def handler(self, websocket):
        key=uks256.UKey.new()
        cipher = uks256.Cipher(key=key)
        self.clients.add(websocket)
        async for message in websocket:
            if message=="</key_req>":
                await websocket.send(("<KEY>|"+key))
                continue
            words = message.replace('"', "").replace("'", "").split()
            command = words[0]
            args = words[1:]
            await self.run_command(websocket, command.replace("/", ""), cipher, args=args)

    async def __run_async__(self):
        async with serve(self.handler, "localhost", self.port, max_size=(2**32)):
            await asyncio.Future()

    def run(self):
        try:
            asyncio.run(self.__run_async__())
        except KeyboardInterrupt:
            print("Forced Shutdown")
            exit(0)
        except EOFError:
            print("Forced Shutdown")
            exit(0)

    def command(self, name):
        def decorator(func):
            self.commands[name] = func
            return func
        return decorator
    
    async def run_command(self, websocket, name:str, cipher:uks256.Cipher=None, args:list=[]):
        command_function = self.commands.get(name)
        if command_function:
            argspec = inspect.getfullargspec(command_function)
            arg_names = argspec.args; del arg_names[0]; del arg_names[0]
            argsX = {}
            for i, arg in enumerate(arg_names):
                argsX[arg] = args[i]
            try:
                return await command_function(websocket, cipher, **argsX)
            except Exception as e:
                print(e)
        else:
            print(f"Command '/{name}' not found.")



class Client():
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.websocket=None
        self.cipher=None
        self.commands = {}

    async def connect(self) -> None:
        self.websocket = await websockets.connect(f"ws://{self.host}:{self.port}", max_size=(2**32))

    async def send(self, message: str) -> None:
        await self.websocket.send(message)

    async def receive(self) -> str:
        try:
            return await self.websocket.recv()
        except websockets.exceptions.ConnectionClosedOK:
            pass
    
    async def handle(self) -> str:
        while True:
            recv = await self.receive()
            if not recv:
                break

            words = recv.replace('"', "").replace("'", "").split()
            command = words[0]
            args = words[1:]
            await self.run_command(command.replace("/", ""), args=args)
    
    async def disconnect(self) -> None:
        await self.websocket.close()

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.websocket.close()

    def is_connected(self):
        return self.websocket and self.websocket.open
    
    async def handshake(self):
        await self.send("</key_req>")
        signature = await self.receive()
        if signature.startswith("<KEY>|"):
            signature = signature.split("|")[-1]
            self.cipher=uks256.Cipher(key=signature)


    def command(self, name):
        def decorator(func):
            self.commands[name] = func
            return func
        return decorator
    
    async def run_command(self, name:str, args:list=[]):
        command_function = self.commands.get(name)
        if command_function:
            argspec = inspect.getfullargspec(command_function)
            arg_names = argspec.args
            argsX = {}
            for i, arg in enumerate(arg_names):
                argsX[arg] = args[i]
            try:
                return await command_function(**argsX)
            except Exception as e:
                print(e)
        else:
            print(f"Command '/{name}' not found.")