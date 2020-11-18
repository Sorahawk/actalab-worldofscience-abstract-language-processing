import json

with open('dictionary.json') as jsonfile:
	dictionary = json.load(jsonfile)

to_delete = []

while True:
	delete_word = input('Word to remove from dictionary: ').lower()

	if delete_word == 'done':
		break
	to_delete.append(delete_word)

for key in to_delete:
	del dictionary[key]

with open('dictionary.json', 'w', encoding='utf-8') as writefile:
	json.dump(dictionary, writefile, ensure_ascii=False, indent=4)

print('Processing completed.')
