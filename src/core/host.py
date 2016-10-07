import socket
import sys
import subprocess

def run_host(host_obj):
    host_status = host_obj.get_alive()
    if host_status is None:
        host_obj.set_alive(True)
        host_obj.run()
        # host_obj.first_run()
    elif host_status is False:
        host_obj.toggle_alive()
        host_obj.run()
    else:
        host_obj.update()

def kill_host(host_obj):
    host_status = host_obj.get_alive()
    if host_status is True:
        host_obj.kill()

class Host:
    __is_alive = None
    server_address = ('localhost', 15579)

    def __init__(self, fileToWrite=None):
        self.fileWrite = fileToWrite
        self.fw("Initialized host\n")
    
    def first_run(self):
        print("test")

    def run(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.fw('starting up on %s port %s\n' % self.server_address)
        self.sock.bind(self.server_address)
        self.sock.listen(5)
        while True:
            self.fw("Waiting for a connection...\n")
            try:
                connection, client_address = self.sock.accept()
                self.fw("Connection from {}\n".format(client_address))
                # Receive the data in small chunks and retransmit it
                while True:
                    data = connection.recv(2048).decode()
                    self.fw('received "%s"\n' % data)
                    if data:
                        self.fw("executing client's request\n")
                        compl = subprocess.run(data, universal_newlines=True, stdout=subprocess.PIPE)
                        response = compl.stdout
                        self.fw("resp: " + response)
                        connection.sendall(response.encode())
                        data = None
                        # connection.sendall(data.encode())
                    else:
                        self.fw('no more data from {}\n'.format(client_address))
                        break
                    
            finally:
                # Clean up the connection
                connection.close()         

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