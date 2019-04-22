from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
user = Table('user', pre_meta,
    Column('id', INTEGER, primary_key=True, nullable=False),
    Column('email', VARCHAR(length=120)),
    Column('password_hash', VARCHAR(length=128)),
    Column('username', VARCHAR(length=64)),
    Column('description', VARCHAR(length=140)),
    Column('last_seen', DATETIME),
)

user = Table('user', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('username', String(length=64)),
    Column('email', String(length=120)),
    Column('password_hash', String(length=128)),
    Column('description', String(length=140)),
    Column('sign', String(length=20)),
    Column('job', String(length=20)),
    Column('location', String(length=100)),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['user'].columns['last_seen'].drop()
    post_meta.tables['user'].columns['job'].create()
    post_meta.tables['user'].columns['location'].create()
    post_meta.tables['user'].columns['sign'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['user'].columns['last_seen'].create()
    post_meta.tables['user'].columns['job'].drop()
    post_meta.tables['user'].columns['location'].drop()
    post_meta.tables['user'].columns['sign'].drop()
