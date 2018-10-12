import sqlite3

conn = sqlite3.connect('streaming_english_test.sqlite')
cur = conn.cursor()

cur.execute("select * from tweets where user_location = '' OR user_time_zone IS null OR time_offset IS '';")
print(len(cur.fetchall()))

try:
	cur.execute('''DELETE FROM tweets WHERE user_location = '' OR user_time_zone IS null OR time_offset IS ""''')
	print("Deleted Successfully!")
except:
	print("unable to find table or delete data")
for rows in cur:
	print(rows)

	
conn.commit()
conn.close()