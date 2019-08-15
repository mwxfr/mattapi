# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

import platform
from setuptools import setup, find_packages

PACKAGE_NAME = 'mattapi'
PACKAGE_VERSION = '0.2'

INSTALL_REQUIRES = [
'pyautogui==0.9.41',
'python-dateutil==2.8.0',
'opencv-python==4.0.0.21',
'pytesseract==0.2.6',
'numpy==1.16.1',
'image==1.5.27',
'pyperclip==1.7.0',
'packaging==19.0',
'pynput==1.4',
'mozinfo==1.0.0',
'mss==4.0.1',
'more-itertools==5.0.0',
'psutil==5.6.3',
'funcy==1.11'
]

if platform.system() == "Linux":
    INSTALL_REQUIRES.append('xlib')

TESTS_REQUIRE = [
]

DEV_REQUIRES = [
]

setup(
    name=PACKAGE_NAME,
    version=PACKAGE_VERSION,
    description='Test API Iris',
    classifiers=[
        'Environment :: Console',
        'Development Status :: 1 - Planning Development Status',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)',
        'Natural Language :: English',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows :: Windows 10',
        'Operating System :: Microsoft :: Windows :: Windows 7',
        'Operating System :: Microsoft :: Windows :: Windows 8',
        'Operating System :: Microsoft :: Windows :: Windows 8.1',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3.7',
        'Topic :: Software Development :: Quality Assurance',
        'Topic :: Software Development :: Testing'
    ],
    keywords=['automation', 'testing'],
    author='Matt Wobensmith',
    author_email='itsmatt@pacbell.net',
    url='https://github.com/mwxfr/mattapi',
    download_url='https://github.com/mwxfr/mattapi/latest.tar.gz',
    license='MPL2',
    packages=find_packages(),
    python_requires='>=3.7.3',
    include_package_data=True,  # See MANIFEST.in
    zip_safe=False,
    use_2to3=False,
    install_requires=INSTALL_REQUIRES,
    tests_require=TESTS_REQUIRE,
    extras_require={'dev': DEV_REQUIRES},  # For `pip install -e .[dev]`
    entry_points={
        'console_scripts': []
    }
)
