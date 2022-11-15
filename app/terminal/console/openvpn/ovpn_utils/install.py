import os
import re
from urllib.request import urlopen

from app.utilities.logger import logger
from app.utilities.utils import get_ip_address
from console import Console, FuncItem
from console.colors import color_name

RCLOCAL = '/etc/rc.local'

OPENVPN_PATH = '/etc/openvpn'
EASYRSA_PATH = os.path.join(OPENVPN_PATH, 'easy-rsa')
EASYRSA_PKI_PATH = os.path.join(EASYRSA_PATH, 'pki')

EASYRSA_PKI_CA = os.path.join(EASYRSA_PKI_PATH, 'ca.crt')
EASYRSA_TLS_CRYPT = os.path.join(OPENVPN_PATH, 'tls-crypt.key')

EASYRSA_PKI_CERT_PATH = os.path.join(EASYRSA_PKI_PATH, 'issued/')
EASYRSA_PKI_KEY_PATH = os.path.join(EASYRSA_PKI_PATH, 'private/')

CLIENT_COMMON_CONFIG = os.path.join(OPENVPN_PATH, 'client-common.txt')

ROOT_PATH = os.path.expanduser('~')

__list_of_ip = re.findall(
    r'^\s+inet\s+(\d+\.\d+\.\d+\.\d+)\/\d+.*scope\s+global.*$',
    os.popen('ip -4 addr').read(),
    re.MULTILINE,
)

IP_ADDRESS = __list_of_ip[0] if __list_of_ip else get_ip_address()

EASYRSA_VERSION = '3.0.7'
EASYRSA_NAME = 'EasyRSA-%s.tgz' % EASYRSA_VERSION
EASYRSA_URL = 'https://github.com/OpenVPN/easy-rsa/releases/download/v%s/%s' % (
    EASYRSA_VERSION,
    EASYRSA_NAME,
)

CURRENT_PATH = os.getcwd()


def create_common_client_config(port: int, protocol: str) -> None:
    with open(CLIENT_COMMON_CONFIG, 'w') as f:
        f.write(
            '\n'.join(
                [
                    'client',
                    'proto %s' % protocol,
                    'remote 127.0.0.1 %s' % port,
                    'dev tun',
                    'resolv-retry infinite',
                    'nobind',
                    'persist-key',
                    'persist-tun',
                    'remote-cert-tls server',
                    'verify-x509-name server name',
                    'auth SHA256',
                    'auth-nocache',
                    'cipher AES-128-GCM',
                    'tls-client',
                    'tls-version-min 1.2',
                    'tls-cipher TLS-ECDHE-ECDSA-WITH-AES-128-GCM-SHA256',
                    'ignore-unknown-option block-outside-dns',
                    'setenv opt block-outside-dns # Prevent Windows 10 DNS leak',
                    'verb 3',
                    'auth-user-pass',
                    'keepalive 10 120',
                    'float',
                ]
            )
        )


def confirm_ip_address() -> bool:
    global IP_ADDRESS

    IP_ADDRESS2 = urlopen('https://api.ipify.org').read().decode('utf8')

    if not IP_ADDRESS:
        IP_ADDRESS = os.popen('hostname -I | cut -d\' \' -f1').read().strip()

    if IP_ADDRESS == IP_ADDRESS2:
        IP_ADDRESS = IP_ADDRESS2

    if not IP_ADDRESS:
        logger.error('Não foi possível encontrar o IP do servidor.')
        return False

    logger.info((color_name.YELLOW + 'IP do servidor: %s' + color_name.END) % IP_ADDRESS)
    result = input('Confirmar IP do servidor? [s/N] ')

    if result.lower() != 's':
        result = input(color_name.YELLOW + 'Digite o IP do servidor: ' + color_name.END)

        if not result:
            logger.error('IP do servidor não confirmado.')
            return False

        IP_ADDRESS = result

    return True


def get_port_openvpn() -> int:
    console = Console('Porta do OpenVPN')
    console.append_item(FuncItem('1194', lambda: '1194', shuld_exit=True))
    console.append_item(FuncItem('8888', lambda: '8888', shuld_exit=True))
    console.append_item(
        FuncItem(
            'Custom',
            lambda: input(color_name.YELLOW + 'Digite a porta: ' + color_name.END),
            shuld_exit=True,
        )
    )
    console.show()
    port = console.item_returned

    if port is not None and not port.isdigit():
        logger.error('Porta não definida.')
        raise ValueError('Porta não definida.')

    return int(port)


def get_dns_openvpn() -> str:
    def get_system_dns() -> str:
        template = 'push "dhcp-option DNS %s"'
        dns = '\n'.join(
            [
                template % line.strip()
                for line in os.popen(
                    'grep -v \'#\' /etc/resolv.conf | grep \'nameserver\' | grep -E -o \'[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\''
                ).readlines()
                if line.strip()
            ]
        )

        return dns

    console = Console('Escolha o DNS do OpenVPN:')
    console.append_item(
        FuncItem(
            'DNS do sistema',
            lambda: get_system_dns(),
            shuld_exit=True,
        )
    )
    console.append_item(
        FuncItem(
            'Google DNS',
            lambda: 'push "dhcp-option DNS 8.8.8.8"\npush "dhcp-option DNS 8.8.4.4"',
            shuld_exit=True,
        )
    )
    console.append_item(
        FuncItem(
            'OpenDNS',
            lambda: 'push "dhcp-option DNS 208.67.222.222"\npush "dhcp-option DNS 208.67.220.220"',
            shuld_exit=True,
        )
    )
    console.append_item(
        FuncItem(
            'Cloudflare',
            lambda: 'push "dhcp-option DNS 1.1.1.1"\npush "dhcp-option DNS 1.0.0.1"',
            shuld_exit=True,
        )
    )
    console.show()

    if console.item_returned is None:
        logger.error('DNS não definido.')
        raise ValueError('DNS não definido.')

    return console.item_returned


def get_protocol_openvpn() -> str:
    console = Console('Escolha o protocolo do OpenVPN:')
    console.append_item(
        FuncItem(
            'UDP',
            lambda: 'UDP',
            shuld_exit=True,
        )
    )
    console.append_item(
        FuncItem(
            'TCP',
            lambda: 'TCP',
            shuld_exit=True,
        )
    )
    console.show()

    if console.item_returned is None:
        logger.error('Protocolo não definido.')
        raise ValueError('Protocolo não definido.')

    return console.item_returned


def update_package() -> None:
    os.system('apt-get update -y 1>/dev/null 2>&1')


def install_packages() -> None:
    os.system('apt-get install openvpn iptables openssl ca-certificates zip -y 1>/dev/null 2>&1')


def setup_dir() -> None:
    if os.path.exists(EASYRSA_PATH):
        os.system('rm -rf %s' % EASYRSA_PATH)

    os.system('mkdir -p %s' % EASYRSA_PATH)


def download_easyrsa() -> None:
    os.system('wget %s -O %s -o /dev/null' % (EASYRSA_URL, EASYRSA_NAME))


def build_easyrsa() -> None:
    os.system(
        'tar -xzf %s --strip-components=1 --directory %s 1>/dev/null 2>&1'
        % (EASYRSA_NAME, EASYRSA_PATH)
    )
    os.system('rm -rf %s' % EASYRSA_NAME)

    if not os.path.exists(EASYRSA_PATH):
        logger.error('Não foi possível baixar o EasyRSA.')
        raise ValueError('Não foi possível baixar o EasyRSA.')

    os.system('chown -R root:root %s' % EASYRSA_PATH)
    easyrsa = os.path.join(EASYRSA_PATH, 'easyrsa')
    os.chdir(EASYRSA_PATH)

    os.system('%s init-pki 1>/dev/null 2>&1' % easyrsa)
    os.system('%s --batch build-ca nopass 1>/dev/null 2>&1' % easyrsa)
    os.system('%s gen-dh 1>/dev/null 2>&1')
    os.system('%s build-server-full server nopass 1>/dev/null 2>&1' % easyrsa)
    os.system('EASYRSA_CRL_DAYS=3650 %s gen-crl 1>/dev/null 2>&1' % easyrsa)
    os.system(
        ' '.join(
            [
                'cp',
                'pki/ca.crt',
                'pki/private/ca.key',
                'pki/issued/server.crt',
                'pki/private/server.key',
                '/etc/openvpn/easy-rsa/pki/crl.pem',
                '/etc/openvpn',
            ]
        )
    )

    os.system('chown -R nobody:nogroup %s >/dev/null' % os.path.join(OPENVPN_PATH, 'crl.pem'))
    os.system('openvpn --genkey --secret %s >/dev/null' % EASYRSA_TLS_CRYPT)
    os.chdir(CURRENT_PATH)


def build_server_config(port: int, protocol: str, dns: str) -> None:
    config_file = 'server.conf'
    with open(os.path.join(OPENVPN_PATH, config_file), 'w') as f:
        f.write(
            '\n'.join(
                [
                    'port %s' % port,
                    'management localhost 7505',
                    'proto %s' % protocol.lower(),
                    'dev tun',
                    'user nobody',
                    'group nogroup',
                    'persist-key',
                    'persist-tun',
                    'keepalive 10 120',
                    'topology subnet',
                    'server 10.8.0.0 255.255.255.0',
                    'ifconfig-pool-persist ipp.txt',
                    '%s' % dns,
                    'push "redirect-gateway def1 bypass-dhcp"',
                    'dh none',
                    'ecdh-curve prime256v1',
                    'tls-crypt tls-crypt.key',
                    'crl-verify crl.pem',
                    'ca ca.crt',
                    'cert server.crt',
                    'key server.key',
                    'auth SHA256',
                    'cipher AES-128-GCM',
                    'ncp-ciphers AES-128-GCM',
                    'tls-server',
                    'tls-version-min 1.2',
                    'tls-cipher TLS-ECDHE-ECDSA-WITH-AES-128-GCM-SHA256',
                    'status /var/log/openvpn/status.log',
                    'verb 3',
                    'duplicate-cn',
                    'username-as-common-name',
                    'plugin %s login'
                    % os.popen('find /usr -type f -name \'openvpn-plugin-auth-pam.so\'')
                    .readline()
                    .strip(),
                ]
            )
        )

        os.makedirs('/var/log/openvpn', exist_ok=True)


def build_ip_forward() -> None:
    os.system('sysctl -w net.ipv4.ip_forward=1 1>/dev/null 2>&1')

    with open('/proc/sys/net/ipv4/ip_forward', 'w') as f:
        f.write('1')


def build_rc_local() -> None:
    config = '\n'.join(
        [
            '#!/bin/sh -e',
            'iptables -t nat -A POSTROUTING -s 10.8.0.0/24 -j SNAT --to 10.0.0.4',
            'echo 1 > /proc/sys/net/ipv4/ip_forward',
            'echo 1 > /proc/sys/net/ipv6/conf/all/disable_ipv6',
            'iptables -A INPUT -p tcp --dport 25 -j DROP',
            'iptables -A INPUT -p tcp --dport 110 -j DROP',
            'iptables -A OUTPUT -p tcp --dport 25 -j DROP',
            'iptables -A OUTPUT -p tcp --dport 110 -j DROP',
            'iptables -A FORWARD -p tcp --dport 25 -j DROP',
            'iptables -A FORWARD -p tcp --dport 110 -j DROP',
            'exit 0',
        ]
    )

    with open(RCLOCAL, 'w') as f:
        f.write(config)

    os.system('chmod +x %s' % RCLOCAL)


def build_iptables(ip: str, port: int, protocol: str) -> None:
    os.system('iptables -t nat -A POSTROUTING -s 10.8.0.0/24 -j SNAT --to %s' % ip)

    if os.system('pgrep firewalld') == 0:
        os.system('firewall-cmd --zone=public --add-port=%s/%s' % (port, protocol))
        os.system('firewall-cmd --zone=trusted --add-source=10.8.0.0/24')
        os.system('firewall-cmd --permanent --zone=public --add-port=%s/%s' % (port, protocol))
        os.system('firewall-cmd --permanent --zone=trusted --add-source=10.8.0.0/24')

    if os.system('iptables -L -n | grep -qE \'REJECT|DROP\'') == 0:
        os.system('iptables -I INPUT -p %s --dport %s -j ACCEPT' % (protocol, port))
        os.system('iptables -I FORWARD -s 10.8.0.0/24 -j ACCEPT')
        os.system('iptables -F')
        os.system('iptables -I FORWARD -m state --state RELATED,ESTABLISHED -j ACCEPT')


def build_service_openvpn() -> None:
    if os.system('pgrep systemd-journal >/dev/null') == 0:
        os.system('systemctl restart openvpn@server.service 1>/dev/null 2>&1')
    else:
        os.system('/etc/init.d/openvpn restart 1>/dev/null 2>&1')


def openvpn_install() -> None:
    if not confirm_ip_address():
        return

    port = get_port_openvpn()
    protocol = get_protocol_openvpn()
    dns = get_dns_openvpn()

    if not port or not protocol or not dns:
        return

    protocol = protocol.lower()
    dns = dns.lower()

    logger.info('Processo de instalação iniciado...')
    logger.info('Por favor, aguarde...\n')
    logger.info('Porta: %s' % port)
    logger.info('Protocolo: %s' % protocol)
    logger.info(
        'DNS: %s' % ' '.join([line.split()[3].replace('"', '') for line in dns.split('\n')])
    )

    update_package()
    install_packages()
    setup_dir()
    download_easyrsa()
    build_easyrsa()
    build_server_config(port, protocol, dns)
    build_ip_forward()
    build_rc_local()
    build_iptables(IP_ADDRESS, port, protocol)
    build_service_openvpn()
    create_common_client_config(port, protocol)


def uninstall_openvpn() -> None:
    os.system('rm -rf %s' % OPENVPN_PATH)
    os.system('rm -rf /usr/share/doc/openvpn*')
    os.system('find /home/ -maxdepth 2 -name "*.ovpn" -delete')
    os.system('find /root/ -maxdepth 1 -name "*.ovpn" -delete')

    if os.system('pgrep systemd-journal 1>/dev/null 2>&1') == 0:
        os.system('systemctl stop openvpn 1>/dev/null 2>&1')
        os.system('systemctl disable openvpn 1>/dev/null 2>&1')
        os.system('systemctl daemon-reload 1>/dev/null 2>&1')
    else:
        os.system('/etc/init.d/openvpn stop 1>/dev/null 2>&1')
        os.system('update-rc.d -f openvpn remove 1>/dev/null 2>&1')

    os.system('apt-get purge openvpn -y 1>/dev/null 2>&1')
    os.system('apt-get autoremove -y 1>/dev/null 2>&1')
    os.system('apt-get clean -y 1>/dev/null 2>&1')
