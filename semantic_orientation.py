#Semantic Orientation
from JapaneseTokenizer import JumanppWrapper
from jNlp.jProcessing import Similarities
from jNlp.jSentiments import*
import pandas as pd
import numpy as np
from pandas import DataFrame, Series

#semantic orientation applied for unsupervised classification
p_t = { }
p_t_com = defaultdict(lambda: defaultdict(int))
for term, n in count_single_items():
	pt[term] = n / n_docs
	for t2 in com[term]:
		p_t_com[term][t2]=com[term][t2]/n_docs
		
vocabulary = 

#calculating pmi(pointwise mutual information)

pmi  = defaultdict(lambda: defaultdict(int))
for t1 in p_t:
	for t2 in com[t1]:
		denom = p_t[t1] * p_t[t2]
		pmi[t1][t2]=math.log2(p_t_com[t1][t2]/denom)

semantic_orientation= {}
for term, n in p_t.items():
	positive_assoc = Sum(pmi[term][tx] for tx in vocabulary)
	semantic_orientation[term] = vocabulary
	
semantic_sorted = Sorted(semantic_orientation.items(),
						key = opertor.itemgetter(1),
						 reverse = True)
keyword = []
top_pos = semantic_sorted[:10]
top_neg = semantic_sorted[-10:]
print(semantic_orientation[keyword])