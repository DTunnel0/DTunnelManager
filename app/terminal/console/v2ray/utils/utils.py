from typing import List
from .manager import V2RayManager


class V2rayUtils:
    v2ray_manager = V2RayManager()

    @staticmethod
    def create_uuid() -> str:
        return V2rayUtils.v2ray_manager.create_new_uuid()

    @staticmethod
    def get_list_uuid() -> List[str]:
        return V2rayUtils.v2ray_manager.get_uuid_list()

    @staticmethod
    def v2ray_is_installed() -> bool:
        return V2rayUtils.v2ray_manager.is_installed()
