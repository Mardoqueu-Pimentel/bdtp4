#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import configparser
import json
import lzma
import pathlib
import psycopg2 as pg
import tqdm

from bdtp4.util import Oven


def populateProduct(conn, cur, inputFile):
	print('Populating product')
	with lzma.open(inputFile) as file:
		values = []
		for line in file:
			product = json.loads(line)
			product = tuple(
				product.get(key, None)
				for key in ['Id', 'ASIN', 'title', 'group', 'salesrank']
			)
			product = cur.mogrify('(%s,%s,%s,%s,%s)', product)
			values.append(product)

		try:
			cur.execute(
				b'INSERT INTO product(id,asin,title,"group",sales_rank) VALUES ' +
				b','.join(values)
			)
			conn.commit()
		except Exception as e:
			print(e)
			conn.rollback()
			conn.reset()


def populateCategories(conn, cur, inputFile):
	print('Populating category')
	with lzma.open(inputFile) as file:
		uniqueCategories = set(
			cur.mogrify('(%s,%s)', cat)
			for product in map(json.loads, file) if 'categories' in product
			for catList in product['categories']
			for cat in catList
		)

		try:
			cur.execute(
				b'INSERT INTO category(id,name) VALUES ' +
				b','.join(uniqueCategories)
			)
			conn.commit()
		except Exception as e:
			print(e)
			conn.rollback()
			conn.reset()


def populateProductCategory(conn, cur, inputFile):
	print('Populating product_category')
	with lzma.open(inputFile) as file:
		values = set(
			cur.mogrify('(%s,%s,%s)', (prod.get('Id', None), catId, i))
			for prod in map(json.loads, file)
			if 'categories' in prod
			for catList in prod['categories']
			for i, (catId, catName) in enumerate(catList)
		)

		for batch in tqdm.tqdm(Oven(values, len(values) // 10), total=len(values) / 10):
			try:
				cur.execute(
					b'INSERT INTO product_category(prod_id,cat_id,index) VALUES ' +
					b','.join(batch)
				)
				conn.commit()
			except Exception as e:
				print(e)
				conn.rollback()
				conn.reset()


def populateProductSimilar(conn, cur, inputFile):
	print('Populating product_similar')
	with lzma.open(inputFile) as file:
		prods = {
			prod['ASIN']: {key: prod[key] for key in ['Id', 'similar'] if key in prod}
			for prod in map(json.loads, file)
		}

	values = (
		cur.mogrify('(%s,%s)', (prod.get('Id', None), prods[sim].get('Id', None)))
		for prod in prods.values()
		if 'similar' in prod
		for sim in prod['similar']
		if sim in prods
	)

	try:
		cur.execute(
			b'INSERT INTO product_similar(first_prod_id,second_prod_id) VALUES ' +
			b','.join(values)
		)
		conn.commit()
	except Exception as e:
		print(e)
		conn.rollback()
		conn.reset()


def populateReview(conn, cur, inputFile):
	print('Populating review')
	with lzma.open(inputFile) as file:
		values = set(
			cur.mogrify(
				'(to_timestamp(%s),%s,%s,%s,%s,%s)',
				(review['time'], prod['Id'], review['customer_id'], review['rating'], review['votes'], review['helpful'])
			)
			for prod in map(json.loads, file)
			if 'reviews' in prod
			for review in prod['reviews']
		)

		try:
			for batch in Oven(values, 500000):
				cur.execute(
					b'INSERT INTO review(time,prod_id,customer_id,rating,votes,helpful) VALUES ' +
					b','.join(batch)
				)
				conn.commit()
		except Exception as e:
			print(e)
			conn.rollback()
			conn.reset()


def main(*args, config, **kwargs):
	dbName = config['db']['name']
	user = config['db']['user']
	password = config['db']['password']

	dataDir = config['bdtp4']['data-dir']
	dataDir = pathlib.Path(dataDir)
	inputFile = dataDir / 'dataset.json.xz'

	conn = pg.connect(dbname=dbName, user=user, password=password)
	cur = conn.cursor()

	tables: list = kwargs['tables']
	toPopulate = []

	if 'all' in tables:
		tables.remove('all')
		toPopulate = [
			populateProduct, populateCategories, populateProductCategory,
			populateProductSimilar, populateReview
		]
	else:
		for x in tables:
			toPopulate.append({
				'product': populateProduct,
				'category': populateCategories,
				'product_category': populateProductCategory,
				'product_similar': populateProductSimilar,
				'review': populateReview
			}[x])

	for f in toPopulate:
		f(conn, cur, inputFile)


def run():
	argParser = argparse.ArgumentParser('Populate the database')
	argParser.add_argument(
		'tables',
		metavar='T',
		help='The table to populate',
		choices=['all', 'product', 'category', 'product_category', 'product_similar', 'review'],
		nargs='+'
	)
	args = argParser.parse_args().__dict__

	config = configparser.ConfigParser()
	config.read('bdtp4.config')

	main(config=config, **args)


if __name__ == '__main__':
	run()
