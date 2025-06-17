import sqlite3

from time import time
from sqlalchemy import Boolean, create_engine, Column, Integer, String, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import Float

DEBUG_STATUS = False
db_name = ["dbbot.sqlite"]

dbname = db_name[0]

Base = declarative_base()
engine = create_engine(f'sqlite:///{dbname}', echo=DEBUG_STATUS)
Session = sessionmaker(bind=engine)
session = Session()

class User(Base):
    __tablename__ = 'users'
    userid = Column(BigInteger, primary_key=True, unique=True, nullable=False)
    joined = Column(BigInteger, nullable=False)
    link_status = Column(Boolean, default=False)

Base.metadata.create_all(engine)

def add_new_user(user_id):
    try:
        # check user exist or no
        existing_user = session.get(User, user_id)
        if existing_user:
            return "User already exists"

        new_user = User(userid=user_id, joined=int(time()))
        session.add(new_user)
        session.commit()
        return "User added successfully"

    except SQLAlchemyError as e:
        session.rollback()
        return f"Error: {e}"

def GET_users_id():
    try:
        user_ids = session.query(User.userid).all()
        return [uid[0] for uid in user_ids]  # each row is a tuple like (userid,)
    except SQLAlchemyError as e:
        return f"Error: {e}"
    
def link_status(user_id):
    try:
        user_status = session.query(User.link_status).filter_by(userid=user_id).first()
        return user_status
    except SQLAlchemyError as e:
        return f"Error: {e}"

def update_linkStatus(user_id):
    try:
        user = session.query(User).filter_by(userid=user_id).first()
        if user:
            user.link_status = True
            session.commit()
            return "User updated successfully"
        else:
            return "User not found"
    except SQLAlchemyError as e:
        session.rollback()
        return f"Error: {e}"