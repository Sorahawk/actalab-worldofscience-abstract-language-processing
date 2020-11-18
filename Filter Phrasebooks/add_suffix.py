import json

with open('suffixes.json') as jsonfile:
	suffixes = json.load(jsonfile)

while True:
	new_suffix = input('Suffix to add to list: ')

	if new_suffix == 'done':
		break

	suffixes[new_suffix] = 1

with open('suffixes.json', 'w', encoding='utf-8') as writefile:
	json.dump(suffixes, writefile, ensure_ascii=False, indent=4)

print('Processing completed.')
