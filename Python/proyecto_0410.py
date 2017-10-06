
# coding: utf-8

# # <font color='blue'>Getting Twitter and saving in MongoDB</font>
# 
# 

# ****** ******

# In[1]:

# get_ipython().system('mongod')


# In[2]:

# get_ipython().system('pip install pymongo')


# In[3]:

# Tweepy, Datetime e Json
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
#from datetime import datetime
import tweepy
import json
from tweepy.parsers import JSONParser
from pymongo import MongoClient


# In[4]:

consumer_key = "xxxxxxxxxxxxxxxxx"


# In[5]:

consumer_secret = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"


# In[6]:

access_token = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"


# In[7]:

access_token_secret = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"


# In[8]:

auth = OAuthHandler(consumer_key, consumer_secret)


# In[9]:

auth.set_access_token(access_token, access_token_secret)


# In[10]:

api=tweepy.API(auth, parser=JSONParser())


# In[11]:

tweets = api.search(q="Big Data",lang = "es", rpp=10, since_id=None, geocode="40.383333,-3.716667,300mi", show_user=True)


# In[12]:

tweets1 = json.dumps(tweets)


# In[13]:

tweets2 = json.loads(tweets1)


# In[14]:

client = MongoClient('localhost', 27017)


# In[15]:

db = client.twitterdb


# In[16]:

col = db.tweets 


# In[17]:

tweetsid = col.insert_one(tweets2).inserted_id


# In[18]:

for rec in db.tweets.find():
    print(rec)


# In[ ]:



