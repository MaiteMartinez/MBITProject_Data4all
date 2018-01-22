import pandas as pd
from pandas.tools.plotting import table
from pandas.io.json import json_normalize
import numpy as np
import string
import re
from collections import Counter
import unicodedata
import langid
import nltk
from nltk.corpus import stopwords   # stopwords to detect languagecvbgf
from nltk.tokenize import wordpunct_tokenize, TweetTokenizer
from utilities.languages_names import to_two_letters, from_two_letters
from utilities.stop_words import my_stop_words
import matplotlib.pyplot as plt
from utilities.functions import *
from relevance_model.Clasificacion import *


# *********************************************
# Language detection with stop words
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
# Language detection with langid
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
# Classification as person
# *********************************************

# Text to lower case, tokenize, remmove accents and "ñ"
def remove_accents(input_str):
    try:
        nfkd_form = unicodedata.normalize('NFKD', str(input_str))
        only_ascii = nfkd_form.encode('ascii', errors='ignore').decode('utf-8').replace(u'\xf1', 'n')
        text = only_ascii.lower()
    except NameError:
        pass        
    return text
# Counts the words in text tat are names included in the list nombres
def word_count(text, nombres):
	word_count = 0
	for word in text.split():
		if word in nombres:
			word_count += 1
		else:
			word_count
	return word_count
def to_str(s):
    if s is None:
        return ''
    return str(s)	
# *********************************************
# User selection
# *********************************************

def classify_by_language(df, col_name):		

	clean_texts, lang_os, lang_cs, lang_s, assigned_langs = list(zip(*map(get_assigned_language, df[col_name])))
	
	print("Procesado el texto de "+str(len(clean_texts))+" tweets")
	diffs = [0 if x == y else 1 for x,y in zip(lang_os, lang_cs)]	
	print("Hay un "+str(round(sum(diffs)*100/len(diffs), 2))+"% de tweets con idioma diferente")
	df[col_name + "_clean_texts"] = clean_texts
	df[col_name + "_lang_os"] = lang_os
	df[col_name + "_lang_cs"] = lang_cs
	df[col_name + "_diffs"] = diffs
	df[col_name + "_lang_s"] = lang_s
	df[col_name + "_assigned_lang"] = assigned_langs
	
	return df

def get_relevant_topic_tweets(tweets_texts):		
	# here Fabio's model
	return [1]*len(tweets_texts)

def get_if_person(df):	
	# remove accents from user.name and description of the user
	df.loc[:, 'user_name'] = df['user_name'].apply(remove_accents)
	df.loc[:, 'user_bio'] = df['user_bio'].apply(remove_accents)
	
	# *****************************************************
	# First criteria: we need some person  name in the user name
	# *****************************************************
	# List with people names and surnames in english and spanish
	nombres = [line.strip() for line in open('utilities/nombres.txt', 'r')]
	# pattern to check in user_name person names
	pat = '|'.join([r'\b{}\b'.format(x) for x in nombres])
	# % of words in the field user_name which are also in the list of names
	df['check_user_name'] = (df['user_name'].apply(word_count, nombres = nombres))*100/(df['user_name'].str.split().str.len())


	# *****************************************************
	# Second criteria: using bag of words with terms corresponding to
	# people and to not_people
	# *****************************************************
	# List of words in the description referring to a person and not a person.
	# The latter ones should not appear in the description if it is the 
	# description of a person
	persona = [line.strip() for line in open('utilities/term_persona.txt', 'r')]
	no_persona = [line.strip() for line in open('utilities/term_emp.txt', 'r')]

	# patterns to identify the words in the description that match some word in persona or in no_persona
	patron_2 = '|'.join([r'\b{}\b'.format(x) for x in persona]) 
	patron_3 = '|'.join([r'\b{}\b'.format(x) for x in no_persona]) 

	# New column with a 1 if any word in persona appears in the description
	# or if no words of no_persona appear in the description
	# or if no words of no_persona appear in the user name
	df["check_descrip_1"] = ((df['user_bio'].str.contains(patron_2).astype(int))| 
							(~df['user_bio'].str.contains(patron_3))|
							(~df['user_name'].str.contains(patron_3))).astype(int)

	# *****************************************************
	# Third criteria: url is a blog or a profile in linkedin
	# *****************************************************
	df['url'] = df['url'].apply(to_str)
	patron_4 = ('|'.join(['linked', 'blog']))
	df["check_url"] = df['url'].str.contains(patron_4).astype(int)

	# *****************************************************
	# Final distinction
	# *****************************************************
	# To be identified as a person, we need
	#  a 1 in the second criteria and more than a 30% of words in user name that are names
	# or that the url is a blog or a profile in linkedin
	df['is_person'] = ( ((df["check_descrip_1"] == 1) & (df["check_user_name"] >= 30))
						|(df['check_url'] == 1) ).astype(int)

	return df

def smart_remove_duplicated_users(tweets_data, relevant_fields):
	control_field = []
	for i in range(len(tweets_data[tweets_data.columns[1]])):
		cstr=""
		for f in relevant_fields:
			cstr += tweets_data[f][i]
		control_field.append(cstr)
	tweets_data["control_field"] = control_field
	clean_tweets_data = tweets_data.groupby("control_field", as_index = False).first()
	return clean_tweets_data.drop('control_field', 1)

# *********************************************
# MAIN
# *********************************************
	
def select_users(all_tweets_data):
	
	# ********************************************
	# classify tweet languages, and draw some graphs: select languages for later analysis
	# ********************************************
	all_tweets_lang_class = classify_by_language ( all_tweets_data, "text")
	
	file_name = "tables/2_1_all_tweets_text_lang_class.xlsx"
	save_df(all_tweets_lang_class, file_path = file_name)
		
	toprint = 20
	# assigned languages for tweet texts
	langs = [from_two_letters[x] if x !="unknown" else x for x in all_tweets_lang_class["text_assigned_lang"]]
	frequency_bar_graph(langs, 
						toprint, 
						"Idiomas de los tweets (totales)", 
						oblue,
						figure_path="images/assigned_languages.png")
	print ( "Se han clasificado los " +str(len(langs))+" textos de los tweets en "
			+str(len(set(all_tweets_lang_class["text_assigned_lang"]))) + " idiomas diferentes")
	count = Counter(langs)
	main_l = ["spanish", "english"]
	sizes = [count[l]/len(langs) for l in main_l] +[sum(count[k] if k not in main_l else 0 for k in count.keys())/len(langs)]
	labels = main_l + ["others"]
	explode = (0.1, 0, 0)  # only "explode" the first slice (i.e. 'Original')
	colors = [oblue, oyellow, ogreen1]
	file_path = "images/assigned_languages_proportions.png"
	highlighted_pie_graph(sizes, labels, explode, colors, file_path)
	print ( "En los textos de los tweets, hay un " +str(count["unknown"]/len(langs) * 100.)+" de unknowns del "
			+str(sum(count[k] if k not in main_l else 0 for k in count.keys())/len(langs)*100.) + " de others")
	
	# ********************************************
	# classify users bio texts by language and draw some graphs: select languages for later analysis
	# ********************************************	
	# first remove duplicated users
	# here we take the first time that a user appears. If her/his data has changed through time, we
	# only retrieve one of the versions... no idea of which one
	unique_users = all_tweets_lang_class.groupby("user_id", as_index = False).first()
		
	unique_users_lang_class = classify_by_language (unique_users, "user_bio")
	
	file_name = "tables/2_2_unique_users_bios_text_lang_class.xlsx"
	save_df(unique_users_lang_class, file_path = file_name)
	
	
	# assigned languages for user bios
	langs = [from_two_letters[x] if x !="unknown" else x for x in unique_users_lang_class["user_bio_assigned_lang"]]
	frequency_bar_graph(langs, 
						toprint, 
						"Idiomas de las bios de los usuarios (totales)", 
						oblue,
						figure_path="images/user_bios_assigned_languages.png")
	print ( "Se han clasificado los " +str(len(langs))+" textos de los tweets en "
			+str(len(set(unique_users_lang_class["user_bio_assigned_lang"]))) + " idiomas diferentes")
	count = Counter(langs)
	main_l = ["spanish", "english", "unknown"]
	sizes = [count[l]/len(langs) for l in main_l] +[sum(count[k] if k not in main_l else 0 for k in count.keys())/len(langs)]
	labels = main_l + ['others']
	explode = (0.1, 0, 0, 0)  # only "explode" the 1st slice (i.e. 'Original')
	colors = [oblue, oyellow, ogreen1, ored]
	file_path = "images/user_bios_assigned_languages_proportions.png"
	highlighted_pie_graph(sizes, labels, explode, colors, file_path)	

	# ********************************************
	# classification if tweet texts topics are relevant for the selection process or not
	# ********************************************
	
	# all_tweets_data["is_relevant_text"] = get_relevant_topic_tweets(all_tweets_data["text"])
	arquivo = "C:\\DATOS\\MBIT\\Proyecto\\MBITProject_Data4all\\Python\\relevance_model\\modelo_nb.sav"
	all_tweets_clean_texts = pd.DataFrame()
	all_tweets_clean_texts["text"] = all_tweets_data["text"].apply(remove_stopwords)
	all_tweets_data["is_relevant_text"] = procesando_modelo(arquivo,all_tweets_clean_texts)
	file_name = "tables/2_3_relevant_all_twets_data.xlsx"
	save_df(all_tweets_data, file_path = file_name)

	# only relevant tweets data remain
	relevant_twets_data = all_tweets_data[all_tweets_data["is_relevant_text"]==1]
	file_name = "tables/2_4_relevant_twets_data.xlsx"
	save_df(relevant_twets_data, file_path = file_name)

	# draw some graphs for the memoir and retrieve some numbers
	number_of_tweets = len(all_tweets_data["user_id"])
	number_of_relevant_tweets = len(relevant_twets_data["user_id"])
	p = number_of_relevant_tweets/number_of_tweets
	sizes = [p, 1.-p]
	labels = ["relevant", "not relevant"]
	explode = (0.1, 0)
	colors = [oblue, oyellow]
	file_path = "images/relevant_tweets_proportion.png"
	highlighted_pie_graph(sizes, labels, explode, colors, file_path)
	print("From "+str(number_of_tweets)+" tweets analized, we've found "+str(number_of_tweets)+
			" relevant ones, that represent a "+str(round(p*100.,2))+"% of total")

	# ********************************************
	# remove users with the same user id, url, user name and user bio
	# ********************************************
	# first we remove duplicate users, taking care that the url, user name and user description are
	# the same (had not changed throughout the downloaded timeline)
	equal_fields = ["user_id", "url", "user_name", "user_bio"]	

	# this two codes do the same. but with drop_duplicates some warning created by misleading
	# assignments in subsequent code arise.Thus we need a deepcopy.
	# unique_users = smart_remove_duplicated_users(relevant_twets_data, equal_fields)
	from copy import deepcopy
	unique_users = deepcopy(relevant_twets_data.drop_duplicates(subset = equal_fields))
	print("We had " + str(len(relevant_twets_data["user_id"]))+ " relevant tweets, and from those we extract " 
			+str(len(unique_users["user_id"]))+" relevant users whose data "+str(equal_fields)+
			" is not duplicated ")

	# ********************************************
	# check which ones are persons
	# ********************************************
	relevant_users_data = get_if_person(unique_users)	
	file_name = "tables/2_5_relevant_twets_data_is_person.xlsx"
	save_df(relevant_users_data, file_path = file_name)

	# ********************************************
	# only users identified as people remain
	# ********************************************
	person_users = relevant_users_data[relevant_users_data["is_person"] == 1]
	
	# draw some graphs for the memoir and retrieve some numbers
	number_of_users = len(relevant_users_data["user_id"])
	number_of_person_users = len(person_users["user_id"])
	p = number_of_person_users/number_of_users
	sizes = [p, 1.-p]
	labels = ["persons", "not persons"]
	explode = (0.1, 0)
	colors = [oblue, oyellow]
	file_path = "images/relevant_users_proportion.png"
	highlighted_pie_graph(sizes, labels, explode, colors, file_path)
	print("From "+str(number_of_users)+" users analized, we've found "+str(number_of_person_users)+
			" classified as persons, that represent a "+str(round(p*100.,2))+"% of total")

	# ********************************************
	# remove duplicated persons
	# ********************************************
	unique_person_users = person_users.groupby("user_id", as_index = False).first()
	number_of_unique_id = len(unique_person_users["user_id"])
	print("From "+str(number_of_person_users)+" classified as persons, there are "
			+str(number_of_unique_id)+ " unique user_id, that is, there were "
			+str(number_of_person_users - number_of_unique_id)+
			"users with different user name, url or description in the downloaded data")
	
	return unique_person_users[["user_id","user_name", "user_screenname"]]

if __name__ == '__main__':
	try:
		# ********************************************
		# read the data stored form MongoDB database
		# ********************************************
		file_path = "tables/2_all_tweets.xlsx"
		all_tweets_data = read_df(file_path)
		selected_users = select_users(all_tweets_data)
		file_path = "tables/3_selected_users.xlsx"
		save_df(selected_users, file_path = file_path)
	except KeyboardInterrupt:
		print ('\nGoodbye! ')  