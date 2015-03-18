import os
import sys
from distutils.sysconfig import get_python_lib
from setuptools import find_packages, setup

setup(
    # Application name:
    name="digital-register-frontend",

    # Version number (initial):
    version="0.1.0",

    # Application author details:
    author="land registry",
    author_email="mikael.allison@digital.landregistry.co.uk",

    classifiers=[
        'Development Status :: Beta',
        'Environment :: Web Environment',
        'Framework :: flask',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],

    # Packages
    packages=find_packages(),

    # License
    license='Land_Reg',

    # Include additional files into the package
    include_package_data=True,

    scripts=['run_dev.py'],

    # Details
    url="https://github.com/LandRegistry/digital-register-frontend",

    # Dependent packages (distributions)
    install_requires=[
        "Flask==0.10.1",
        "Jinja2==2.7.3",
        "MarkupSafe==0.23",
        "Werkzeug==0.9.6",
        "itsdangerous==0.24",
        "requests==2.5.1",
        "python-dateutil==2.4",
        "gunicorn",
    ],
)
