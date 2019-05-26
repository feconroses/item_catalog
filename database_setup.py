import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class User(Base):
    """
    Registered user information is stored in db
    """

    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))


class Category(Base):
    """
    Registered category information is stored in db
    """
    __tablename__ = 'category'

    name = Column(String(80), nullable=False)
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User, cascade="delete")

    @property
    def serialize(self):
        # Returns object data in easily serializeable formate
        return {
            'name': self.name,
            'id': self.id,
            'user_id': self.user_id,
        }


class CategoryItem(Base):
    """
    Registered category items information is stored in db
    """
    __tablename__ = 'category_item'

    name = Column(String(80), nullable=False)
    id = Column(Integer, primary_key=True)
    description = Column(String(250))
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship(Category, cascade="delete")
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User, cascade="delete")

    @property
    def serialize(self):
        # Returns object data in easily serializeable formate
        return {
            'name': self.name,
            'description': self.description,
            'id': self.id,
            'user_id': self.user_id,
            'category_id': self.category_id,
        }


engine = create_engine('sqlite:///catalog.db')

Base.metadata.create_all(engine)
