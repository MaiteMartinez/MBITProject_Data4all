
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
df1=df.drop(df.columns.difference(['_id','lang','source','user.description','user.id','user.lang','user.name','user.screen_name','user.url','text']),1)


# Convierte texto a minúsculas, tokeniza, quita acentos y "ñ"
def remove_accents(input_str):
    try:
        nfkd_form = unicodedata.normalize('NFKD', str(input_str))
        only_ascii = nfkd_form.encode('ascii', errors='ignore').decode('utf-8').replace(u'\xf1', 'n')
        text = only_ascii.lower()
    except NameError:
        pass
        
    return text


# Convierto el texto del campo user.name 
df1.loc[:, 'user.name'] = df1['user.name'].apply(remove_accents)


# Lista con nombres y apellidos de personas en español e ingles
nombres = [line.strip() for line in open('nombres.txt', 'r')]


pat = '|'.join([r'\b{}\b'.format(x) for x in nombres]) # patrón para chequear en el user.name las coincidencias con los nombres de personas




# Cuenta el total de palabras coincidentes con los nombres incluidos en la lista nombres 
def word_count(text):
    word_count = 0
    for word in text.split():
        if word in nombres:
            word_count += 1
        else:
            word_count
    return word_count


# % de palabras incluidas en user.name que coinciden con la lista de nombres y apellidos en español e ingles
df1['Check_user name'] = (df1['user.name'].apply(word_count))*100/(df1['user.name'].str.split().str.len())


# Convierto el texto del campo user.description 
df1.loc[:, 'user.description'] = df1['user.description'].apply(remove_accents)


# Lista de palabras que puede aparecer en la descripción si se trata de una persona
persona = ['emprendedor','persona', 'licenciado', 'ingeniero','freelance','licenciada','ingeniera','padre','madre','estudiante','consultor','director','directora']


# Lista de palabras que no deberían aparecer en la descripción si se trata de una persona
no_persona = [line.strip() for line in open('term_emp.txt', 'r')]


# patrón de búsqueda de las palabras incluidas en la lista persona y en la de no_persona
patron_2 = '|'.join([r'\b{}\b'.format(x) for x in persona]) 
patron_3 = '|'.join([r'\b{}\b'.format(x) for x in no_persona]) 


# Incluir una nueva columna con valor 1 si la columna user.description contiene alguna de las palabras en la lista persona
df1["Check_descrip_1"] = (df1['user.description'].str.contains(patron_2).astype(int)|(~df1['user.description'].str.contains(patron_3))|(~df1['user.name'].str.contains(patron_3))).astype(int)


# Variable con la condicion para asignar cada tweet a una persona o a una empresa

cond= (df1["Check_descrip_1"] == 1) & (df1['Check_user name'] >= 30)


# Asignar a la columna es_persona 1 con la condicion anterior
df1['Es_persona']=cond.astype(int)



#df1.applymap(type) # comprobar tipos


df1['_id'] = df1['_id'].astype(str) # cambiar el tipo de la columna para poder exportar a excel


#df1.applymap(type) # comprobar tipos


writer = pd.ExcelWriter('/Users/Silvia/Filtro_pers.xlsx', engine='xlsxwriter')
df1.to_excel(writer,'Sheet1')
writer.save()

