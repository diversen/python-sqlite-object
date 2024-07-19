"""
mysql_object

Small library to make it easier to work with MySQL in Python.
"""

__version__ = "0.0.2"
__author__ = 'Dennis Iversen'
__credits__ = '10kilobyte.com'

from .sqlite_object import SQLiteObject, get_sqlite_object
from .sql_query import SQLQuery