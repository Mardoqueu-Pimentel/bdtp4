#!/usr/bin/env python
# -*- coding: utf-8 -*-
import configparser
import lzma
import pathlib
import subprocess

from bdtp4.parallelParser import parse


def main(*args, config, **kwargs):
	inputFile = config['preprocess']['amazon-meta']
	dataDir = config['bdtp4']['data-dir']

	dataDir = pathlib.Path(dataDir)
	dataDir.mkdir(exist_ok=True)
	outputFile = dataDir / 'dataset.json'

	with lzma.open(outputFile) as file:
		for prod in parse(pathlib.Path(inputFile)):
			print(prod, file=file)

	subprocess.run(['xz', '-z9evv', '--threads=0', outputFile])


def run():
	config = configparser.ConfigParser()
	config.read('bdtp4.config')
	main(config=config)


if __name__ == '__main__':
	run()
