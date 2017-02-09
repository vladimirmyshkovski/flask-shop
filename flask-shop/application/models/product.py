# coding: utf-8
from datetime import datetime
from .base import *


class Product(Base):
    name = db.Column(db.String(50), unique=True)
    subname = db.Column(db.String(50))
    image = db.Column(db.String(50), unique=True)
    images = db.Column(db.String(250))
    prices = db.Column(db.String(250))
    colors = db.Column(db.String(250))
    sizes = db.Column(db.String(50))
    params = db.Column(db.String(250))
    
    def __repr__(self):
        return '<Product %s>' % self.name
