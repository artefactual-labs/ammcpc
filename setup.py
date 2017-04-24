# -*- coding: utf-8 -*-

"""setup.py: setuptools control."""


import re
from setuptools import setup


version = re.search(
    '^__version__\s*=\s*"(.*)"',
    open('ammcpc/ammcpc.py').read(),
    re.M
    ).group(1)


with open("README.rst", "rb") as f:
    long_descr = f.read().decode("utf-8")


setup(
    name="ammcpc",
    packages=["ammcpc"],
    entry_points={
        "console_scripts": ['ammcpc = ammcpc.ammcpc:main']
        },
    version=version,
    description="Python command line wrapper around MediaConch policy checks.",
    long_description=long_descr,
    author='Artefactual',
    author_email='info@artefactual.com',
    license='AGPL',
    install_requires=['lxml'],

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: GNU Affero General Public License v3',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
    ],

)
