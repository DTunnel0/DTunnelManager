import os
import re
import typing as t
from scripts import CERT_PATH, SOCKS_PATH


class Flag:
    def __init__(self, flag: str, port: int) -> None:
        self._flag = flag
        self.port = port

    @staticmethod
    def get_running_port(flag: str) -> int:
        cmd = 'ps aux'
        result = os.popen(cmd).read()
        pattern = re.compile(r'--{flag}-port (\d+)'.format(flag=flag.lower()))
        match = pattern.search(result)
        return int(match.group(1)) if match else 0

    @staticmethod
    def create(flag: str, default_port: int = -1) -> 'Flag':
        port = Flag.get_running_port(flag) or default_port
        return Flag(flag, port)

    @property
    def flag(self) -> str:
        return '--{flag}-port {port}'.format(flag=self._flag.lower(), port=self.port)


class OpenVpnFlag(Flag):
    def __init__(self, port: int) -> None:
        super().__init__('OPENVPN', port)


class SSHFlag(Flag):
    def __init__(self, port: int) -> None:
        super().__init__('SSH', port)


class V2rayFlag(Flag):
    def __init__(self, port: int) -> None:
        super().__init__('V2RAY', port)


class FlagList:
    def __init__(self, flags: t.List[Flag]) -> None:
        self._flag_map = {flag._flag: flag for flag in flags}

    def get(self, flag: str) -> Flag:
        return self._flag_map[flag]

    def set(self, flag: Flag) -> None:
        self._flag_map[flag._flag] = flag

    def __str__(self) -> str:
        return ' '.join([flag.flag for flag in self._flag_map.values()])

    def __repr__(self) -> str:
        return str(self)


class Screen:
    def __init__(self, screen_name, command):
        self.screen_name = screen_name
        self.command = command

    def is_running(self) -> bool:
        return self.screen_name in os.popen('screen -ls').read()

    def execute(self) -> None:
        if not self.is_running():
            os.system('screen -dmS {} {}'.format(self.screen_name, self.command))

    def kill(self) -> None:
        if self.is_running():
            os.system('screen -X -S {} quit'.format(self.screen_name))

    def restart(self) -> None:
        self.kill()
        self.execute()

    def __repr__(self):
        return 'Screen({})'.format(self.screen_name)

    @staticmethod
    def all() -> t.List[str]:
        cmd = 'screen -ls'
        return re.findall(r'\d+\.(.*)\t', os.popen(cmd).read())


class SocksManager:
    _screen_name = 'socks:{mode}:{port}'

    def __init__(
        self,
        port: int,
        flag_list: FlagList,
        mode: str,
        ssl: bool = False,
    ):
        self.port = port
        self.flag_list = flag_list
        self.mode = mode
        self.ssl = ssl

    @property
    def command(self) -> str:
        cmd = 'python3 {socks_path} --port {port} {flags}'.format(
            socks_path=SOCKS_PATH,
            port=self.port,
            flags=self.flag_list,
        )
        if self.ssl:
            cmd += ' --cert {cert_path}'.format(cert_path=CERT_PATH)
        return cmd

    @property
    def screen(self) -> Screen:
        return Screen(
            self._screen_name.format(
                mode=self.mode,
                port=self.port,
            ),
            self.command,
        )

    def is_running(self) -> bool:
        return self.screen.is_running()

    def start(self) -> None:
        self.screen.execute()

    def stop(self) -> None:
        self.screen.kill()

    def restart(self) -> None:
        self.screen.restart()

    @staticmethod
    def get_running_port(mode: str = 'http') -> int:
        pattern = r'socks:{}:(\d+)'.format(mode)
        for screen in Screen.all():
            match = re.match(pattern, screen)
            if match:
                return int(match.group(1))
        return 0
