

# Installing FreeTDS #

Needed packages (Ubuntu)
  * freetds-common
  * freetds-bin
  * tsodbc

Installing the packages:

```
$sudo apt-get install freetds-common freetds-bin tsodbc
```

# Configuring FreeTDS #

Edit the freetds.conf file so it contains your SQL server settings
Available options in [the FreeTDS documentation for freetds.conf](http://www.freetds.org/userguide/freetdsconf.htm).

```
$sudo vim /etc/freetds/freetds.conf
```

Add the following

```
[SERVERNAME]
host = xxx.xxx.xxx.xxx
port = 1433
tds version = 8.0
```

SERVERNAME is used in your ODBC configuration file

# Testing FreeTDS #

Try making a connection through FreeTDS first before setting up ODBC by issuing a query.

```
$tsql -S SERVERNAME -U USERNAME
locale is "en_US.UTF-8"
locale charset is "UTF-8"
Password: PASSWORD
```

SERVERNAME
> the same reference from freetds.conf

USERNAME
> your database username

PASSWORD
> your database password

If your login succeeds, try selecting some data

```
1> SELECT TOP 1 * FROM TABLENAME
2> GO
(resultset)
1> EXIT
```

TABLENAME
> a table in your database. If your user doesn't have a default database, try using the DATABASE.dbo.TABLENAME format.

For domain authentication use DOMAIN\USERNAME. More details about domain particulars see [the FreeTDS documentation about domain logins](http://www.freetds.org/userguide/domains.htm)

If you can't query your database, something in the FreeTDS configuration is wrong. See the [FreeTDS troubleshooting page](http://www.freetds.org/userguide/troubleshooting.htm)

# Configuring the ODBC source #

Create a new file 'odbc.ini' under /etc

```
#vim /etc/odbc.ini
```

Add the following

```
[ODBC Data Sources]
ODBCNAME = Microsoft SQL Server

[ODBCNAME]
Driver = FreeTDS
Description = A wonderful description goes here
Trace = No
Servername = SERVERNAME
Database = DATABASENAME

[Default]
Driver = /usr/lib/odbc/libtdsodbc.so
```

ODBCNAME
> the ODBC reference you'll be using in your django configuration
SERVERNAME
> the same reference from freetds.conf
DATABASENAME
> your database (schema) name

# Testing the ODBC configuration #

Try to connect and execute a query in the ODBC context using isql.

```
$isql -v ODBCNAME USERNAME PASSWORD
+---------------------------------------+
| Connected!                            |
|                                       |
| sql-statement                         |
| help [tablename]                      |
| quit                                  |
|                                       |
+---------------------------------------+
```

Try selecting some data

```
SQL> SELECT TOP 1 * FROM TABLENAME
(resultset)
SQL> QUIT
```

If all of this works out, you should be able to reference the ODBC source in django-pyodbc.
See the [settings wiki page](Settings.md)

--Tim Adam