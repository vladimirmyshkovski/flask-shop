# coding: utf-8
from datetime import datetime
from .base import *


class Product(Base):
    link = db.Column(db.String(50), unique=True)
    name = db.Column(db.String(50), unique=True)
    subname = db.Column(db.String(50))
    images = db.Column(db.String(550))
    prices = db.Column(db.String(250))
    colors_imgs = db.Column(db.String(250))
    colors_links = db.Column(db.String(250))
    sizes = db.Column(db.String(250))
    params = db.Column(db.String(250))
    views = db.Column(db.String(5), default='0')
    
    def __repr__(self):
        return '<Product %s>' % self.name
