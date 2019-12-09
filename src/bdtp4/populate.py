#!/usr/bin/env python
# -*- coding: utf-8 -*-
import configparser
import json
import lzma
import pathlib
import psycopg2 as pg


def main(*args, config, **kwargs):
	dbName = config['db']['name']
	user = config['db']['user']
	password = config['db']['password']

	dataDir = config['bdtp4']['data-dir']
	dataDir = pathlib.Path(dataDir)
	inputFile = dataDir/'dataset.json.xz'

	conn = pg.connect(dbname=dbName, user=user, password=password)
	cur = conn.cursor()

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

	print('Populating category')




def run():
	config = configparser.ConfigParser()
	config.read('bdtp4.config')
	main(config=config)


if __name__ == '__main__':
	run()
