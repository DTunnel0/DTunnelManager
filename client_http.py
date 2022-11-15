import socket
import ssl
import subprocess
import threading
import select


class Server(threading.Thread):
    def __init__(self, client: socket.socket):
        super().__init__()
        self.client = client

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def run(self):
        self.socket.bind(('0.0.0.0', 8080))
        self.socket.listen(1)

        while True:
            client, addr = self.socket.accept()
            self.handle_client(client)

    def handle_client(self, client: socket.socket):
        while True:
            r, w, e = select.select([self.client, client], [], [])
            if self.client in r:
                data = self.client.recv(8192)
                print('[SERVER]', data)
                if not data:
                    break
                client.send(data)
            if client in r:
                data = client.recv(8192)
                # print('[CLIENT]', data)
                if not data:
                    break
                self.client.send(data)
        self.client.close()
        client.close()


host = 'w.dutra01.xyz'
port = 443

sni = 'www.google.com'
payload = b'GET / HTTP/1.1\r\nHost: %s\r\n\r\n' % sni.encode('utf-8')

ctx = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
soc = socket.create_connection((host, port), timeout=5)
soc = ctx.wrap_socket(soc, server_hostname=sni)

soc.send(payload)
print(soc.recv(8192))

server = Server(soc)
server.start()
subprocess.call(['ssh -D 1080 -N vpn@localhost -p 8080'], shell=True)

soc.close()
