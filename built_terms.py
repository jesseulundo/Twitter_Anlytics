import operator 
import sqlite3
from nltk import *
from nltk.corpus import knbc
from nltk.corpus import jeita
from collections import Counter
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import string
import zlib
import time
import nltk.tokenize.api
import tinysegmenter
import re
import math
from textblob import TextBlob as tb

conn = sqlite3.connect('streaming_data.sqlite')
cur = conn.cursor()

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
def tf(word, blob):
	return blob.words.count(word)/len(blob.words)
def n_containing(word, bloblist):
	return sum(1 for blob in bloblist if word in blob.words)
def idf(word, bloblist):
	return math.log(len(bloblist)/(1+n_containing(word, bloblist)))
def tfidf(word, blob, bloblist):
	return tf(word, blob) * idf(word, bloblist)



segmenter = tinysegmenter.TinySegmenter()
count_all = Counter()

def j_stopwords():
	japanese_stopwords = ["これ", "それ", "あれ", "この", "その", "あの", "ここ", "そこ", "あそこ", "こちら",
						"どこ", "だれ", "なに", "なん", "何", "私", "貴方", "貴方方", "我々", "私達",
						"あの人", "あのかた", "彼女", "彼", "です", "あります", "おります", "います", "は", 
						"が", "の", "に", "を", "で", "え", "から", "まで", "より", "も", "どの", "と", "し",
						"それで", "しかし", "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l",
						"m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z", ".", 
						",", '"', "'", "/", "|", "?", "!", ";", "*", ":", "+", '\\', "_", "の", "に",
						"は", "を", "た", "が", "で", "て", "と", "し", "れ", "さ", "ある"," いる", "も", "する", 
						"から", "な", "こと", "として", "い", "や", "れる", "など", "なっ", "ない", "この", "ため", 
						"その", "あっ", "よう", "また", "もの", "という", "あり", "まで", "られ", "なる", "へ", "か", 
						"だ", "これ", "によって", "により", "おり", "より", "による", "ず", "なり", "られる", "において",
						"ば", "なかっ", "なく", "しかし", "について", "せ", "だっ", "その後", "できる", "それ", "う", 
						"ので", "なお", "のみ", "でき", "き", "つ", "における", "および", "いう", "さらに", "でも", 
						"ら", "たり", "その他", "に関する", "たち", "ます", "ん", "なら", "に対して", "特に", "せる", "及び", 
						"これら", "とき", "では", "にて", "ほか", "ながら", "うち", "そして", "とともに", "ただし", "かつて", 
						"それぞれ", "または", "お", "ほど", "ものの", "に対する", "ほとんど", "と共に", "といった", "です", 
						"とも", "ところ", "ここ", "あっ", "あり", "ある", "い", "いう", "いる", "う", "うち", "お", "および",
						"おり", "か", "かつて", "から", "が", "き", "ここ", "こと", "この", "これ", "これら", "さ", "さらに",
						"し", "しかし", "する", "ず", "せ", "せる", "そして", "その", "その他", "その後", "それ","️️",
						"それぞれ", "た", "ただし", "たち", "ため", "たり", "だ", "だっ", "つ", "て", "で", "でき",'×',
						"できる", "です", "では", "でも", "と", "という", "といった", "とき", "ところ", "として", "とともに",
						"とも", "と共に", "な", "ない", "なお", "なかっ", "ながら", "なく", "なっ", "など", "なら",'→','／',
						"なり", "なる", "に", "において", "における", "について", "にて", "によって", "により","による",'🗻',
						"に対して", "に対する", "に関する", "の", "ので", "のみ", "は", "ば", "へ", "ほか", "ほとんど",'×',
						"ほど", "ます", "また", "または", "まで", "も", "もの", "ものの", "や", "よう", "より", "ら", "られ",
						"られる", "れ", "れる", "を", "ん", "及び", "特に", "、", "。", "年", "「", "」", "月", "『", "』",
						"(", ")", "`", "``", "',", "'RT", "&",'\\n','\\u3000',',)','。\\','u3000','://','.co','T',
						"…'",'！\\','\\nhttps',',\\',"'【",'1','nhttps','】\\','！！','10','\\n日本','【','0','？\\',
						'」\\','4','8','n2017','...','08',')\\','2','\\u3000す','.\\','\\u3000の','：','00','\\u3000な',
						'｣','💗💗','♪\\','「丹','✨\\','\\u3000り','gt','\\u3000お','\\u3000い','▷\\','\\nいい','^Y','』\\',
						'18','5','）\\','→\\','……','＃',')\\n','\\u3000に','（','🍦💓','🍦⭐','️🍦','💓\\n', '\\u3000 ま',"。'",
						'…\\','(^','1960','…','！','】','・','さん','）','？','─','ヽ','━','〜','┃','～','🌸','＼','あ','️️','__',
						'い','う','え','お','か','き','く','け','こ','た','ち','つ','て','と','さ','し','す','せ','そ','が','ぎ','ぐ',
						'げ','ご','ざ','じ','ず','ぜ','ぞ','だ','ぢ','づ','で','ど','な','に','ぬ','ね','の','は','ひ','ふ','へ','ほ',
						'ば','び','ぶ','べ','ぼ','ぱ','ぴ','ぷ','ぺ','ぽ','ま','み','む','め','も','や','ゆ','よ','ら','り','る','れ',
						'ろ','わ','を','ん', 'RT']
	return japanese_stopwords
result = cur.execute("SELECT message FROM tweets WHERE date BETWEEN 'Fri Sep 08 00:00:00 +0000 2017' AND 'Fri Sep 08 23:59:59 +0000 2017'")
punctuation = list(string.punctuation)
stop = stopwords.words('english') + punctuation +j_stopwords()
for lines in result:
	segments = [segmenter.tokenize(x) for x in preprocess(lines[0])]
	for i, s in enumerate(segments):
		if "https" in s:
			segments[i] = ["".join(s)]
	
	#print(segmenter.tokenize(lines[0]))
	#terms_all = [term for term in segmenter.tokenize(preprocess(str(lines))) if term not in stop]
	segments = [item for segment in segments for item in segment]
	#print(segments)
	terms_all = [term for term in segments if term not in stop]
	terms_all = [term for term in terms_all if not term.isdigit()]

	count_all.update(terms_all)
	terms_single = set(terms_all)	

most_common = count_all.most_common(300)
sorted(most_common,key=lambda x:x[1])
most_common = dict(most_common)
print(most_common)

for c, vl in most_common.items():
	cur.execute('''insert or ignore into term_frequency (term, amount)
	values (?, ?)''', (c, vl))
	
x = sorted(most_common, key=most_common.get, reverse=True)
highest = None
lowest = None
for k in x[:100]:
	if highest is None or highest < most_common[k]:
		highest = most_common[k]
	if lowest is None or lowest > most_common[k]:
		lowest = most_common[k]
print('Range of most_common:',highest,lowest)

bigsize = 80
smallsize = 20

fhand = open('twtword1.js','w', encoding='utf-8')
fhand.write("twtword1 = [")
first = True
for k in x[:100]:
	if not first : fhand.write( ",\n")
	first = False
	size = most_common[k]
	size = (size - lowest) / float(highest - lowest)
	size = int((size * bigsize) + smallsize)
	fhand.write("{text: '"+k+"', size: "+str(size)+"}")
fhand.write("\n];\n")

print("Output written to twtword1.js")
print("Open twtword.htm in a browser to see the vizualization")

conn.commit()	
conn.close()