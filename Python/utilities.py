import pandas as pd
import matplotlib.pyplot as plt
from copy import deepcopy



# *********************************************
# Plots
# *********************************************
def frequency_bar_graph(vector, toprint, titulo, color, figure_path):
	from copy import deepcopy
	h = deepcopy(vector)
	occ = [1]*len(h)
	new_df = pd.DataFrame({'h':h,'occ':occ })	
	# para cada hashtag, nos quedamos con el número de veces que ha aparecido
	new_df2 = new_df.groupby(new_df['h'], as_index = False).count()
	hashtags = [x for x in new_df2["h"]]
	occurrences = [x for x in new_df2["occ"]]
	list1, list2  = zip(*sorted(zip(occurrences, hashtags), reverse=True))
	# for i in range(toprint):
		# print ("El hashtag "+str(list2[i])+" ha aparecido " + str(list1[i]) + " veces")
	idx = [x for x in range(toprint)]
	plt.clf()
	fig,ax = plt.subplots()
	ax.bar(idx, list1[:toprint], width=0.8, color=color, )
	ax.set_xticks(idx)
	ax.set_xticklabels(list2[:toprint], rotation=90)
	plt.xlabel("")
	plt.tight_layout()
	plt.title(titulo)
	plt.savefig(figure_path)
	return
	
def highlighted_pie_graph(sizes, labels, explode, colors, file_path):	
	plt.clf()
	fig1, ax1 = plt.subplots()
	ax1.pie(sizes, 
			explode=explode, 
			labels=labels, 
			autopct='%1.1f%%',
			shadow=True, 
			startangle=90,
			colors = colors)
	ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
	# plt.show()
	plt.savefig(file_path)
	return