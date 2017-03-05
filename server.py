# Author : Shubham Aggarwal
# Handle : shuboy2014
# Last Updated : 05-03-2017

import socket
import threading
import sys


class Server(object):

    '''
    Proxy Server compatible for http
    '''

    def __init__(self, **kwargs):
        self.severSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.severSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.severSocket.bind((kwargs["hostname"], kwargs["port"]))
        self.clients = []

    @staticmethod
    def get_host_port(url):
        # default port is 80
        host, port = None, 80

        # https:// or http://
        if url[0:8] == 'https://' or url[0:7] == 'http://':
            host = url[8:] if url[0:8] == 'https://' else url[7:]
        else:
            host = url

        try:
            slash_index = host.index('/')
        except ValueError:
            slash_index = -1

        try:
            colon_index = host.index(':')
        except ValueError:
            colon_index = -1

        if colon_index != -1 and slash_index > colon_index:
            port = int(host[colon_index:slash_index])
            host = host[0:colon_index]
        else:
            host = host[:slash_index]

        return host, port

    def proxy_thread(self, c, addr):

        request = c.recv(1024)
        url = (request.split('\n')[0]).split()[1]

        host, port = self.get_host_port(url)
        print(host, port)
        # Now proxy serve behave like a client
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        sock.connect((host, port))
        sock.sendall(request)

        # Response by a web server
        try:
            while True:
                data = sock.recv(1024)
                if len(data) == 0:
                    break
                else:
                    c.sendall(data)

                if len(data) < 1024:
                    break
            sock.close()
            c.close()
        except socket.error as error:
            print(error)
            if sock:
                sock.close()
            if c:
                c.close()
        finally:
            return

    def listening(self):
        print("listening for connection")
        self.severSocket.listen(10)
        while True:
            # Blocking
            c, addr = self.severSocket.accept()
            new_thread = threading.Thread(target=self.proxy_thread, args=(c, addr))
            new_thread.setDaemon(True)
            new_thread.start()
            self.clients.append(new_thread)

    def closing(self):
        self.severSocket.close()
        sys.exit()


if __name__ == '__main__':
    x = Server(hostname='0.0.0.0', port=12345)
    x.listening()
    x.closing()
