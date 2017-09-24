from __future__ import absolute_import, print_function
import csv
import tweepy
import pdb

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
	consumer_key= "XoZ54xxhuB4ec7BPDJj2ptot2"
	consumer_secret= "wd2iBsAiBnxLslDZMiAaSWBnbA62e8sXnjey5Q3DCm4XX3RI3J"
	access_token="906950076123185152-4NoTPkFaDBTB5GiipLLbWJ42SWRLzEJ"
	access_token_secret="dqD1Tw9r0PBwaI2tkfwSvsqImTyBiKEBoTW5I7XtWcQik"
	# If the authentication was successful, you should
	# see the name of the account print out
	api = getTwitterApi(consumer_key,consumer_secret,access_token, access_token_secret)
	print('********** api creada  para usuario '+api.me().screen_name+' ******************')

	# here we go: miguel tweets
	twitter_username = "mancebox"
	number_of_tweets = 100

	#get tweets
	tweets = api.user_timeline(screen_name = twitter_username,count = number_of_tweets)
	# pdb.set_trace()


	#create array of tweet information: username, tweet id, date/time, text
	tweets_for_csv = [[twitter_username,tweet.id_str, tweet.created_at, tweet.text.encode("utf-8")] for tweet in tweets]

	#write to a new csv file from the array of tweets
	print ("writing to tweets.csv".format(twitter_username))
	with open("tweets.csv".format(twitter_username) , 'w+') as file:
		writer = csv.writer(file, delimiter='|')
		writer.writerows(tweets_for_csv)