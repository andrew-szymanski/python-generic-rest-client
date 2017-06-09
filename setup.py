from distutils.core import setup

setup(
    name='python-generic-rest-client',
    version='0.1',
    author='Andrew Szymanski',
    author_email='',
    packages=['cli'],
    scripts=['cli/cli.py',],
    url='https://github.com/andrew-szymanski/python-generic-rest-client',
    license='LICENSE.txt',
    description='Basic extendable python REST client, based on restkit',
    long_description=open('README.md').read(),
    install_requires=[
        "simplejson>=2.5.2",
        "restkit>=4.2.2",
    ],
)