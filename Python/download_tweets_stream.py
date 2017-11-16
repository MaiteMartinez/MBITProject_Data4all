from __future__ import absolute_import, print_function
import csv
import tweepy
import pdb
from OpenMongoDB import MongoDBConnection
import pymongo
import json
import sys, string, os
import csv
import pdb
import time

#Import the necessary methods from tweepy library
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream


#This is a basic listener that just prints received tweets to stdout.
class StdOutListener(StreamListener):
	def __init__(self, collection):		
		self.collection = collection

	def on_data(self, data):
		try:
			# tweet_json = json.loads(json.dumps(data._json))
			tweet_json = json.loads(data)
			tweetsid = self.collection.insert_one(tweet_json).inserted_id
			print(tweetsid)
			print (tweet_json["text"])
			return True
		except BaseException as e:
			print ('failed ondata,',str(e))
			time.sleep(5)

	def on_error(self, status):
		print (status)


if __name__ == '__main__':
	#This handles Twitter authetification and the connection to Twitter Streaming API
	keys_file  = open("set_up.py", "r") 
	keys_dict = eval(keys_file.read())
	consumer_key= keys_dict["Twitter_keys"]["consumer_key"]
	consumer_secret= keys_dict["Twitter_keys"]["consumer_secret"]
	access_token= keys_dict["Twitter_keys"]["access_token"]
	access_token_secret= keys_dict["Twitter_keys"]["access_token_secret"]

	#MongoDB connection
	data_base_name = "query1_spanish_stream"
	collection_name = "col_" + data_base_name
	db = MongoDBConnection("set_up.py").client[data_base_name]
	collection = db[collection_name]

	#stream connection
	l = StdOutListener(collection)
	auth = OAuthHandler(consumer_key, consumer_secret)
	auth.set_access_token(access_token, access_token_secret)
	stream = Stream(auth, l)

	#This line filter Twitter Streams to capture data by the keywords: 'Amsterdam'
	# stream.filter(track=["Python","R","SQL","machine learning", "data mining"],languages = ["es"])
	stream.filter(track=["#Python","#SQL","#machine learning", "#machinelearning", "#datamining", "#data mining"],languages = ["es"])


