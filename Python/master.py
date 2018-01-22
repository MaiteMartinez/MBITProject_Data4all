 
from db_to_table import *
from descrptives import *
from user_selection import *
from user_rank import *


# *********************************************
# Run all processes
# *********************************************

def run_all_processes():
	data_base_name = "query1_spanish_stream"
	set_up_path = "keys/set_up.py"
	
	# descriptives
	run_descriptives(data_base_name, set_up_path)

	# db_to_table
	all_tweets_data = create_tables(data_base_name, set_up_path)
	# user_selection
	selected_users = select_users(all_tweets_data)
	file_path = "tables/3_selected_users.xlsx"
	save_df(selected_users, file_path = file_path)
	# user_rank
	ranked_users = get_ranked_users(selected_users)
	file_path = "tables/4_ranked_users.xlsx"
	save_df(ranked_users, file_path = file_path)

	print ("Finished Process, data ready for visualization")



if __name__ == '__main__':

	try:
		print("%%%%%%%%%%%%%%%   Starting task at "+str(datetime.datetime.now()))
		run_all_processes()
	except KeyboardInterrupt:
		print ('\nGoodbye! ')  