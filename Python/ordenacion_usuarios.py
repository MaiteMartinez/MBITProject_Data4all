from __future__ import absolute_import, print_function
import tweepy
from OpenMongoDB import MongoDBConnection
import pymongo
import json
from TweeterAPIConnection import TweeterAPIConnection
import datetime
import pandas as pd
from db_to_table import save_df
import networkx as nx
import matplotlib.pyplot as plt# Tweets to retrieve in the timeline query


n_tuits = 200



def check_if_of_interest(text):
	return True

def get_h_index (n_retweets):
	# needs a vector with the citations (number of retweets) of each published tweet
	nr = sorted(n_retweets, reverse = True)
	h = 0
	for i in range(1, len(nr)+1):
		if nr[i-1]>=i : h=i
		else: break
	return h

# https://codereview.stackexchange.com/questions/101905/get-all-followers-and-friends-of-a-twitter-user

def get_followers_ids(user_id, user_ids_set, api):
	ids = []
	page_count = 0
	for page in tweepy.Cursor(api.followers_ids, id=user_id, count=5000).pages():
		page_count += 1
		# print ("Getting page " +str(page_count)+" for followers ids " + str(user_id))
		ids.extend(set(map(str, page)) & user_ids_set)
	return ids

def get_friends_ids(user_id, user_ids_set, api):
	ids = []
	page_count = 0
	for page in tweepy.Cursor(api.friends_ids, id=user_id, count=5000).pages():
		page_count += 1
		# print ("Getting page " +str(page_count)+" for friends ids " + str(user_id))
		ids.extend(set(map(str, page)) & user_ids_set)
	return ids

def get_h_index_data(df2, api):
	people_data = df2[["user_id", "user_name", "user_screenname"]]
	# people_data = pd.DataFrame()
	# n_users = 20
	# people_data["user_id"] = df2["user_id"][:n_users]
	# people_data["user_name"] = df2["user_name"][:n_users]
	# people_data["user_screenname"] = df2["user_screenname"][:n_users]
	total_tweets = []
	tweets_of_interest_as_percentage_of_total = []
	retweets_as_percentage_of_interest = []
	h_index = []
	first_citations = []
	errors = []
	for i in range(len(people_data["user_id"])):		
		user_id = people_data["user_id"][i]		
		print("Processing user number "+str(i)+" of " + str(len(people_data["user_id"]))+" user_id = "+str(user_id))
		
		# timeline extraction: caring for errors for protected, unexistent, etc. user timelines
		try:
			user_cursor = api.user_timeline(user_id = user_id,
											screen_name = people_data["user_screenname"][i],
											count = n_tuits)
			errors.append("")
		except tweepy.TweepError as e:
			print ("Failed to download user " + str(user_id) + " timeline")
			print (" Exception: " + str(e))
			print ("Skipping... ")
			user_cursor = []
			errors.append(e)
			
		is_retweet = 0
		is_of_interest = 0
		total = 0
		how_many_retweets = []
		for status in user_cursor:
			# process status here				
			tweet_json = json.loads(json.dumps((status._json)))
			# extract text
			text = tweet_json["text"]
			try:
				text = tweet_json["extended_tweet"]["full_text"]			
			except:
				pass
			# check if tweet is of interest
			if (check_if_of_interest(text)):
				is_of_interest += 1
				if text.startswith("RT"): 
					is_retweet += 1
				else:
					try:
						q = tweet_json["quote_count"]
					except:
						q = 0

					try:
						r = tweet_json["retweet_count"]
					except:
						r = 0
					how_many_retweets.append(q+r)
			# count of how many tweets downloaded
			total += 1		

		# note data for this user
		total_tweets.append(total)
		tweets_of_interest_as_percentage_of_total.append(is_of_interest/total)
		retweets_as_percentage_of_interest.append(is_retweet/is_of_interest)
		h = get_h_index(how_many_retweets)
		h_index.append(h)
		first_citations.append(sorted(how_many_retweets, reverse = True)[ : h+1])			

		# if i > n_users-2:break

	# vectors to data frame
	people_data["total_tweets"] = total_tweets
	people_data["tweets_of_interest_as_percentage_of_total"] = tweets_of_interest_as_percentage_of_total
	people_data["retweets_as_percentage_of_interest"] = retweets_as_percentage_of_interest
	people_data["h_index"] = h_index
	people_data["first_citations"] = first_citations

	file_name = "C:/DATOS/MBIT/Proyecto/MBITProject_Data4all/Python/people_data.xlsx"
	save_df(people_data, file_name)
	return people_data

def get_relation_graph(df2, api):
	users_ids = df2["user_id"]
	user_ids_set = set(users_ids)
	n_users = 2
	errors=[""]*len(users_ids)
	relations = []
	for i in range(len(users_ids)):		
		user_id = users_ids[i]		
		print("Getting relations for user number "+str(i)+" of " + str(len(users_ids))+" user_id = "+str(user_id))
		followers_ids = []
		# followers extraction: caring for errors 
		try:
			followers_ids = get_followers_ids(user_id, user_ids_set, api)
		except tweepy.TweepError as e:
			print ("Failed to get followers/followed for user " + str(user_id) + " timeline")
			print (" Exception: " + str(e))
			print ("Skipping... ")
			errors[i] = e
		 # A está relacionado con el usuario B si A sigue a B
		this_user_rels = [(x, user_id) for x in followers_ids]
		relations.extend(this_user_rels)
		if i > n_users:break

	errors_df = pd.DataFrame({"user_id": user_id, "errors": errors})
	file_name = "C:/DATOS/MBIT/Proyecto/MBITProject_Data4all/Python/graph_errors.xlsx"
	save_df(errors_df, file_name)

	# directed graph creation
	DG = nx.DiGraph()
	DG.add_nodes_from(users_ids)
	DG.add_edges_from(set(relations))
	
	return errors_df, DG

def main():
	#This handles Twitter authentification and the connection to Twitter Streaming API
	# wait_on_rate_limit=True to wait until rate limits reset, instead of failing
	# rate limit when getting followed/followers is easily reached
	api = TweeterAPIConnection(keys_file_name = "set_up.py").getTwitterApi(wait_on_rate_limit = True)

	# users info
	file_name = "C:/DATOS/MBIT/Proyecto/MBITProject_Data4all/Python/unique_users_lang_class.xlsx"
	df_columns = pd.read_excel(open(file_name, "rb"), sheetname = 'Sheet1', header = 0).columns
	converter = {col: str for col in df_columns} 
	df = pd.read_excel(open(file_name, "rb"), sheetname = 'Sheet1', header = 0, converters = converter)
	na_value =  "None"
	df2 = df.fillna(value = na_value)
	
	# h_index_df = get_h_index_data(df2, api)

	graph_errors_df, directed_graph = get_relation_graph(df2, api)
	nx.write_gml(directed_graph, "relations_graph.gml")
	

if __name__ == '__main__':
	try:
		print("%%%%%%%%%%%%%%%   Starting task at "+str(datetime.datetime.now()))
		main()
	except KeyboardInterrupt:
		print ('\nGoodbye! ')  


