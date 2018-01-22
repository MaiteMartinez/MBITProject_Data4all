 
import pandas as pd
import tweepy
import json
import pymongo
import datetime
from OpenMongoDB import MongoDBConnection
import time
from copy import deepcopy
from utilities.functions import *

# *********************************************
# relevant text/users fields from db
# *********************************************

def get_relevant_tuit_fields(tweet_cursor, na_value):
	# host tuit fields
	tweet_id = []
	host_text = []
	host_source = []
	host_user_id = []
	host_user_name = []
	host_user_screenname = []
	host_user_bio = []
	host_hashtags = []
	host_url = []
	# retweeted tuit fields, if any
	retweeted_id = []
	retweeted_text = []
	retweeted_source = []
	retweeted_user_id = []
	retweeted_user_name = []
	retweeted_user_screenname = []
	retweeted_user_bio = []
	retweeted_hashtags = []
	retweeted_url = []
	# quoted tuit fields, if any
	quoted_id = []
	quoted_text = []
	quoted_source = []
	quoted_user_id = []
	quoted_user_name = []
	quoted_user_screenname = []
	quoted_user_bio = []
	quoted_hashtags = []
	quoted_url = []

	
	for t in tweet_cursor:		
		tweet_id.append(t["id_str"])
		# host tweet
		try:
			host_text.append(t["extended_tweet"]["full_text"])			
		except:
			host_text.append(t["text"])
		host_source.append(t["source"])
		host_user_id.append(t["user"]["id_str"])
		host_user_name.append(t["user"]["name"])
		host_user_screenname.append(t["user"]["screen_name"])
		host_user_bio.append(t["user"]["description"])
		host_hashtags.append([d["text"] for d in t["entities"]["hashtags"]])
		host_url.append(t["user"]["url"])

		try:
			obj = t["retweeted_status"]
			retweeted_id.append(obj["id_str"])
			try:
				retweeted_text.append(obj["extended_tweet"]["full_text"])			
			except:
				retweeted_text.append(obj["text"])
			retweeted_source.append(obj["source"])
			retweeted_user_id.append(obj["user"]["id_str"])
			retweeted_user_name.append(obj["user"]["name"])
			retweeted_user_screenname.append(obj["user"]["screen_name"])
			retweeted_user_bio.append(obj["user"]["description"])
			retweeted_hashtags.append([d["text"] for d in obj["entities"]["hashtags"]])
			retweeted_url.append(obj["user"]["url"])
		except:
			retweeted_id.append(na_value)
			retweeted_text.append(na_value)			
			retweeted_source.append(na_value)			
			retweeted_user_id.append(na_value)
			retweeted_user_name.append(na_value)
			retweeted_user_screenname.append(na_value)
			retweeted_user_bio.append(na_value)
			retweeted_hashtags.append([])
			retweeted_url.append(na_value)

		try:
			obj = t["quoted_status"]
			quoted_id.append(obj["id_str"])
			try:
				quoted_text.append(obj["extended_tweet"]["full_text"])			
			except:
				quoted_text.append(obj["text"])
			quoted_source.append(obj["source"])
			quoted_user_id.append(obj["user"]["id_str"])
			quoted_user_name.append(obj["user"]["name"])
			quoted_user_screenname.append(obj["user"]["screen_name"])
			quoted_user_bio.append(obj["user"]["description"])
			quoted_hashtags.append([d["text"] for d in obj["entities"]["hashtags"]])
			quoted_url.append(obj["user"]["url"])
		except:
			quoted_id.append(na_value)
			quoted_text.append(na_value)			
			quoted_source.append(na_value)
			quoted_user_id.append(na_value)
			quoted_user_name.append(na_value)
			quoted_user_screenname.append(na_value)
			quoted_user_bio.append(na_value)
			quoted_hashtags.append([])	
			quoted_url.append(obj["user"]["url"])


		
	df = pd.DataFrame({"tweet_id" : tweet_id,
						"host_text" : host_text,
						"host_source" : host_source,
						"host_user_id" : host_user_id,
						"host_user_name" : host_user_name,
						"host_user_screenname" : host_user_screenname,
						"host_user_bio" : host_user_bio,
						"host_hashtags" : host_hashtags,
						"host_url" : host_url,

						"retweeted_id" : retweeted_id,
						"retweeted_text" : retweeted_text,
						"retweeted_source" : retweeted_source,
						"retweeted_user_id" : retweeted_user_id,
						"retweeted_user_name" : retweeted_user_name,
						"retweeted_user_screenname" : retweeted_user_screenname,
						"retweeted_user_bio" : retweeted_user_bio,
						"retweeted_hashtags" : retweeted_hashtags,
						"retweeted_url" : retweeted_url,

						"quoted_id" : quoted_id,
						"quoted_text" : quoted_text,
						"quoted_source" : quoted_source,
						"quoted_user_id" : quoted_user_id,
						"quoted_user_name" : quoted_user_name,
						"quoted_user_screenname" : quoted_user_screenname,
						"quoted_user_bio" : quoted_user_bio,
						"quoted_hashtags" : quoted_hashtags,
						"quoted_url" : quoted_url})
	return df	

# *********************************************
# relevant text/users fields from all info (host, retweeted and quoted tweets)
# *********************************************

def get_all_users_info(df, na_value = "None"):
	# host tuit fields
	tweet_id = [x for x in df["tweet_id"]]
	text = [x for x in df["host_text"]]
	source = [x for x in df["host_source"]]
	user_id = [x for x in df["host_user_id"]]
	user_name = [x for x in df["host_user_name"]]
	user_screenname =[x for x in df["host_user_screenname"]]
	user_bio = [x for x in df["host_user_bio"]]
	hashtags = [x for x in  df["host_hashtags"]]
	url = [x for x in  df["host_url"]]
	type = ["host"] * len(hashtags)
	print ( "host tweets", len(tweet_id) )

	# retweeted tuit fields, if any
	for i in range(len(df["retweeted_id"])):
		if df["retweeted_id"][i] != na_value:
			tweet_id.append(df["retweeted_id"][i])
			text.append(df["retweeted_text"][i])
			source.append(df["retweeted_source"][i])
			user_id.append(df["retweeted_user_id"][i])
			user_name.append(df["retweeted_user_name"][i])
			user_screenname.append(df["retweeted_user_screenname"][i])
			user_bio.append(df["retweeted_user_bio"][i])
			hashtags.append(df["retweeted_hashtags"][i])
			url.append(df["retweeted_url"][i])
			type.append("retweeted") 
	
	print ( "host+retweeted tweets", len(tweet_id) )

	# quoted tuit fields, if any
	for i in range(len(df["quoted_id"])):
		if df["quoted_id"][i] != na_value:
			tweet_id.append(df["quoted_id"][i])
			text.append(df["quoted_text"][i])
			source.append(df["quoted_source"][i])
			user_id.append(df["quoted_user_id"][i])
			user_name.append(df["quoted_user_name"][i])
			user_screenname.append(df["quoted_user_screenname"][i])
			user_bio.append(df["quoted_user_bio"][i])
			hashtags.append(df["quoted_hashtags"][i])
			url.append(df["quoted_url"][i])
			type.append("quoted") 
			
	print ( "host+retweeted+quoted tweets", len(tweet_id) )
	
	df = pd.DataFrame({"tweet_id" : tweet_id,
						"text" : text,
						"source" : source,
						"user_id" : user_id,
						"user_name" : user_name,
						"user_screenname" : user_screenname,
						"user_bio" : user_bio,
						"hashtags" : hashtags,
						"url" : url,
						"type" : type})
						
	return df	


# *********************************************
# MAIN
# *********************************************

def create_tables(data_base_name, set_up_path):
	#MongoDB connection
	data_base_name = "query1_spanish_stream"
	collection_name = "col_" + data_base_name
	mongo_conn = MongoDBConnection("keys/set_up.py")
	db = mongo_conn.client[data_base_name]
	collection = db[collection_name]

	# build tables with relevant fields
	na_value =  "None"
	df2 = get_relevant_tuit_fields(collection.find(), na_value)	
	save_df(df2, file_path = 'tables/1_original_tweets.xlsx')
	
	# file_path = "tables/1_original_tweets_table.xlsx"
	# df2 = read_df(file_path)
	
	df3 = df2.fillna(value = na_value)
	df4 = get_all_users_info(df3, na_value = na_value)
	save_df(df4, file_path = 'tables/2_all_tweets.xlsx')
	
	return df4

if __name__ == '__main__':

	try:
		print("%%%%%%%%%%%%%%%   Starting task at "+str(datetime.datetime.now()))
		data_base_name = "query1_spanish_stream"
		set_up_path = "keys/set_up.py"
		all_tweets_df = create_tables(data_base_name, set_up_path)
	except KeyboardInterrupt:
		print ('\nGoodbye! ')  