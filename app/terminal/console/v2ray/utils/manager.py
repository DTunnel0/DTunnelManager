import os
import uuid
import time

from typing import List
from .config import V2RayConfig

V2RAY_CMD_INSTALL = 'bash -c \'bash <(curl -L -s https://multi.netlify.app/go.sh) -f \''
V2RAY_CMD_UNINSTALL = 'bash -c \'bash <(curl -L -s https://multi.netlify.app/go.sh) --remove \''


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
    old = '/usr/bin/v2ray/v2ray -config /etc/v2ray/config.json'
    new = '/usr/bin/v2ray/v2ray run -c /etc/v2ray/config.json'
    target = '/etc/systemd/system/v2ray.service'

    data = open(target).read()
    data = data.replace(old, new)

    with open(target, 'w') as f:
        f.write(data)


class V2RayManager:
    def __init__(self) -> None:
        self.config = V2RayConfig()

    @staticmethod
    def install() -> bool:
        cmd = V2RAY_CMD_INSTALL
        status = os.system(cmd) == 0

        if status:
            _normalize_service_v2ray()
            V2RayConfig().create(port=1080, protocol='vless')
            V2RayManager.restart()

        return status

    @staticmethod
    def uninstall() -> bool:
        cmd = V2RAY_CMD_UNINSTALL
        status = os.system(cmd) == 0
        return status and not V2RayManager.is_installed()

    @staticmethod
    def is_installed() -> bool:
        return os.path.exists('/usr/bin/v2ray/v2ray')

    @staticmethod
    def is_running() -> bool:
        cmd = 'ps -ef | grep \'\/usr\/bin\/v2ray\/v2ray\' | grep -v grep'
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

    def create_new_uuid(self) -> str:
        config_data = self.config.load()
        uuid = create_uuid()

        config_data['inbounds'][0]['settings']['clients'].append(
            {
                'id': uuid,
                'flow': 'xtls-rprx-direct',
            }
        )

        self.config.save(config_data)
        self.restart()
        return uuid

    def remove_uuid(self, uuid: str) -> None:
        config_data = self.config.load()
        config_data['inbounds'][0]['settings']['clients'] = [
            client
            for client in config_data['inbounds'][0]['settings']['clients']
            if client['id'] != uuid
        ]

        self.config.save(config_data)
        self.restart()

    def get_uuid_list(self) -> List[str]:
        config_data = self.config.load()
        return [client['id'] for client in config_data['inbounds'][0]['settings']['clients']]
