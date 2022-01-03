import json
import time

# import sqlalchemy as db

# engine = db.create_engine('sqlite:///db.sqlite', connect_args={'check_same_thread': True})  # Create test.sqlite automatically
# connection = engine.connect()
# metadata = db.MetaData()

scheduler_video = db.Table(
    'scheduler_video', metadata,
    db.Column('id', db.Integer(), nullable=False, primary_key=True, autoincrement=True),
    db.Column('video_id', db.String(255), nullable=False),
    db.Column('shared', db.Boolean(), default=False),
    db.Column('share_number', db.Integer(), default=0),
    db.Column('co_khi', db.Boolean(), default=False),
    db.Column('xay_dung', db.Boolean(), default=False),
    db.Column('go', db.Boolean(), default=False),
    db.Column('options', db.Boolean(), default=False),
    db.Column('groups_shared', db.Text(), default=""),
    db.Column('created_date', db.Integer(), default=0),
)

via_share = db.Table(
    'via_share', metadata,
    db.Column('id', db.Integer(), nullable=False, primary_key=True, autoincrement=True),
    db.Column('fb_id', db.String(255), nullable=False),
    db.Column('password', db.String(255), nullable=False),
    db.Column('mfa', db.String(255), nullable=False),
    db.Column('email', db.String(255)),
    db.Column('email_password', db.String(255)),
    db.Column('proxy', db.String(255)),
    db.Column('date', db.String(255)),
    db.Column('share_number', db.Integer()),
    db.Column('group_joined', db.Text()),
    db.Column('status', db.String(255)),
)


joining_group = db.Table(
    'joining_group', metadata,
    db.Column('id', db.Integer(), nullable=False, primary_key=True, autoincrement=True),
    db.Column('name', db.String(255), nullable=False),
    db.Column('group_type', db.String(255), nullable=False)
)

metadata.create_all(engine)  # Creates the table

if __name__ == '__main__':
    # metadata.create_all(engine)  # Creates the table
    # Inserting record one by one
    # query = db.insert(scheduler_video).values(video_id='448537403359670', created_date=int(time.time()))
    # ResultProxy = connection.execute(query)

    query = db.insert(via_share).values(
        fb_id="123", password="232", mfa="123",
        email="123", email_password="123",
        proxy="123", share_number=0,
        group_joined=json.dumps([""]), date="",
        status="live"
    )
    ResultProxy = connection.execute(query)