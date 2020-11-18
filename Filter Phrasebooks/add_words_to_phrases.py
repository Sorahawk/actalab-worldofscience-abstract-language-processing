import json

with open('phrases.json') as jsonfile:
	phrases = json.load(jsonfile)

while True:
	new_phrase = input('Phrase to add to list: ')

	if new_phrase == 'done':
		break

	phrases[new_phrase] = 1

with open('phrases.json', 'w', encoding='utf-8') as writefile:
	json.dump(phrases, writefile, ensure_ascii=False, indent=4)

print('Processing completed.')
