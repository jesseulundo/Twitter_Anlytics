import MeCab
import sqlite3
import operator
import sys
import os
from JapaneseTokenizer import JumanWrapper
from JapaneseTokenizer import JumanppWrapper
from JapaneseTokenizer import MecabWrapper
from JapaneseTokenizer import KyteaWrapper
from JapaneseTokenizer.datamodels import TokenizedResult
from JapaneseTokenizer import init_logger
from nltk.corpus import stopwords
from jNlp.jProcessing import Similarities
from jNlp.jSentiments import*
from nltk import *
from nltk.tokenize import word_tokenize
import string
import logging
import socket
import six
import pandas as pd
import numpy as np
from pandas import DataFrame, Series

#connecting to database
conn = sqlite3.connect('streaming_data.sqlite')
cur = conn.cursor() 
stop_words=[]

#Selecting the messages
result = cur.execute("SELECT  message FROM tweets WHERE date LIKE '% Nov%'")
#result = cur.execute("SELECT message FROM tweets WHERE date LIKE '%Oct%'")
fhand = open('ja_stopword.txt', encoding ="utf-8")
#parsing the Japanese stop words
count = 0
for words in fhand:
	words = words.strip('\n')
	if words not in stop_words:
		stop_words.append(words)
punctuation = list(string.punctuation)		
jp_stop_words = stop_words + stopwords.words('english') + punctuation + ["RT", '', ' ' ]

#parsing and tokenizing twitts fro the database
output = []
#result = result.fetchall()
#conn.close()
jumanpp_wrapper = JumanppWrapper()
jp_wn = 'wnjpn-all.tab'
en_swn = 'SentiWordNet_3.0.0_20130122.txt'
classifier = Sentiment()
classifier.train(en_swn, jp_wn)
for sentences in result.fetchall():
	
	try:
		sentences = sentences[0]
		msg_tokenized = jumanpp_wrapper.tokenize(sentence=sentences, is_feature=False, is_surface=False).convert_list_object()
		print(msg_tokenized)
		filtered_sentences = [w for w in msg_tokenized if not w in jp_stop_words]
		filtered_sentences = [item.replace(' ', '' ) for item in filtered_sentences]
		print('============SENTIMENT RESULTS===================')	
		#print(sentences, classifier.baseline(str(filtered_sentences)))
		data = classifier.baseline(str(filtered_sentences))
		output.append((sentences, data[0], data[1]))
		count = count +1
		print(count, sentences, data)
		#atentado para escrever para o tipo de ficheiro csv
		#df.to_cvs('trying_csv_file.csv', index=False, header=False)
	except: pass

output = pd.DataFrame(output,columns=["sentence","pScore","nScore"])
output["classification"] = "Neutral"
output.loc[output.pScore > output.nScore, "classification"] = "Positive"
output.loc[output.pScore < output.nScore, "classification"] = "Negative"
print(output)
#df = pd.read_sql()
#output.to_sql("sent", conn, flavor = None, schema = None, if_exists='append', chunksize=None, dtype=None)

#output.to_csv("sentiment_Aug_test.csv", mode = 'a', index=False,encoding="utf-8")
output.to_excel("sentiment_Nov.xlsx", index=False)
#output.to_excel("sentiment_Aug_test.xlsx", startrow=len(output)+1, index=False)


#cur.execute("insert or ignore into sent (sentiments, sent_classifier) VALUES (?, ?) ", (sentences, classifier.baseline(str(filtered_sentences))))
#conn.commit()
	
conn.close()





