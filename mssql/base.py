"""
MSSQL database backend for Django.

Requires pyodbc 2.0.38 or higher (http://pyodbc.sourceforge.net/)

pyodbc params:
DATABASE_NAME               - Database name. Required. 
DATABASE_HOST               - SQL Server instance in "server\instance" format.
DATABASE_PORT               - SQL Server instance port.
DATABASE_USER               - Database user name. If not given then the
                              Integrated Security will be used.
DATABASE_PASSWORD           - Database user password.
DATABASE_ODBC_DSN           - A named DSN can be used instead of DATABASE_HOST.
DATABASE_ODBC_DRIVER        - ODBC Driver. Defalut is "{Sql Server}".
DATABASE_ODBC_EXTRA_PARAMS  - Additional parameters for the ODBC connection.
                              The format is "param=value;param=value".
DATABASE_COLLATE            - Collations 
"""
from django.db.backends import BaseDatabaseWrapper, BaseDatabaseFeatures, util
from django.core.exceptions import ImproperlyConfigured
from django.conf import settings
from operations import DatabaseOperations
import datetime
import os

if not hasattr(settings, "DATABASE_COLLATE"):
    settings.DATABASE_COLLATE = 'Latin1_General_CI_AS'

try:
    import pyodbc as Database
    version = tuple(map(int, Database.version.split('.')))
    if version < (2,0,38) :
        raise ImportError("pyodbc 2.0.38 or newer is required; you have %s" % Database.version)
except ImportError, e:
    raise ImproperlyConfigured("Error loading pymssq/pyodbc modules: %s" % ex)

try:
    # Only exists in Python 2.4+
    from threading import local
except ImportError:
    # Import copy of _thread_local.py from Python 2.4
    from django.utils._threading_local import local

DatabaseError = Database.DatabaseError
IntegrityError = Database.IntegrityError

class DatabaseFeatures(BaseDatabaseFeatures):
    allows_group_by_ordinal = False
    allows_unique_and_pk = True
    autoindexes_primary_keys = True
    needs_datetime_string_cast = True
    needs_upper_for_iops = False
    supports_constraints = True
    supports_tablespaces = True
    uses_case_insensitive_names = True
    uses_custom_query_class = True
    supports_usecs = False
    time_field_needs_date = False

class DatabaseWrapper(BaseDatabaseWrapper):
    features = DatabaseFeatures() 
    ops = DatabaseOperations()
    sqlserver_version = None

    # Collations:       http://msdn2.microsoft.com/en-us/library/ms184391.aspx
    #                   http://msdn2.microsoft.com/en-us/library/ms179886.aspx
    # T-SQL LIKE:       http://msdn2.microsoft.com/en-us/library/ms179859.aspx
    # Full-Text search: http://msdn2.microsoft.com/en-us/library/ms142571.aspx
    #   CONTAINS:       http://msdn2.microsoft.com/en-us/library/ms187787.aspx
    #   FREETEXT:       http://msdn2.microsoft.com/en-us/library/ms176078.aspx

    operators = {
        # Since '=' is used not only for string comparision there is no way
        # to make it case (in)sensitive. It will simply fallback to the
        # database collation.
        'exact': '= %s',
        'iexact': 'LIKE %s COLLATE ' + settings.DATABASE_COLLATE,
        'contains': 'LIKE %s COLLATE ' + settings.DATABASE_COLLATE,
        'icontains': 'LIKE %s COLLATE '+ settings.DATABASE_COLLATE,
        'gt': '> %s',
        'gte': '>= %s',
        'lt': '< %s',
        'lte': '<= %s',
        'startswith': 'LIKE %s COLLATE ' + settings.DATABASE_COLLATE,
        'endswith': 'LIKE %s COLLATE ' + settings.DATABASE_COLLATE,
        'istartswith': 'LIKE %s COLLATE ' + settings.DATABASE_COLLATE,
        'iendswith': 'LIKE %s COLLATE ' + settings.DATABASE_COLLATE,

        # TODO: remove, keep native T-SQL LIKE wildcards support
        # or use a "compatibility layer" and replace '*' with '%'
        # and '.' with '_'
        'regex': 'LIKE %s COLLATE ' + settings.DATABASE_COLLATE,
        'iregex': 'LIKE %s COLLATE ' + settings.DATABASE_COLLATE,

        # TODO: freetext, full-text contains...
    }

    def __init__(self, autocommit=False, **kwargs):
        super(DatabaseWrapper, self).__init__(autocommit=autocommit, **kwargs)
        self.connection = None
        self.queries = []

    def cursor(self):
        from django.conf import settings
        if self.connection is None:
            if settings.DATABASE_NAME == '':
                raise ImproperlyConfigured("You need to specify DATABASE_NAME in your Django settings file.")

            if not settings.DATABASE_HOST and not hasattr(settings, "DATABASE_ODBC_DSN"):
                raise ImproperlyConfigured("You need to specify DATABASE_HOST or DATABASE_ODBC_DSN  in your Django settings file.")

            if settings.DATABASE_PORT:
                host_str = '%s:%s' % ( settings.DATABASE_HOST ,settings.DATABASE_PORT)
            else:
                host_str = settings.DATABASE_HOST

            odbc_string=""

            if hasattr(settings, "DATABASE_ODBC_DSN"):
                odbc_string += "DSN=%s;" % settings.DATABASE_ODBC_DSN
            else:
                odbc_string += "Server=%s;" % host_str

            if settings.DATABASE_USER:
                odbc_string += "Uid=%s;Pwd=%s;" % (settings.DATABASE_USER, settings.DATABASE_PASSWORD)
            else:
                odbc_string += "Integrated Security=SSPI;"

            odbc_string += "Database=%s" % settings.DATABASE_NAME

            if hasattr(settings, "DATABASE_ODBC_EXTRA_PARAMS"):
                odbc_string +=  ";" + settings.DATABASE_ODBC_EXTRA_PARAMS

            self.connection = Database.connect(odbc_string, self.options["autocommit"])

        cursor = CursorWrapper(self.connection.cursor())
        if not self.sqlserver_version:
            cursor.execute("SELECT cast(SERVERPROPERTY('ProductVersion') as varchar)")
            self.sqlserver_version = int(cursor.fetchone()[0].split('.')[0])
            from operations import SQL_SERVER_2005_VERSION
            if self.sqlserver_version >= SQL_SERVER_2005_VERSION:
                from creation import DATA_TYPES
                DATA_TYPES['TextField'] = 'nvarchar(max)'
            cursor = CursorWrapper(self.connection.cursor())
        if settings.DEBUG:
            return util.CursorDebugWrapper(cursor, self)
        return cursor

class CursorWrapper(object):
    """
    A wrapper around the pyodbc cursor that:
        2. Replaces '%s' parameter placeholder in sql queries to '?' (pyodbc specific).
    """
    def __init__(self, cursor):
        self.cursor = cursor

    def format_sql(self, sql):
        # pyodbc uses '?' instead of '%s' as parameter placeholder.
        if "%s" in sql:
            sql = sql.replace('%s', '?')
        return sql

    def format_params(self, params):
        ps = []
        for p in params:
            if isinstance(p, unicode): 
                if os.name == 'nt':
                    ps.append(p)
                else:
                    ps.append(unicode(p).encode('utf-8')) # convert from unicode to utf-8 for pyodbc use freetds under Linux
            elif isinstance(p,type(True)): # convert bool to integer
                if p:
                    ps.append(1)
                else:
                    ps.append(0)
            else:
                ps.append(p)
        return tuple(ps)

    def execute(self, sql, params=()):
        sql = self.format_sql(sql)
        params = self.format_params(params)
        return self.cursor.execute(sql, params)

    def executemany(self, sql, param_list):
        sql = self.format_sql(sql)
        new_param_list = [self.format_params(params) for params in param_list]
        return self.cursor.executemany(sql, new_param_listp)

    def fetchone(self):
        row = self.cursor.fetchone()
        if row is not None:
            # Convert row to tuple (pyodbc Rows are not sliceable).
            return tuple(row)
        return row

    def fetchmany(self, chunk):
        return [tuple(row) for row in self.cursor.fetchmany(chunk)]

    def fetchall(self):
        return [tuple(row) for row in self.cursor.fetchall()]

    def __getattr__(self, attr):
        if attr in self.__dict__:
            return self.__dict__[attr]
        else:
            return getattr(self.cursor, attr)
