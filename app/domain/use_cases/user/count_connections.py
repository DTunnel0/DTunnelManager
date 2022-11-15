from app.domain.interfaces.user_gateway import UserGatewayInterface


class CountUserConnection:
    def __init__(self, gateway: UserGatewayInterface) -> None:
        self.gateway = gateway

    def execute(self, username: str) -> int:
        return self.gateway.count_connections(username)
