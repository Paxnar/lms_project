import sqlalchemy
from sqlalchemy import orm
from flask_login import UserMixin
from .db_session import SqlAlchemyBase


class ProfileImage(SqlAlchemyBase, UserMixin):
    __tablename__ = 'profiles'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    data = sqlalchemy.Column(sqlalchemy.BLOB, unique=True)
    user = orm.relation("User", back_populates='profile_relation')

    def __repr__(self):
        return f'<ProfileImage> {self.id} {self.data}'
