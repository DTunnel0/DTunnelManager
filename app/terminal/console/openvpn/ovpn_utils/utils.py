import os

from .install import (
    EASYRSA_PATH,
    EASYRSA_PKI_CA,
    EASYRSA_PKI_CERT_PATH,
    EASYRSA_PKI_KEY_PATH,
    CLIENT_COMMON_CONFIG,
    EASYRSA_TLS_CRYPT,
    ROOT_PATH,
    OPENVPN_PATH,
    CURRENT_PATH,
)


def create_ovpn_client(username: str) -> str:
    os.chdir(EASYRSA_PATH)

    easyrsa = os.path.join(EASYRSA_PATH, 'easyrsa')
    os.system('%s build-client-full %s nopass 1>/dev/null' % (easyrsa, username))

    ovpn_config_template = '\n'.join(
        [
            '%s',
            '<ca>',
            '%s',
            '</ca>',
            '<cert>',
            '%s',
            '</cert>',
            '<key>',
            '%s',
            '</key>',
            '<tls-crypt>',
            '%s',
            '</tls-crypt>',
        ]
    )

    cert = open(EASYRSA_PKI_CERT_PATH + username + '.crt').read().strip()
    start_preffix = '-----BEGIN CERTIFICATE-----'
    end_preffix = '-----END CERTIFICATE-----'

    start = cert.find(start_preffix)
    end = cert.find(end_preffix)

    cert = cert[start : end + len(end_preffix)]  # noqa

    ovpn_config = ovpn_config_template % (
        open(CLIENT_COMMON_CONFIG).read().strip(),
        open(EASYRSA_PKI_CA).read().strip(),
        cert,
        open(EASYRSA_PKI_KEY_PATH + username + '.key').read().strip(),
        open(EASYRSA_TLS_CRYPT).read().strip(),
    )

    path = os.path.join(ROOT_PATH, username + '.ovpn')

    with open(path, 'w') as f:
        f.write(ovpn_config)

    os.chdir(CURRENT_PATH)
    return path


def check_exists_ovpn_client(username: str) -> bool:
    path = os.path.join(ROOT_PATH, username + '.ovpn')
    return os.path.exists(path)


def remove_ovpn_client(username: str) -> None:
    os.chdir(EASYRSA_PATH)

    easyrsa = os.path.join(EASYRSA_PATH, 'easyrsa')
    os.system('%s revoke %s 1>/dev/null' % (easyrsa, username))
    os.system('%s gen-crl 1>/dev/null' % easyrsa)

    os.chdir(CURRENT_PATH)

    path = os.path.join(ROOT_PATH, username + '.ovpn')
    os.remove(path)

    os.remove(EASYRSA_PKI_CERT_PATH + username + '.crt')
    os.remove(EASYRSA_PKI_KEY_PATH + username + '.key')
    os.remove(EASYRSA_PKI_KEY_PATH + username + '.csr')

    os.remove(EASYRSA_PKI_KEY_PATH + 'private/' + username + '.key')
    os.remove(EASYRSA_PKI_KEY_PATH + 'reqs/' + username + '.req')
    os.remove(EASYRSA_PKI_KEY_PATH + 'issued/' + username + '.crt')


class OpenVPNUtils:
    @property
    def is_installed(self) -> bool:
        return os.path.exists(OPENVPN_PATH)

    @property
    def is_running(self) -> bool:
        return (
            os.system('pgrep openvpn') == 0
            or os.path.exists(OPENVPN_PATH)  # noqa
            and os.path.exists(os.path.join(OPENVPN_PATH, 'server.conf'))  # noqa
        )

    def check_exists_ovpn(self, username: str) -> bool:
        return check_exists_ovpn_client(username)

    def create_ovpn(self, username: str) -> str:
        if not check_exists_ovpn_client(username):
            return create_ovpn_client(username)
        return os.path.join(ROOT_PATH, username + '.ovpn')

    def remove_ovpn(self, username: str) -> bool:
        if check_exists_ovpn_client(username):
            remove_ovpn_client(username)
            return True
        return False


class OpenVPNService:
    def __init__(self, utils: OpenVPNUtils) -> None:
        self.utils = utils

    def start(self) -> None:
        if self.utils.is_installed and not self.utils.is_running:
            os.system('systemctl start openvpn')

    def stop(self) -> None:
        if self.utils.is_installed and self.utils.is_running:
            os.system('systemctl stop openvpn')

    def restart(self) -> None:
        if self.utils.is_installed and self.utils.is_running:
            os.system('systemctl restart openvpn')
