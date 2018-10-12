import math
from textblob import TextBlob as tb
import sqlite3

def tf(word, blob):
	return blob.words.count(word)/len(blob.words)
def n_containing(word, bloblist):
	return sum(1 for blob in bloblist if word in blob.words)
def idf(word, bloblist):
	return math.log(len(bloblist)/(1+n_containing(word, bloblist)))
def tfidf(word, blob, bloblist):
	return tf(word, blob) * idf(word, bloblist)
	
conn = sqlite3.connect('streaming_data.sqlite')
cur = conn.cursor()

result = cur.execute('SELECT message FROM tweets')

for lines in result:
	bloblist = [lines]
	for i, blob in enumerate(bloblist):
		print("Top words in tweets{}".format(i+1))
		scores = {word: tfidf(word, blob, bloblist) for word in blob.words}
		sorted_words = sorted(scores.items(), key=lambda x:x[1], reserve=True)
		for word,score in sorted_words[:3]:
			print("\t Word: {}, TF-IDF:{}".format(word, round(score,5)))
conn.commit()
conn.close()