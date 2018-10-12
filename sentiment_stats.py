import pandas as pd
import numpy as np
from pandas import DataFrame



fhand = pd.ExcelFile(r'C:/Users/jwa/Desktop/Jesse/python/twitter_analytics/twitter_data/sentiment_Nov.xlsx')

obj = fhand.parse('Sheet1')
frame = DataFrame(obj)
frame2 = frame.drop_duplicates(subset=['sentence'], keep=False) 

frame2 = frame2.join(pd.get_dummies(frame2.classification))

key_words = ["夏", "海", "暑い", "雨", "秋", "寒い", "台風", "冬"]
result = []

for kw in key_words:
	frame3 = frame2[frame2.sentence.str.contains(kw, na=False)][["Positive","Negative","Neutral"]].sum()
	result.append(frame3)

output = DataFrame(result, index=[key_words])

output = output.T; output.index.name='Classification' 

print(output)


output.to_csv("sentiment_stats_Nov.csv")

output.plot(kind='bar');


