from __future__ import absolute_import, print_function
import tweepy
import json
from TweeterAPIConnection import TweeterAPIConnection
import time
import pandas as pd
from db_to_table import save_df
import networkx as nx
import matplotlib.pyplot as plt
from utilities.functions import *
from user_selection import get_assigned_language
from relevance_model.Clasificacion1 import *
from relevance_model.Clasificacion1 import remove_stopwords as class_model_remove_stopwords

# Tweets to retrieve in the timeline query
n_tuits = 200



def check_if_of_interest(modelo_v1, text):
	clean_text = class_model_remove_stopwords(text)
	pred_x = modelo_v1.predict([clean_text])
	# try:
		# print ( str(text)+"  ****  "+str(clean_text) + " ***** "+str(pred_x))
	# except:
		# pass
	return pred_x[0]

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
	languages = []

	# for relevance of tweets classification
	arquivo = "C:\\DATOS\\MBIT\\Proyecto\\MBITProject_Data4all\\Python\\relevance_model\\modelo_clf.sav"
	modelo_v1 = pickle.load(open(arquivo,'rb'))

	for i in range(len(people_data["user_id"])):		
		user_id = people_data["user_id"][i]		
		print("Processing user number "+str(i)+" of " + str(len(people_data["user_id"]))+" user_id = "+str(user_id))
		
		# timeline extraction: caring for errors for protected, unexistent, etc. user timelines
		try:
			user_cursor = api.user_timeline(user_id = user_id,
											screen_name = people_data["user_screenname"][i],
											count = n_tuits)
			errors.append("0")
		except tweepy.TweepError as e:
			print ("Failed to download user " + str(user_id) + " timeline")
			print (" Exception: " + str(e))
			print ("Skipping... ")
			user_cursor = []
			errors.append(str(e))
			
		is_retweet = 0
		is_of_interest = 0
		total = 0
		how_many_retweets = []
		langs = []
		for status in user_cursor:
			# process status here				
			tweet_json = json.loads(json.dumps((status._json)))
			# extract text
			text = tweet_json["text"]
			try:
				text = tweet_json["extended_tweet"]["full_text"]			
			except:
				pass
			# retrieve tweet languaje
			langs.append(get_assigned_language(text)[-1])
			# check if tweet is of interest
			if (check_if_of_interest(modelo_v1, text)):
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
		tweets_of_interest_as_percentage_of_total.append(is_of_interest/total if total !=0 else 0)
		retweets_as_percentage_of_interest.append(is_retweet/is_of_interest if is_of_interest !=0 else 0)
		h = get_h_index(how_many_retweets)
		h_index.append(h)
		first_citations.append(sorted(how_many_retweets, reverse = True)[ : h+1])			
		languages.append(set(langs))
		
		print(" total = %d, of interest = %d, "%(total,is_of_interest))

		# if i > n_users-2:break

	# vectors to data frame
	people_data["total_tweets"] = total_tweets
	people_data["tweets_of_interest_as_percentage_of_total"] = tweets_of_interest_as_percentage_of_total
	people_data["retweets_as_percentage_of_interest"] = retweets_as_percentage_of_interest
	people_data["h_index"] = h_index
	people_data["first_citations"] = first_citations
	people_data["h_index_errors"] = errors
	people_data["languages"] = languages

	file_path = "tables/4_1_h_index_ranked_users.xlsx"
	save_df(people_data, file_path = file_path)
	
	return people_data

def get_relation_graph(users_df, api):
	users_ids = users_df["user_id"]	
	user_ids_set = set(users_ids)
	errors=[""]*len(users_ids)
	relations = []
	final_users = []
	for i in range(len(users_ids)):		
		user_id = users_ids[i]		
		print("Getting relations for user number "+str(i)+" of " + str(len(users_ids))+" user_id = "+str(user_id))
		# followers extraction: caring for errors 
		try:
			followers_ids = get_followers_ids(user_id, user_ids_set, api)
			# A está relacionado con el usuario B si A sigue a B
			this_user_rels = [(x, user_id) for x in followers_ids]
			relations.extend(this_user_rels)			
			final_users.append(user_id)
		except tweepy.TweepError as e:
			print ("Failed to get followers/followed for user " + str(user_id) + " timeline")
			print (" Exception: " + str(e))
			print ("Skipping... ")
			errors[i] = str(e)

	users_df["graph_errors"] = errors 
	file_name = "tables/4_2_users_graph_errors.xlsx"
	save_df(users_df, file_name)

	# directed graph creation
	DG = nx.DiGraph()
	DG.add_nodes_from(final_users)
	DG.add_edges_from(set(relations))
	
	return users_df, DG

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

def print_basic_graph_properties(G, file_path = "graph/graph_properties.txt"): 
	
	output_string = ""
	if  type(G) != nx.classes.digraph.DiGraph:
		raise Exception ("NetworkX directed graph expected")
	output_string += " Type of object " + str(type(G)) + "\n"
	output_string += " It has  " + str(len(G.nodes())) + " nodes and " +\
		str(len(G.edges()))+ " edges \n"

	pathlengths = []
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
	output_string += " ******  average shortest path length %s" % (sum(pathlengths)/len(pathlengths))+" \n"

	# Strongly connected component 
	is_wk_connected = nx.is_weakly_connected(G)
	output_string += " Is the graph strongly connected? -> " + str(nx.is_strongly_connected(G))+"   \n"
	n = nx.number_strongly_connected_components(G)
	output_string += "It has "+str(n)+" strongly connected components  \n"
	# time consuming
	largest = max(nx.strongly_connected_component_subgraphs(G), key=len)
	output_string += "the largest strongly connected component has  "+str(len(largest))+" nodes, which are a " + str(len(largest)/len(G)*100)+"% of total nodes  \n"
	output_string += "for the largest component, the descriptive measures are: \n" 
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
def normalize_vector(v):
	mx = max(v)
	if mx > 0: 
		v = [x/mx for x in v]
	return v

def get_users_centralities(users_df, G):
	# The degree centralities values are normalized by dividing by the maximum possible 
	# degree in a simple graph n-1 where n is the number of nodes in G.
	users_df["degree"] = [nx.degree_centrality(G).get(x,0) for x in users_df["user_id"]]
	users_df["in_degree"] = [nx.in_degree_centrality(G).get(x,0) for x in users_df["user_id"]]
	users_df["out_degree"] = [nx.out_degree_centrality(G).get(x,0) for x in users_df["user_id"]]
	# For directed graphs this is “left” eigenvector centrality which corresponds to the in-edges 
	# in the graph. For out-edges eigenvector centrality first reverse the graph with G.reverse().
	try:
		users_df["eigenvector"] = [nx.eigenvector_centrality_numpy(G).get(x,0) for x in users_df["user_id"]]
	except Exception as e:
		print("Eigenvector numpy failed " + str(e))
		users_df["eigenvector"] = [nx.eigenvector_centrality(G).get(x,0) for x in users_df["user_id"]]
	# normalize values
	users_df["eigenvector"] = normalize_vector(users_df["eigenvector"])
	# katz_centrality(G, alpha=0.1, beta=1.0,...) default values
	# The parameter alpha should be strictly less than the inverse of largest eigenvalue 
	# of the adjacency matrix for the algorithm to converge. You can use 
	# max(nx.adjacency_spectrum(G)) to get λmax
	l_max = max([abs(x) for x in nx.adjacency_spectrum(G)])
	a = 0.1
	if l_max != 0:
		a = 0.8/l_max

	try:
		users_df["katz_bonacich"] = [nx.katz_centrality_numpy(G, alpha = a, beta = 1.0, normalized=True).get(x,0) for x in users_df["user_id"]]
	except Exception as e:
		print ("Katz-Bonacich numpy failed " + str(e))
		users_df["katz_bonacich"] = [nx.katz_centrality(G, alpha = a, beta = 1.0, normalized=True).get(x,0) for x in users_df["user_id"]]

	try:
		users_df["pagerank"] = [nx.pagerank_numpy(G, alpha = 0.85).get(x,0) for x in users_df["user_id"]]
	except Exception as e:
		print ("pagerank numpy failed " + str(e))
		try:
			users_df["pagerank"] = [nx.pagerank_scipy(G, alpha = 0.85).get(x,0) for x in users_df["user_id"]]
		except Exception as e:
			print ("pagerank scipy failed " + str(e))
			users_df["pagerank"] = [nx.pagerank(G, alpha = 0.85).get(x,0) for x in users_df["user_id"]]
	# normalize values
	users_df["pagerank"] = normalize_vector(users_df["pagerank"])
	# The closeness centrality is normalized to (n-1)/(|G|-1) where n is the number of nodes 
	# in the connected part of graph containing the node. If the graph is not completely 
	# connected, this algorithm computes the closeness centrality for each connected part 
	# separately scaled by that parts size.
	users_df["closeness"] = [nx.closeness_centrality(G).get(x,0) for x in users_df["user_id"]]
	users_df["betweenness"] = [nx.betweenness_centrality(G, normalized=True).get(x,0) for x in users_df["user_id"]]
	return users_df



def get_ranked_users(people_data):
	#This handles Twitter authentification and the connection to Twitter Streaming API
	# wait_on_rate_limit=True to wait until rate limits reset, instead of failing
	# rate limit when getting followed/followers is easily reached
	api = TweeterAPIConnection(keys_file_name = "keys/set_up.py").getTwitterApi(wait_on_rate_limit = True)

	people_data = get_h_index_data(people_data, api)

	file_path = "tables/4_1_h_index_ranked_users.xlsx"
	people_data = read_df(file_path)

	# ********************************************
	# user errors
	# ********************************************
	# we have probably had some users with timeline errors. 
	# draw some graphs for the memoir and retrieve some numbers
	number_of_users = len(people_data["user_id"])
	different_errors = [str(x) for x in people_data["h_index_errors"] if x !="0"]
	number_of_errors = len(different_errors)
	p = number_of_errors/number_of_users
	sizes = [p, 1.-p]
	labels = ["errors", "ok"]
	explode = (0.1, 0)
	colors = [oyellow, oblue]
	file_path = "images/errors_in_h_index_proportion.png"
	highlighted_pie_graph(sizes, labels, explode, colors, file_path)
	print("From "+str(number_of_users)+" users timelines analized, we've found "+str(number_of_errors)+
			" errors, that represent a "+str(round(p*100.,2))+"% of total")
	if len(different_errors)>0:
		print(different_errors)
		frequency_bar_graph(different_errors, min(10, len(different_errors)), "More frequent errors", oblue, "images/error_messages_in_h_index.png")

	# ********************************************
	# graph construction, just with non error users from h_index process
	# ********************************************
	people_data, directed_graph = get_relation_graph(people_data, api)
	nx.write_gml(directed_graph, "graph/relations_graph.gml")
	
	# directed_graph = nx.read_gml("graph/relations_graph.gml")
	
	print_basic_graph_properties(directed_graph, file_path = "graph/graph_properties.txt")

	ranked_users = get_users_centralities(people_data, directed_graph)

	return ranked_users

if __name__ == '__main__':
	try:
		start = time.time()
		print("%%%%%%%%%%%%%%%   Starting task at "+str(start))
		# ********************************************
		# read the data stored form user_selection process
		# ********************************************
		file_path = "tables/3_selected_users.xlsx"
		selected_users = read_df(file_path)
		ranked_users = get_ranked_users(selected_users)
		file_path = "tables/4_ranked_users.xlsx"
		save_df(ranked_users, file_path = file_path)
		print("%%%%%%%%%%%%%%%   time ellapsed "+str((time.time()-start)/60) + " minutes")
	except KeyboardInterrupt:
		print ('\nGoodbye! ')  


