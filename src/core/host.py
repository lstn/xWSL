import socket
import sys
import subprocess
import os
import asyncio
import logging

dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(dir_path); sys.path.append(os.path.join(dir_path, ".."))

from core import common
from core import constants as const

class fwc:
    fileWriter = None
    @classmethod
    async def init_fwc(cls, fileToWrite=None):
        fileWriter = fileToWrite
        return cls(fileToWrite=fileWriter)
    
    def __init__(self, fileToWrite=None):
        self.fwMixin.fileWrite = fileToWrite
    
    @classmethod
    async def fw(cls, *args):
        if cls.fileWrite is not None:
            await cls.fileWrite.write(*args)

    class fwMixin:
        fileWriter = None

        @classmethod
        async def fw(cls, *args):
            if cls.fileWrite is not None:
                await cls.fileWrite.write(*args)

class SockServer(common.AsyncObjMixins, common.AsyncSockMixins, fwc.fwMixin):
    """
    Instanciate with `init_server`, not __init__.
    """
    _sock_alive = None
    sock = None

    @classmethod
    async def init_server(cls, server_address):
        server_address = server_address
        sock, sock_alive = await cls.start_socket(cls, server_address)

        return cls(sock, sock_alive)
    
    def __init__(self, sock, sock_alive):
        self.sock = sock
    
    async def start_socket(self, server_address):
        if not self._sock_alive:
            try:
                loop = asyncio.get_event_loop()
                sock = await loop.run_in_executor(None, socket.socket, socket.AF_INET, socket.SOCK_STREAM)
                await loop.run_in_executor(None, sock.bind, server_address)
                await loop.run_in_executor(None, sock.listen, const.SOCK.MAX_LISTENS)
                sock_alive = True
                return sock, sock_alive
            except Exception as e:
                return None, False
        else:
            return self.sock, self._sock_alive

    async def terminate(self):
        await self.fileWrite.flush

class Host(common.AsyncxWSLMixins, common.AsyncSockMixins, fwc.fwMixin):
    __is_alive = None

    @classmethod
    async def init_host(cls):
        loop = asyncio.get_event_loop()
        return cls()

    def __init__(self):
        pass
    
    async def process(self):
        loop = asyncio.get_event_loop()
        has_connection_flag = False
        csock = get_sock_server()
        self.connection = None
        
        while not has_connection_flag:
            self.fw("Waiting for a connection...\n")
            try:
                self.connection, client_address = await loop.run_in_executor(None, csock.accept)
                self.fw("Connection from {}\n".format(client_address))
                has_connection_flag = True
                
                response, rlen, rsize = await self.await_command() #
                self.fw("Sending ack request for {} bytes...\n".format(rsize))
                self.send_bytesize(rsize)
                self.await_ack()
                self.send_result(response)

            except socket.timeout:    
                self.fw("socket timed out\n")  
                has_connection_flag = False

            finally:
                if self.connection is not None:
                    self.connection.close()  
                has_connection_flag = False    

    async def await_command(self):
        received_command_flag = False

        while not received_command_flag:
            data = self.recv(const.XWSL_RECV_SIZES["cmd"], self.connection)
            self.fw('received "%s"\n' % data)
            if data:
                self.fw("Sending command for further processing\n")
                cmd_fn, command = self.process_command(data)
                return cmd_fn(command)

    async def process_command(self, command):
        loop = asyncio.get_event_loop()

        cmdarray = await self.cmdstring_to_cmdarray(command)
        mode = await self.get_mode_from_modifier(cmdarray[0])
        cmdarray = cmdarray[1:]
        command = await self.cmdarray_to_cmdstring(cmdarray)
        cmd_fn = await loop.run_in_executor(None, getattr, self, mode, const.SOCK.DEFAULT_MODE)
        return cmd_fn, command

    async def await_ack(self):
        received_ack_flag = False

        while not received_ack_flag:
            ack_confirmation = await self.recv(const.XWSL_RECV_SIZES["ack"], self.connection)
            if ack_confirmation:
                cmdarray = await self.cmdstring_to_cmdarray(ack_confirmation)
                mode = await self.get_mode_from_modifier(cmdarray[0])
                if mode is "ack":
                    received_resp_size_flag = True
                    return ack_confirmation
                else:
                    ack_confirmation = None ##

    
    async def send_bytesize(self, bytesize):
        ack_msg = "{} {}".format(const.XWSL_RESP_RMODES["bytesize"], bytesize)
        await self.sendall(ack_msg, self.connection)
    
    async def send_result(self, result):
        result_msg = "{} {}".format(const.XWSL_RESP_RMODES["data"], result)
        await self.sendall(result_msg, self.connection)

    async def run(self, command):
        loop = asyncio.get_event_loop()
        outs, response = None, None
        self.fw("running client's request\n")

        cmd_runner = await subprocess.Popen(command, universal_newlines=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        try:
            await cmd_runner.communicate(timeout=2)
        except subprocess.TimeoutExpired:
            pass
            # Will likely not be able to get output.
        try:
            if cmd_runner.poll() is not None:
                outs, errs = await cmd_runner.communicate(timeout=8)
        except subprocess.TimeoutExpired:
            pass 

        if outs is not None and len(outs) > 0:
            response = outs
        rlen = len(response) if response is not None else 0
        if(rlen == 0):
            response = "Process `{}` run.".format(command)
            rlen = len(response)
        rsize = sys.getsizeof(response)

        return response, rlen, rsize
               

    async def cmd(self, command):
        self.fw("executing client's request\n")

        cmd_runner = await subprocess.run(command, shell=True, universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        response = cmd_runner.stdout
        rlen = len(response)
        if(rlen == 0):
            response = "Command `{}` executed.".format(command)
            rlen = len(response)
        rsize = sys.getsizeof(response)

        return response, rlen, rsize
        

    async def start(self, command):
        self.fw("starting client's request\n")
        command = "{} {}".format("start", command)
        scode = await subprocess.call(command, shell=True, universal_newlines=True)

        response = "Request `{}` started (stat code {}).".format(command, scode)
        rlen = len(response)
        rsize = sys.getsizeof(response)

        return response, rlen, rsize

    async def update(self):
        self.fw("test33\n")

    async def kill(self):
        self.fw("test66\n")

    async def set_alive(self, status):
        self.__is_alive = status

    async def toggle_alive(self):
        self.__is_alive = not self.__is_alive

    async def get_alive(self):
        return self.__is_alive


class HostManager(fwc.fwMixin):
    _host, _sock_server, _fwc_serv = None, None, None
    
    @classmethod
    async def init_hostmanager(cls, server_address=const.SOCK.DEFAULT_SERVER, fileToWrite=None):
        fwc_serv = await fwc.init_fwc(**const.KWARGS.FWC_SERV)
        hostObj = await Host.init_host(**const.KWARGS.HOST)
        sock_server = await SockServer.init_server(**const.KWARGS.SOCK_SERVER)

        return cls(hostObj, sock_server, fwc_serv)

    def __init__(self, hostObj, sock_server, fwc_serv):
        self._host = hostObj
        self._sock_server = sock_server
        self._fwc_serv = fwc_serv

    @staticmethod
    async def run(server_address=const.SOCK.DEFAULT_SERVER, fileToWrite=None):
        host_manager = await HostManager.init_hostmanager(**const.KWARGS.HOSTMANAGER)
        print(host_manager)
        await host_manager.run_host(host_manager._host)

        return host_manager
    
    @staticmethod
    async def run_host(host_obj):
        host_status = host_obj.get_alive()
        if host_status is None:
            host_obj.set_alive(True)
            await host_obj.init_host()
        elif host_status is False:
            host_obj.toggle_alive()
            await host_obj.init_host()
        else:
            await host_obj.update()

    @staticmethod
    async def kill_host(host_obj):
        host_status = host_obj.get_alive()
        if host_status is True:
            await host_obj.kill()


    async def get_host(): return self._host
    async def set_host(*args, **kwargs): self._host = None
    async def get_sock_server(): return self._sock_server
    async def set_sock_server(*args, **kwargs): self._sock_server = await SockServer.init_server(*args, **kwargs)
    async def get_fwc_serv(): return self._fwc_serv
    async def set_fwc_serv(*args, **kwargs): self._fwc_serv = await fwc.init_fwc(*args, **kwargs)


loop = asyncio.get_event_loop()
loop.run_until_complete(HostManager.run(server_address=const.SOCK.DEFAULT_SERVER, fileToWrite=None))
loop.close()

