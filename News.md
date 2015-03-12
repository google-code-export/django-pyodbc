django-pyodbc development news.

## SVN [revision 157](https://code.google.com/p/django-pyodbc/source/detail?r=157) ##

This is the minimal development revision of django-pyodbc trunk you need to use if you are
following Django trunk development ([revision 10026](https://code.google.com/p/django-pyodbc/source/detail?r=10026) or newer). An internal refactoring in handling of Django settings by database connections and cursors has been implemented and this made necessary the modifications we implemented in [r155](https://code.google.com/p/django-pyodbc/source/detail?r=155) and [r157](https://code.google.com/p/django-pyodbc/source/detail?r=157).

We took the opportunity to migrate the DATABASE\_ODBC\_DRIVER, DATABASE\_ODBC\_DSN and
DATABASE\_ODBC\_EXTRA\_PARAMS settings to the DATABASE\_OPTIONS dictionary setting. This
will allow django-pyodbc to be compatible with current and future work on multi-database
support for Django.

This is a backward-incompatible change for setups that were using at least one of these
three settings.

The equivalent DATABASE\_OPTIONS keys are 'driver, 'dsn' and 'extra\_params' respectively.

## SVN [revision 138](https://code.google.com/p/django-pyodbc/source/detail?r=138) ##

Starting with this revision, a new `django-1.0.x` SVN branch is available where
a version of django-pyodbc compatible with the 1.0.x Django branch is being maintained.
This means it's kept stable without being disrupted by the potentially unstable
or buggy changes made on trunk to accompany Django own trunk development.

You can checkout it by using

```
$ svn checkout http://django-pyodbc.googlecode.com/svn/branches/django-1.0.x
```

## SVN [revision 135](https://code.google.com/p/django-pyodbc/source/detail?r=135) ##

In this revision, code that had been maintained and developed in a testing branch was merged into trunk fixing several bugs in SQL query building without, as far as we know, introducing new bugs. there is still work to be done in order to reach the full Django ORM functionality both with SQL Server 2000 and SQL Server 2005.

## SVN [revision 79](https://code.google.com/p/django-pyodbc/source/detail?r=79) ##

Backend-specific setting `DATABASE_COLLATE` has been renamed to `DATABASE_COLLATION` to have a more correct spelling and to be consistent with Django's [`TEST\_DATABASE\_COLLATION`](http://docs.djangoproject.com/en/dev/ref/settings/#test-database-collation) setting.

## SVN [revision 66](https://code.google.com/p/django-pyodbc/source/detail?r=66) ##

The backend module name has been changed in a backwards incompatible way, you will need to change your `DATABASE_ENGINE` setting from `'mssql'` to `'sql_server.pyodbc'`.

## SVN [revision 30](https://code.google.com/p/django-pyodbc/source/detail?r=30) ##

Updated code to be compatible with Django as of [r8426](http://code.djangoproject.com/changeset/8426).

Also, work has been started to merge fixes and changes from a development branch to trunk, to be in good shape to accompany the imminent Django 1.0 release.

## SVN [revision 24](https://code.google.com/p/django-pyodbc/source/detail?r=24) ##

Updated code to be compatible with Django as of [r8296](http://code.djangoproject.com/changeset/8296) (see Django ticket [#5461](http://code.djangoproject.com/ticket/5461)).

## SVN [revision 21](https://code.google.com/p/django-pyodbc/source/detail?r=21) ##

Updated code to be compatible with Django as of [r8131](http://code.djangoproject.com/changeset/8131) (see Django ticket [#7560](http://code.djangoproject.com/ticket/7560)).