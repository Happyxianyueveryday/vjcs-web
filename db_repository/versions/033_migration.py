from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
post = Table('post', pre_meta,
    Column('id', INTEGER, primary_key=True, nullable=False),
    Column('body', VARCHAR(length=160)),
    Column('user_id', INTEGER),
    Column('timestamp', DATETIME),
    Column('filename', VARCHAR(length=160)),
)

post = Table('post', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('body', String(length=160)),
    Column('timestamp', DateTime),
    Column('user_id', Integer),
    Column('filedir', String(length=160)),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['post'].columns['filename'].drop()
    post_meta.tables['post'].columns['filedir'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['post'].columns['filename'].create()
    post_meta.tables['post'].columns['filedir'].drop()
