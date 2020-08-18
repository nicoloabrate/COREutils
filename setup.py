"""
Author: N. Abrate.

File: setup.py

Description: Class for handling nuclear reactor geometries.
"""
from setuptools import setup, find_packages

setup(
   name='coreutils',
   version='0.0.1',
   author='N. Abrate',
   author_email='nicolo.abrate@polito.it',
   url='https://nicolo_abrate@bitbucket.org/nicolo_abrate/coreutils.git',
   package_name = ['coreutils'],
   packages=setuptools.find_packages(),
   license='LICENSE.md',
   description='',
   long_description=open('README.md').read(),
   classifiers=[
        "Programming Language :: Python :: 3",
        "License :: MIT License",
        "Operating System :: OS independent",
    ],
    python_requires='>=3.6',
)
