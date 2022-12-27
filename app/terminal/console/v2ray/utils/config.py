import json
import os

from .template import config as v2ray_config_template


class V2RayConfig:
    def __init__(self, config_path: str) -> None:
        self.config_path = config_path
        self.config_data: dict = {}

    def load(self) -> dict:
        if not os.path.exists(self.config_path):
            self.create(port=1080, protocol='vless')

        with open(self.config_path, 'r') as f:
            self.config_data = json.load(f)

        return self.config_data

    def save(self, config_data: dict) -> None:
        with open(self.config_path, 'w') as f:
            json.dump(config_data, f, indent=4)

    def create(self, port: int, protocol: str) -> None:
        v2ray_config_template['inbounds'][0]['port'] = port
        v2ray_config_template['inbounds'][0]['protocol'] = protocol
        self.save(v2ray_config_template)
