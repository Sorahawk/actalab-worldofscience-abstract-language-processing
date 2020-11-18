import json

with open('dictionary.json') as jsonfile:
	dictionary = json.load(jsonfile)

while True:
	new_word = input('Word to add to dictionary: ').lower()

	if new_word == 'done':
		break

	dictionary[new_word] = 1

with open('dictionary.json', 'w', encoding='utf-8') as writefile:
	json.dump(dictionary, writefile, ensure_ascii=False, indent=4)

print('Processing completed.')
