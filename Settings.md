## Settings ##

### Standard Django settings ###

`DATABASE_NAME`
> String. Database name. Required.

`DATABASE_HOST`
> String. SQL Server instance in `"server\instance"` format.

`DATABASE_PORT`
> String. Server instance port.

`DATABASE_USER`
> String. Database user name. If not given then MS Integrated Security will
> be used.

`DATABASE_PASSWORD`
> String. Database user password.

`DATABASE_OPTIONS`
> Dictionary. Currently, the following backend-specific keys are available:

> `autocommit`
> > Boolean. Indicates if pyodbc should direct the the ODBC driver to
> > activate the autocommit feature. By default autocommit is turned off.


> `MARS_Connection`
> > Boolean. Only relevant when running on Windows and with SQL Server 2005
> > or later through MS _SQL Server Native client driver_ (i.e. setting
> > `DATABASE_ODBC_DRIVER` to `"SQL Native Client"`). See
> > http://msdn.microsoft.com/en-us/library/ms131686.aspx. Default value
> > is `False`.


> `host_is_server`
> > Boolean. Only relevant if using the FreeTDS ODBC driver under
> > Unix/Linux.
> > By default, when using the FreeTDS ODBC driver the value specified in
> > the `DATABASE_HOST` setting is used in a `SERVERNAME` ODBC
> > connection string component instead of being used in a `SERVER`
> > component; this means that this value should be the name of a
> > _dataserver_ definition present in the `freetds.conf` FreeTDS
> > configuration file instead of a hostname or an IP address.
> > But if this option is present and it's value is True, this special
> > behavior is turned off.
> > See http://freetds.org/userguide/dsnless.htm for more information.


> `datefirst`
> > Numeric. Directs the SQL Server to set which day is considered the first
> > day of the week for the Django ORM QuerySet 'week\_day' lookup. By default
> > django-pyodbc set this to 7 (Sunday, see http://msdn.microsoft.com/en-us/library/aa259210(SQL.80).aspx) to be compatible with the Django convention (see http://docs.djangoproject.com/en/dev/ref/models/querysets/#week-day).


> `dsn`
> > String. A named DSN can be used instead of `DATABASE_HOST`.


> `driver`
> > String. ODBC Driver to use. Default is `"SQL Server"` on Windows and
> > `"FreeTDS"` on other platforms.


> `extra_params`
> > String. Additional parameters for the ODBC connection. The format is
> > `"param=value;param=value"`.


> `collation`
> > String. Name of the collation to use when performing text field lookups
> > against the database. Default value is `"Latin1_General_CI_AS"`. For
> > chinese language you can set it to ```"Chinese_PRC_CI_AS"```.

### `django-pyodbc`-specific settings ###

`DATABASE_ODBC_DSN`

> Deprecated, please use `DATABASE_OPTIONS['dsn']` instead.

`DATABASE_ODBC_DRIVER`
> Deprecated, please use `DATABASE_OPTIONS['driver']` instead.

`DATABASE_EXTRA_PARAMS`
> Deprecated, please use `DATABASE_OPTIONS['extra_params']` instead.

`DATABASE_COLLATION`
> This setting will be deprecated soon, please use `DATABASE_OPTIONS['collation']` instead.