from bs4 import BeautifulSoup
import requests
import re
import pandas as pd
import datetime

category = ['Politics','Economic','Social','Culture','World','IT']

#웹에서 요청하는 것처럼 설정하기
headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.0.0 Safari/537.36'}
            # 개발자 도구 - 네트워크 - 아무 리소스 - 요청 헤더 - user-agent

df_titles = pd.DataFrame()

#파싱 시작
for i in range(6):
    # 섹션 별로 파싱
    url='https://news.naver.com/main/main.naver?mode=LSD&mid=shm&sid1=10{}'.format(i)
    # 주소로 웹페이지 요소 긁어오기
    resp = requests.get(url, headers=headers)
    soup = BeautifulSoup(resp.text, 'html.parser')
    # re로 전처리
    title_tags = soup.select('.cluster_text_headline')
    titles = []
    for title_tag in title_tags :
        # 자연어 처리 - 정규표현식을 이용하여 헤드라인에서 한글과 공백만 남기고 제거
        title = re.compile('[^가-힣 ]').sub('', title_tag.text)
        titles.append(title)
    df_section_titles = pd.DataFrame(titles, columns=['titles'])
    df_section_titles['category'] = category[i]
    df_titles = pd.concat([df_titles, df_section_titles], axis='rows', ignore_index=True)

#파싱이 끝난 데이터 -> csv 파일
df_titles.to_csv('./crawling_data/naver_headline_news{}.csv'.format(
    datetime.datetime.now().strftime('%Y%m%d')), index=False)