from setuptools import setup
from sqlite_object import __version__

setup(
    name='sqlite_object',
    version=__version__,    
    description='Simple way to query SQLITE',
    url='https://github.com/diversen/python-sqlite-object',
    author='Dennis Iversen',
    author_email='dennis.iversen@gmail.com',
    license='MIT',
    packages=['sqlite_object'],

    classifiers=[
        'Development Status :: 1 - Planning',
        'Operating System :: POSIX :: Linux',        
        'Programming Language :: Python :: 3.10',
    ],
)
