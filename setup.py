from distutils.core import setup

setup(
    name='sourceroute',
    version='1.0',
    packages=['netaddr', 'netifaces'],
    url='',
    license='',
    author='robbiewilson',
    author_email='robbie@robbiewilson.com',
    description='Uses iprules2 to create ip rules to properly handle multiple nics in linux'
)
