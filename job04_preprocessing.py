import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from konlpy.tag import Okt
from keras.preprocessing.text import Tokenizer
from keras.utils import pad_sequences
from sklearn.preprocessing import LabelEncoder
from keras.utils import to_categorical
import pickle

pd.set_option('display.unicode.east_asian_width', True)
df = pd.read_csv('./crawling_data/naver_news_titles_20220526.csv')

X = df['titles']
Y = df['category']

encoder = LabelEncoder()
labered_Y = encoder.fit_transform(Y)
label = encoder.classes_
with open('./models/encoder.pickle','wb') as f:
    pickle.dump(encoder, f) #label을 뽑아내주는 encoder를 pickle

#OneHotEncoding
onehot_Y = to_categorical(labered_Y)

#자연어 처리 시작
okt = Okt() #OpenKoreanTokenizer = 한국어를 형태소 단위로 잘라서 labeling. dictionary의 형태를 갖게 됨

#뉴스 기사 타이틀 전부 형태소 단위로 자름
for i in range(len(X)):
    X[i] = okt.morphs(X[i], stem=True)

stopwords=pd.read_csv('./crawling_data/stopwords.csv', index_col=0)

#한글자와 불용어 제거
for i in range(len(X)) :
    words = []
    for j in range(len(X[i])):
        if len(X[i][j]) > 1:
            if X[i][j] not in list(stopwords['stopword']):
                words.append(X[i][j])
    X[i] = ' '.join(words)

#토큰화 하기
token=Tokenizer() #단어사전을 저장함
token.fit_on_texts(X)
tokened_X = token.texts_to_sequences(X)
wordsize = len(token.word_index) + 1 #빈 0번까지 포함

#token이 단어사전을 저장하므로 pickle
with open('./models/news_token.pickle', 'wb') as f:
    pickle.dump(token, f)

#토큰화 된 문장 리스트 중에서 문장이 가장 긴 요소를 찾아 나머지 요소들을 가장 긴 문장만큼 padding 함
max = 0
for i in range(len(tokened_X)) :
    if max < len(tokened_X[i]) :
        max = len(tokened_X[i])
X_pad = pad_sequences(tokened_X, max)

#train, test set split
X_train, X_test, Y_train, Y_test = train_test_split(X_pad, onehot_Y, test_size=0.1)
print(X_train.shape, Y_train.shape)
print(X_test.shape, Y_test.shape)

xy = X_train, X_test, Y_train, Y_test
np.save('./crawling_data/news_data_max_{}_wordsize_{}'.format(max, wordsize), xy)