import csv
import tweepy
import pdb
import pymongo
import json
from pprint import pprint
from OpenMongoDB import MongoDBConnection
import pymongo




if __name__ == '__main__':
	data_base_name = "query1_spanish_stream"
	collection_name = "col_" + data_base_name
	# connection to mongodb
	db = MongoDBConnection("set_up.py").client[data_base_name]
	collection = db[collection_name]
	# para ver la lista de las bases de datos que tiene el mongo instaladas
	# print(client.database_names())

	print("**************************"+ str(collection.count()))
	my_tweet = {}	
	# for document in collection.find({"text": {"$regex" : "machine", "$options" : "i"}}):
	for document in collection.find():		
		# print(document["id_str"])
		try:			
			# pprint(document)
			# print(document["text"])
			t = {}
			t["user"] = document["user"]["name"]
			t["user_description"] = document["user"]["description"]
			t["text"] = document["text"]
			t["created at"] = document["created_at"]
			pprint(t)
			my_tweet[document["id_str"]] = t

			if(len(my_tweet) >200): break
		except:
			continue
	
	f = open("one_tweet.py","w")
	pprint(my_tweet, f)
	f.close()