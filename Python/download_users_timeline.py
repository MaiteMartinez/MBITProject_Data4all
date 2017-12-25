from __future__ import absolute_import, print_function
import tweepy
from OpenMongoDB import MongoDBConnection
import pymongo
import json
from TweeterAPIConnection import TweeterAPIConnection
import datetime
import pandas as pd


def main():
	#This handles Twitter authentification and the connection to Twitter Streaming API
	keys_file  = open("set_up.py", "r") 
	keys_dict = eval(keys_file.read())
	consumer_key= keys_dict["Twitter_keys"]["consumer_key"]
	consumer_secret= keys_dict["Twitter_keys"]["consumer_secret"]
	access_token= keys_dict["Twitter_keys"]["access_token"]
	access_token_secret= keys_dict["Twitter_keys"]["access_token_secret"]

	# wait_on_rate_limit=True to wait until rate limits reset, instead of failing
	# rate limit when getting followed/followers is easily reached
	api = TweeterAPIConnection(keys_file_name = "set_up.py").getTwitterApi(wait_on_rate_limit=True)

	#MongoDB connection
	data_base_name = "timelines"	
	mongo_conn = MongoDBConnection("set_up.py")	
	# borramos la database:
	mongo_conn.client.drop_database(data_base_name)
	db = mongo_conn.client[data_base_name]

	# users info
	file_name = "C:/DATOS/MBIT/Proyecto/MBITProject_Data4all/Python/all_tweets_lang_class.xlsx"
	df_columns = pd.read_excel(open(file_name, "rb"), sheetname = 'Sheet1', header = 0).columns
	converter = {col: str for col in df_columns} 
	df = pd.read_excel(open(file_name, "rb"), sheetname = 'Sheet1', header = 0, converters = converter)
	na_value =  "None"
	df2 = df.fillna(value = na_value)
	people_net={}
	for i in range(len(df2["user_id"])):
		# TIMELINES
		collection_name = "col_" + str(df2["user_id"][i])
		collection = db[collection_name]
		user_id = df2["user_id"][i]
		user_cursor = api.user_timeline(user_id = user_id,
										screen_name = df2["user_screenname"][i],
										count=2)
		for status in user_cursor:
			# process status here				
			tweet_json = json.loads(json.dumps((status._json)))
			try:
				tweetid = collection.insert_one(tweet_json).inserted_id
			except Exception as e:
				print ("Tweet load failed *******  "+str(e))
			try:
				print(df2["user_name"][i]+"   "+str(tweet_json["user"]["name"]))
			except:
				pass

		# FOLLOWERS and FOLLOWED
		people_net[str(user_id)] = {}
		people_net[str(user_id)]["follower_ids"] = get_followers_ids(user_id, api)
		people_net[str(user_id)]["followed_ids"] = get_friends_ids(user_id, api)
		if i > 10:break
	f = open("users_net.py", "w")
	from pprint import pprint 
	pprint(people_net,f)
	f.close()
# https://codereview.stackexchange.com/questions/101905/get-all-followers-and-friends-of-a-twitter-user

def get_followers_ids(user_id, api):
    ids = []
    page_count = 0
    for page in tweepy.Cursor(api.followers_ids, id=user_id, count=5000).pages():
        page_count += 1
        # print 'Getting page {} for followers ids'.format(page_count)
        ids.extend(page)

    return ids

def get_friends_ids(user_id, api):
    ids = []
    page_count = 0
    for page in tweepy.Cursor(api.friends_ids, id=user_id, count=5000).pages():
        page_count += 1
        # print 'Getting page {} for friends ids'.format(page_count)
        ids.extend(page)
    return ids

	

if __name__ == '__main__':
	try:
		print("%%%%%%%%%%%%%%%   Starting task at "+str(datetime.datetime.now()))
		main()
	except KeyboardInterrupt:
		print ('\nGoodbye! ')  


