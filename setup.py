"""
Copyright (c) 2017 5GTANGO
ALL RIGHTS RESERVED.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

Neither the name of the SONATA-NFV, 5GTANGO
nor the names of its contributors may be used to endorse or promote
products derived from this software without specific prior written
permission.

This work has been performed in the framework of the 5GTANGO project,
funded by the European Commission under Grant number 761493 through
the Horizon 2020 and 5G-PPP programmes. The authors would like to
acknowledge the contributions of their colleagues of the 5GTANGO
partner consortium (www.5gtango.eu).
"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# configure plugin name here
PLUGIN_NAME = "tng-sp-ia-wtapi"

# generate a name without dashes
PLUGIN_NAME_CLEAR = "tapi_wrapper"

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name=PLUGIN_NAME_CLEAR,

    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # https://packaging.python.org/en/latest/single_source_version.html
    version='0.1',

    description='5GTANGO Transport API wrapper',
    long_description=long_description,

    # The project's main homepage.
    url='https://github.com/sonata-nfv/tng-sp-ia-wtapi/',

    # Author details
    author='Juan Luis de la Cruz',
    author_email='jdelacruz@cttc.es',

    # Choose your license
    license='Apache 2.0',

    packages=find_packages(),
    install_requires=[
        'amqpstorm',
        'pytest',
        'PyYAML',
        'requests',
        'pycodestyle',
        'coloredlogs',
        'psycopg2',
    ],
    setup_requires=['pytest-runner'],

    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # pip to create the appropriate form of executable for the target platform.
    entry_points={
        'console_scripts': [
            '%s=%s.__main__:main' % (PLUGIN_NAME, PLUGIN_NAME_CLEAR),
        ],
    },
)
