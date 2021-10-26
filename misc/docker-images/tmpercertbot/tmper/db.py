from datetime import datetime
from pony.orm import *

status = [
    'Success', 'Not found', 'Invalid key',
]
status_dict = {k:v for v,k in enumerate(status)}

db = Database()

class File(db.Entity):
    code = PrimaryKey(str, auto=False)
    size = Required(int)
    filename = Required(str)
    key = Optional(str)
    num = Required(int)

    upload_time = Required(datetime)
    exp_time = Required(datetime)

class Download(db.Entity):
    code = Required(str)
    time = Required(datetime)
    status = Required(int)

@db_session
def record_upload(code, filename, size, exp, key=''):
    File(
        code=code, filename=filename, size=size,
        upload_time=datetime.now(), exp_time=exp,
        key=key
    )

@db_session
def record_download(code, status):
    Download(
        code=code, status=status_dict[status],
        time=datetime.now()
    )

def get_file(code):
    pass

db.bind('sqlite', ':memory:')
#db.bind('sqlite', 'database.sqlite', create_db=True)
db.generate_mapping(create_tables=True)


