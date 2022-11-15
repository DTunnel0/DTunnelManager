from setuptools import setup, find_packages
from app import __author__, __email__
from app.version import __version__


PACKAGES = find_packages() + ['scripts']
REQUIREMENTS = [
    'sqlalchemy',
    'pytest',
    'distro',
    'pytelegrambotapi==4.6.0',
    'python-daemon',
]
VERSION = __version__

DESCRIPTION = open('README.md').read()
AUTHOR = __author__
AUTHOR_EMAIL = __email__
URL = 'https://github.com/DuTra01/DTunnelManager.git'
LICENSE = 'MIT'

PACKAGE_DATA = {'scripts': ['*']}


setup(
    name='DTunnelManager',
    version=VERSION,
    long_description=DESCRIPTION,
    long_description_content_type='text/markdown',
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    url=URL,
    platforms=['linux'],
    license=LICENSE,
    packages=PACKAGES,
    package_data=PACKAGE_DATA,
    include_package_data=True,
    install_requires=REQUIREMENTS,
    entry_points={
        'console_scripts': [
            'vps     = app.__main__:main',
            'vps-bot = bot.__main__:main',
        ],
    },
)
