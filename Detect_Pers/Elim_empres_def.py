
# coding: utf-8

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
from datetime import datetime
from datetime import date, timedelta as td


# Acceder a las colecciones
MONGO_HOST= 'mongodb://localhost/tweetsdb'
client = MongoClient(MONGO_HOST)
db = client.tweetsdb
col = db.col_query1_spanish_stream


# Crear un dataframe con los datos
cursor1 = col.find()
dataframe = list(cursor1)
df = json_normalize(dataframe)


list(df.columns.values)





# Me quedo solo con algunos campos
df1=df.drop(df.columns.difference(['_id','source','user.description','user.id','user.name',
                                   'user.url','text','user.created_at','user.statuses_count']),1)


# In[7]:


# Convierte texto a minúsculas, tokeniza, quita acentos y "ñ"
def remove_accents(input_str):
    try:
        nfkd_form = unicodedata.normalize('NFKD', str(input_str))
        only_ascii = nfkd_form.encode('ascii', errors='ignore').decode('utf-8').replace(u'\xf1', 'n')
        text = only_ascii.lower()
    except NameError:
        pass
        
    return text


# In[8]:


# Obtener el nombre del orígen de los tweets
def get_source_name(x):
    value = re.findall(pattern="<[^>]+>([^<]+)</a>", string=x)
    if len(value) > 0:
        return value[0]
    else:
        return ""


# In[9]:


# Nueva columna con el nombre del orígen
df1["Source_name"] = df1["source"].apply(get_source_name)


# In[10]:


# Convierto el texto del campo Source_name
df1.loc[:, 'Source_name'] = df1['Source_name'].apply(remove_accents)


# In[11]:


# Convierto el texto del campo user.name 
df1.loc[:, 'user.name'] = df1['user.name'].apply(remove_accents)


# In[12]:


# Convierto el texto del campo user.description 
df1.loc[:, 'user.description'] = df1['user.description'].apply(remove_accents)


# In[13]:


# Elimino duplicados de usuarios (user.id) siempre y cuando tengan los campos seleccionados en subset iguales
df1 = df1.drop_duplicates(subset=("user.id","user.description","user.name","Source_name"))


# In[14]:


# Lista de herramientas o dispositivos para utomatizar tareas 
HH_device = ['ifttt','roundteam','botize',"statistics for it", "koica retweeter","tweet old post","powerapps and flow","voicestorm"]


# In[15]:


df1["User_type_source"] = np.where((df1['Source_name'].isin(HH_device)), 1,0)


# In[16]:


# Lista con nombres y apellidos de personas en español e ingles
nombres = [line.strip() for line in open('nombres.txt', 'r')]


# In[17]:


pat = '|'.join([r'\b{}\b'.format(x) for x in nombres]) # patrón para chequear en el user.name las coincidencias con los nombres de personas


# In[18]:


# Cuenta el total de palabras coincidentes con los nombres incluidos en la lista nombres 
def word_count(text):
    word_count = 0
    for word in text.split():
        if word in nombres:
            word_count += 1
        else:
            word_count
    return word_count


# In[19]:


def to_str(s):
    if s is None:
        return ''
    return str(s)


# In[20]:


from datetime import datetime
import re

#remove milliseconds
remove_ms = lambda x:re.sub("\+\d+\s","" , x)

#make string into a dataframe
mk_df = lambda x:datetime.strptime(remove_ms(x), "%a %b %d %H:%M:%S %Y")

# Format datetime object
my_form = lambda x:"{:%Y-%m-%d}".format(mk_df(x))


# In[21]:


# Obtener el numero de dias de antiguedad de la cuenta y poder dividirla por el numero de tweets obteniendo así la frecuencia.

df1["user.created_at"] = df1["user.created_at"].apply(my_form)
df1["user.created_at"]= pd.to_datetime(df1["user.created_at"])
df1['user_days'] =  pd.datetime.now().date()-df1["user.created_at"] 
df1['user_days']= df1['user_days'].dt.days


# In[22]:


# Frecuencia de publicacion
df1['tweets/day'] = round(df1["user.statuses_count"]/df1['user_days'],2)


# In[23]:


df1['user.url'] = df1['user.url'].apply(to_str)


# In[24]:


patron_4 = ('|'.join(['linked']))


# In[25]:


df1["Check_url"] = df1['user.url'].str.contains(patron_4).astype(int)


# In[26]:


# % de palabras incluidas en user.name que coinciden con la lista de nombres y apellidos en español e ingles
df1['Check_user name'] = (df1['user.name'].apply(word_count))*100/(df1['user.name'].str.split().str.len())


# In[27]:


# Lista de palabras que puede aparecer en la descripción si se trata de una persona
persona = ['emprendedor','persona', 'licenciado', 'ingeniero','freelance','licenciada','ingeniera','padre','madre','estudiante','consultor','director','directora',
          'person', 'graduated', 'engineer', 'father', 'mother', 'student', 'consultant', 'director']


# In[28]:


# Lista de palabras que no deberían aparecer en la descripción si se trata de una persona
no_persona = [line.strip() for line in open('term_emp.txt', 'r')]


# In[29]:


# patrón de búsqueda de las palabras incluidas en la lista persona y en la de no_persona
patron_2 = '|'.join([r'\b{}\b'.format(x) for x in persona]) 
patron_3 = '|'.join([r'\b{}\b'.format(x) for x in no_persona]) 


# In[30]:


# Incluir una nueva columna con valor 1 si la columna user.description contiene alguna de las palabras en la lista persona
df1["Check_descrip_1"] = (df1['user.description'].str.contains(patron_2).astype(int)|(~df1['user.description'].str.contains(patron_3))|(~df1['user.name'].str.contains(patron_3))).astype(int)


# In[31]:


# Variable con la condicion para asignar cada tweet a una persona o a una empresa

cond= (((df1["Check_descrip_1"] == 1) & (df1['Check_user name'] >= 30) & (df1['tweets/day'] <= 350 ) & (df1["User_type_source"] != 1))|(df1['Check_url'] == 1))


# In[32]:


# Asignar a la columna es_persona 1 con la condicion anterior
df1['Es_persona']=cond.astype(int)


# In[33]:


#df1[:20]


# In[34]:


#df1.applymap(type) # comprobar tipos


# In[35]:


df1['_id'] = df1['_id'].astype(str) # cambiar el tipo de la columna para poder exportar a excel


# In[36]:


#df1.applymap(type) # comprobar tipos


# In[37]:


writer = pd.ExcelWriter('/Users/Silvia/Filtro_pers_26_01.xlsx', engine='xlsxwriter')
df1.to_excel(writer,'Sheet1')
writer.save()

