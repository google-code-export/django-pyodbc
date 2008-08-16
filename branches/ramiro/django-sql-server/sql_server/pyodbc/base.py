"""
MS SQL Server database backend for Django.

Requires pyodbc 2.0.38 or higher (http://pyodbc.sourceforge.net/)
"""
from django.db.backends import *
from django.core.exceptions import ImproperlyConfigured
from sql_server.pyodbc.client import DatabaseClient
from sql_server.pyodbc.creation import DatabaseCreation
from sql_server.pyodbc.introspection import DatabaseIntrospection
from sql_server.pyodbc.operations import DatabaseOperations
import os

try:
    import pyodbc as Database
    version = tuple(map(int, Database.version.split('.')))
    if version < (2, 0, 38):
        raise ImportError("pyodbc 2.0.38 or newer is required; you have %s" % Database.version)
except ImportError, e:
    raise ImproperlyConfigured("Error loading pyodbc module: %s" % e)

DatabaseError = Database.DatabaseError
IntegrityError = Database.IntegrityError

class DatabaseFeatures(BaseDatabaseFeatures):
    uses_custom_query_class = True
    can_use_chunked_reads = False
    #uses_savepoints = True


class DatabaseWrapper(BaseDatabaseWrapper):

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
        'iexact': 'LIKE %s COLLATE Latin1_General_CI_AS',
        'contains': "LIKE %s ESCAPE '\\' COLLATE Latin1_General_CS_AS",
        'icontains': "LIKE %s ESCAPE '\\'COLLATE Latin1_General_CI_AS",
        'gt': '> %s',
        'gte': '>= %s',
        'lt': '< %s',
        'lte': '<= %s',
        'startswith': "LIKE %s ESCAPE '\\' COLLATE Latin1_General_CS_AS",
        'endswith': "LIKE %s ESCAPE '\\' COLLATE Latin1_General_CS_AS",
        'istartswith': "LIKE %s ESCAPE '\\' COLLATE Latin1_General_CI_AS",
        'iendswith': "LIKE %s ESCAPE '\\' COLLATE Latin1_General_CI_AS",

        # TODO: remove, keep native T-SQL LIKE wildcards support
        # or use a "compatibility layer" and replace '*' with '%'
        # and '.' with '_'
        'regex': 'LIKE %s COLLATE Latin1_General_CS_AS',
        'iregex': 'LIKE %s COLLATE Latin1_General_CI_AS',

        # TODO: freetext, full-text contains...
    }

    def __init__(self, autocommit=False, **kwargs):
        super(DatabaseWrapper, self).__init__(autocommit=autocommit, **kwargs)

        self.features = DatabaseFeatures()
        self.ops = DatabaseOperations()
        self.client = DatabaseClient()
        self.creation = DatabaseCreation(self)
        self.introspection = DatabaseIntrospection(self)
        self.validation = BaseDatabaseValidation()

        self.connection = None
        self.driver_needs_utf8 = False

    def _cursor(self, settings):
        if self.connection is None:
            if not settings.DATABASE_NAME:
                raise ImproperlyConfigured("You need to specify DATABASE_NAME in your Django settings file.")

            connstr = []
            if hasattr(settings, "DATABASE_ODBC_DSN"):
                connstr.append("DSN=%s" % settings.DATABASE_ODBC_DSN)
            else:
                if settings.DATABASE_HOST:
                    host_str = settings.DATABASE_HOST
                else:
                    host_str = 'localhost'
                if settings.DATABASE_PORT:
                    host_str += ',%s' % settings.DATABASE_PORT
                connstr.append("Server=%s" % host_str)

            if hasattr(settings, "DATABASE_ODBC_DRIVER"):
                odbc_driver = settings.DATABASE_ODBC_DRIVER
            else:
                if os.name == 'nt':
                    odbc_driver = "SQL Server"
                else:
                    odbc_driver = "FreeTDS"
            connstr.append("Driver={%s}" % odbc_driver)

            if settings.DATABASE_USER:
                connstr.append("Uid=%s;Pwd=%s" % (settings.DATABASE_USER, settings.DATABASE_PASSWORD))
            else:
                connstr.append("Integrated Security=SSPI")

            connstr.append("Database=%s" % settings.DATABASE_NAME)

            if hasattr(settings, "DATABASE_ODBC_EXTRA_PARAMS"):
                connstr.append(settings.DATABASE_ODBC_EXTRA_PARAMS)

            self.connection = Database.connect(';'.join(connstr), autocommit=self.options["autocommit"])
            self.connection.cursor().execute("SET DATEFORMAT ymd")

            # http://msdn.microsoft.com/en-us/library/ms131686.aspx
            #if self.ops.sql_server_ver >= 2005:
            #    if (connection is using the 'SQL Server Native Client') and
            #        (MARS feature is enabled):
            #        self.features.can_use_chunked_reads = True
            #
            #    # How to use the conn string to activate it: Add
            #    # "MARS_Connection=yes" to DATABASE_ODBC_EXTRA_PARAMS

            if self.ops.sql_server_ver < 2005:
                self.creation.data_types['TextField'] = 'ntext'
            if self.connection.getinfo(Database.SQL_DRIVER_NAME) != 'SQLSRV32.DLL':
                self.driver_needs_utf8 = True
            # FreeTDS can't execute some sql like CREATE DATABASE ... etc. in
            # Multi-statement, so need commit for avoid this
            if not self.connection.autocommit:
                self.connection.commit()

        return CursorWrapper(self.connection.cursor(), self.driver_needs_utf8)


class CursorWrapper(object):
    """
    A wrapper around cursor that takes in account some
    particularities of the pyodbc DB-API 2.0 implementation.
    """
    def __init__(self, cursor, driver_needs_utf8):
        self.cursor = cursor
        self.driver_needs_utf8 = driver_needs_utf8

    def format_sql(self, sql):
        # pyodbc uses '?' instead of '%s' as parameter placeholder.
        if "%s" in sql:
            sql = sql.replace('%s', '?')
        return sql

    def format_params(self, params):
        fp = []
        for p in params:
            if isinstance(p, unicode):
                if self.driver_needs_utf8:
                    fp.append(p.encode('utf-8'))
                else:
                    fp.append(p)
            elif isinstance(p, str):
                if self.driver_needs_utf8:
                    fp.append(p.decode('utf-8').encode('utf-8'))
                else:
                    fp.append(p)
            elif isinstance(p, type(True)):
                if p:
                    fp.append(1)
                else:
                    fp.append(0)
            else:
                fp.append(p)
        return tuple(fp)

    def execute(self, sql, params=()):
        sql = self.format_sql(sql)
        params = self.format_params(params)
        return self.cursor.execute(sql, params)

    def executemany(self, sql, params_list):
        sql = self.format_sql(sql)
        # pyodbc's cursor.executemany() doesn't support an empty param_list
        if not params_list:
            if '?' in sql:
                return
        else:
            raw_pll = params_list
            params_list = [self.format_params(p) for p in raw_pll]
        return self.cursor.executemany(sql, params_list)

    def format_results(self, rows):
        if not self.driver_needs_utf8:
            return rows
        fr = []
        for row in rows:
            if isinstance(row, str):
                fr.append(row.decode('utf-8'))
            else:
                fr.append(row)
        return tuple(fr)

    def fetchone(self):
        row = self.cursor.fetchone()
        if row is not None:
            # Convert row to tuple (pyodbc Rows are not sliceable).
            return tuple(self.format_results(row))
        return row

    def fetchmany(self, chunk):
        return [tuple(self.format_results(row)) for row in self.cursor.fetchmany(chunk)]

    def fetchall(self):
        return [tuple(self.format_results(row)) for row in self.cursor.fetchall()]

    def __getattr__(self, attr):
        if attr in self.__dict__:
            return self.__dict__[attr]
        return getattr(self.cursor, attr)
