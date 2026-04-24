from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class UserDB(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)

    posts = relationship("PostDB", back_populates="author")
    comments = relationship("CommentDB", back_populates="author")

class PostDB(Base):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    content = Column(String)
    author_id = Column(Integer, ForeignKey("users.id"))

    author = relationship("UserDB", back_populates="posts")
    comments = relationship("CommentDB", back_populates="post")

class CommentDB(Base):
    __tablename__ = "comments"
    id = Column(Integer, primary_key=True, index=True)
    content = Column(String)
    author_id = Column(Integer, ForeignKey("users.id"))
    post_id = Column(Integer, ForeignKey("posts.id"))

    author = relationship("UserDB", back_populates="comments")
    post = relationship("PostDB", back_populates="comments")