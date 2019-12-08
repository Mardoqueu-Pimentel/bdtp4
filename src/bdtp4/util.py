class Oven(object):
	def __init__(self, iterable, size: int = None):
		self.iterable = iterable
		self.size = size if size else len(iterable) // 100

	def __iter__(self):
		batch = []
		for x in self.iterable:
			batch.append(x)
			if len(batch) >= self.size:
				yield batch
				batch = []
		if batch:
			yield batch
