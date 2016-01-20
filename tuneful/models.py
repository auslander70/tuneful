import os.path

from flask import url_for
from sqlalchemy import Column, Integer, String, Sequence, ForeignKey
from sqlalchemy.orm import relationship

from tuneful import app
from .database import Base, engine

class Song(Base):
  __tablename__ = "songs"
  
  id = Column(Integer, primary_key=True)
  
  file = relationship("File", uselist=False, backref="song")


class File(Base):
  __tablename__ = "files"
  
  id = Column(Integer, primary_key=True)
  filename = Column(String(512))
  
  song_id = Column(Integer, ForeignKey('songs.id'), nullable=False)