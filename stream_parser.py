from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
import sqlite3
import json
import ssl

conn = sqlite3.connect('streaming_tweets_1.sqlite')
cur = conn.cursor()
cur.execute('''CREATE TABLE IF NOT EXISTS Tweets
			(user_id INTEGER PRIMARY KEY, message TEXT, date TEXT, place TEXT)''')

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

consumer_key = "AZkEWyAoUXV66atxT5Kf7J42D"
consumer_secret = "3Tr85xny2o4JCvuo1Id60PQMlRQ8NgloflFBspc0XcDnjRiVU3"
token_key = "891815667279609856-cqK6u7ermbAorHGhbbZDqu3aVnYVbE3"
token_secret = "tYZogzRWvmvYV5ejM8J6BDvHCG8B9gNyuKzFcpWLWsIVD"

class StdOutListner(StreamListener):
	def on_data(self, data):
		
		data = json.loads(data)
		
		id = data.get("id", "")
		text = data.get("text", "")
		date = data.get("created_at", "")
		place = data.get("user", {}).get("location", "")
		
		try:
			cur.execute('''INSERT OR IGNORE INTO Tweets
				(user_id, message, date, place) VALUES (?, ?, ?, ?)''', (id,text,date,place))
			conn.commit()
			print(data)
		except: 
			print("Skipped!")
			print(data)
			
		return data
	
	def on_error(self, status):
		print (status)
		
if __name__ == '__main__':
	l = StdOutListner()
	auth = OAuthHandler(consumer_key, consumer_secret)
	auth.set_access_token(token_key, token_secret)
	Stream = Stream(auth, l)
	Stream.filter(track=["夏","暑い","寒い日","台風"])

conn.close()
	
	
