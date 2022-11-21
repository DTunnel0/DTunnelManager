import os
import uuid
import time

from typing import List, Union
from .config import V2RayConfig

V2RAY_CMD_INSTALL = 'bash -c \'bash <(curl -L https://raw.githubusercontent.com/v2fly/fhs-install-v2ray/master/install-release.sh)\''  # noqa
V2RAY_CMD_UNINSTALL = 'bash -c \'bash <(curl -L https://raw.githubusercontent.com/v2fly/fhs-install-v2ray/master/install-release.sh) --remove \''  # noqa
V2RAY_BIN_PATH = '/usr/local/bin/v2ray'
V2RAY_CONFIG_PATH = '/usr/local/etc/v2ray/config.json'
V2RAY_SERVICE_PATH = '/etc/systemd/system/v2ray.service'


def create_uuid() -> str:
    import hashlib
    import random
    import string

    string_pool = string.ascii_letters + string.digits
    data = ''.join(random.choice(string_pool) for _ in range(32))
    data += str(int(time.time()))
    data += str(uuid.getnode())

    hash_data = hashlib.sha256(data.encode('utf-8')).hexdigest()

    return str(uuid.uuid5(uuid.NAMESPACE_DNS, hash_data))


def _normalize_service_v2ray() -> None:
    from .template import service_template as service_v2ray_template

    with open(V2RAY_SERVICE_PATH, 'w') as f:
        f.write(service_v2ray_template)

    os.system('systemctl daemon-reload')


class V2RayManager:
    def __init__(self) -> None:
        self.config = V2RayConfig(V2RAY_CONFIG_PATH)

    def install(self) -> bool:
        status = os.system(V2RAY_CMD_INSTALL) == 0

        if status:
            _normalize_service_v2ray()
            self.config.create(port=1080, protocol='vless')
            V2RayManager.restart()

        return status

    def uninstall(self) -> bool:
        cmd = V2RAY_CMD_UNINSTALL
        status = os.system(cmd) == 0
        return status and not V2RayManager.is_installed()

    @staticmethod
    def is_installed() -> bool:
        return os.path.exists(V2RAY_BIN_PATH)

    @staticmethod
    def is_running() -> bool:
        cmd = 'netstat -tunlp | grep v2ray'
        return os.system(cmd) == 0

    @staticmethod
    def start() -> bool:
        cmd = 'systemctl start v2ray'
        return os.system(cmd) == 0

    @staticmethod
    def stop() -> bool:
        cmd = 'systemctl stop v2ray'
        return os.system(cmd) == 0

    @staticmethod
    def restart() -> bool:
        cmd = 'systemctl restart v2ray'
        return os.system(cmd) == 0

    def get_running_port(self) -> int:
        config_data = self.config.load()
        return config_data['inbounds'][0]['port']

    def change_port(self, port: int) -> bool:
        config_data = self.config.load()
        config_data['inbounds'][0]['port'] = port

        self.config.save(config_data)
        self.restart()

        return self.is_running()

    def create_client(self, email: Union[str, None] = None) -> str:
        config_data = self.config.load()
        uuid = create_uuid()

        config_data['inbounds'][0]['settings']['clients'].append(
            {
                'id': uuid,
                'flow': 'xtls-rprx-direct',
                'email': email,
            }
        )

        self.config.save(config_data)
        self.restart()
        return uuid

    def edit_client(self, uuid: str, email: Union[str, None]) -> None:
        config_data = self.config.load()
        for client in config_data['inbounds'][0]['settings']['clients']:
            if client['id'] == uuid:
                client['email'] = email

        self.config.save(config_data)
        self.restart()

    def delete_client(self, uuid: str) -> None:
        config_data = self.config.load()
        config_data['inbounds'][0]['settings']['clients'] = [
            client
            for client in config_data['inbounds'][0]['settings']['clients']
            if client['id'] != uuid
        ]

        self.config.save(config_data)
        self.restart()

    def get_clients(self) -> List[str]:
        config_data = self.config.load()
        return [client['id'] for client in config_data['inbounds'][0]['settings']['clients']]
