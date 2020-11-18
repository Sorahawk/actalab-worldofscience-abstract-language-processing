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


def process_datafile(data, compiled_data):
	for article in data:
		i = 0
		for eVvalue, datatype in article['eV Data'].items():
			if datatype == 'gap':
				eVproperty = 'Bandgap'
			elif datatype == 'activation':
				eVproperty = 'Activation Energy'

			article_data = {'material': article['Predicted Material'], 'property': eVproperty, 'propertyVal': eVvalue, 'sentence': article['Abstract'][i], 'year': article['Year'], 'DOI': article['DOI']}

			compiled_data.append(article_data)
			i += 1

	return compiled_data


def main():
	compiled_data = []

	for x in range(100):
		try:
			data = read_file('Abstract Data', 'Abstract Data {}.json'.format(x))
			compiled_data = process_datafile(data, compiled_data)
		except:
			pass

	write_data(compiled_data, get_path('Prepared Data', 'Prepared Data.json'))


main()
print('Processing completed.')
