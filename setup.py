"""
SQLAlchemy-Defaults
-------------------

Smart SQLAlchemy defaults for lazy guys, like me.
"""

from setuptools import setup, Command
import subprocess


class PyTest(Command):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        errno = subprocess.call(['py.test'])
        raise SystemExit(errno)


extras_require = {
    'test': [
        'pytest==2.2.3',
        'Pygments>=1.2',
        'Jinja2>=2.3',
        'docutils>=0.10',
        'flexmock>=0.9.7',
        'psycopg2>=2.4.6',
        'PyMySQL==0.6.1',
    ]
}


setup(
    name='SQLAlchemy-Defaults',
    version='0.4.1',
    url='https://github.com/kvesteri/sqlalchemy-defaults',
    license='BSD',
    author='Konsta Vesterinen',
    author_email='konsta@fastmonkeys.com',
    description=(
        'Smart SQLAlchemy defaults for lazy guys, like me.'
    ),
    long_description=__doc__,
    packages=['sqlalchemy_defaults'],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=[
        'six',
        'SQLAlchemy>=0.7.8',
    ],
    extras_require=extras_require,
    cmdclass={'test': PyTest},
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
