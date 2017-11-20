import sys, string, os
import pymongo
from pymongo.errors import ServerSelectionTimeoutError
import subprocess

class MongoDBConnection:
	def __init__(self, mongo_server_path_file):
		s = subprocess.check_output('tasklist', shell=True)
		if ("mongod.exe" not in str(s)):
			print("MongoDB connection not available, opening one")
			path_file  = open(mongo_server_path_file, "r") 
			mypath = eval(path_file.read())["MongoDB_path"]
			retval = os.getcwd()
			print ("Current working directory %s" % retval)
			os.chdir(mypath)
			print ("Changed to %s" % mypath)
			os.system("mongod.exe")
			os.chdir(retval)
			print ("Back to %s" % retval)
			print("********************" + str(mongo_conn.client.database_names()))
		else:
			print("Connecting with current MongoDB")
		self.client = pymongo.MongoClient('localhost', 27017)
		try:
			info = self.client.server_info() # Forces a call.			
		except ServerSelectionTimeoutError:
			print("Server is down.")
		
		

	def closeConnection(self):
		self.client.close()

if __name__ == '__main__':
	try:
		print("%%%%%%%%%%%%%%%   probando mongodb connector")
		mongo_conn = MongoDBConnection("set_up.py")
		print(mongo_conn.client.database_names())
		spurious_db = ['query1_spanish_stream','query1', 'query2_spanish', 'test', 'twitter_data_base', 'twitter_db']
		for db_name in spurious_db: mongo_conn.client.drop_database(db_name)
		print(mongo_conn.client.database_names())
	except KeyboardInterrupt:
		print ('\nGoodbye! ')  