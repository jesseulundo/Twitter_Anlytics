import sqlite3
import time
import zlib

conn = sqlite3.connect('streaming_data14_08.sqlite')
cur = conn.cursor()

cur.execute('SELECT user_id, message FROM tweets')
words = dict()
for message_row in cur:
	words[message_row[0]] = message_row[1]

cur.execute('SELECT user_id, message FROM tweets')
word = dict()
for message_row in cur:
	word[message_row[0]]= (message_row[0],message_row[1])

print("Loaded words = ",len(word), "users=",len(words))

