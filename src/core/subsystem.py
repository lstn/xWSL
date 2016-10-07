import socket
import sys

from . import common
from . import constants as const

def run_client(argv):
    mode = argv[1]
    command = common.xWSLSockMixin.cmdarray_to_cmdstring(argv[2:])
    _client = Client()
    _client.prepare(mode, command)

class Client(common.xWSLSockMixin):
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
        # print('connecting to %s port %s' % self.server_address)
        self.sock.connect(self.server_address)

        try:
            self.sendall(command, self.sock)
            data = self.await_response()
            print(data)

        except socket.timeout:
            print("Socket timed out")

        finally:
            # print('closing socket')
            self.sock.close()

    def await_response(self):
        received_resp_size_flag = False

        while not received_resp_size_flag:
            resp_size = self.recv(XWSL_RECV_SIZES["bytesize"], self.sock)
            if resp_size:
                cmdarray = self.cmdstring_to_cmdarray(resp_size)
                mode = self.get_mode_from_modifier(cmdarray[0])
                if mode is "bytesize":
                    received_resp_size_flag = True
                    resp_size = cmdarray[1]
                    self.sendall(const.XWSL_RESP_RMODES["ack"], self.sock) # send back ack
                else:
                    resp_size = None
        
        resp_size = (int) resp_size
        while True:
            resp = self.recv(resp_size+1, self.sock)
            if resp:
                cmdarray = self.cmdstring_to_cmdarray(resp)
                mode = self.get_mode_from_modifier(cmdarray[0])
                if mode is "data":
                    resp = self.cmdarray_to_cmdstring(cmdarray[1:])
                    return resp
                else:
                    resp = None

if __name__ == '__main__':
    run_client(sys.argv)