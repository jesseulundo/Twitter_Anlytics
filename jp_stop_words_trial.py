from jp_token_preprocessing import JpTokenPreprocessing 
import MeCab

def tokenize(text):
	tagger = MeCab.Tagger()
	node = tagger.parseToNode(text)
	while node:
		if '名詞' in node.feature:
			surface = node.surface
			yield surface
		node = node.next

		if __name__=='__main__':
			text = """
			これは自然言語処理に必須な前処理のためのモジュールです。
    		形態素解析や、n-gramでトークン化した後のフィルタリング、正規化を補助します。
    		一語だけのトークンや'1234'のような数字だけのトークン、'!!'のような記号だけのトークンのフィルタリング、
    		全角文字'ＰＹＴＨＯＮ'の半角化、英単語'Word'の小文字化といった正規化も行えます。
    		さらに必ず除外したいトークンをストップワードに設定することもできます。
			"""
			stopwords = ['これ', 'こと']
			
			tokens = tokenize(text)
			
			print(list(tokens))
			tokens = tokenize(text)
			preprocessor = JpTokenPreprocessing(number = False,
																						  symbol = False,
																						  case = 'lower',
																						  unicode = 'NFKC',
																						  min_len = 2,
																						  stopwords=stopwords)
			
			tokens = preprocessor.preprocessing(tokens)
			
			print(list(tokens))
			