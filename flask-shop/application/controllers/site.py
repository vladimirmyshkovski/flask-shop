# coding: utf-8
from flask import render_template, Blueprint, flash
from ..models import db, Product, Parse
import csv 
import json


bp = Blueprint('site', __name__)


@bp.route('/')
def index():
    """Index page."""
    new_products = Product.query.order_by(Product.created_at.desc()).limit(8)
    all_products = Product.query.limit(16)

    return render_template('site/index/index.html', 
    	new_products=new_products,
    	all_products=all_products)


@bp.route('/layout')
def layout():
    """Layout page."""

    return render_template('layout.html')


@bp.route('/about')
def about():
    """About page."""
    return render_template('site/about/about.html')


@bp.route('/<keyword>')
def product(keyword):
    """Product page."""
    query = Product.query
    product = query.filter(Product.link.endswith(keyword)).first()
    product.views = int(product.views)+1
    db.session.add(product)
    db.session.commit()
    
    return render_template('site/product/product.html', product=product)


@bp.context_processor
def menu():
	categories = [category.subname for category in Product.query.group_by(Product.subname).all()]
	return dict(categories=categories)




@bp.route('/parse', methods=['GET'])
def parse():
	db.create_all()

	from bs4 import BeautifulSoup
	from urllib.request import urlopen, Request
	import csv
	from selenium import webdriver
	import time
	import math
	import ast
	from sqlalchemy.exc import IntegrityError, InterfaceError, InvalidRequestError


	BASE_URL = "http://distance.pl/kolekcja.html" 
	driver = webdriver.PhantomJS()


	def get_html(url):
	    driver.get(url)
	    driver.set_window_position(0,0)
	    driver.set_window_size(100000, 200000)
	    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
	    time.sleep(5) 
	    html = driver.page_source

	    return html

	def get_soup(html):
	    try:
	        soup = BeautifulSoup(html, 'html.parser')
	    except AttributeError: return None
	    return soup

	def get_page_count(html):
	    soup = BeautifulSoup(html, "html.parser")
	    productsleft = soup.find('div', class_='pagination__item_lefts').b.text
	    return productsleft


	def get_links(html):
	    links = []
	    soup = BeautifulSoup(html, "html.parser")
	    products = soup.find('ul', class_='pList').find_all('a', 'pList__item__link')
	    for link in products:
	        links.append(link.get('href'))
	    return links


	def get_sub(soup):
	    try:
	        breadcrumb = soup.find('ul', class_='breadcrumb').find_all('li', class_='breadcrumb__item')
	        sub = []
	        for item in breadcrumb:
	            sub.append(item.text)
	    except AttributeError: return None
	    return sub


	def get_imgs(soup):
	    try:
	        images = soup.find('div', class_='product__images__thumbs').find_all('a')
	        imgs = []
	        for item in images:
	            imgs.append(item.get('href')[2:])
	    except AttributeError: return None
	    return imgs


	def get_prices(soup):
	    try:
	        prc = soup.find('div', class_='product__data__field__content--price')
	        em = (prc.find('em').text).split(' ')[0]
	        sale = 'None'
	       	if prc.find('del'):
	       		sale = (prc.find('del').text).split(' ')[0]
	       	prices = [em, sale]
	    except AttributeError: return None
	    return prices


	def get_colors_imgs(soup):
	    try:
	        clrs = soup.find('div', class_='product__data__colors__list').find_all('li', class_='')
	        colors_imgs = []
	        for i in clrs:
	        	colors_imgs.append(i.img.get('src'))
	    except AttributeError: return None
	    return colors_imgs


	def get_colors_links(soup):
	    try:
	        clrs = soup.find('div', class_='product__data__colors__list').find_all('li', class_='')
	        colors_links = []
	        for i in clrs:
	        	if i.a:
	        		colors_links.append(i.a.get('href'))
	        	else:
	        		colors_links.append('None')
	        	#colors_links.append(i.a.get('href'))
	    except AttributeError: return None
	    return colors_links


	def get_sizes(soup):
	    try:
	        szs = soup.find('div', class_='product__data__sizes__data').find_all('label')
	        sizes = []
	        for i in szs:
	            sizes.append(i.text)
	    except AttributeError: return None
	    return sizes


	def get_params(soup):
	    try:
	        prms = soup.find('div', class_='pTabs__tab').find_all('tr')
	        params = {i.th.text : i.td.text for i in prms}
	    except AttributeError: return None
	    return params


	def get_parse(soup):
		sub = get_sub(soup)
		if sub: 
			subname = None
		else:
			subname = sub[-2].replace('\n', '')
		imgs = get_imgs(soup)
		prices = get_prices(soup)
		colors_imgs = get_colors_imgs(soup)
		colors_links = get_colors_links(soup)
		sizes = get_sizes(soup)
		params = get_params(soup)
		product = []
		product = dict(
	    	sub 		= subname,
	        name 		= (sub[-1].replace('\t', '')).replace('\n', ''),
	        imgs 		= str(imgs),
	        prices 		= str(prices),
			colors_imgs = str(colors_imgs),
			colors_links = str(colors_links),
	        sizes 		= str(sizes),
			params 		= str(params)
	            )
		return product

	links = []
	parsing = Parse.query.order_by(Parse.id.desc()).first()
	n = 1
	if parsing is None:
		parsing = Parse(current_product=0, count_products=get_page_count(get_html(BASE_URL + '?page=' + str(n))))
		db.session.add(parsing)
		db.session.commit()
		k = 0
	else:
		if int(parsing.current_product) == int(parsing.count_products):
			parsing = Parse(current_product=0, count_products=get_page_count(get_html(BASE_URL + '?page=' + str(n))))
			db.session.add(parsing)
			db.session.commit()
			k = 0
		else:
			print('parsing is not None!')
		k = parsing.current_product
		n = parsing.page_number
		print('n is : ' + str(n))
		print('k is : ' + str(k))
	while (int(get_page_count(get_html(BASE_URL + '?page=' + str(n))))) > 0:
		linkss = get_links(get_html(BASE_URL + '?page=' + str(n)))
		for link in linkss:
			try:
				product = get_parse(get_soup(get_html(link)))
				thisproduct = Product.query.filter(Product.name == product['name']).first()
				if thisproduct is not None:
					if int(thisproduct.prices[2:-2].split("', '")[0][:-3]) == int(product['prices'][2:-2].split("', '")[0][:-3]):
						print(int(thisproduct.prices[2:-2].split("', '")[0][:-3]))
						print(int(product['prices'][2:-2].split("', '")[0][:-3]))
						pass
						print('product is finded!')
					else:
						print(thisproduct.prices[2:-2].split("', '")[0][:-3])
						print(product['prices'][2:-2].split("', '")[0][:-3])
						thisproduct.prices = product['prices']
						db.session.add(thisproduct)
						print('prise is updated!')
				else:
					print(product['prices'][2:-2].split("', '")[0][:-3])
					print(link)
					prod = Product(
							link 		= link,
							name 		= product['name'], 
							subname 	= product['sub'],
							images 		= product['imgs'],
							colors_imgs = product['colors_imgs'],
							colors_links= product['colors_links'],
							prices 		= product['prices'],
							sizes 		= product['sizes'],
							params 		= product['params']
						)

					db.session.add(prod)
					print(prod)
					k = int(k)+1
					print('k is : ' + str(k))
					parsing.current_product = k
					db.session.add(parsing)
				db.session.commit()
			except IntegrityError: 
				continue
			except InvalidRequestError: 
				continue
		n = int(n) + 1
		parsing.page_number = str(n)
		print(parsing.page_number)
	driver.quit()

	return render_template('site/index/index.html')
