"""
Author: N. Abrate.

File: setup.py

Description: Class for handling nuclear reactor geometries.
"""
from setuptools import find_packages
from distutils.core import setup

requirements = "requirements.txt"

setup(
   name='COREutils',
   version='0.0.1',
   author='N. Abrate',
   author_email='nicolo.abrate@polito.it',
   url='https://github.com/nicoloabrate/COREutils',
   package_name = ['coreutils'],
   packages=find_packages(),
   license='LICENSE.md',
   description='Handle core geometry and data for reactor physics applications',
   long_description=open('README.md').read(),
   long_description_content_type="text/markdown",
   test_suite="tests",
   setup_requires=['pytest-runner'],
   tests_require=['pytest'],
   include_package_data=True,
   classifiers=[
        "Programming Language :: Python :: 3",
        "License :: MIT License",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "Operating System :: OS independent",
    ],
    install_requires=open(requirements).read().splitlines(),
    python_requires='>=3.6',
)
