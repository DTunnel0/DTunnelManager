import os


def pause(text='\nEnter para continuar'):
    input('\033[1;32m' + text + '\033[0m')


def get_ip_address():
    path = os.path.join(os.path.expanduser('~'), '.ip')

    if os.path.exists(path):
        with open(path, 'r') as f:
            return f.read().strip()

    try:
        import socket

        host = 'api.ipify.org'
        port = 80

        soc = socket.create_connection((host, port))
        soc.send(b'GET / HTTP/1.1\r\nHost: %s\r\n\r\n' % host.encode('utf-8'))
        ip = soc.recv(4096).decode('utf-8').split('\r\n')[-1]

        with open(path, 'w') as f:
            f.write(ip.strip())

        return ip.strip()

    except Exception as e:
        return '0.0.0.0'
