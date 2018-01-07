from __future__ import absolute_import, print_function
import tweepy
from OpenMongoDB import MongoDBConnection
import pymongo
import json
from TweeterAPIConnection import TweeterAPIConnection
import time
import pandas as pd
from db_to_table import save_df
import networkx as nx
import matplotlib.pyplot as plt# Tweets to retrieve in the timeline query
from utilities import *


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

def basic_measures(G):
	output_string = ""
	output_string += ("radius: %d" % nx.radius(G)) + "\n"
	output_string += ("diameter: %d" % nx.diameter(G)) + "\n"
	output_string += ("average_shortest_path_length: %d" % nx.average_shortest_path_length(G)) + "\n"
	# output_string += ("eccentricity: %s" % nx.eccentricity(largest)) + "\n"  %this is a dictionary
	# output_string += ("center: %s" % nx.center(largest)) + "\n"
	# output_string += ("periphery: %s" % periphery(largest)) + "\n"
	# output_string += ("density: %s" % nx.density(largest)) + "\n"
	return output_string

def print_basic_graph_properties(G, file_path = "graph_properties.txt"): 
	
	output_string = ""
	if  type(G) != nx.classes.digraph.DiGraph:
		raise Exception ("NetworkX directed graph expected")
	output_string += " Type of object " + str(type(G)) + "\n"
	

	pathlengths=[]
	output_string += "source vertex {target:length, } for some nodes \ n "
	count = 0
	for v in G.nodes():
		# Compute the shortest path lengths from source to all reachable nodes
		spl = nx.single_source_shortest_path_length(G,v)
		count += 1
		if count < 20:
			output_string += '%s %s' % (v,spl) 
			output_string += "\n"
		for p in spl.values():
			pathlengths.append(p)
	# histogram of lengths of paths
	histogram_graph(pathlengths, "Distribución de la menor longitud de los caminos", oyellow, "images/pathlengths_distribution.png")

	output_string += "    \n"
	output_string += " ******  average shortest path length %s" % (sum(pathlengths)/len(pathlengths))

	# Strongly connected component 
	is_wk_connected = nx.is_weakly_connected(G)
	output_string += " Is the graph strongly connected? -> " + str(nx.is_strongly_connected(G))+"   \n"
	n = nx.number_strongly_connected_components(G)
	output_string += "It has "+str(n)+" strongly connected components  \n"
	# time consuming
	largest = max(nx.strongly_connected_component_subgraphs(G), key=len)
	output_string += "the largest strongly connected component has  "+str(len(largest))+" nodes, which are a " + str(len(largest)/len(G)*100)+"% of total nodes  \n"
	output_string += "for the largest component, the descriptive measures are: " 
	output_string += basic_measures(largest) 

	# Weakly connected component 
	output_string += " Is the graph weakly connected? -> " + str(nx.is_weakly_connected(G))+"     \n"
	n = nx.number_weakly_connected_components(G)
	output_string += "It has "+str(n)+" weakly connected components  \n"
	# time consuming
	largest = max(nx.weakly_connected_component_subgraphs(G), key=len)
	output_string += "the largest weakly connected component has  "+str(len(largest))+" nodes, which are a " + str(len(largest)/len(G)*100)+"% of total nodes  \n"
	
	degree_sequence =[d for n, d in G.degree()]
	histogram_graph(degree_sequence, "Distribucion del grado", oyellow, "images/degree_distribution.png")
	degree_sequence = [d for n, d in G.in_degree()]
	histogram_graph(degree_sequence, "Distribución del in-degree", oyellow, "images/indegree_distribution.png")
	degree_sequence = [d for n, d in G.out_degree()]
	histogram_graph(degree_sequence, "Distribución del out-degree", oyellow, "images/outdegree_distribution.png")
		
	output_string += "El coeficiente de transitividad del grafo es "+ str(nx.transitivity(G))

	print (output_string)
	f = open(file_path,'w')
	f.write(output_string)
	f.close()
	return


def get_users_centralities(df2, DG):
	centrality = degree_centrality(G)
	df2["degree"] = [centrality.get(x,0) for x in df2["users_id"]]
	return df2



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
	
	h_index_df = get_h_index_data(df2, api)

	graph_errors_df, directed_graph = get_relation_graph(df2, api)
	nx.write_gml(directed_graph, "relations_graph.gml")
	
	# directed_graph = nx.read_gml("relations_graph.gml")
	
	print_basic_graph_properties(directed_graph, file_path = "graph_properties.txt")

	# df = get_users_centralities(df2, directed_graph)

if __name__ == '__main__':
	try:
		start = time.time()
		print("%%%%%%%%%%%%%%%   Starting task at "+str(start))
		main()
		print("%%%%%%%%%%%%%%%   time ellapsed "+str((time.time()-start)/60) + " minutes")
	except KeyboardInterrupt:
		print ('\nGoodbye! ')  


