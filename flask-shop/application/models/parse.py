# coding: utf-8
from datetime import datetime
from .base import *


class Parse(Base):
	current_product = db.Column(db.String(4))
	count_products = db.Column(db.String(4))
	page_number = db.Column(db.String(3), default='0')

	def __repr__(self):
		return '<Parse %s>' % self.id
