import pandas as pd
import glob
import datetime

data_path = glob.glob('./crawling_data/*')
print(data_path)

df = pd.DataFrame()
for path in data_path:
    df_temp = pd.read_csv(path)
    #빈 dataframe과 불러들여온 csv파일을 합침
    df = pd.concat([df, df_temp])
df.dropna(inplace=True)
df.reset_index(inplace=True, drop=True) #인덱스가 있는 것을 합친다면 인덱스를 버림
print(df.head())
print(df.tail())
print(df['category'].value_counts())
df.info()
df.to_csv('./crawling_data/naver_news_titles_{}.csv'.format(
    datetime.datetime.now().strftime('%Y%m%d')), index=False)