import os

from .install import openvpn_install, uninstall_openvpn, OPENVPN_PATH
from .utils import OpenVPNService, OpenVPNUtils


class OpenVPNManager:
    def __init__(self, utils: OpenVPNUtils, service: OpenVPNService) -> None:
        self.utils = utils
        self.service = service

    def install(self) -> bool:
        try:
            openvpn_install()
            return self.utils.is_installed
        except (Exception, KeyboardInterrupt):
            return False

    def uninstall(self) -> bool:
        uninstall_openvpn()
        return not self.utils.is_installed

    def create_ovpn_client(self, username: str = 'dtunnel') -> None:
        self.utils.create_ovpn(username)

    def remove_ovpn_client(self, username: str = 'dtunnel') -> None:
        self.utils.remove_ovpn(username)

    def start(self) -> bool:
        self.service.start()
        return self.utils.is_running

    def stop(self) -> bool:
        self.service.stop()
        return not self.utils.is_running

    def restart(self) -> bool:
        self.service.restart()
        return self.utils.is_running

    def change_openvpn_port(self, port: int) -> None:
        with open(os.path.join(OPENVPN_PATH, 'server.conf'), 'r') as f:
            lines = f.readlines()

        with open(os.path.join(OPENVPN_PATH, 'server.conf'), 'w') as f:
            for line in lines:

                if 'port' in line:
                    line = 'port {}\n'.format(port)

                f.write(line)

    def get_current_port(self) -> int:
        with open(os.path.join(OPENVPN_PATH, 'server.conf'), 'r') as f:
            lines = f.readlines()

        for line in lines:
            if 'port' in line:
                port = int(line.split(' ')[1])
                return port

        return 1194
