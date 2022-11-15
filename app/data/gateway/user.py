import os

from app.domain.interfaces.user_gateway import (
    UserGatewayInterface,
    CreateUserInputGateway,
    UpdateUserInputGateway,
)


class SystemUserGateway(UserGatewayInterface):
    def create(self, data: CreateUserInputGateway) -> int:
        cmd = 'useradd -e {} -M -N -s /bin/false {}'.format(
            data.expiration_date,
            data.username,
        )
        if os.system(cmd) != 0:
            raise Exception('Could not create user')

        cmd = 'echo \'{}:{}\' | chpasswd'.format(data.username, data.password)
        if os.system(cmd) != 0:
            cmd = 'userdel -r {}'.format(data.username)
            os.system(cmd)
            raise Exception('Could not set password')

        return self.get_user_id(data.username)

    def delete(self, username: str) -> None:
        cmd = 'userdel -r {} 2>/dev/null'.format(username)
        if os.system(cmd) != 0:
            raise Exception('Could not delete user')

    def update(self, data: UpdateUserInputGateway) -> None:
        if data.password:
            cmd = 'echo \'{}:{}\' | chpasswd'.format(data.username, data.password)
            if os.system(cmd) != 0:
                raise Exception('Could not set password')

        if data.expiration_date:
            cmd = 'chage -E {} {}'.format(data.expiration_date, data.username)
            if os.system(cmd) != 0:
                raise Exception('Could not set expiration date')

    def get_user_id(self, username: str) -> int:
        return int(os.popen('id -u {}'.format(username)).read())

    def count_connections(self, username: str) -> int:
        count = self.__ssh_connections(username)
        count += self.__openvpn_connections(username)
        return count

    def __ssh_connections(self, username: str) -> int:
        cmd = 'ps -u {} 2>/dev/null | grep sshd | grep -v grep'.format(username)
        return len(os.popen(cmd).readlines())

    def __openvpn_connections(self, username: str) -> int:
        cmd = 'ps -u {} 2>/dev/null | grep openvpn | grep -v grep'.format(username)
        return len(os.popen(cmd).readlines())