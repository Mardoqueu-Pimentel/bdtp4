import datetime


def parse(filename):
	IGNORE_FIELDS = ['Total items', 'reviews']
	entry = {}
	categories = []
	reviews = []

	with open(filename) as file:

		for line in file:
			line = line.strip()
			colonPos = line.find(':')

			if line.startswith('Id'):
				if reviews:
					entry['reviews'] = reviews
				if categories:
					entry['categories'] = categories
				yield entry
				entry = {}
				categories = []
				reviews = []
				rest = line[colonPos + 2:]
				entry['id'] = rest.strip()

			elif line.startswith('similar'):
				similar_items = line.split()[2:]
				entry['similar'] = similar_items

			elif line.find('cutomer:') != -1:
				review_info = line.split()
				reviews.append({
					'time': datetime.datetime.strptime(review_info[0], "%Y-%m-%d").timestamp(),
					'customer_id': review_info[2],
					'rating': int(review_info[4]),
					'votes': int(review_info[6]),
					'helpful': int(review_info[8])
				})

			elif line.startswith('|'):
				categories.append(line)

			elif colonPos != -1:
				eName = line[:colonPos]
				rest = line[colonPos + 2:]

				if eName not in IGNORE_FIELDS:
					entry[eName] = rest.strip()

	if reviews:
		entry['reviews'] = reviews
	if categories:
		entry['categories'] = categories

	yield entry
