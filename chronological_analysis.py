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


def categorise_entry(title):
	tel_keys = ['Te', 'Telluride', 'telluride']
	sel_keys = ['Se', 'Selenide', 'selenide']
	sul_keys = ['S', 'Sulfide', 'sulfide']

	if any(k in title for k in tel_keys):
		return 'Te'
	elif any(k in title for k in sel_keys):
		return 'Se'
	elif any(k in title for k in sul_keys):
		return 'S'
	else:
		return None


def process_datafile(data, chronological_data):
	for entry in data:
		year = entry['Year']
		category = categorise_entry(entry['Predicted Material'])

		if category:
			if year in chronological_data[category]:
				chronological_data[category][year] += 1
			else:
				chronological_data[category][year] = 1

	return chronological_data


def compile_data():
	chronological_data = {'Te': {}, 'Se': {}, 'S':{}}

	for x in range(100):
		try:
			data = read_file('Abstract Data', 'Abstract Data {}.json'.format(x))
			chronological_data = process_datafile(data, chronological_data)
		except:
			pass
 
	z = 0
	for key, category in chronological_data.items():
		for key, year in category.items():
			z += year

	print('Total Number of Results: {}'.format(z))
	return chronological_data


def plot_graph(chronological_data):
	chrono_list = {'Te': [[], []], 'Se': [[], []], 'S':[[], []]}

	for key, category_data in chronological_data.items():
		for year, results in category_data.items():
			chrono_list[key][0].append(year)
			chrono_list[key][1].append(results)

	tellurides = chrono_list['Te']
	selenides = chrono_list['Se']
	sulfides = chrono_list['S']

	plt.plot(tellurides[0], tellurides[1], label='Tellurides')
	plt.plot(selenides[0], selenides[1], label='Selenides')
	plt.plot(sulfides[0], sulfides[1], label='Sulfides')
	plt.legend()
	plt.show()

plot_graph(compile_data())
