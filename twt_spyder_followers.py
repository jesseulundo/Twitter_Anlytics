import urllib.request, urllib.parse, urllib.error
import twurl
import json
import sqlite3
import ssl

TWITTER_URL = 'https://api.twitter.com/1.1/followers/list.json?'

conn = sqlite3.connect('followers.sqlite')
cur = conn.cursor()

cur.executescript('''
create table if not exists follower(
	id integer primary key,
	name text unique,
	retrieved integer);
	
create table if not exists twitter_account(
	de_id integer,
	para_id integer,
	UNIQUE(de_id, para_id))
''')

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

while True:
	account = input('Enter a Twitter account, or quit: ')
	if (account == 'quit'): break
	if (len(account) < 1):
		cur.execute('select id, name from followers where retrieved = 0 LIMIT 1')
		try:
			(id, account) = cur.fetchone()
		except:
			print('No unretrieved Twitter accounts found')
			continue
	else:
		cur.execute('select id from follower where name = ? LIMIT 1',
					(account, ))
		try:
			id = cur.fetchone()[0]
		except:
			cur.execute('''insert or ignore into follower 
						(name, retrieved) values (?, 0)''', (account, ))
			conn.commit()
			if cur.rowcount != 1:
				print('Error inserting account:', account)
				continue
			id = cur.lastrowid
	url = twurl.augment(TWITTER_URL, {'screen_name': account, 'count': '100'})
	print('Retrieving account', account)
	try:
		connection= urllib.request.urlopen(url, context=ctx)
	except Exception as err:
		print('Failed to Retrieve', err)
		break
		
	data = connection.read().decode()
	headers = dict(connection.getheaders())
	
	print('Remaining', headers['x-rate-limit-remaining'])
	
	try:
		js = json.loads(data)
	except:
		print('Unable to parse json')
		print(data)
		break
		
	if 'users' not in js:
		print('Incorrect JSON received')
		print(json.dumps(js, indent=4))
		continue
		
	cur.execute('update follower SET retrieved=1 where name = ?', (account, ))
	
	countnew = 0
	countold = 0
	for u in js['users']:
		follower = u['screen_name']
		print(follower)
		cur.execute('select id from follower where name = ? LIMIT 1', (follower, ))
		
		try:
			follower_id = cur.fetchone()[0]
			countold = countold + 1
		except:
			cur.execute('''insert or ignore into follower (name, retrieved)
						VALUES (?, 0)''',(follower, ))
			conn.commit()
			if cur.rowcount != 1:
				print('Error inserting account:', follower)
				continue
			follower_id = cur.lastrowid
			countnew = countnew + 1
		cur.execute('''insert or ignore into twitter_account (de_id, para_id)
					VALUES (?, ?)''', (id, follower_id))
	print('New accounts = ', countnew, ' revisited= ', countold)
	print('Remaining', headers['x-rate-limit-remaining'])
	conn.commit()
cur.close()