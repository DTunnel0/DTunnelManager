from app.domain.interfaces.user_gateway import UserGatewayInterface
from app.domain.interfaces.user_repositoery import UserRepositoryInterface


class DeleteUserUseCase:
    def __init__(self, repo: UserRepositoryInterface, gateway: UserGatewayInterface) -> None:
        self.__repo = repo
        self.__gateway = gateway

    def execute(self, id: int) -> None:
        user = self.__repo.get_by_id(id)
        self.__gateway.delete(user.username)
        self.__repo.delete(id)
