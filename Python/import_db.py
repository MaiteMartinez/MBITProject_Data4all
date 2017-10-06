import csv
import tweepy
import pdb
import pymongo
import json


if __name__ == '__main__':

	client = pymongo.MongoClient('localhost', 27017)
	# print(client.database_names())
	# para ver la lista de las bases de datos que tiene el mongo instaladas
	db = client.twitter_data_base
	collection = db.twitter_collection
	
	one_tweet_text = collection.find_one()

	
 
	print(str(collection.find_one()).encode('utf-8'))
