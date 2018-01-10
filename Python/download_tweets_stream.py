from __future__ import absolute_import, print_function
import tweepy
from OpenMongoDB import MongoDBConnection
import pymongo
import json
import sys, string, os
import csv
import pdb
import time
import codecs
import datetime


#Import the necessary methods from tweepy library
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream


#Listener
class StreamListener_to_db(StreamListener):
	def __init__(self, collection):		
		self.collection = collection
		print("************  New stream created at " + str(datetime.datetime.now()))

	def on_data(self, data):
		tweet_json = json.loads(data)
		try:
			tweetid = self.collection.insert_one(tweet_json).inserted_id
			print ( "========   twit loaded " + str(tweetid) +" at "+str(datetime.datetime.now()) )
			return True # keep stream alive
		except BaseException as e:
			print ('failed ondata,',str(e))
			time.sleep(5) # reload stream


	def on_error(self, status):
		text_error = '*********** ERROR ** Status code = %s at %s\n' % (status_code,datetime.datetime.now())
		print (text_error)
		return True # keep stream alive

	def on_exception(self,exception):
		text_error = '*********** EXCEPTION  ** %s at %s\n' % (exception,datetime.datetime.now())
		print (text_error) 
		return True # keep stream alive

	def on_timeout(self):
		#print 'paso por on_timeout\n'
		text_error = '*********** TIMEOUT at %s\n' % ( datetime.datetime.now())
		print (text_error)
		return False #restart streaming
 




def main():
	#This handles Twitter authentification and the connection to Twitter Streaming API
	keys_file  = open("set_up.py", "r") 
	keys_dict = eval(keys_file.read())
	consumer_key= keys_dict["Twitter_keys"]["consumer_key"]
	consumer_secret= keys_dict["Twitter_keys"]["consumer_secret"]
	access_token= keys_dict["Twitter_keys"]["access_token"]
	access_token_secret= keys_dict["Twitter_keys"]["access_token_secret"]

	#MongoDB connection
	data_base_name = "query1_spanish_stream"
	collection_name = "col_" + data_base_name
	mongo_conn = MongoDBConnection("set_up.py")
	db = mongo_conn.client[data_base_name]
	collection = db[collection_name]

	#stream connection
	l = StreamListener_to_db(collection)
	auth = OAuthHandler(consumer_key, consumer_secret)
	auth.set_access_token(access_token, access_token_secret)
	

	#query to search tweets: ',' is or, ' ' is and
	query = ["#machine learning", "#machinelearning", "#datamining", "#data mining",\
			"#Python","#SQL", "#hadoop", "#bigdata", "#tableau", "#pentaho", "#rstats"]
	exit = False
	while not exit: # Making permanent streaming with exception handling 
		try:
			stream = Stream(auth, l)
			stream.filter(track=query,languages = ["es"])
		except KeyboardInterrupt:
			print ('\nGoodbye! ')
			exit = True
		except:			
			print ("Error. Restarting Stream....  ")
			time.sleep(5)			
	

if __name__ == '__main__':
	try:
		print("%%%%%%%%%%%%%%%   Starting task at "+str(datetime.datetime.now()))
		main()
	except KeyboardInterrupt:
		print ('\nGoodbye! ')  


