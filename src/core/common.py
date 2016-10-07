import shlex
from . import constants as const

class xWSLSockMixin:
    def sendall(self, command, channel):
        channel.sendall(command.encode("UTF-8"))
    
    def recv(self, size, channel):
        return channel.recv(size).decode("UTF-8")
    
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