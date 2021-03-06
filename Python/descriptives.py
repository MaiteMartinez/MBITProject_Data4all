import nltk
# nltk.download()
 
import numpy as np
import pandas as pd
import tweepy
import json
import pymongo
import string
import re
from nltk.tokenize import TweetTokenizer
from nltk.corpus import stopwords
from collections import Counter
import datetime
from OpenMongoDB import MongoDBConnection
# from scipy.misc.pilutil import imread
from imageio import imread
from random import uniform
from pandas.tools.plotting import table
  
from wordcloud import WordCloud, STOPWORDS  # package used to generate word clouds
from PIL import Image
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
from pylab import rcParams
import time
import matplotlib.dates as mdates
from copy import deepcopy
from utilities.functions import *

# *********************************************
# duplicated tuits?
# *********************************************

def are_there_duplicated_tuits(twitter_cursor):
	us = []
	for t in twitter_cursor:
		us.append(t["id_str"])
	print ("Hay "+str(len(us))+" en la base de datos, de los cuales "+str(len(set(us)))+" son únicos")
	print ("hay "+str(len(us) - len(set(us)))+" repetidos")
	return len(us),len(set(us))


# *********************************************
# Word cloud functions
# *********************************************
 
def process(text, tokenizer = TweetTokenizer(), stopwords=[]):
    # Processa o texto dos tweeters: lowercase, tokenize, stopword remove, digits remove e retorna lista de strings
    text = text.lower()
    text = re.sub(r'https:.*$', ":", text) # remove a http(URL)
    tokens = tokenizer.tokenize(text)
    #for tok in tokens:
    #    if tok not in stopwords and not tok.isdigit():
    #        return [tok]
    return[tok for tok in tokens if tok not in stopwords and not tok.isdigit()]

def random_color_func_twitter(word=None, font_size=None, position=None,  orientation=None, font_path=None, random_state=None):
	rgb = [85.0, 172.0, 238.0] # azul de twitter en rgb
	h,s,l = get_h_s_l_from_rgb(rgb)
	return "hsl({}, {}%, {}%)".format(h,s,l)

def random_color_func_bios(word=None, font_size=None, position=None,  orientation=None, font_path=None, random_state=None):
	rgb = [x*255. for x in oblue] # azul del proyecto en rgb
	h,s,l = get_h_s_l_from_rgb(rgb)
	return "hsl({}, {}%, {}%)".format(h,s,l)


def random_color_func_project_colors(word=None, font_size=None, position=None,  orientation=None, font_path=None, random_state=None):
	project_colors =[oyellow, oblue, ogreen1, ogreen2, ored]
	rgb_vector = [[x*255. for x in c] for c in project_colors] 
	hsl_vector = [get_h_s_l_from_rgb(rgb) for rgb in rgb_vector]
	h,s,l = hsl_vector[np.random.random_integers(0, high=len(hsl_vector)-1)]
	return "hsl({}, {}%, {}%)".format(h,s,l)


def get_h_s_l_from_rgb(rgb):
	rgb = [x/255. for x in rgb]
	mn = min(rgb)
	mx = max(rgb)
	# lumnance
	l = (mn+mx)/2.0
	# saturation
	s = 0.0
	if (l>mn) and (l<0.5): s =  (mx-mn)/(mn+mx)
	if (l>mn) and (l>=0.5): s =  (mx-mn)/(2.0-mn-mx)
	# hue
	h = 0.0
	if (mx == rgb[0]): h =(rgb[1]-rgb[2])/(mx-mn)	
	elif (mx == rgb[2]): h = 2.0 + (rgb[2]-rgb[0])/(mx-mn)
	else:  h = 4.0 + (rgb[0]-rgb[1])/(mx-mn)
	# h = int(360.0 * 85.0 / 255.0)
    # s = int(100.0 * 172.0 / 255.0)
    # l = int(100.0 * float(random_state.randint(60, 120)) / 255.0) #238
	# print (h,s,l)	
	h = int(60*h)
	s = int(100*s) 
	l = int(100*l*uniform(60,95)/100.)
	return h, s, l
	



def show_words_cloud(text,
					font_path="fonts/CabinSketch-Regular.ttf",
					original_figure_path = "images/originals/twitter_image.png",
					figure_path = "images/twitter_worldcloud.png",
					color_function = None):
	plt.clf()
	if original_figure_path is not None:
		twitter_mask = imread(original_figure_path)
		max_words = 3000
	else:
		twitter_mask = None
		max_words = 8000
	wcloud = WordCloud(font_path = font_path,
						background_color = None, 
						mask = twitter_mask, 
						mode = "RGBA",
						max_words = max_words,
						color_func=color_function,
						stopwords=STOPWORDS.add("RT"),
						max_font_size = 60,
						relative_scaling=1)
	wcloud.generate(text)
	plt.figure()
	plt.imshow(wcloud)
	plt.tight_layout()
	plt.axis("off")
	plt.savefig(figure_path, bbox_inches='tight')

def create_word_cloud(tweet_cursor,
					fields = ["text"],
					font_path="fonts/CabinSketch-Regular.ttf",
					original_figure_path = "images/originals/twitter_image.png",
					figure_path = "images/twitter_worldcloud.png",
					color_function = None):
		
	tweet_tokenizer = TweetTokenizer()
	punct = list(string.punctuation)
	stopword_list = stopwords.words('spanish') \
					+ stopwords.words('english') \
					+ punct  \
					+ ['rt','via','...','¿','si','cómo','“','”','¡','q','esas','cosas','https']
	tf = Counter()

	t_count = 0
	for docto in tweet_cursor:		
		obj = docto
		for f in fields: obj = obj[f]
		try:
			tokens = process(text = obj,
							 tokenizer = tweet_tokenizer,
							 stopwords=stopword_list)
			tf.update(tokens)	
			t_count +=1	
		except:
			pass
			
		# if(t_count > 100): break
	print("La word cloud ha procesado el texto de "+str(t_count)+" tuits")
	word_lista = ' '
	for tag, count in tf.most_common(500):
		# try:
			# print("{}:{}".format(tag,count))
		# except:
			# pass
		word_lista = word_lista+','+tag
	show_words_cloud(word_lista,font_path, original_figure_path, figure_path, color_function)

# *********************************************
# retwitted proportion. original tuits,
# true retuits and retuits without information of retweeted status or quoted status
# *********************************************
def create_retweeted_proportion_graph(twitter_cursor, figure_path = "retweeted_proportions.png"):
	original = 0
	retweets = 0
	weird_retweets = 0
	ct = 0
	for t in twitter_cursor:
		if t["text"].startswith("RT"):
			try:
				try:
					t["retweeted_status"]
					retweets += 1
				except:
					t["quoted_status"]
					retweets += 1
			except:
				weird_retweets += 1	
		else:
			original += 1
		ct += 1
	print("Tenemos "+str(ct)+" tuits, de los cuales hay: ")
	print(str(original)+ " originales")
	print(str(retweets)+ " retweets")
	print(str(weird_retweets)+ " weird_retweets (aquellos que empiezan por RT y no tienen info de lo retuiteado)")
	print ("La suma da "+str(retweets+weird_retweets+original))
	sizes = [original, retweets, weird_retweets]
	labels = 'Original', 'Retweets', 'Weird retweets' 
	explode = (0.1, 0, 0)  # only "explode" the 2nd slice (i.e. 'Original')
	colors = [oyellow, oblue, ogreen1]

	highlighted_pie_graph(sizes, labels, explode, colors, figure_path)

# *********************************************
# number of twits per day
# *********************************************

def create_time_graph(twitter_cursor, figure_path = "time_histogram.png"):	
	ts = [time.strftime('%Y-%m-%d %H:%M:%S', 
						time.strptime(t["created_at"],'%a %b %d %H:%M:%S +0000 %Y')) 
						for t in twitter_cursor]
	ts2 = [datetime.datetime.strptime(x, '%Y-%m-%d %H:%M:%S').date() for x in ts]
	new_df = pd.DataFrame(pd.to_datetime(ts2), columns=['dates'])
	plt.clf()
	new_df.groupby((new_df['dates'].dt.year, 
					new_df['dates'].dt.month,
					new_df['dates'].dt.day)).count().plot(kind="bar", 
														color = [oblue])
	L = plt.legend()
	L.get_texts()[0].set_text('Numero de tuits')	
	plt.xticks(rotation=90)
	plt.xlabel("")
	plt.tight_layout()
	plt.savefig(figure_path)

# *********************************************
# number of retwits. discarding weird retuits
# *********************************************

def create_times_retweeted_graph(RT_twitter_cursor, figure_path = "images/retweeted_graph.png"):
	# this twitter cursor should contain only those tuits starting by RT
	# guardamos, para cada tuit que ha sido retuiteado, el número de retuits que lleva contabilizados
	id_str = []
	n_retweets = []
	host_ids = []
	for t in RT_twitter_cursor:
		try:
			try:
				id_str.append(t["retweeted_status"]["id_str"])
				n_retweets.append(t["retweeted_status"]["retweet_count"])
				host_ids.append(t["id_str"])
			except:
				id_str.append(t["quoted_status"]["id_str"])
				n_retweets.append(t["quoted_status"]["retweet_count"])
				host_ids.append(t["id_str"])
		except:
			pass
	new_df = pd.DataFrame({'id_str':id_str, 'n_retweets':n_retweets})

	print ("Tenemos " + str(len(id_str)) + " tuits que son retuits genuinos, con info de lo retuiteado")
	print ("En estos tuits se han retuiteado " + str(len(set(id_str))) + " tuits distintos")
	
	explore = 5
	
	sorted_retweets = deepcopy(n_retweets)
	sorted_retweets.sort(reverse=True)
	for i in range(explore):
		times = sorted_retweets[i]
		print ("El tuit numero "+str(i+1)+" por numero de retuits o citas,")
		print ("ha sido retuiteado o citado "+ str(times) + " veces")
		id = id_str[n_retweets.index(times)]
		host_id = host_ids[n_retweets.index(times)]
		print ("El id de este tuit es " + id+" y aparece en el tuit " + host_id)

	plt.clf()

	# para cada tuit id, nos quedamos con el máximo de veces que se ha retuiteado 
	# de las que hemos contabilizado
	new_df2 = new_df.groupby(new_df['id_str'], as_index = False).max()
	new_df2.plot(kind="hist", color = [oblue], legend = None, bins = 20)
	plt.xticks(rotation=90)
	plt.xlabel("Numero de retuits")
	plt.ylabel("Numero de tuits")
	plt.tight_layout()
	plt.savefig(figure_path.replace(".png", "_hist.png"))
	
	
	plt.clf()
	new_df3 = new_df2.groupby(new_df2['n_retweets'], as_index = False).count()
	plt.scatter(x= new_df3["n_retweets"], y=new_df3["id_str"], color = [oblue])
	# L = plt.legend()
	# L.get_texts()[0].set_text('Numero de tuits')	
	plt.xticks(rotation=90)
	plt.xlabel("Numero de retuits")
	plt.ylabel("Numero de tuits")
	plt.tight_layout()
	plt.savefig(figure_path.replace(".png", "_scatter.png"))

# *********************************************
# number of tuits vs number of users and distinct users
# *********************************************
def create_tuits_distict_users_relations_graph(twitter_cursor, figure_path = "images/tuits_users_graph.png"):
	ts = []
	users = []
	for t in twitter_cursor:
		ts.append(time.strftime('%Y-%m-%d %H:%M:%S', 
				time.strptime(t["created_at"],'%a %b %d %H:%M:%S +0000 %Y')))
		users.append(t["user"]["id_str"])
	print ("Tenemos "+str(len(set(users)))+" usuarios distintos")
	list1, list2 = zip(*sorted(zip(ts, users)))
	distinct_users = []
	for i in range(1,len(list1)):
		distinct_users.append(len(set(users[:i])))
	
	plt.clf()	
	plt.scatter(x= range(1,len(list1)), y=distinct_users, color = [oblue])
	# L = plt.legend()
	# L.get_texts()[0].set_text('Numero de tuits')	
	plt.xticks(rotation=90)
	plt.xlabel("Numero de tuits")
	plt.ylabel("Numero de usuarios distintos")
	plt.tight_layout()
	plt.savefig(figure_path)

# *********************************************
# number of tuits by user
# *********************************************

def create_tuits_by_user_graph(twitter_cursor, figure_path = "images/tuits_by_user_graph.png"):
	users=[]
	tweet_id = []
	user_names = []
	user_screen_names = []
	for t in twitter_cursor:
		users.append(t["user"]["id_str"])
		tweet_id.append(t["id_str"])
		user_names.append(t["user"]["name"])
		user_screen_names.append(t["user"]["screen_name"])
	new_df = pd.DataFrame({'users':users,'tweet_id':tweet_id })
	plt.clf()
	# para cada user id, nos quedamos con el número de tuits suyos que tenemos
	new_df2 = new_df.groupby(new_df['users'], as_index = False).count()
	new_df2.plot(kind="hist", color = [oblue], legend = None, bins = 20)
	plt.xticks(rotation=90)
	plt.xlabel("Numero de tuits")
	plt.ylabel("Numero de usuarios")
	plt.tight_layout()
	plt.savefig(figure_path)

	plt.clf()
	new_df3 = new_df2.groupby(new_df2['tweet_id'], as_index = False).count()
	plt.scatter(x= new_df3["tweet_id"], y=new_df3["users"], color = [oblue])
	plt.xticks(rotation=90)
	plt.xlabel("Numero de tuits")
	plt.ylabel("Numero de usuarios")
	plt.tight_layout()
	plt.savefig(figure_path.replace(".png", "_scatter.png"))

	explore = 5	
	n_tuits = [x for x in new_df2["tweet_id"]]
	users_id = [x for x in new_df2["users"]]
	list1, list2, = zip(*sorted(zip(n_tuits, users_id), reverse=True))
	for i in range(explore):
		print ("El usuario numero "+str(i+1)+" por numero de tuits ha publicado" + str(list1[i]) + " tuits")
		print ("El id de este usuario es " + str(list2[i]))

	frequency_bar_graph(user_names, 20, "", oyellow, figure_path.replace(".png", "_bargraph.png"))
	

# *********************************************
# number of tuits with localization data
# *********************************************
def create_geolocalized_graph(twitter_cursor, figure_path = "images/geolocalized_proportions.png"):
	localized = []
	ct = 0
	for t in twitter_cursor:
		if t["place"] is not None:
			localized.append(t["id_str"])
		ct +=1
	sizes = [len(localized), ct-len(localized)]
	labels = 'Con localización', 'Sin localización' 
	explode = (0.1, 0)  # only "explode" the 1st slice (i.e. 'con')
	colors = [oyellow, oblue]

	highlighted_pie_graph(sizes, labels, explode, colors, figure_path)

# *********************************************
# hashtags info
# *********************************************

def hashtags_cloud(hashtags_vector, figure_path):
	h = [p for p in set(hashtags_vector)]
	text = h[0]
	for i in range(1,len(h)):
		text += " "+h[i]
	img_mask = imread("images/originals/hash2.png")
	wcloud = WordCloud(background_color = None, 
						max_words = 3000,
						max_font_size = 60,
						mask = img_mask,
						mode = "RGBA",
						relative_scaling=1,
						color_func = random_color_func_project_colors)
	wcloud.generate(text)
	plt.figure()
	plt.imshow(wcloud)
	plt.tight_layout()
	plt.axis("off")
	plt.savefig(figure_path, bbox_inches='tight')


def create_hashtags_info(twitter_cursor, figure_path = "images/hashtags.png"):
	hashtags_host = []
	hashtags_total = []
	for t in twitter_cursor:		
		try:
			host_hashtag_obj = t['extended_tweet']['entities']['hashtags']
		except:
			host_hashtag_obj = t['entities']['hashtags']
		hashtags_host.extend([d["text"] for d in host_hashtag_obj])
		hashtags_total.extend([d["text"] for d in host_hashtag_obj])

		# hashtags of quoted tuit, if any
		quoted_hashtag_obj = []
		try:
			quoted_hashtag_obj = t['quoted_status']['extended_tweet']['entities']['hashtags']
		except:
			try:
				quoted_hashtag_obj = t['quoted_status']['entities']['hashtags']
			except:
				pass
		hashtags_total.extend([d["text"] for d in quoted_hashtag_obj])

		# hashtags of retweeted tuit, if any
		rt_hashtag_obj = []
		try:
			rt_hashtag_obj = t['retweeted_status']['extended_tweet']['entities']['hashtags']
		except:
			try:
				rt_hashtag_obj = t['retweeted_status']['entities']['hashtags']
			except:
				pass
		hashtags_total.extend([d["text"] for d in rt_hashtag_obj])

	hashtags_cloud(hashtags_total, figure_path.replace(".png", "_total_wordcloud.png"))
	hashtags_cloud(hashtags_host, figure_path.replace(".png", "_host_wordcloud.png"))
	toprint = 20
	frequency_bar_graph(hashtags_total, toprint, "Totales", oyellow, figure_path.replace(".png", "_total_occurs.png"))
	frequency_bar_graph(hashtags_host, toprint, "Tuits principales", oyellow, figure_path.replace(".png", "_host_occurs.png"))

# *********************************************
# source info
# *********************************************
def clean_source(source):
	value = re.findall(pattern="<[^>]+>([^<]+)</a>", string=source)
	if len(value) > 0:
		return value[0]
	else:
		return ""
	return source

def create_source_info(twitter_cursor, figure_path = "images/source.png"):
	source_host = []
	source_total = []
	for t in twitter_cursor:		
		source_host.append(clean_source(t['source']))
		source_total.append(clean_source(t['source']))
		
		# source of quoted tuit, if any
		quoted_source = None
		try:
			quoted_source = t['quoted_status']["source"]
		except:
			pass
		if quoted_source is not None:
			source_total.append(clean_source(quoted_source))

		# source of retweeted tuit, if any
		retweeted_source = None
		try:
			retweeted_source = t['retweeted_status']["source"]
		except:
			pass
		if retweeted_source is not None:
			source_total.append(clean_source(retweeted_source))

	toprint = 20
	print (len(source_total))
	print (len(source_host))
	frequency_bar_graph(source_total, toprint, "Totales", oyellow, figure_path.replace(".png", "_total.png"))
	frequency_bar_graph(source_host, toprint, "Tuits principales", oyellow, figure_path.replace(".png", "_host.png"))

	
	person_sources = ["twitter web client", "twitter for android", "twitter for iphone", "twitter for ipad", "twitter lite", "tweet old post", "voicestorm"]
	count = Counter(source_host)
	p = sum(count[k] if k.lower() in person_sources else 0 for k in count.keys())/len(source_host)
	sizes = [p, 1.-p]
	labels = ["possible person", "others"]
	explode = (0.1, 0) 
	colors = [oblue, oyellow]
	highlighted_pie_graph(sizes, labels, explode, colors, figure_path.replace(".png", "_people_percentage_host.png"))
	count = Counter(source_total)
	p = sum(count[k] if k.lower() in person_sources else 0 for k in count.keys())/len(source_total)
	sizes = [p, 1.-p]
	highlighted_pie_graph(sizes, labels, explode, colors, figure_path.replace(".png", "_people_percentage_total.png"))

	

# *********************************************
# MAIN ::: run_descriptives
# *********************************************

def run_descriptives(data_base_name, set_up_path):
	#MongoDB connection
	collection_name = "col_" + data_base_name
	mongo_conn = MongoDBConnection(set_up_path)
	db = mongo_conn.client[data_base_name]
	collection = db[collection_name]

	total_tuits, unique_tuits = are_there_duplicated_tuits(collection.find())

	# # tuits text word cloud
	create_word_cloud(collection.find(),
					font_path="fonts/CabinSketch-Regular.ttf",
					original_figure_path = "images/originals/twitter_image.png",
					figure_path = "images/twitter_worldcloud.png",
					color_function = random_color_func_twitter)
	create_retweeted_proportion_graph(collection.find(), figure_path = "images/retweeted_proportions.png")
	create_time_graph(collection.find(), figure_path = "images/time_histogram.png")

	# for those twits that are a retwit of another one, look for the number of times that twit has been
	# retwitted
	twitter_cursor = collection.find({"text": {'$regex' : '^RT'}})
	create_times_retweeted_graph(twitter_cursor, figure_path = "images/retweeted_graph.png")
	create_tuits_distict_users_relations_graph(collection.find(), figure_path = "images/tuits_users_graph.png")
	create_tuits_by_user_graph(collection.find(), figure_path = "images/tuits_by_user_graph.png")
	create_geolocalized_graph(collection.find(), figure_path = "images/geolocalized_proportions.png")
	create_hashtags_info(collection.find(), figure_path = "images/hashtags.png")

	# # wordcloud for users descriptions with a figure shape
	create_word_cloud(collection.find(),
					fields = ["user", "description"],
					font_path="fonts/CabinSketch-Regular.ttf",
					original_figure_path = "images/originals/two_people.jpg",
					figure_path = "images/bios_worldcloud.png",
					color_function = random_color_func_project_colors)
	# square wordcloud for users descriptions
	create_word_cloud(collection.find(),
					fields = ["user", "description"],
					font_path="fonts/MiriamLibre-Regular.ttf",
					original_figure_path = None,
					figure_path = "images/bios_worldcloud2.png",
					color_function = random_color_func_project_colors)
	
	create_source_info(collection.find(), figure_path = "images/sources.png")

if __name__ == '__main__':
	try:
		print("%%%%%%%%%%%%%%%   Starting task at "+str(datetime.datetime.now()))
		data_base_name = "query1_spanish_stream"
		set_up_path = "keys/set_up.py"
		run_descriptives(data_base_name, set_up_path)
	except KeyboardInterrupt:
		print ('\nGoodbye! ')  