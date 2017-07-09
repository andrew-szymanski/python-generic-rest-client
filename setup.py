#from distutils.core import setup
from setuptools import setup, find_packages

setup(
    name='python-rest-clients',
    version='0.1',
    author='Andrew Szymanski',
    author_email='',
    packages=find_packages(),
    scripts=['cli/cli.py',],
    url='https://github.com/andrew-szymanski/python-rest-clients',
    license='LICENSE.txt',
    description='Collection for python REST clients for PoCs, which share the same cli and pip install framework',
    long_description=open('README.md').read(),
    install_requires=[
        "simplejson>=2.5.2",
        "restkit>=4.2.2",
    ],
)
