from TweeterAPIConnection import TweeterAPIConnection
from OpenMongoDB import MongoDBConnection
import pymongo
import tweepy
import json
import sys, string, os
import csv
import pdb

if __name__ == '__main__':
	# API connection
	api = TweeterAPIConnection(keys_file_name = "keys/set_up.py").getTwitterApi()
	# here we go: search tweets for this query
	query1 = ((("#machine" and "#learning") or ("#data" and "#mining")) and 
			("#python" or 
			 "SQL" or 
			"#hadoop" or 
			"#bigdata" or 
			"#tableau" or
			"#pentaho"))

	data_base_name = "query1_spanish"
	collection_name = "col_" + data_base_name
	db = MongoDBConnection("keys/set_up.py").client[data_base_name]
	collection = db[collection_name]
	# ojo, esto borra todo lo que hubiera almacenado
	# collection.delete_many({})

	for data in tweepy.Cursor(api.search,q=query1, lang="es").items():		
		tweet_json = json.loads(json.dumps(data._json))
		tweetsid = collection.insert_one(tweet_json).inserted_id
		print(tweetsid)
		print (str(data.text).encode("utf-8"))
