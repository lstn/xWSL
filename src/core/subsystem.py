import socket
import sys

def run_client(argv):
    cmdlet = ' '.join(argv[1:])
    _client = Client()
    _client.run(cmdlet)

class Client:
    server_address = ('localhost', 15579)

    def __init__(self):
        pass
    
    def run(self, message='This is the message.  It will be repeated.'):
        print("test")
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print('connecting to %s port %s' % self.server_address)
        self.sock.connect(self.server_address)

        try:
            # Send data
            print('sending "%s"' % message)
            self.sock.sendall(message.encode())

            # Look for the response
            amount_received = 0
            amount_expected = len(message)
            
            while True:
                data = self.sock.recv(2048).decode()
                if data:
                    print('received "%s"' % data)
                    break

        finally:
            print('closing socket')
            self.sock.close()

if __name__ == '__main__':
    run_client(sys.argv)