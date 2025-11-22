import socket
import sys
import os 
import re

dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(dir_path); sys.path.append(os.path.join(dir_path, ".."))

from core import common
from core import constants as const

def run_client(argv):
    mode = argv[1]
    command = common.xWSLMixins.cmdarray_to_cmdstring(argv[2:])
    _client = Client()
    _client.prepare(mode, command)

class Client(common.xWSLMixins, common.SockMixins):
    server_address = const.SOCK.DEFAULT_SERVER

    def __init__(self):
        pass

    def prepare(self, mode, command):
        modifier = self.get_modifier_from_mode(mode)
        if modifier is None:
            return
        
        command = "{} {}".format(modifier, command)
        self.process(command)
        

    def process(self, command):

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect(self.server_address)

        try:
            self.sendall(command, self.sock)
            data = self.await_response()
            print(data)

        except socket.timeout:
            print("Socket timed out")

        finally:
            self.sock.close()

    def await_response(self):
        received_resp_size_flag = False

        while not received_resp_size_flag:
            resp_size = self.recv(const.XWSL_RECV_SIZES["bytesize"], self.sock)
            if resp_size:
                cmdarray = self.cmdstring_to_cmdarray(resp_size)
                mode = self.get_mode_from_modifier(cmdarray[0])
                if mode is "bytesize":
                    received_resp_size_flag = True
                    resp_size = int(cmdarray[1])
                    self.sendall(const.XWSL_RESP_RMODES["ack"], self.sock) # send back ack
                else:
                    resp_size = None
        
        while True:
            resp = self.recv(resp_size+1, self.sock)
            if resp: 
                mode = self.get_mode_from_modifier(resp[0:2])
                resp = resp[3:]
                if mode is "data":
                    return resp
                else:
                    resp = None

if __name__ == '__main__':
    run_client(sys.argv)