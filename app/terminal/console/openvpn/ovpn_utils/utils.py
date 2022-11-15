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


class OpenVPNUtils:
    @staticmethod
    def openvpn_is_running() -> bool:
        status = os.system('pgrep openvpn >/dev/null') == 0
        return status

    @staticmethod
    def openvpn_is_installed() -> bool:
        status = OpenVPNUtils.openvpn_is_running()

        if not status:
            status = os.path.exists(OPENVPN_PATH) and os.path.exists(
                os.path.join(OPENVPN_PATH, 'server.conf')
            )

        return status

    @staticmethod
    def create_ovpn_client(username: str) -> str:
        return create_ovpn_client(username)

    @staticmethod
    def remove_ovpn_client(username: str) -> bool:
        path = os.path.join(ROOT_PATH, username + '.ovpn')

        if os.path.exists(path):
            os.remove(path)
            return True

        return False
