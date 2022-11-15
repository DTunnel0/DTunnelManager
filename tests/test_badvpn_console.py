import pytest

from app.modules.console.badvpn_console import BadvpnInstaller, BadvpnFlag, BadvpnScreenManager


def test_badvpn_flag_flag():
    flag = BadvpnFlag(
        listen_addr='127.0.0.1:7300',
        max_clients=1100,
    )

    assert flag.flag == '--listen-addr 127.0.0.1:7300 --max-clients 1100'
    assert flag.command() == '/usr/bin/badvpn-udpgw --listen-addr 127.0.0.1:7300 --max-clients 1100'
