import operator
import sqlite3
from nltk import *
from nltk.corpus import knbc
from nltk.corpus import jeita
from collections import Counter
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import string
import time
import zlib
import nltk.tokenize.api
import tinysegmenter
import re
import math
import pandas as pd
import numpy as np
from textblob import TextBlob as tb
from collections import defaultdict

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
						'ろ','わ','を','ん','rt','RT','ああ']
	return japanese_stopwords

def join_if_url(ls):
	if "http" in ls[0]:
		return "".join(ls)
	return ls
	
def list_to_str(ls):
	return "[" + ",".join(["'{}'".format(x) if type(x) is str else str(x) for x in ls]) + "]"
	
punctuation = list(string.punctuation)
stop = stopwords.words('english') + punctuation +j_stopwords()

cur.execute('SELECT message, date FROM tweets')
	
df = pd.DataFrame(cur.fetchall(),columns=["tweets","date"])
df.date = df.date.apply(lambda x: x.split())
df.date = df.date.apply(lambda x: "{} {} {}".format(x[1],x[2],x[5]))
df.date = pd.to_datetime(df.date,format="%b %d %Y")

df = df.groupby("date")[["tweets"]].aggregate(lambda x: list(x))

#lista = defaultdict(list)
#for v, k in cur:
#	dates = k[0:10]
#	lista[dates].append(v)	
	
#df = pd.DataFrame({"tweets":list(lista.values())},index=lista.keys())

df.tweets = df.tweets.apply(lambda x: " ".join(x))
df.tweets = df.tweets.apply(lambda x: preprocess(x,True))
df = df.iloc[57:81]


df["tokens"] = df.tweets.apply(lambda x: [segmenter.tokenize(y) for y in x])
df.tokens = df.tokens.apply(lambda x: [join_if_url(s) for s in x])
df.tokens = df.tokens.apply(lambda x: [item for segment in x for item in segment])
#df["tokens"] = df.tweets.apply(lambda x: segmenter.tokenize(" ".join(x)))

lens = [len(token) for token in df.tokens]
df_out = pd.DataFrame({"date": np.repeat(df.index,lens),
						"tokens": np.hstack(df.tokens)})
						
df_out = df_out[~df_out.tokens.isin(stop)]
df_out = df_out[~df_out.tokens.str.isdigit()]

df_out["count"] = 1
df = df_out.groupby(["date","tokens"]).agg({"count":pd.np.sum}).reset_index().set_index("date")

check_top_n = False
if check_top_n:
	for d in df.index.unique():
		print(df.loc[d].sort_values(by="count",ascending=False).head(10))

key_words = {"夏", "海", "暑い", "雨", "秋", "寒い", "台風", "冬"}

df = df[df.tokens.isin(key_words)].reset_index()

df = df.pivot_table(index="date",columns="tokens",aggfunc=sum,fill_value=0)
df.index = df.index.strftime("%Y%m%d")
df.to_csv("count_keywords_Nov.csv")
output_cols = ["date"] + df.columns.levels[1].values.tolist()
output_data = df.reset_index().values
header_str = list_to_str(output_cols)
print(output_cols)
print(output_data)

fhand = open('twtline.js', 'w', encoding='utf-8')
fhand.write("twtline = [")
fhand.write(header_str + ",")

for x in output_data:
	print(x)
	row_str = list_to_str(x)
	fhand.write("\n" + row_str + ",")
	
fhand.write("];")

raise SystemExit()
##################################

word_frequency = dict()
date_words = dict()

print(list(lista.keys()))
print(lista.values())

raise SystemExit()

for datas, msg in lista.items():
	print(datas)
	count_all = Counter()
	word_frequency[datas] = msg
	msg = " ".join(msg)
	segments = [segmenter.tokenize(x) for x in preprocess(msg)]
	
	for i, s in enumerate(segments):
		if "https" in s:
			segments[i] = ["".join(s)]
		
	segments = [item for segment in segments for item in segment]
	terms_all = [term for term in segments if term not in stop]
	terms_all = [term for term in terms_all if not term.isdigit()]
	count_all.update(terms_all)
	terms_single = set(terms_all)
	most_common = count_all.most_common(2000)
	sorted(most_common,key=lambda x:x[1])
	date_words[datas] = most_common

	
key_words = {"夏", "海", "暑い", "雨", "秋", "寒い", "台風", "冬"}

result = {key: [(ky, vl) for ky, vl in value if ky in key_words] for key, value in date_words.items()}
result2 = pd.DataFrame({k:dict(v) for k,v in result.items()}).T.fillna(0)
result2.columns = [x.replace(" ","") for x in result2.columns]
df_init = result2.groupby(result2.columns,axis=1).sum()

output = df_init.reset_index().to_json(orient="values")

#print(result)
#raise SystemExit()

df_init = pd.DataFrame(np.zeros((len(result.keys()),len(key_words))),columns=key_words)

i=0
for key,value in result.items():
	print(i,key)
	for vals in value:
		print(vals[0],vals[1])
		if vals[0].replace(" ","") not in key_words:
			continue
		else:
			df_init.ix[i,vals[0].replace(" ","")]+=vals[1]
	i=i+1

df_init.index = result.keys()
print(df_init)
df_init.to_csv("count_keywords_2000.csv")

print(df_init.reset_index().to_json(orient="values"))

new_result1 = dict(df_init)
lista = {}
fhand = open('twtline.js', 'w', encoding='utf-8')
fhand.write()
# for nk,nv in new_result1.items():
	# fhand.write(",'"+nk+"'")
# fhand.write("]")
# new_result = dict(df_init)

# for order, pairs in result.items():
	# print(order)
	# fhand.write(",\n['"+order+"'")
	# pairs = dict(pairs)
	# for kw, vlr in pairs.items():
		#key = (order, kw)
		#val = pair
	#print(val)
		#fhand.write(","+str(val))
	#fhand.write("]");
#fhand.write("\n];\n")

# print("Output is written to twline.js")
# print("Open twline.htm to visualize the data")

	

	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
