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
			file = mypath + "mongod.exe"
			subprocess.call([file])
		else:
			print("Connecting with current MongoDB")
		self.client = pymongo.MongoClient('localhost', 27017)
		print("********************" + str(self.client.database_names()))
		try:
			info = self.client.server_info() # Forces a call.			
		except ServerSelectionTimeoutError:
			print("Server is down.")
		
		

	def closeConnection(self):
		self.client.close()

if __name__ == '__main__':
	try:
		# connection to mongodb
		conn = MongoDBConnection("set_up.py")
	except KeyboardInterrupt:
		print ('\nGoodbye! ')  