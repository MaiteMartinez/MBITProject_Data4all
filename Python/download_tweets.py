from __future__ import absolute_import, print_function
import csv
import tweepy
import pdb
import pymongo
import json


def getTwitterApi(consumer_key,consumer_secret,access_token, access_token_secret):
	# == OAuth Authentication ==
	#
	# This mode of authentication is the new preferred way
	# of authenticating with Twitter.
	api = None
	try:
		auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
		auth.set_access_token(access_token, access_token_secret)
		api = tweepy.API(auth)		
	except:
		print("Error conexión con el API de Twitter")
	return api

if __name__ == '__main__':
	# The consumer keys can be found on your application's Details
	# page located at https://dev.twitter.com/apps (under "OAuth settings")
	# The access tokens can be found on your applications's Details
	# page located at https://dev.twitter.com/apps (located
	# under "Your access token")
	keys_file  = open("twitter_keys.py", "r") 
	keys_dict = eval(keys_file.read())
	user = "Maite"
	consumer_key= keys_dict[user]["consumer_key"]
	consumer_secret= keys_dict[user]["consumer_secret"]
	access_token= keys_dict[user]["access_token"]
	access_token_secret= keys_dict[user]["access_token_secret"]

	# If the authentication was successful, you should
	# see the name of the account print out
	api = getTwitterApi(consumer_key,consumer_secret,access_token, access_token_secret)
	print('********** api creada  para usuario '+api.me().screen_name+' ******************')

	# here we go: miguel tweets
	twitter_username = "mancebox"
	number_of_tweets = 100
	query = "python"

	#get tweets
	# tweets = api.search(screen_name = twitter_username,count = number_of_tweets)
	# tweets = api.search(q=query,count = number_of_tweets, languages=["es"])
	# pdb.set_trace()

	# ojo, lanzar el servidor de mongodb en 
	# C:\Program Files\MongoDB\Server\3.4\bin\mongod.exe
	# el puerto debe coincidir con el puerto al que se llama en el mongoclient
	client = pymongo.MongoClient('localhost', 27017)
	db = client.twitter_data_base
	collection = db.twitter_collection
	for data in tweepy.Cursor(api.search,q=query).items():		
		tweet_json = json.loads(json.dumps(data._json))
		# collection.insert_one(tweet_json)
		tweetsid = collection.insert_one(tweet_json).inserted_id
		print(tweetsid)
 
	print(db.twitter_collection.findOne().encode('utf-8'))

	# for tweet in collection.find():
	  # print (str(tweet["text"]).encode('utf-8'))

	#create array of tweet information: username, tweet id, date/time, text
	# tweets_for_csv = [[tweet.username,tweet.id_str, tweet.created_at, tweet.text.encode("utf-8")] for tweet in tweets]

	#write to a new csv file from the array of tweets
	# print ("writing to tweets.csv".format(twitter_username))
	# with open("tweets.csv".format(twitter_username) , 'w+') as file:
		# writer = csv.writer(file, delimiter='|')
		# writer.writerows(tweets_for_csv)