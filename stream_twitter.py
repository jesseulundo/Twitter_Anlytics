import time
import json
import sqlite3
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream 
import ssl

conn = sqlite3.connect('streaming_data.sqlite')
cur = conn.cursor()

cur.executescript('''
create table if not exists tweets(
	user_id INTEGER PRIMARY KEY, 
	message TEXT, 
	date TEXT,
	coordinates float,
	country text,
	country_cod text,
	user_location text,
	user_time_zone text,
	time_offset integer
);
create table if not exists term_frequency(
	id_term  INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
	term TEXT,
	amount INTEGER
);
''')   

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

consumer_key = "AZkEWyAoUXV66atxT5Kf7J42D"
consumer_secret = "3Tr85xny2o4JCvuo1Id60PQMlRQ8NgloflFBspc0XcDnjRiVU3"
token_key = "891815667279609856-cqK6u7ermbAorHGhbbZDqu3aVnYVbE3"
token_secret = "tYZogzRWvmvYV5ejM8J6BDvHCG8B9gNyuKzFcpWLWsIVD"
start_time = time.time()


class StdOutListner(StreamListener):
	#def __init__(self, start_time, time_limit=0.020):
		#self.time = start_time
		#self.limit = time_limit
		
	def on_data(self, data):
		
		data = json.loads(data)
		
		
		id = data.get("id", "")
		text = data.get("text", "")
		date = data.get("created_at", "")
		coordinates = ((data["place"] or {}).get("bounding_box") or {}).get("coordinates", "")
		country = ((data["place"] or {}).get("country") or "")
		country_cod = ((data["place"] or {}).get("country_cod") or "")
		user_location = ((data["user"] or {}).get("location") or "")
		user_time_zone = ((data["user"] or {}).get("time_zone") or "")
		time_offset = ((data["user"] or {}).get("utc_offset") or "")
		try:
			cur.execute('''INSERT OR IGNORE INTO tweets
				(user_id, message, date, coordinates, country, country_cod, user_location, user_time_zone, time_offset) 
				VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''', (id,text,date,coordinates,country,country_cod,user_location,user_time_zone,time_offset))
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
	Stream.filter(track=["台風","暑い", "夏", "秋", "寒い", "雨", "冬", "海"])

conn.close()