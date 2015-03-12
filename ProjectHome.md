## Description ##

A [Django](http://djangoproject.com/) external database backend for _MS SQL Server_ that uses ODBC by employing the [pyodbc](http://code.google.com/p/pyodbc/) library, supports SQL Server 2000 and 2005.

Pyodbc seems to be a mature, viable way to access SQL Server from Python in multiple platforms and is actively maintained. It's also used by SQLAlchemy for SQL Server connections.

### Important ###

If you are following Django trunk development and have [revision 10026](https://code.google.com/p/django-pyodbc/source/detail?r=10026) or newer, the
minimal development revision of django-pyodbc trunk you need to use is [r157](https://code.google.com/p/django-pyodbc/source/detail?r=157).

Also, the DATABASE\_ODBC\_DRIVER, DATABASE\_ODBC\_DSN and DATABASE\_ODBC\_EXTRA\_PARAMS settings were migrated to the DATABASE\_OPTIONS dictionary setting in this revision.

This is a backward-incompatible change for setups that were using at least one of these three settings. The equivalent DATABASE\_OPTIONS keys are 'driver, 'dsn' and 'extra\_params' respectively.

SVN `trunk` development follows closely Django development, so it needs a recent checkout of Django SVN trunk. On Jan 24, 2009 ([r138](https://code.google.com/p/django-pyodbc/source/detail?r=138)) a `django-1.0.x` SVN branch was created, its main purpose is to remain compatible with the Django 1.0.x maintenance branch.

See our [News](News.md) page.

## Features ##

  * Works on Windows and Linux (using FreeTDS)
  * Native Unicode support. Every string that goes in is stored as Unicode, and every string that goes out of the database is returned as Unicode. No conversion to/from intermediate encodings takes place, so things like max\_length in CharField works just like expected.
  * Limit/offset emulation supported in SQL Server 2005 and SQL Server 2000.
  * Offset without limit emulation supported in SQL Server 2005.
  * Both Windows Authentication (Integrated Security) and SQL Server Authentication supported.
  * Passes most of the Django test suite.

## Installation ##

  * Install [pyodbc](http://pyodbc.sourceforge.net/).
  * [Download django-pyodbc](http://code.google.com/p/django-pyodbc/source).
  * Add the top directory of your django-pyodbc checkout to your `PYTHONPATH`.
  * In your settings file set the DB engine to `sql_server.pyodbc`.

### Configuration ###

See [Settings](Settings.md). Examples:

On Windows, accessing SQL Server 2005:

```
DATABASE_ENGINE = 'sql_server.pyodbc'
DATABASE_NAME = 'db_name'
DATABASE_USER = 'webapp'
DATABASE_PASSWORD = 'sikrit'
DATABASE_HOST = r'test_server\SQLEXPRESS'
DATABASE_OPTIONS= {
    'driver': 'SQL Native Client',
    'MARS_Connection': True,
}
```

Using FreeTDS plus unixODBC on Linux/Unix, accessing SQL Server 2000:

```
DATABASE_ENGINE = 'sql_server.pyodbc'
DATABASE_NAME = 'the_database'
DATABASE_USER = 'django_access'
DATABASE_PASSWORD = 'guessme'
DATABASE_OPTIONS = {
    'driver': 'FreeTDS',
    'dsn': 'MyDSN', # ODBC DSN name defined in your odbc.ini
}
```

## Testing environments ##

Tested on:

  * SQL Server 2005 Express SP2 and SQL Server 2000 SP4, Python 2.5 and Windows XP.
  * SQL Server 2005, Python 2.5 and Ubuntu 8.04.

## Open issues ##

Currently, the following parts of the Django test suite don't pass:

  * lookup: Regular expressions are not supported out of the box by SQL Server. Only simple wildcard matching with `%`, `_` and `[]` character classes.
  * serializers: Forward references cause foreign key constraint violation.

## Thanks ##

  * Filip Wasilewski. For his pioneering work, proving this was possible and profusely documenting the code with links to relevant vendor technical articles (Django ticket #5246).
  * mamcxi (http://www.elmalabarista.com). For the first implementation using pymssql (Django ticket #5062).
  * Adam Vandenber (from the django-mssql project). For code to distinguish between different Query classes when sub-classing them.
  * All the Django core developers, especially Malcolm Tredinnick. For being an example of technical excellence and for building such an impressive community.
  * The Oracle Django team (Matt Boersma, Ian Kelly) for some excellent ideas when it comes to implement a custom Django DB backend.