import sys, string, os
import pymongo

class MongoDBConnection:
	def __init__(self, mongo_server_path_file):
		path_file  = open(mongo_server_path_file, "r") 
		mypath = eval(path_file.read())["MongoDB_path"]
		retval = os.getcwd()
		print ("Current working directory %s" % retval)
		os.chdir(mypath)
		print ("Changed to %s" % mypath)
		os.system("mongod.exe")
		self.client = pymongo.MongoClient('localhost', 27017)
		os.chdir(retval)
		print ("Back to %s" % retval)


