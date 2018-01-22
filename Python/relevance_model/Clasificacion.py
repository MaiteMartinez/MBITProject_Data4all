
import os
import numpy as np
import pandas as pd
import string
import datetime
import unicodedata
import json
import pymongo
import tweepy
import re
import nltk
import pickle
from collections import Counter
from nltk.tokenize import TweetTokenizer
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cross_validation import train_test_split
from sklearn.metrics import roc_auc_score


def remove_stopwords(text):
    #remove URL
    text = re.sub(r'http\S+','',text)
    text = re.sub(r'\d{1,9}','',text)
   
    # remove punctuaction
    regex = re.compile('[%s]'% re.escape(string.punctuation))

    a=[]
    words = text.split()
    #print(words)
    for i in words:
    
        new_token = regex.sub(u'',i)
        if not new_token == u'':
            a.append(new_token)

    # remove accentuation
    clean_text=[]
    for word in a:
        nfkd = unicodedata.normalize('NFKD',word)
        sin_ac = u''.join([c for c in nfkd if not unicodedata.combining(c)])
        q = re.sub('[^a-zA-Z0-9 \\\]',' ',sin_ac)
        
        clean_text.append(q.lower().strip())

    # remove stopwords spanish and english
    punct = list(string.punctuation)
    stopwords = nltk.corpus.stopwords.words('spanish') + nltk.corpus.stopwords.words('english') +punct + ['rt','via','...','¿','si','cómo','“','”','¡','q','esas','cosas','https']
    content = [w for w in clean_text if w.lower().strip() not in stopwords]
    #print(content)
   
    # remove digit and small word
    tokens= [t for t in content if len(t)>2 and not t.isdigit()]
    ct = ' '.join(tokens)

    return ct


# funcao para limpar o conteudo source
def get_source_name(x):
    value = re.findall(pattern="<[^>]+>([^<]+)</a>", string=x)
    if len(value) > 0:
        return value[0]
    else:
        return ""

# funcion para devolver los contenidos de "hashtags"
def get_hashtags(tweets):
    entities = tweets.get('entities',{})
    hashtags = entities.get('hashtags',{})
    return [tag['text'].lower() for tag in hashtags]

# funcion para devolver los contenidos de "mentions"
def get_mentions(tweets):
    entities = tweets.get('entities',{})
    mentions = entities.get('user_mentions',{})
    return [tag['screen_name'].lower() for tag in mentions]

# funcion para generar un dataframe com algunas variables del tweeter
# Con ese dataframe sera utilizado para generar un muestreo para ser etiquetado
def process_results(results):
    id_list = [tweet["id_str"] for tweet in results]
    data_set = pd.DataFrame(id_list, columns=["id_str"])

    # Processando os Dados do Tweet 
    data_set["text"] = [remove_stopwords(tweet["text"]) for tweet in results]
    data_set["text0"]= [tweet["text"] for tweet in results]
    data_set["created_at"] = [tweet["created_at"] for tweet in results]
    data_set["retweet_count"] = [tweet["retweet_count"] for tweet in results]
    data_set["favorite_count"] = [tweet["favorite_count"] for tweet in results]

    # usando la funcion para limpiar y volver con el "source"
    data_set["source"] = [get_source_name(tweet["source"]) for tweet in results]

    # Procesando los datos del usuario
    data_set["user_id"]          = [tweet["user"]["id_str"] for tweet in results]
    data_set["user_screen_name"] = [tweet["user"]["screen_name"] for tweet in results]
    data_set["user_name"]        = [tweet["user"]["name"] for tweet in results]
    data_set["user_created_at"]  = [tweet["user"]["created_at"] for tweet in results]
    data_set["user_description"] = [tweet["user"]["description"] for tweet in results]
    data_set["user_followers_count"] = [tweet["user"]["followers_count"] for tweet in results]
    data_set["user_friends_count"]   = [tweet["user"]["friends_count"] for tweet in results]
    data_set["user_location"]        = [tweet["user"]["location"] for tweet in results]
    data_set["favourites_count"]     = [tweet["user"]["favourites_count"] for tweet in results]
    data_set["statuses_count"]       = [tweet["user"]["statuses_count"] for tweet in results]
    # Procesando los datos de hashtags y mentions
    data_set["hashtags"] = [get_hashtags(tweet) for tweet in results]
    data_set["mentions"] = [get_mentions(tweet) for tweet in results]
    # Convertendo as datas(fechas) e criando uma coluna tempo de usuario do twitter em dias
    data_set['created_at'] = pd.to_datetime(data_set.created_at)
    data_set['user_created_at'] = pd.to_datetime(data_set.user_created_at)
    data_set['tempo'] = (datetime.date.today() - data_set.user_created_at.dt.date)

    return data_set

# Construindo el modelo
def crear_modelo(df0):
    # Generando 2 dataframe : texto y etiqueta
    df_y = df0.status
    df_x = df0.text

    #  Separando los datos entre treino y teste
    x_train, x_test, y_train, y_test = train_test_split(df_x, df_y, test_size=0.2, random_state=42)

    #
    cv = TfidfVectorizer(use_idf=True, strip_accents = 'ascii', lowercase=True)
    x_traincv = cv.fit_transform(x_train)
    y_train = y_train.astype("int")

    # Construindo el modelo y entrenando el modelo
    mnb = MultinomialNB().fit(x_traincv, y_train)

    # Aplicando el modelo en la base de teste
    x_testcv=cv.transform(x_test)
    pred = mnb.predict(x_testcv)

    # Generando la acuracia
    roc_auc_score(y_test, mnb.predict_proba(x_testcv)[:,1])

    # Salvando o modelo

    arquivo = 'c:\mbit\proyecto\modelo_nb.sav'
    pickle.dump(mnb, open(arquivo,'wb'))
    return arquivo

# Procesando el modelo a partir del modelo salvo (modelo_nb.sav)
def procesando_modelo(arquivo,data_set):
    # Cargando el modelo para aplicarlo
    modelo_v1 = pickle.load(open(arquivo,'rb'))

    # Aplicando el modelo en la base final
    # Para aplicar el modelo el campo 'text' deve estar "limpo" igual como fue hecho por aqui. Eso porque
    # el modelo fue entrenado asi....
    cv = TfidfVectorizer(use_idf=True, strip_accents='ascii', lowercase=True)
    c = 0
    for i in range(len(data_set)):

        a = [data_set['text'][i]]
        b = cv.fit_transform(a)
        print("*******************"+str(a)+"**************"+str(b))

    
        pred_x = modelo_v1.predict(b)

        data_set.set_value(i,'status',pred_x[0])
        if pred_x >= 0.80:
            c = c+1
            t_st = pred_x[0]
            
        i = i + 1
    print(c)
    # df_pred = data_set[data_set.status == 1]
    # df_users = df_pred.groupby('user_id').status.count()
    # return df_users
    return data_set["status"]

if __name__ == '__main__':
    try:
        #Criando a conexão ao MongoDB
        cliente1 = pymongo.MongoClient('localhost', 27017)
        db = cliente1.twitterdb_final
        # Criando a collection "col"
        col = db.tweets_final
        # Generando el cursor con las informaciones de la base tweets del mongodb
        results = []
        tweet_cursor = col.find()
        for tweet in tweet_cursor:
            results.append(tweet)

        # Procesando el dataframe con algunas variables del tweet y del usuario
        data_set = process_results(results)

        # Exportando el dataframe para excell (para analise)
        # data_set.to_excel('saida1.xlsx','Sheet1')

        # Generando una muestra para clasificacion de los twitter entre 0 e 1 (no y si es un tuit de datascience)
        #ds_sample = data_set.sample(n=2000, random_state=45)

        # export to excel la muestra para clasificacion
        # ds_sample.to_excel('ds_sample2.xlsx')

        # volviendo con la muestra(excel) clasificado
        #df0 = pd.read_excel('c:\mbit\proyecto\ds_sample2.xls')

        # Creando el modelo
        #nb_modelo = crear_modelo(df0)

        # Procesando el modelo
        procesando = procesando_modelo('c:\mbit\proyecto\modelo_nb.sav',data_set)

    except KeyboardInterrupt:
        print ('\nGoodbye! ')



