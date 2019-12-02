def parse(filename):
	IGNORE_FIELDS = ['Total items', 'reviews']
	f = open(filename, 'r', encoding='utf-8')
	entry = {}
	categories = []
	reviews = []
	similar_items = []

	for line in f:
		line = line.strip()
		colonPos = line.find(':')

		if line.startswith("Id"):
			if reviews:
				entry["reviews"] = reviews
			if categories:
				entry["categories"] = categories
			yield entry
			entry = {}
			categories = []
			reviews = []
			rest = line[colonPos + 2:]
			entry["id"] = rest.strip().encode('utf8', 'ignore')
		#             entry["id"] = unicode(rest.strip(), errors='ignore')

		elif line.startswith("similar"):
			similar_items = line.split()[2:]
			entry['similar_items'] = similar_items

		# "cutomer" is typo of "customer" in original data
		elif line.find("cutomer:") != -1:
			review_info = line.split()
			reviews.append({'customer_id': review_info[2],
											'rating': int(review_info[4]),
											'votes': int(review_info[6]),
											'helpful': int(review_info[8])})

		elif line.startswith("|"):
			categories.append(line)

		elif colonPos != -1:
			eName = line[:colonPos]
			rest = line[colonPos + 2:]

			if not eName in IGNORE_FIELDS:
				entry[eName] = rest.strip().encode('utf8', 'ignore')
	#                 entry[eName] = unicode(rest.strip(), errors='ignore')

	if reviews:
		entry["reviews"] = reviews
	if categories:
		entry["categories"] = categories

	yield entry
