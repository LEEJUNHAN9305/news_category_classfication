import pandas as pd
import numpy as np
from konlpy.tag import Okt
from keras.utils import pad_sequences
from keras.utils import to_categorical
import pickle
from keras.models import load_model

pd.set_option('display.unicode.east_asian_width', True)
pd.set_option('display.max_columns', 20) #요약하지 말고 모든 columns를 다 출력해라
df = pd.read_csv('./crawling_data/naver_headline_news20220527.csv')

X = df['titles']
Y = df['category']

with open('./models/encoder.pickle', 'rb') as f:
    encoder = pickle.load(f)

labered_Y = encoder.transform(Y) #이미 만든 encoder로 transform만
label = encoder.classes_

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
with open('./models/news_token.pickle', 'rb') as f:
    token = pickle.load(f)

tokened_X = token.texts_to_sequences(X)

#예측대상 padding
for i in range(len(tokened_X)) :
    if len(tokened_X[i]) > 17 :
        tokened_X[i] = tokened_X[i][:17] #모델은 최대 17의 문장 길이만 학습했기 때문에 17을 넘기면 안 됨
X_pad = pad_sequences(tokened_X, 17)

#모델 예측
model = load_model('./models/news_category_classification_model_0.6927609443664551.h5')
preds = model.predict(X_pad)

#모델이 최상위로 분류한 카테고리와 차상위로 높게 분류한 카테고리로 다중분류
predicts = []
for pred in preds:
    most = label[np.argmax(pred)]   # 예측값의 가장 큰 값을 선언해두고
    pred[np.argmax(pred)] = 0       # 0으로 만듦
    second = label[np.argmax(pred)] # 그럼 두번째로 큰 값으로 선언할 수 있음
    predicts.append([most, second]) # 예측값의 가장 큰 값의 indexing number로 index한 값과 두번째로 큰 값을 list 형태로 predicts에 삽입
df['predict'] = predicts

#예측결과 확인해보기
df['OX'] = 0
for i in range(len(df)) :
    if df.loc[i, 'category'] in df.loc[i, 'predict'] :
        df.loc[i, 'OX'] = 'O'
    else :
        df.loc[i, 'OX'] = 'X'
print(df.head(30))

print(df['OX'].value_counts())
print(df['OX'].value_counts()/len(df))

for i in range(len(df)) :
    if df['category'][i] not in df['predict'][i] :
        print(df.iloc[i])