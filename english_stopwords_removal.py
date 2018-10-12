import operator 
import sqlite3
from nltk import *
from nltk.corpus import knbc
from nltk.corpus import jeita
from collections import Counter
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import string
import nltk.tokenize.api
import tinysegmenter
import re

emoticons_str = r"""
	(?:
		[:=;] # Eyes
		[oO\-]? # Nose (optional)
		[D\)\]\(\]/\\OpP] # Mouth
	)"""
regex_str = [
    emoticons_str,
    r'<[^>]+>', # HTML tags
    r'(?:@[\w_]+)', # @-mentions
    r"(?:\#+[\w_]+[\w\'_\-]*[\w_]+)", # hash-tags
    r'http[s]?://(?:[a-z]|[0-9]|[$-_@.&amp;+]|[!*\(\),]|(?:%[0-9a-f][0-9a-f]))+', # URLs
    r'(?:(?:\d+,?)+(?:\.?\d+)?)', # numbers
    r"(?:[a-z][a-z'\-_]+[a-z])", # words with - and '
    r'(?:[\w_]+)', # other words
    r'(?:\S)' # anything else
]
tokens_re = re.compile(r'('+'|'.join(regex_str)+')', re.VERBOSE | re.IGNORECASE)
emoticon_re = re.compile(r'^'+emoticons_str+'$', re.VERBOSE | re.IGNORECASE)

def tokenize(s):
	return tokens_re.findall(s)
def preprocess(s, lowercase=False):
	tokens = tokenize(s)
	if lowercase:
		tokens = [token if emoticon_re.search(token) else token.lower() for token in tokens]
	return tokens
def remove_words():
	palavras = ['RT','n','…','i','。','2017','️','°','、','c','the',
				'！',':/','last','mm','everyone','damn','de','0.0','nme','0',
				'like','2','co','today','A','nhttps','1','5',"can't",'0.00',
				"i'm",'h','f','one','e','🔥','6','4','20',"https://t.co/qxmMbBWQ4H',)",
				'day','go','’',"it's",'3','the','this','new','world','「','」','7',
				'new','😭','00','17','em','pm', ':\\','da','slowly','10','th','my','❤',
				'via','-','☀','(',')','~','..','・','"','SP','https','a','b','c','d','e',
				'f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','x',
				'w','y','z','us', "『", "』",'【','】','170820','8','08','-','😍','🏾','“','19',
				' (','่','19']
	return palavras
conn = sqlite3.connect('streaming_english_test.sqlite')
cur = conn.cursor()
punctuation = list(string.punctuation)
stop = stopwords.words('english')+punctuation+remove_words()
stops = [stops.lower() for stops in stop]
count_all = Counter()
result = cur.execute('SELECT message FROM tweets')
for lines in result:
	line=[line.lower() for line in lines]
	terms_stop = [term for term in preprocess(str(line)) if term not in stops]
	count_all.update(terms_stop)
print(count_all.most_common(100))
conn.commit()
conn.close()