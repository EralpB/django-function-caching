import os
from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()

setup(
    name='django-function-caching',
    version='0.2',
    packages=['functioncaching'],
    description='Advanced function caching',
    long_description=README,
    author='Eralp Bayraktar',
    author_email='imeralpb@gmail.com',
    url='https://github.com/EralpB/django-function-caching/',
    license='MIT',
    install_requires=[
        'Django>=1.6',
        'django-redis>=4.11.0'
    ]
)