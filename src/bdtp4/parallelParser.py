import datetime
import json
import lzma
import pathlib
import re
from collections import defaultdict
from concurrent.futures.process import ProcessPoolExecutor
from concurrent.futures import as_completed

from multiprocessing import cpu_count

from bdtp4.util import Oven
import tqdm


notWanted = {'Total items', 'categories', 'reviews'}
typeDict = {
	'Id': int,
	'salesrank': int
}


def cleaner(result):
	if 'similar' in result:
		result['similar'] = [
			x
			for x in map(str.strip, result['similar'].split()) if x
		][1:]
	if 'categories' in result:
		result['categories'] = [
			[
				[int(catId), catName]
				for catName, catId in re.findall(r'(?<=\|)([^|\[]+)\[(\d+)\]', x)
			]
			for x in result['categories']
		]
		if not result['categories']:
			del result['categories']

	return result


def worker(batch):
	result = []
	for block in batch:
		entry = defaultdict(list)

		for line in (x for x in map(str.strip, block.split('\n')) if x):
			sepIndex = line.find(':')

			if line.startswith('|'):
				entry['categories'].append(line)

			elif line.find('cutomer') != -1:
				review = line.split()
				entry['reviews'].append({
					'time': int(datetime.datetime.strptime(review[0], "%Y-%m-%d").timestamp()),
					'customer_id': review[2],
					'rating': int(review[4]),
					'votes': int(review[6]),
					'helpful': int(review[8])
				})

			elif sepIndex != -1:
				key, value = line[:sepIndex], line[sepIndex + 2:].strip()
				if key not in notWanted:
					entry[key] = typeDict[key](value) if key in typeDict else value

		if entry:
			result.append(cleaner(dict(entry)))

	return [json.dumps(x, ensure_ascii=False, check_circular=False) for x in result]


def parse(path: pathlib.Path):
	with lzma.open(path) as file:
		data = file.read().split('\n\n')

	with ProcessPoolExecutor() as executor:
		futures = (
			executor.submit(worker, batch)
			for batch in Oven(data, 1000)
		)
		total = len(data)
		for elem in tqdm.tqdm(
			(y for x in as_completed(futures) for y in x.result()), total=total
		):
			yield elem
