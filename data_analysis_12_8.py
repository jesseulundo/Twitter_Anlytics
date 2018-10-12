import pandas as pd
import sqlite3

conn = sqlite3.connect('streaming_data.sqlite')
conn.groupby('user_location').size()
conn.close