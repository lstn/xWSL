import shlex
from . import constants as const
import asyncio

# ========================================================================== #
# =========================== Synchronous Mixins =========================== #
# ========================================================================== #
class xWSLMixins:
    @staticmethod
    def cmdstring_to_cmdarray(command):
        return shlex.split(command)
    
    @staticmethod
    def cmdarray_to_cmdstring(cmdarr):
        return ' '.join(cmdarr)

    @staticmethod
    def get_modifier_from_mode(mode):
        return const.XWSL_CMD_CMODES.get(mode[0], None)

    @staticmethod
    def get_mode_from_modifier(modifier):
        return const.XWSL_MODIFIERS.get(modifier, None)

class SockMixins:
    def sendall(self, command, channel):
        channel.sendall(command.encode("UTF-8"))
    
    def recv(self, size, channel):
        return channel.recv(size).decode("UTF-8")

# ========================================================================== #
# ============================== Async Mixins ============================== #
# ========================================================================== #

class AsyncxWSLMixins:
    @staticmethod
    async def cmdstring_to_cmdarray(command):
        return shlex.split(command)
    
    @staticmethod
    async def cmdarray_to_cmdstring(cmdarr):
        return ' '.join(cmdarr)

    @staticmethod
    async def get_modifier_from_mode(mode):
        return const.XWSL_CMD_CMODES.get(mode[0], None)

    @staticmethod
    async def get_mode_from_modifier(modifier):
        return const.XWSL_MODIFIERS.get(modifier, None)


class AsyncSockMixins:
    async def sendall(self, command, channel):
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, channel.sendall(command.encode("UTF-8")))
    
    async def recv(self, size, channel):
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, channel.recv(size).decode("UTF-8"))

# ========================================================================== #
# ================================= Asyncio ================================ #
# ========================================================================== #

class AsyncObjMixins:
    async def __aenter__(self):
        print("enter")

    async def __aexit__(self, *args):
        print("exit")

    def __await__(self):
        return self.__aenter__().__await__()

class AsyncIterMixins:
    def __aiter__(self):
        return self

    async def __anext__(self):
        data = await asyncio.sleep(1)# self.fetch_data()
        if data:
            return data
        else:
            raise StopAsyncIteration

   # async def fetch_data(self):
        