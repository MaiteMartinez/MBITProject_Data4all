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
from scipy.misc import imread
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

# *********************************************
# RGB project colors
# *********************************************

oyellow = [1,0.835294117647059,0.133333333333333]
oblue   = [0.0352941176470588,0.450980392156863,0.541176470588235]
ogreen1 = [0.0196078431372549,0.650980392156863,0.576470588235294]
ogreen2 = [0.0588235294117647,0.737254901960784,0.568627450980392]
ored    = [0.929411764705882,0.258823529411765,0.215686274509804]

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
	
	return "hsl({}, {}%, {}%)".format(h,s,l)


def show_words_cloud(text,
					font_path="fonts/CabinSketch-Regular.ttf",
					original_figure_path = "images/originals/twitter_image.png",
					figure_path = "images/twitter_worldcloud.png"):
	plt.clf()
	twitter_mask = imread(original_figure_path)
	wcloud = WordCloud(font_path = font_path,
						background_color = "white", 
						max_words = 3000,
						mask = twitter_mask, 
						max_font_size = 60,
						width=1800000,
						height=1400000,
						color_func=random_color_func_twitter,
						stopwords=STOPWORDS.add("RT"))
	wcloud.generate(text)
	plt.figure()
	plt.imshow(wcloud)
	plt.axis("off")
	# plt.show()
	plt.savefig(figure_path)

def create_word_cloud(tweet_cursor,
					font_path="fonts/CabinSketch-Regular.ttf",
					original_figure_path = "images/originals/twitter_image.png",
					figure_path = "images/twitter_worldcloud.png"):
		
	tweet_tokenizer = TweetTokenizer()
	punct = list(string.punctuation)
	stopword_list = stopwords.words('spanish') \
					+ stopwords.words('english') \
					+ punct  \
					+ ['rt','via','...','¿','si','cómo','“','”','¡','q','esas','cosas','https']
	tf = Counter()

	t_count = 0
	for docto in tweet_cursor:		
		tokens = process(text=docto["text"],
						 tokenizer = tweet_tokenizer,
						 stopwords=stopword_list)
		tf.update(tokens)
		t_count +=1		
		# if(t_count > 100): break
	print("La word cloud ha procesado el texto de "+str(t_count)+" tuits")
	word_lista = ' '
	for tag, count in tf.most_common(500):
		# try:
			# print("{}:{}".format(tag,count))
		# except:
			# pass
		word_lista = word_lista+','+tag
	show_words_cloud(word_lista,font_path, original_figure_path, figure_path)

# *********************************************
# relevant fields
# *********************************************

def get_relevant_fields(tweet_cursor, file_path = 'tweets_table.xlsx'):
	tweet_id = []
	text = []
	user = []
	user_id = []
	user_bio = []
	is_retweet = []
	created_at = []
	times_retweeted = []
	location = []
	hashtags = []
	
	for t in tweet_cursor:		
		tweet_id.append(t["id_str"])
		# treatment of extended tweets
		txt = t["text"]
		try:
			txt = t["extended_tweet"]["full_text"]
		except:
			pass
		if txt.startswith("RT"):
			try:
				try:
					txt = "RT " + t["retweeted_status"]["extended_tweet"]["full_text"]
				except:
					txt = "RT " + t["quoted_status"]["extended_tweet"]["full_text"]
				# print("retweet de tweet extendido")
			except:
				pass
		else:
			try: 
				txt = t["extended_tweet"]["full_text"]
				# print("tweet extendido")
			except:
				pass
		text.append(txt)
		user.append(t["user"]["name"])
		user_id.append(t["user"]["id_str"])
		user_bio.append(t["user"]["description"])
		is_retweet.append(1 if t["text"].startswith("RT") else 0)
		created_at.append(t["created_at"])
		times_retweeted.append(t["retweet_count"])
		location.append(t["place"])
		hashtags.append([d["text"] for d in t["entities"]["hashtags"]])
	df = pd.DataFrame({'tweet_id': tweet_id,
						'text':text,
						'user':user,
						'user_id':user_id,
						'user_bio':user_bio,
						'is_retweet':is_retweet,
						'created_at':created_at,
						'times_retweeted':times_retweeted,
						'location':location,
						'hashtags':hashtags})
	# Create a Pandas Excel writer using XlsxWriter as the engine.
	writer = pd.ExcelWriter(file_path, engine='xlsxwriter')

	# Convert the dataframe to an XlsxWriter Excel object.
	df.to_excel(writer, sheet_name='Sheet1')

	# Close the Pandas Excel writer and output the Excel file.
	writer.save()
	return df

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

	fig1, ax1 = plt.subplots()
	ax1.pie(sizes, 
			explode=explode, 
			labels=labels, 
			autopct='%1.1f%%',
			shadow=True, 
			startangle=90,
			colors = [oyellow, oblue, ogreen1])
	ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
	# plt.show()
	plt.savefig(figure_path)

# *********************************************
# number of twits per day
# *********************************************

def create_time_graph(df, figure_path = "time_histogram.png"):
	ts = [time.strftime('%Y-%m-%d %H:%M:%S', 
						time.strptime(x,'%a %b %d %H:%M:%S +0000 %Y')) 
						for x in df["created_at"]]
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
def create_tuits_distict_users_relations_graph(df, figure_path = "images/tuits_users_graph.png"):
	ts = [time.strftime('%Y-%m-%d %H:%M:%S', 
						time.strptime(x,'%a %b %d %H:%M:%S +0000 %Y')) 
						for x in df["created_at"]]
	users = df["user_id"]
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

def create_tuits_by_user_graph(df, figure_path = "images/tuits_by_user_graph.png"):
	users = df["user_id"]
	tweet_id = df["tweet_id"]
	new_df = pd.DataFrame({'users':users,'tweet_id':tweet_id })
	plt.clf()
	# para cada user id, nos quedamos con el número de tuits suyos que tenemos
	new_df2 = new_df.groupby(new_df['users'], as_index = False).count()
	print("new_df2")
	print(new_df2[:10])
	new_df2.plot(kind="hist", color = [oblue], legend = None, bins = 20)
	plt.xticks(rotation=90)
	plt.xlabel("Numero de tuits")
	plt.ylabel("Numero de usuarios")
	plt.tight_layout()
	plt.savefig(figure_path)

	plt.clf()
	new_df3 = new_df2.groupby(new_df2['tweet_id'], as_index = False).count()
	plt.scatter(x= new_df3["tweet_id"], y=new_df3["users"], color = [oblue])
	# L = plt.legend()
	# L.get_texts()[0].set_text('Numero de tuits')	
	plt.xticks(rotation=90)
	plt.xlabel("Numero de tuits")
	plt.ylabel("Numero de usuarios")
	plt.tight_layout()
	plt.savefig(figure_path.replace(".png", "_scatter.png"))

	explore = 5	
	n_tuits = [x for x in new_df2["tweet_id"]]
	users_id = [x for x in new_df2["users"]]
	list1, list2  = zip(*sorted(zip(n_tuits, users_id), reverse=True))
	for i in range(explore):
		print ("El usuario numero "+str(i+1)+" por numero de tuits ha publicado" + str(list1[i]) + " tuits")
		print ("El id de este usuario es " + str(list2[i]))
	
	
def main():
	#MongoDB connection
	data_base_name = "query1_spanish_stream"
	collection_name = "col_" + data_base_name
	mongo_conn = MongoDBConnection("set_up.py")
	db = mongo_conn.client[data_base_name]
	collection = db[collection_name]

	fn = 'tweets_table.xlsx'
	# # build a table with relevant fields
	# df = get_relevant_fields(collection.find(), file_path = fn)
	# # in case we already have the file
	df = pd.read_excel(fn)
	
	# total_tuits, unique_tuits = are_there_duplicated_tuits(collection.find())

	# create_word_cloud(collection.find(),
					# font_path="fonts/CabinSketch-Regular.ttf",
					# original_figure_path = "images/originals/twitter_image.png",
					# figure_path = "images/twitter_worldcloud.png")
	# create_retweeted_proportion_graph(collection.find(), figure_path = "images/retweeted_proportions.png")
	# create_time_graph(df, figure_path = "images/time_histogram.png")

	# # for those twits that are a retwit of another one, look for the number of times that twit has been
	# # retwitted
	# twitter_cursor = collection.find({"text": {'$regex' : '^RT'}})
	# create_times_retweeted_graph(twitter_cursor, figure_path = "images/retweeted_graph.png")
	# create_tuits_distict_users_relations_graph(df, figure_path = "images/tuits_users_graph.png")
	create_tuits_by_user_graph(df, figure_path = "images/tuits_by_user_graph.png")


if __name__ == '__main__':
	try:
		print("%%%%%%%%%%%%%%%   Starting task at "+str(datetime.datetime.now()))
		main()
	except KeyboardInterrupt:
		print ('\nGoodbye! ')  