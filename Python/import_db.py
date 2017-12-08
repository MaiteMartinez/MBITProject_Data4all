import csv
import tweepy
import pdb
import pymongo
import json
from pprint import pprint
from OpenMongoDB import MongoDBConnection
import pymongo
from analisis_exploratorio import get_relevant_fields




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
	# get_relevant_fields(collection.find({"id_str" : "936219943137357824"}), file_path = 'one_tuit_table.xlsx')
	# for document in collection.find({"id_str" : "936219943137357824"}):		
	for document in collection.find({"user.name":"narodin80"}):		
		# print(document["id_str"])
		try:	
			# t = {}
			# t["user"] = document["user"]["name"]
			# t["user_description"] = document["user"]["description"]
			# t["text"] = document["text"]
			# t["created at"] = document["created_at"]
			pprint(document)
			# print("**************")
			# print("is place none"+str(document["place"] is None))
			my_tweet[document["id_str"]] = document #t
			if(len(my_tweet) >20): break
		except:
			continue


	f = open("one_tweet.py","w")
	pprint(my_tweet, f)
	f.close()