import json
import matplotlib.pyplot as plt
from pathlib import Path


def get_path(folder, filename):
	return Path(__file__).parent / '{}/{}'.format(folder, filename)


def read_file(folder, filename):
	filetype = filename.split('.')[-1]
	path = get_path(folder, filename)

	with open(path) as readfile:
		if filetype == 'txt':
			output = []
			for line in readfile:
				output.append(line.strip())
			return output
		elif filetype == 'json':
			return json.load(readfile)


def is_float(a):
	try:
		float(a)
		return True
	except ValueError:
		return False


def numeralise_eV(data):
	decimals = []

	data = data.split()
	for x in data:
		if is_float(x):
			x = float(x)

			if x < 10:
				decimals.append(x)

	if decimals:
		return sum(decimals) / len(decimals)
	else:
		return 0


def process_datafile(data, bandgaps, activation_energies):
	for entry in data:
		for eVdata, datatype in entry['eV Data'].items():
			eVdata = numeralise_eV(eVdata)

			if eVdata:
				if datatype == 'gap':
					bandgaps.append(eVdata)
				elif datatype == 'activation':
					activation_energies.append(eVdata)

	return bandgaps, activation_energies


def compile_data():
	bandgaps = []
	activation_energies = []

	for x in range(100):
		try:
			data = read_file('Abstract Data', 'Abstract Data {}.json'.format(x))
			bandgaps, activation_energies = process_datafile(data, bandgaps, activation_energies)
		except:
			pass

	return bandgaps, activation_energies


def plot_histogram(data, label):
	plt.hist(data, bins=100)
	plt.xlabel(label)
	plt.ylabel('Number of Occurrences')
	plt.show()


def main():
	bandgaps, activation_energies = compile_data()

	plot_histogram(bandgaps, 'Bandgaps')
	plot_histogram(activation_energies, 'Activation Energies')


main()
