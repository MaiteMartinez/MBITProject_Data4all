
# coding: utf-8

# In[1]:


import numpy as np
import pandas as pd
from pymongo import MongoClient
import string
import re
import nltk
from nltk.tokenize import TweetTokenizer
import pprint
from pandas.io.json import json_normalize
import unicodedata
from pandas import ExcelWriter #para exportar a excel


# In[2]:


# Acceder a las colecciones
MONGO_HOST= 'mongodb://localhost/tweetsdb'
client = MongoClient(MONGO_HOST)
db = client.tweetsdb
col = db.col_query1_spanish_stream


# In[3]:


# Crear un dataframe con los datos
cursor1 = col.find()
dataframe = list(cursor1)
df = json_normalize(dataframe)


# In[4]:


list(df.columns.values)


# In[5]:


# Me quedo solo con algunos campos
df1=df.drop(df.columns.difference(['_id','lang','source','user.description','user.id','user.lang','user.name','user.screen_name','user.url','text']),1)


# In[6]:


# Convierte texto a minúsculas, tokeniza, quita acentos y "ñ"
def remove_accents(input_str):
    try:
        nfkd_form = unicodedata.normalize('NFKD', str(input_str))
        only_ascii = nfkd_form.encode('ascii', errors='ignore').decode('utf-8').replace(u'\xf1', 'n')
        text = only_ascii.lower()
    except NameError:
        pass
        
    return text


# In[7]:


# Convierto el texto del campo user.name 
df1.loc[:, 'user.name'] = df1['user.name'].apply(remove_accents)


# In[8]:


# Lista con nombres y apellidos de personas en español e ingles
nombres = [line.strip() for line in open('nombres.txt', 'r')]


# In[9]:


pat = '|'.join([r'\b{}\b'.format(x) for x in nombres]) # patrón para chequear en el user.name las coincidencias con los nombres de personas


# In[10]:


# Cuenta el total de palabras coincidentes con los nombres incluidos en la lista nombres 
def word_count(text):
    word_count = 0
    for word in text.split():
        if word in nombres:
            word_count += 1
        else:
            word_count
    return word_count


# In[11]:


def to_str(s):
    if s is None:
        return ''
    return str(s)


# In[12]:


df1['user.url'] = df1['user.url'].apply(to_str)


# In[13]:


patron_4 = ('|'.join(['linked', 'blog']))


# In[14]:


df1["Check_url"] = df1['user.url'].str.contains(patron_4).astype(int)


# In[15]:


# % de palabras incluidas en user.name que coinciden con la lista de nombres y apellidos en español e ingles
df1['Check_user name'] = (df1['user.name'].apply(word_count))*100/(df1['user.name'].str.split().str.len())


# In[16]:


# Convierto el texto del campo user.description 
df1.loc[:, 'user.description'] = df1['user.description'].apply(remove_accents)


# In[17]:


# Lista de palabras que puede aparecer en la descripción si se trata de una persona
persona = ['emprendedor','persona', 'licenciado', 'ingeniero','freelance','licenciada','ingeniera','padre','madre','estudiante','consultor','director','directora']


# In[18]:


# Lista de palabras que no deberían aparecer en la descripción si se trata de una persona
no_persona = [line.strip() for line in open('term_emp.txt', 'r')]


# In[19]:


# patrón de búsqueda de las palabras incluidas en la lista persona y en la de no_persona
patron_2 = '|'.join([r'\b{}\b'.format(x) for x in persona]) 
patron_3 = '|'.join([r'\b{}\b'.format(x) for x in no_persona]) 


# In[20]:


# Incluir una nueva columna con valor 1 si la columna user.description contiene alguna de las palabras en la lista persona
df1["Check_descrip_1"] = (df1['user.description'].str.contains(patron_2).astype(int)|(~df1['user.description'].str.contains(patron_3))|(~df1['user.name'].str.contains(patron_3))).astype(int)


# In[21]:


# Variable con la condicion para asignar cada tweet a una persona o a una empresa

cond= ((df1["Check_descrip_1"] == 1) & (df1['Check_user name'] >= 30))|(df1['Check_url'] == 1)


# In[22]:


# Asignar a la columna es_persona 1 con la condicion anterior
df1['Es_persona']=cond.astype(int)


# In[23]:


df1[:20]


# In[24]:


#df1.applymap(type) # comprobar tipos


# In[25]:


df1['_id'] = df1['_id'].astype(str) # cambiar el tipo de la columna para poder exportar a excel


# In[26]:


#df1.applymap(type) # comprobar tipos


# In[27]:


writer = pd.ExcelWriter('/Users/Silvia/Filtro_pers.xlsx', engine='xlsxwriter')
df1.to_excel(writer,'Sheet1')
writer.save()

