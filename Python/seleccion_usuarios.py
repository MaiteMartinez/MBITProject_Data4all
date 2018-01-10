 
import pandas as pd
import string
import re
from collections import Counter
from pandas.tools.plotting import table

import langid
from nltk.corpus import stopwords   # stopwords to detect languagecvbgf
from db_to_table import save_df
from nltk.tokenize import wordpunct_tokenize
from languages_names import to_two_letters, from_two_letters
from stop_words import my_stop_words
import matplotlib.pyplot as plt
from utilities import frequency_bar_graph, highlighted_pie_graph

# *********************************************
# RGB project colors
# *********************************************

oyellow = [1,0.835294117647059,0.133333333333333]
oblue   = [0.0352941176470588,0.450980392156863,0.541176470588235]
ogreen1 = [0.0196078431372549,0.650980392156863,0.576470588235294]
ogreen2 = [0.0588235294117647,0.737254901960784,0.568627450980392]
ored    = [0.929411764705882,0.258823529411765,0.215686274509804]


# *********************************************
# Deteccion idioma con stop words
# *********************************************



 
def get_language_likelihood(input_text):
	"""Return a dictionary of languages and their likelihood of being the 
	natural language of the input text
	""" 
	input_text = input_text.lower()
	input_words = wordpunct_tokenize(input_text)

	language_likelihood = {}
	total_matches = 0
	for language in stopwords._fileids:
		stop_w = stopwords.words(language)
		if language in my_stop_words.keys():
			stop_w += my_stop_words[language]
		language_likelihood[language] = len(set(input_words) & set(stop_w))

	return language_likelihood
 
def get_language(input_text):
	"""Return the most likely language of the given text
	""" 
	likelihoods = get_language_likelihood(input_text)
	l = sorted(likelihoods, key=likelihoods.get, reverse=True)[0]	
	return to_two_letters[l]


# *********************************************
# Deteccion idioma con langid
# *********************************************
 
def process(text, tokenizer = None, stopwords=[]):
    # Processa o texto dos tweeters: lowercase, tokenize, stopword remove, digits remove e retorna lista de strings
    text = text.lower()
    text = re.sub(r'https:.*$', ":", text) # remove a http(URL)
    tokens = tokenizer.tokenize(text)
    #for tok in tokens:
    #    if tok not in stopwords and not tok.isdigit():
    #        return [tok]
    return[tok for tok in tokens if tok not in stopwords and not tok.isdigit()]

def clean(orig_text):
    # elimina urls, menciones, etiquetas y emoticonos, en minúsculas	
	text = orig_text.lower()
	text = re.sub(r"http\S+", "", text) # remove a http(URL)
	emoji_pattern = re.compile("["
								"\U0001F600-\U0001F64F"  # emoticons
								"\U0001F300-\U0001F5FF"  # symbols & pictographs
								"\U0001F680-\U0001F6FF"  # transport & map symbols
								"\U0001F1E0-\U0001F1FF"  # flags (iOS)
								"]+", flags=re.UNICODE)
	text = emoji_pattern.sub(r'', text) # remove some emojis, probably not all
	# remove mentions and hashtags
	text = re.sub(r"@\S+", "", text) # remove mentions
	text = re.sub(r"#\S+", "", text) # remove hashtags
	# remove RT, rt
	text = re.sub(r"^rt", "", text)
	return text

def get_assigned_language(text):
	clean_text = clean(text)
	lang_o = langid.classify(text)[0]
	lang_c = langid.classify(clean_text)[0]
	diff = 0 if lang_o==lang_c else 1
	l = lang_o
	lang_stop =""
	if lang_o != lang_c:
		lang_stop = get_language(text)
		if (lang_stop in [lang_o, lang_c]):
			l = lang_o if lang_stop == lang_o else lang_c
		else:
			l = "unknown"
	return clean_text, lang_o, lang_c, lang_stop, l
	
# *********************************************
# User selection
# *********************************************

def classify_by_language(df, col_name):		

	clean_texts, lang_os, lang_cs, lang_s, assigned_langs = list(zip(*map(get_assigned_language, df[col_name])))
	
	print("Procesado el texto de "+str(len(clean_texts))+" tuits")
	diffs = [0 if x == y else 1 for x,y in zip(lang_os, lang_cs)]	
	print("Hay un "+str(round(sum(diffs)*100/len(diffs), 2))+"% de tuits con idioma diferente")
	df[col_name + "_clean_texts"] = clean_texts
	df[col_name + "_lang_os"] = lang_os
	df[col_name + "_lang_cs"] = lang_cs
	df[col_name + "_diffs"] = diffs
	df[col_name + "_lang_s"] = lang_s
	df[col_name + "_assigned_lang"] = assigned_langs
	
	return df



# *********************************************
# MAIN
# *********************************************
	
def main():
	# ********************************************
	# read the data stored form MongoDB database
	# ********************************************
	file_name = "C:/DATOS/MBIT/Proyecto/MBITProject_Data4all/Python/all_tweets.xlsx"
	df_columns = pd.read_excel(open(file_name, "rb"), sheetname = 'Sheet1', header = 0).columns
	converter = {col: str for col in df_columns} 
	df = pd.read_excel(open(file_name, "rb"), sheetname = 'Sheet1', header = 0, converters = converter)
	na_value =  "None"
	all_tweets = df.fillna(value = na_value)
	
	# ********************************************
	# classify tuit languages, and draw some graphs
	# ********************************************
	all_tuits_lang_class = classify_by_language ( all_tweets, "text")
	
	file_name = "C:/DATOS/MBIT/Proyecto/MBITProject_Data4all/Python/all_tweets_lang_class.xlsx"
	save_df(all_tuits_lang_class, file_path = file_name)
		
	toprint = 20
	# assigned languages for tuit texts
	langs = [from_two_letters[x] if x !="unknown" else x for x in all_tuits_lang_class["text_assigned_lang"]]
	frequency_bar_graph(langs, 
						toprint, 
						"Idiomas de los tuits (totales)", 
						oblue,
						figure_path="images/assigned_languages.png")
	print ( "Se han clasificado los " +str(len(langs))+" textos de los tuits en "
			+str(len(set(all_tuits_lang_class["text_assigned_lang"]))) + " idiomas diferentes")
	count = Counter(langs)
	main_l = ["spanish", "english"]
	sizes = [count[l]/len(langs) for l in main_l] +[sum(count[k] if k not in main_l else 0 for k in count.keys())/len(langs)]
	labels = main_l + ["others"]
	explode = (0.1, 0, 0)  # only "explode" the 2nd slice (i.e. 'Original')
	colors = [oblue, oyellow, ogreen1]
	file_path = "images/assigned_languages_proportions.png"
	highlighted_pie_graph(sizes, labels, explode, colors, file_path)
	print ( "En los textos de los tuits, hay un " +str(count["unknown"]/len(langs) * 100.)+" de unknowns del "
			+str(sum(count[k] if k not in main_l else 0 for k in count.keys())/len(langs)*100.) + " de others")
	
	# ********************************************
	# here classification if tuit texts are data science or not, to add to all tuits info
	# later on, this will be used to classify the users into relevant for selection process or not
	# ********************************************
	# code here, code here, code here
	
	# ********************************************
	# select relevant users (those whose tuits are classified before as data_science)
	# ********************************************
	# code here, code here, code here
	
	# ********************************************
	# classify users bio texts in person, bot, company
	# ********************************************
	
	# first remove duplicated users
	# here we take the first time that a user appears. If her/his data has changed through time, we
	# only retrieve one of the versions... no idea of which one
	unique_users = all_tuits_lang_class.groupby("user_id", as_index = False).first()
		
	unique_users_lang_class = classify_by_language ( unique_users, "user_bio")
	
	file_name = "C:/DATOS/MBIT/Proyecto/MBITProject_Data4all/Python/unique_users_lang_class.xlsx"
	save_df(unique_users_lang_class, file_path = file_name)
	
	
	# assigned languages for user bios
	langs = [from_two_letters[x] if x !="unknown" else x for x in unique_users_lang_class["user_bio_assigned_lang"]]
	frequency_bar_graph(langs, 
						toprint, 
						"Idiomas de las bios de los usuarios (totales)", 
						oblue,
						figure_path="images/user_bios_assigned_languages.png")
	print ( "Se han clasificado los " +str(len(langs))+" textos de los tuits en "
			+str(len(set(unique_users_lang_class["user_bio_assigned_lang"]))) + " idiomas diferentes")
	count = Counter(langs)
	main_l = ["spanish", "english", "unknown"]
	sizes = [count[l]/len(langs) for l in main_l] +[sum(count[k] if k not in main_l else 0 for k in count.keys())/len(langs)]
	labels = main_l + ['others']
	explode = (0.1, 0, 0, 0)  # only "explode" the 1st slice (i.e. 'Original')
	colors = [oblue, oyellow, ogreen1, ored]
	file_path = "images/user_bios_assigned_languages_proportions.png"
	highlighted_pie_graph(sizes, labels, explode, colors, file_path)	
	
	return

if __name__ == '__main__':
	try:
		main()
	except KeyboardInterrupt:
		print ('\nGoodbye! ')  