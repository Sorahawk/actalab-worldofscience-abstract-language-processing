import copy
import json
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
		elif filetype == 'bib':
			return btp.load(readfile)


def write_data(consolidated_data, path):
	with open(path, 'w', encoding='utf-8') as writefile:
		json.dump(consolidated_data, writefile, ensure_ascii=False, indent=4)


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


def process_datafile(data, chalcogenides, eV_data, eV_hitcount):
	for entry in data:
		append_entry = False
		category = categorise_entry(entry['Predicted Material'])

		if category:
			for data, datatype in entry['eV Data'].items():
				data = numeralise_eV(data)

				if data:
					append_entry = True
					eV_data[category][datatype] += data
					eV_hitcount[category][datatype] += 1

			if append_entry:
				chalcogenides[category].append(entry)

	return chalcogenides, eV_data, eV_hitcount


def main():
	chalcogenides = {'Te': [], 'Se': [], 'S': []}
	eV_data = {'Te': {}, 'Se': {}, 'S': {}}
	for category in eV_data:
		eV_data[category]['gap'] = 0
		eV_data[category]['activation'] = 0
	eV_hitcount = copy.deepcopy(eV_data)

	for x in range(100):
		try:
			data = read_file('Abstract Data', 'Abstract Data {}.json'.format(x))
			chalcogenides, eV_data, eV_hitcount = process_datafile(data, chalcogenides, eV_data, eV_hitcount)
		except:
			pass

	for key, value in chalcogenides.items():
		write_data(value, get_path('Chalcogenides', '{}.json'.format(key)))

	outdata = []
	for key, value in eV_data.items():
		material_outdata = {}
		material_outdata['Material'] = key
		material_outdata['Number of Articles'] = len(chalcogenides[key])
		material_outdata['Number of Results'] = 'Bandgap: {}, Activation Energy: {}'.format(eV_hitcount[key]['gap'], eV_hitcount[key]['activation'])
		material_outdata['Average Bandgap'] = value['gap'] / eV_hitcount[key]['gap']
		material_outdata['Average Activation Energy'] = value['activation'] / eV_hitcount[key]['activation']
		outdata.append(material_outdata)
		print(material_outdata)

	write_data(outdata, get_path('Chalcogenides', 'Results.json'))


main()
