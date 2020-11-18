import json
import bibtexparser as btp
from pathlib import Path
from chemdataextractor.doc import Paragraph, Sentence


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


# write data to output file
def write_data(consolidated_data, path):
	with open(path, 'w', encoding='utf-8') as writefile:
		json.dump(consolidated_data, writefile, ensure_ascii=False, indent=4)


def is_float(a):
	try:
		float(a)
		return True
	except ValueError:
		return False


# check if word is element name
def is_element(word):
	if word[0].upper() + word[1:].lower() in elementnames:
		return True
	else:
		return False


# check if any phrase from the phrasebook is in the title
def is_in_phrases(title):
	for p in phrases:
		if p in title:
			title = title.replace(p, ' ')
	return title


# check if any suffix is in the remaining filtered title
def has_suffix(title):
	for s in suffixes:
		if s in title:
			title = title.replace(s, '')
	return title


# check if any word in the title is in the dictionary
def is_in_dictionary(title_words):
	filtered_title = []
	for word in title_words:
		if word.lower() not in dictionary:
			filtered_title.append(word)
	return ' '.join(filtered_title)


def remove_surrounding_brackets(word):
	if word[0] == '(' and word[-1] == ')':
		word = word[1:-1]
	return word


# process savedrecs files from Web of Science
def process_savedrecs(recnumber):
	articles = []
	if recnumber == 0:
		filename = 'savedrecs.bib'
	else:
		filename = 'savedrecs ({}).bib'.format(recnumber)

	for entry in read_file('savedrecs', filename).entries:
		if 'abstract' in entry and 'doi' in entry:
			if 'eV' in entry['abstract']:
				articles.append(entry)
	return articles


def append_data(article_data, eV_data, keyword, sentence):
	article_data['eV Data'][' '.join(eV_data)] = keyword
	article_data['Abstract'].append(sentence)
	return article_data, [], True


def process_sentence(sen, article_data, valid_eV, keyword, sentence):
	# split sentence in words/tokens
	words = Sentence(sen).pos_tagged_tokens
	skip_next = 0

	for i in range(len(words)):
		if skip_next:
			skip_next -= 1
		else:
			eV_data = []

			if words[i][0] == 'eV' and is_float(words[i-1][0]):
				# look for '___ eV to ___ eV'
				if len(words) > i + 3:
					if words[i+3][0] == 'eV' and words[i+1][0] != 'and':
						x = -1

						while x <= 3:
							eV_data.append(words[i+x][0])
							x += 1

						article_data, eV_data, valid_eV = append_data(article_data, eV_data, keyword, sentence)
						skip_next = 3  # signal function to ignore next eV occurrence since already processed

				if not skip_next:
					# otherwise look for '___ eV' or '___ to ___ eV'
					if is_float(words[i-3][0]):
						x = -3
					else:
						x = -1

					while x <= 0:
						eV_data.append(words[i+x][0])
						x += 1

					article_data, eV_data, valid_eV = append_data(article_data, eV_data, keyword, sentence)

	return article_data, valid_eV


# process specific articles picked out from savedrecs
def process_articles(articles, recnumber):
	hitcount = 0
	consolidated_data = []

	for art in articles:
		doi = art['doi'].strip('{}')
		if doi not in DOI:
			article_data = {'Original Title': None, 'Predicted Material': None, 'eV Data': {}, 'Abstract': [], 'Year': None, 'DOI': None}
			valid_eV = False

			abstract = art['abstract'].strip('{}')

			# process each sentence
			for sen in Paragraph(abstract).sentences:
				sen = str(sen).replace('\n', ' ')
				sen_low = sen.lower()

				if 'activation' in sen_low:
					article_data, valid_eV = process_sentence(sen, article_data, valid_eV, 'activation', sen)
				elif 'gap' in sen_low:
					article_data, valid_eV = process_sentence(sen, article_data, valid_eV, 'gap', sen)

			if valid_eV:
				title = art['title'].strip('{}').replace('\n', ' ')

				filtered_title = is_in_dictionary(is_in_phrases(title).split())

				if filtered_title:
					if not is_element(filtered_title):
						keywords = ['sulfide', 'selenide', 'telluride']
						# remove keywords if filtered title starts with it
						filtered_title = filtered_title.split()
						
						for key in keywords:
							if filtered_title[0].lower() == key:
								filtered_title = filtered_title[1:]
								break

						# remove repeated words in title and join list back into string
						filtered_title = ' '.join([i for n, i in enumerate(filtered_title) if (i not in filtered_title[:n]) or (i == '=') or (i == 'Hydrogen')])

						# remove leading/trailing suffixes and surrounding brackets
						filtered_title = remove_surrounding_brackets(has_suffix(filtered_title))

						'''
						prediction_data = Paragraph(filtered_title).records.serialize()
						predicted_title = []

						if not prediction_data:  # if CDE cannot predict the material
							predicted_title = ['*' + filtered_title]
						else:
							for name in prediction_data:
								predicted_title.append(name['names'][0])
						'''

						article_data['Original Title'] = title
						article_data['Predicted Material'] = filtered_title
						article_data['Year'] = art['year'].strip('{}')
						article_data['DOI'] = doi

						consolidated_data.append(article_data)
						DOI.append(doi)
						hitcount += 1

	# write data file for each corresponding savedrecs file
	path = get_path('Abstract Data', 'Abstract Data {}.json'.format(recnumber))
	write_data(consolidated_data, path)
	return hitcount


filt = 'Filter Phrasebooks'
dictionary = read_file(filt, 'dictionary.json')
phrases = read_file(filt, 'phrases.json')
suffixes = read_file(filt, 'suffixes.json')
elementnames = read_file(filt, 'element_names.txt')

DOI = []
hitcount = []

for x in range(100):
	try:
		print(x)
		articles = process_savedrecs(x)
		hitcount.append(process_articles(articles, x))
	except:
		pass

write_data(DOI, get_path('Abstract Data', 'DOI.json'))

outdata = [sum(hitcount), hitcount]
print(outdata)
write_data(outdata, get_path('Abstract Data', 'Hitcount.json'))

print('Processing completed.')
