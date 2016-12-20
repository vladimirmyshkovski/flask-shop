# coding: utf-8
from flask import render_template, Blueprint, flash
from ..models import db, Product
import csv 


bp = Blueprint('site', __name__)


@bp.route('/')
def index():
    """Index page."""
    new_products = Product.query.order_by(Product.created_at.desc()).limit(8)
    all_products = Product.query.limit(6)

    return render_template('site/index/index.html', 
    	new_products=new_products,
    	all_products=all_products)


@bp.route('/about')
def about():
    """About page."""
    return render_template('site/about/about.html')



#@bp.context_processor
#def menu():








@bp.route('/parse')
def parse():
	db.create_all()

	from bs4 import BeautifulSoup
	from urllib.request import urlopen, Request
	import csv
	from selenium import webdriver
	import time
	import math

	BASE_URL = "http://distance.pl/kolekcja.html" 
	driver = webdriver.PhantomJS()


	def get_html(url):
	    #driver = webdriver.PhantomJS()
	    driver.get(url)
	    driver.set_window_position(0,0)
	    driver.set_window_size(100000, 200000)
	    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
	    time.sleep(5) 
	    html = driver.page_source
	    #driver.save_screenshot('screen.png')
	    #driver.quit()
	    return html

	def get_soup(html):
	    try:
	        soup = BeautifulSoup(html, 'html.parser')
	    except AttributeError: return None
	    return soup

	def get_page_count(html):
	    soup = BeautifulSoup(html, "html.parser")
	    productsleft = soup.find('div', class_='pagination__item_lefts').b.text
	    #print('products has left : ' + productsleft)
	    return productsleft


	def get_links(html):
	    links = []
	    soup = BeautifulSoup(html, "html.parser")
	    products = soup.find('ul', class_='pList').find_all('a', 'pList__item__link')
	    for link in products:
	        links.append(link.get('href'))
	    #print(links)
	    return links


	def get_sub(soup):
	    try:
	        breadcrumb = soup.find('ul', class_='breadcrumb').find_all('li', class_='breadcrumb__item')
	        sub = []
	        for item in breadcrumb:
	            sub.append(item.text)
	    except AttributeError: return None
	    return sub


	def get_img(soup):
	    try:
	        img = soup.find('img', class_='gtm--big_image').get('data-lazy')
	    except AttributeError: return None
	    return img


	def get_imgs(soup):
	    try:
	        images = soup.find('div', class_='product__images__thumbs').find_all('a')
	        imgs = []
	        for item in images:
	            imgs.append(item.get('href'))
	    except AttributeError: return None
	    return imgs


	def get_prices(soup):
	    try:
	        prc = soup.find('div', class_='product__data__field__content--price').span
	        prices = []
	        for item in prc.find_all():
	            prices.append(item.text)
	    except AttributeError: return None
	    return prices


	def get_colors(soup):
	    try:
	        clrs = soup.find('div', class_='product_-data__colors__list')
	        colors_links = [i.get('href') if i else [None] for i in clrs.find_all('a')]
	        colors_imgs = [i.get('src') for i in clrs.find_all('img')]
	        colors = {link.link: {img.img for img in colors_imgs} for link in colors_links}
	    except AttributeError: return None
	    return colors


	def get_sizes(soup):
	    try:
	        szs = soup.find('div', class_='products__data__sizes__data').find_all('label')
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
	    #soup = BeautifulSoup(html, 'html.parser')
	    sub = get_sub(soup)
	    img = get_img(soup)
	    #img = check(soup.find('img', class_='gtm--big_image').get('data-lazy'))
	    imgs = get_imgs(soup)
	    #imgs = check(soup.find('div', class_='product__images__thumbs').find_all('a'))
	    prices = get_prices(soup)
	    #prices = check(soup.find('div', class_='product__data__field__content--price').span)
	    colors = get_colors(soup)
	    #colors = check(soup.find('div', class_='product__data__colors__list'))
	    sizes = get_sizes(soup)
	    #sizes = check(soup.find('div', class_='product__data__sizes__data').find_all('label'))
	    params = get_params(soup)
	    #params = check(soup.find('div', class_='pTabs__tab').find_all('tr'))
	    product = []
	    product.append({
	        'sub':sub[-2],
	        'name':sub[-1],
	        'img':img,
	        'imgs':imgs,
	        'prices':prices,
	        'colors':colors,
	        #'colors-links':[color.get('href') if colors else [None] for color in colors.find_all('a')],
	        #'colors-imgs':[color.get('src') for color in colors.find_all('img')],
	        'sizes':sizes,
	        'params':params
	            })
	        #'colors_links':[i.find('a').get('href') for i in colors],
	        #'color_imgs':[i.find('img').get('src') for i in colors]
	    print(product)
	    return product

	links = []
	n = 1
	while (int(get_page_count(get_html(BASE_URL + '?page=' + str(n))))) > 0:
	        #lastpage = int(get_page_count(get_html(BASE_URL + '?page=' + str(n)))) / int(len(get_products(get_html(BASE_URL + '?page=' + str(n))))) 
	    linkss = get_links(get_html(BASE_URL + '?page=' + str(n))) 
	    for link in linkss:
	       	product = get_parse(get_soup(get_html(link)))
	       	product = dict(product)
	        prod = Product(name=product['name'], subname=product['sub'], image=product['image'], images=product['images'], prices=product['prices'], colors=product['colors'], sizes=product['sizes'])
	        db.session.add(prod)
	        db.session.commit()
	    n += 1
	        #print('products count is : ' + str (len(products)))
	        #print('parsed URL is : ' + BASE_URL + '?page=' + str(n))
	        #print('Count of products : ' + str(len(products)))
	    #products.extend(get_products(get_html(BASE_URL + '?page=' + str(n))))
	driver.quit()
	    #save(products, BASE_URL.split('/')[-1].replace('.html', '') + '.csv')
	
	"""Parsing csv file


	with open('/home/narnik/Программы/BS4/distance/distance-complete.csv') as f:
		r = csv.reader(f)
		for i in r:
			print(i[0])
			flash(i)
			product = Product(
				name=i[0],
				subname=i[1],
				image=i[3],
				images=i[4],
				prices=i[5],
				colors=i[6],
				sizes=i[7],
				)
			db.session.add(product)
			db.session.commit()
			"""
	return render_template('site/index/index.html')