import socket
import sys
import subprocess
import os

from . import common
from . import constants as const

def run_host(host_obj):
    host_status = host_obj.get_alive()
    if host_status is None:
        host_obj.set_alive(True)
        host_obj.init_host()
        # host_obj.first_run()
    elif host_status is False:
        host_obj.toggle_alive()
        host_obj.init_host()
    else:
        host_obj.update()

def kill_host(host_obj):
    host_status = host_obj.get_alive()
    if host_status is True:
        host_obj.kill()

class Host(common.xWSLSockMixin):
    __is_alive = None
    _sock_alive = False
    server_address = const.SOCK.DEFAULT_SERVER

    def __init__(self, fileToWrite=None):
        self.fileWrite = fileToWrite
        self.fw("Initialized host\n")

    def init_host(self):
        self.start_socket()
        self.process()

    def start_socket(self):
        if not self._sock_alive:
            self._sock_alive = True
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.fw('starting up on %s port %s\n' % self.server_address)
            self.sock.bind(self.server_address)
            self.sock.listen(const.SOCK.MAX_LISTENS)
        else:
            self.fw('Sock is already up on %s port %s\n' % self.server_address)

    def process(self):
        has_connection_flag = False
        
        while not has_connection_flag:
            self.fw("Waiting for a connection...\n")
            try:
                connection, client_address = self.sock.accept()
                self.fw("Connection from {}\n".format(client_address))
                has_connection_flag = True
                
                response, rlen, rsize = self.await_command(connection)
                self.fw("Sending ack request for {} bytes...\n".format(rsize))
                self.send_bytesize(rsize)
                self.await_ack(connection)
                self.send_result(response, connection)

            except socket.timeout:    
                self.fw("socket timed out\n")  
                has_connection_flag = False

            finally:
                connection.close()  
                has_connection_flag = False
    
    def await_command(self, connection):
        received_command_flag = False

        while not received_command_flag:
            data = self.recv(const.XWSL_RECV_SIZES["cmd"], connection)
            self.fw('received "%s"\n' % data)
            if data:
                self.fw("Sending command for further processing\n")
                cmd_fn, command = self.process_command(data)
                return cmd_fn(command)
                

    def await_ack(self, connection):
        received_ack_flag = False

        while not received_ack_flag:
            ack_confirmation = self.recv(XWSL_RECV_SIZES["ack"], connection)
            if ack_confirmation:
                cmdarray = self.cmdstring_to_cmdarray(ack_confirmation)
                mode = self.get_mode_from_modifier(cmdarray[0])
                if mode is "ack":
                    received_resp_size_flag = True
                    return ack_confirmation
                else:
                    ack_confirmation = None
                
        

    def process_command(self, command):
        cmdarray = self.cmdstring_to_cmdarray(data)
        mode = self.get_mode_from_modifier(cmdarray[0])
        cmdarray = cmdarray[1:]
        command = self.cmdarray_to_cmdstring(cmdarray)
        cmd_fn = getattr(self, mode, const.SOCK.DEFAULT_MODE)
        return cmd_fn, command
    
    def send_bytesize(self, bytesize, connection):
        ack_msg = "{} {}".format(const.XWSL_RESP_RMODES["bytesize"], bytesize)
        self.sendall(ack_msg, connection)
    
    def send_result(self, result, connection):
        result_msg = "{} {}".format(const.XWSL_RESP_RMODES["data"], result)
        self.sendall(result_msg, connection)

    def run(self, command):
        self.fw("running client's request\n")

        cmd_runner = subprocess.Popen(command, universal_newlines=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        try:
            cmd_runner.communicate(timeout=2)
        except subprocess.TimeoutExpired:
            pass
            #Will likely not be able to get output.
        try:
            if cmd_runner.poll() is not None:
                outs, errs = cmd_runner.communicate(timeout=8)
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

        # while True:
        #     self.fw("Waiting for a connection...\n")
        #     try:
        #         connection, client_address = self.sock.accept()
        #         self.fw("Connection from {}\n".format(client_address))
        #         # Receive the data in small chunks and retransmit it
        #         while True:
        #             data = connection.recv(const.XWSL_RECV_SIZES["cmd"]).decode()
        #             self.fw('received "%s"\n' % data)
        #             if data:
        #                 self.fw("executing client's request\n")
        #                 compl = subprocess.run(data, shell=True, universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        #                 response = compl.stdout
        #                 response = "Command executed" if not response else response
        #                 self.fw("resp: " + response)
        #                 connection.sendall(response.encode())
        #                 data = None
        #                 # connection.sendall(data.encode())
        #             else:
        #                 self.fw('no more data from {}\n'.format(client_address))
        #                 break
               

    def cmd(self, command):
        self.fw("executing client's request\n")

        cmd_runner = subprocess.run(command, shell=True, universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        response = cmd_runner.stdout
        rlen = len(response)
        if(rlen == 0):
            response = "Command `{}` executed.".format(command)
            rlen = len(response)
        rsize = sys.getsizeof(response)

        return response, rlen, rsize
        

    def start(self, command):
        self.fw("starting client's request\n")
        command = "{} {}".format("start", command)
        scode = subprocess.call(command, shell=True, universal_newlines=True)

        response = "Request `{}` started (stat code {}).".format(command, scode)
        rlen = len(response)
        rsize = sys.getsizeof(response)

        return response, rlen, rsize

    def update(self):
        self.fw("test33\n")

    def kill(self):
        self.fw("test666\n")

    def set_alive(self, status):
        self.__is_alive = status

    def toggle_alive(self):
        self.__is_alive = not self.__is_alive

    def get_alive(self):
        return self.__is_alive
    
    def fw(self, *args):
        if self.fileWrite is not None:
            self.fileWrite.write(*args)