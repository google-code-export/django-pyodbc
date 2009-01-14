from django.core import management
from django.db import connection
from django.db.models.sql import Query

# XXX: This probably will need to change when Django gets multiple DB
# connection support.
def monkeypatched_call_command(name, *args, **options):
    # XXX: Find a better way to detect if this is done
    # only with django-pydobc conenctions
    if name == 'loaddata' and Query.__name__ == 'PyOdbcSSQuery':
        name = 'ss_loaddata'
    return real_call_command(name, *args, **options)

def replace_loaddata_command():
    management.call_command = monkeypatched_call_command

def restore_loaddata_command():
    management.call_command = real_call_command

real_call_command = management.call_command
replace_loaddata_command()
