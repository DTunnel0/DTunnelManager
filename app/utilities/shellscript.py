import os
import subprocess


def clear_screen() -> None:
    os.system('clear' if os.name == 'posix' else 'cls')


def exec_command(command: str) -> str:
    bash = 'bash -c' if os.name == 'posix' else 'cmd /c'
    bash += ' "' + command + '"'
    data = os.popen(bash).read()
    return data.strip()
