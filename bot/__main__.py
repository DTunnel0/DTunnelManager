import argparse
import importlib

from . import bot

from .config import set_admin_id, set_bot_token, get_admin_id, get_bot_token
from .commands import ALL_MODULES

parser = argparse.ArgumentParser(description='Helper for the bot')
parser.add_argument(
    '--set-token',
    dest='token',
    help='Set the bot token',
)
parser.add_argument(
    '--set-admin',
    dest='admin',
    help='Set the admin id',
    type=int,
)

parser.add_argument('--get-token', dest='get_token', action='store_true', help='Get the bot token')
parser.add_argument('--get-admin', dest='get_admin', action='store_true', help='Get the admin id')

parser.add_argument(
    '--delete-token',
    dest='delete_token',
    action='store_true',
    help='Delete the bot token',
)
parser.add_argument(
    '--delete-admin',
    dest='delete_admin',
    action='store_true',
    help='Delete the admin id',
)
parser.add_argument('--run', dest='run', action='store_true', help='Run the bot in foreground')
parser.add_argument(
    '--start', dest='start', action='store_true', help='Start the bot in background (screen)'
)
parser.add_argument('--stop', dest='stop', action='store_true', help='Stop the bot')
parser.add_argument('--status', dest='status', action='store_true', help='Status of the bot')
parser.add_argument(
    '--pidfile',
    dest='pidfile',
    help='Set the pid file (Linux only)',
    default='/tmp/bot.pid',
)

args = parser.parse_args()


def load_modules():
    for module in ALL_MODULES:
        try:
            importlib.import_module('.commands.' + module, 'bot')
        except ImportError:
            pass


def start_bot_in_background():
    import os

    if os.system('command -v screen > /dev/null') != 0:
        print('screen is not installed')
        print('Install it with "apt install screen"')
        return

    if os.system('screen -ls | grep bot > /dev/null') == 0:
        print('Bot is already running')
        return

    command = 'screen -dmS bot python3 -m bot --run'
    os.system(command)


def start_bot_in_foreground():
    load_modules()

    bot.infinity_polling()


def stop_bot():
    import os

    if os.system('command -v screen > /dev/null') != 0:
        print('screen is not installed')
        print('Install it with "apt install screen"')
        return

    if os.system('screen -ls | grep bot > /dev/null') != 0:
        print('Bot is not running')
        return

    command = 'screen -S bot -X quit'
    os.system(command)


def main():

    args = parser.parse_args()

    if args.token:
        set_bot_token(args.token)

    if args.admin:
        set_admin_id(args.admin)

    if args.get_token:
        print(get_bot_token())

    if args.get_admin:
        print(get_admin_id())

    if args.delete_token:
        set_bot_token('')

    if args.delete_admin:
        set_admin_id(-1)

    if args.run:
        start_bot_in_foreground()

    if args.start:
        start_bot_in_background()

    if args.stop:
        stop_bot()


if __name__ == '__main__':
    main()
