from __future__ import absolute_import, print_function
import csv
import tweepy
import pdb

import time

#Import the necessary methods from tweepy library
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream


#This is a basic listener that just prints received tweets to stdout.
class StdOutListener(StreamListener):

	def on_data(self, data):
		try:
			#print data
			tweet = data.split(',"text":"')[1].split('","source')[0]
			print (tweet)

			saveThis = str(time.time())+ '::'+ tweet #saves time+actual tweet
			saveFile = open('twits.txt','a')
			saveFile.write(saveThis)
			saveFile.write('\n')
			saveFile.close()
			return True
		except BaseException:
			print ('failed ondata,',str(e))
			time.sleep(5)

def on_error(self, status):
	print (status)


if __name__ == '__main__':
	consumer_key= "XoZ54xxhuB4ec7BPDJj2ptot2"
	consumer_secret= "wd2iBsAiBnxLslDZMiAaSWBnbA62e8sXnjey5Q3DCm4XX3RI3J"
	access_token="906950076123185152-4NoTPkFaDBTB5GiipLLbWJ42SWRLzEJ"
	access_token_secret="dqD1Tw9r0PBwaI2tkfwSvsqImTyBiKEBoTW5I7XtWcQik"


	#This handles Twitter authetification and the connection to Twitter Streaming API
	l = StdOutListener()
	auth = OAuthHandler(consumer_key, consumer_secret)
	auth.set_access_token(access_token, access_token_secret)
	stream = Stream(auth, l)

	#This line filter Twitter Streams to capture data by the keywords: 'Amsterdam'
	# stream.filter(track=["Python","R","SQL","machine learning", "data mining"],languages = ["es"])
	stream.filter(track=["Python","SQL","machine learning", "data mining"],languages = ["es"])


