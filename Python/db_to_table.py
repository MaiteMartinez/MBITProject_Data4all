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
# relevant text/users fields
# *********************************************

def get_relevant_text_users_fields(tweet_cursor, file_path = 'user_tweets_table.xlsx'):
	# host tuit fields
	tweet_id = []
	host_text = []
	host_user_name = []
	host_user_screenname = []
	host_user_bio = []
	host_hashtags = []
	# retweeted tuit fields, if any
	retweeted_id = []
	retweeted_text = []
	retweeted_user_name = []
	retweeted_user_screenname = []
	retweeted_user_bio = []
	retweeted_hashtags = []
	# quoted tuit fields, if any
	quoted_id = []
	quoted_text = []
	quoted_user_name = []
	quoted_user_screenname = []
	quoted_user_bio = []
	quoted_hashtags = []

	
	for t in tweet_cursor:		
		tweet_id.append(t["id_str"])
		# host tweet
		try:
			host_text.append(t["extended_tweet"]["full_text"])			
		except:
			host_text.append(t["text"])
		host_user_name.append(t["user"]["name"])
		host_user_screenname.append(t["user"]["screen_name"])
		host_user_bio.append(t["user"]["description"])
		host_hashtags.append([d["text"] for d in t["entities"]["hashtags"]])

		try:
			obj = t["retweeted_status"]
			retweeted_id.append(obj["id_str"])
			try:
				retweeted_text.append(obj["extended_tweet"]["full_text"])			
			except:
				retweeted_text.append(obj["text"])
			retweeted_user_name.append(obj["user"]["name"])
			retweeted_user_screenname.append(obj["user"]["screen_name"])
			retweeted_user_bio.append(obj["user"]["description"])
			retweeted_hashtags.append([d["text"] for d in obj["entities"]["hashtags"]])
		except:
			retweeted_id.append("")
			retweeted_text.append("")			
			retweeted_user_name.append("")
			retweeted_user_screenname.append("")
			retweeted_user_bio.append("")
			retweeted_hashtags.append([])

		try:
			obj = t["quoted_status"]
			quoted_id.append(obj["id_str"])
			try:
				quoted_text.append(obj["extended_tweet"]["full_text"])			
			except:
				quoted_text.append(obj["text"])
			quoted_user_name.append(obj["user"]["name"])
			quoted_user_screenname.append(obj["user"]["screen_name"])
			quoted_user_bio.append(obj["user"]["description"])
			quoted_hashtags.append([d["text"] for d in obj["entities"]["hashtags"]])
		except:
			quoted_id.append("")
			quoted_text.append("")			
			quoted_user_name.append("")
			quoted_user_screenname.append("")
			quoted_user_bio.append("")
			quoted_hashtags.append([])	


		
	df = pd.DataFrame({"tweet_id" : tweet_id,
						"host_text" : host_text,
						"host_user_name" : host_user_name,
						"host_user_screenname" : host_user_screenname,
						"host_user_bio" : host_user_bio,
						"host_hashtags" : host_hashtags,

						"retweeted_id" : retweeted_id,
						"retweeted_text" : retweeted_text,
						"retweeted_user_name" : retweeted_user_name,
						"retweeted_user_screenname" : retweeted_user_screenname,
						"retweeted_user_bio" : retweeted_user_bio,
						"retweeted_hashtags" : retweeted_hashtags,

						"quoted_id" : quoted_id,
						"quoted_text" : quoted_text,
						"quoted_user_name" : quoted_user_name,
						"quoted_user_screenname" : quoted_user_screenname,
						"quoted_user_bio" : quoted_user_bio,
						"quoted_hashtags" : quoted_hashtags})

	# Create a Pandas Excel writer using XlsxWriter as the engine.
	writer = pd.ExcelWriter(file_path, engine='xlsxwriter')
	# Convert the dataframe to an XlsxWriter Excel object.
	df.to_excel(writer, sheet_name='Sheet1')
	# Close the Pandas Excel writer and output the Excel file.
	writer.save()
	return df




# *********************************************
# MAIN
# *********************************************

def main():
	#MongoDB connection
	data_base_name = "query1_spanish_stream"
	collection_name = "col_" + data_base_name
	mongo_conn = MongoDBConnection("set_up.py")
	db = mongo_conn.client[data_base_name]
	collection = db[collection_name]

	# build tables with relevant fields
	# df = get_relevant_fields(collection.find(), file_path = 'tweets_table.xlsx')
	df2 = get_relevant_text_users_fields(collection.find(), file_path = 'user_tweets_table.xlsx')
	

if __name__ == '__main__':
	try:
		print("%%%%%%%%%%%%%%%   Starting task at "+str(datetime.datetime.now()))
		main()
	except KeyboardInterrupt:
		print ('\nGoodbye! ')  