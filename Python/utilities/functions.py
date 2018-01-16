import pandas as pd
import matplotlib.pyplot as plt
from copy import deepcopy
from collections import Counter

# *********************************************
# RGB project colors
# *********************************************

oyellow = [1,0.835294117647059,0.133333333333333]
oblue   = [0.0352941176470588,0.450980392156863,0.541176470588235]
ogreen1 = [0.0196078431372549,0.650980392156863,0.576470588235294]
ogreen2 = [0.0588235294117647,0.737254901960784,0.568627450980392]
ored    = [0.929411764705882,0.258823529411765,0.215686274509804]



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

def histogram_graph(vector, titulo, color, figure_path, percentage = True):
	vector_count = Counter(vector)
	deg, cnt = zip(*vector_count.items())
	if percentage:
		if sum(cnt) != len(vector):
			raise Exception("Problem in histogram: not the same original values than counted")
		cnt = [x/len(vector) for x in cnt]

	plt.clf()
	fig, ax = plt.subplots()
	plt.bar(deg, cnt, width=0.80, color=color)

	plt.title(titulo)
	# plt.ylabel("Count")
	# plt.xlabel("Degree")
	ax.set_xticks([d + 0.4 for d in deg])
	ax.set_xticklabels(deg)
	plt.savefig(figure_path)
	return
	
# *********************************************
# Saving Tables
# *********************************************	
def save_df(df, file_path = 'default_name.xlsx'):
	# Create a Pandas Excel writer using XlsxWriter as the engine.
	writer = pd.ExcelWriter(file_path, engine='xlsxwriter')
	# Convert the dataframe to an XlsxWriter Excel object.
	df.to_excel(writer, sheet_name='Sheet1')
	# Close the Pandas Excel writer and output the Excel file.
	writer.save()
	return

# *********************************************
# Reading Tables
# *********************************************	
def read_df(file_name, na_value = "None", convert_columns_to_string = True ):
	df = pd.DataFrame()
	if convert_columns_to_string: 
		df_columns = pd.read_excel(open(file_name, "rb"), sheetname = 'Sheet1', header = 0).columns
		converter = {col: str for col in df_columns} 
		df = pd.read_excel(open(file_name, "rb"), sheetname = 'Sheet1', header = 0, converters = converter)
	else:
		df = pd.read_excel(open(file_name, "rb"), sheetname = 'Sheet1', header = 0)
	return df.fillna(value = na_value)