import sqlalchemy
from sqlalchemy import orm
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin
from werkzeug.security import check_password_hash, generate_password_hash

from .db_session import SqlAlchemyBase


class User(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    email = sqlalchemy.Column(sqlalchemy.String(65534), index=True, unique=True, nullable=False)
    hashed_password = sqlalchemy.Column(sqlalchemy.String(65534), nullable=False)
    surname = sqlalchemy.Column(sqlalchemy.String(65534))
    name = sqlalchemy.Column(sqlalchemy.String(65534), nullable=False)
    phone = sqlalchemy.Column(sqlalchemy.String(65534))
    country = sqlalchemy.Column(sqlalchemy.String(65534))
    language = sqlalchemy.Column(sqlalchemy.String(65534))
    profile_image = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("profiles.id"))
    profile_relation = orm.relation('ProfileImage')

    def __repr__(self):
        return f'<User> {self.id} {self.name} {self.email}'

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)
