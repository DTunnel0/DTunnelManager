import os
import typing as t
import urllib.request

from datetime import datetime, timedelta
from .shellscript import exec_command


def load_all_users() -> t.List[str]:
    path = '/etc/passwd'
    data = []

    with open(path) as f:
        for line in f:
            split = line.split(':')
            if split[0] != 'nobody' and int(split[2]) >= 1000:
                data.append(split[0])

    return data


def find_user_by_name(name: str) -> t.Optional[str]:
    users = load_all_users()
    return next((user for user in users if user == name), None)


def count_users(users: t.List[str] = None) -> int:
    return len(users or load_all_users())


def get_pids_ssh(user: str) -> t.List[int]:
    command = f'ps -u {user}'
    output = exec_command(command)
    return [
        int(line.split()[0])
        for line in output.split('\n')[1:]
        if line and line.split()[-1] == 'sshd'
    ]


def count_connections(user: str) -> int:
    command = f'ps -u {user} | grep sshd | wc -l'
    output = exec_command(command)
    return int(output.strip()) if output else 0


def days_to_date(days: int) -> str:
    return (datetime.now() + timedelta(days=days)).strftime('%d/%m/%Y')


def date_to_datetime(date: str) -> datetime:
    if isinstance(date, datetime):
        return date

    try:
        return datetime.strptime(date, '%d/%m/%Y')
    except TypeError:
        try:
            return datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
        except TypeError:
            return datetime.strptime(date, '%Y-%m-%d')


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
