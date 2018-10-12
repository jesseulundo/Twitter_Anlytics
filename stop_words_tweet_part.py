import sqlite3
from jNlp.jTokenize import jTokenize

conn = sqlite3.connect('streaming_data.sqlite')
cur = conn.cursor() 

result = cur.execute("SELECT  message FROM tweets WHERE date BETWEEN 'Fri Sep 08 00:00:00 +0000 2017' AND 'Fri Sep 08 00:05:00 +0000 2017'")
fhand = open('ja_stopword.txt', encoding ="utf-8")
stop_words=[]

for messages in result:
	for message in messages:
		t_message = jTokenize(message)
		print('-'.join(t_message))


#for words in fhand:
#	words = words.strip('\n')
#	if words not in stop_words:
#		stop_words.append(words)
	

#filtered_sentence = [w for w in msg_tokenized if not w in stop_words]
#print("CLEANED:")
#print(filtered_sentence)
