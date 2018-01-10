import tweepy

class TweeterAPIConnection:
	def __init__(self, keys_file_name):
		### this class needs a file stored in the same directory or a path route to find the file
		### of the form {"Twitter_keys":{ "consumer_key": "XXXXX",
							### "consumer_secret" :"XXXXXXXX",
							### "access_token" : "XXXXXX",
							### "access_token_secret" :"XXXXXXXX"}}
		# The consumer keys can be found on your application's Details
		# page located at https://dev.twitter.com/apps (under "OAuth settings")
		# The access tokens can be found on your applications's Details
		# page located at https://dev.twitter.com/apps (located
		# under "Your access token")
		keys_file  = open(keys_file_name, "r") 
		keys_dict = eval(keys_file.read())
		self.consumer_key= keys_dict["Twitter_keys"]["consumer_key"]
		self.consumer_secret= keys_dict["Twitter_keys"]["consumer_secret"]
		self.access_token= keys_dict["Twitter_keys"]["access_token"]
		self.access_token_secret= keys_dict["Twitter_keys"]["access_token_secret"]

	def getTwitterApi(self, wait_on_rate_limit=False):
		# == OAuth Authentication ==
		#
		# This mode of authentication is the new preferred way
		# of authenticating with Twitter.
		api = None
		try:
			auth = tweepy.OAuthHandler(self.consumer_key, self.consumer_secret)
			auth.set_access_token(self.access_token, self.access_token_secret)
			api = tweepy.API(auth, wait_on_rate_limit=wait_on_rate_limit)		
			print('********** api connection creada  for user '+api.me().screen_name+' ******************')
		except:
			print("Error conexión con el API de Twitter")
		return api

if __name__ == '__main__':
	# TEST TEST TEST
	conn = TweeterAPIConnection(keys_file_name = "twitter_keys.py", user = "Maite")
	api = conn.getTwitterApi()
	# If the authentication was successful, you should
	# see the name of the account print out

