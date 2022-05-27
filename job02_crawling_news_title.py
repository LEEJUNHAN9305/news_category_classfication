from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
import pandas as pd
import re
import time

category = ['Politics','Economic','Social','Culture','World','IT']
#섹션 별 기사 갯수를 '세계'면으로 맞추기

pages = [110, 110, 110, 78, 110, 66] # IT, 생활로 맞추면 데이터 손실이 너무 커짐

#webdriver crawling을 위한 각종 옵션
options = webdriver.ChromeOptions()
options.add_argument('lang=ko_KR') #언어설정
# options.add.argument('headless') #브라우저를 메모리 상에만 띄움. colab에서 띄우고 싶으면 이 옵션을 부여
# options.add_argument('--no-sandbox') # Docker
# options.add_argument('--disable-dev-shm-usage') #리눅스
# options.add_argument('--disable-gpu') #리눅스 - 셀레니움의 작업속도를 높이기 위해 gpu 기능 제거


# 크롬 설정 - 크롬 정보 - 버전 확인 - 버전에 맞는 chromedriver 다운로드 - 프로젝트 폴더에 chromedriver 실행파일 복사
driver = webdriver.Chrome('./chromedriver', options=options)

df_titles = pd.DataFrame()

#브라우저에서 crawling
for i in range(0,2):
    titles = []
    for j in range(1,pages[i]+1):
        url = 'https://news.naver.com/main/main.naver?mode=LSD&mid=shm&sid1=10{}#&date=%2000:00:00&page={}'.format(i,j)
        driver.get(url)
        time.sleep(0.2) #0.2초동안 잠깐 멈추기(페이지 로딩 시간을 고려)
        for k in range(1,5):
            for l in range(1,6):
                # 기사 헤드라인의 X-path 규칙 확인 후 X-path를 기준으로 crawling
                x_path = '//*[@id="section_body"]/ul[{}]/li[{}]/dl/dt[2]/a'.format(k,l)
                try:
                    title = driver.find_element_by_xpath(x_path).text
                    title = re.compile('[^가-힣 ]').sub('', title)
                    titles.append(title)
                except NoSuchElementException as e: #X-path가 없음
                    time.sleep(0.5)
                    try:
                        title = driver.find_element_by_xpath(x_path).text #한번 더 기존의 X-path 규칙으로 시도
                        title = re.compile('[^가-힣 ]').sub('', title)
                        titles.append(title)
                    except:
                        try:
                            x_path = '//*[@id="section_body"]/ul[{}]/li[{}]/dl/dt/a'.format(k,l) #다른 X-path 규칙으로 시도
                            title = re.compile('[^가-힣 ]').sub('', title)
                            titles.append(title)
                        except:
                            print('no such element')
                except StaleElementReferenceException as e: #페이지가 완전히 로딩되기 전에 X-path를 참조하는 경우
                    print(e)
                    print(category[i], j, 'page', k * l)
                except :
                    print('error')
        #30페이지씩 crawling 할 때마다 임시로 저장
        if j % 30 == 0 :
            df_selection_titles = pd.DataFrame(titles, columns=['titles'])
            df_selection_titles['category'] = category[i]
            df_titles = pd.concat([df_titles, df_selection_titles], ignore_index=True)
            df_selection_titles.to_csv('./crawling_data_{}_{}_{}.csv'.format(category[i], j-29, j), index=False)
            title = [] #30개씩 저장하고 title을 비워둠
    #30페이지씩 crawling 하고 남은 페이지 저장
    df_selection_titles = pd.DataFrame(titles, columns=['titles'])
    df_selection_titles['category'] = category[i]
    df_titles = pd.concat([df_titles, df_selection_titles], ignore_index=True)
    df_selection_titles.to_csv('./crawling_data_{}_last.csv'.format(category[i]), index=False)
    titles=[]
df_selection_titles = pd.DataFrame(titles, columns=['titles'])
df_selection_titles['category'] = category[i]
df_titles = pd.concat([df_titles, df_selection_titles], ignore_index=True)
df_titles.to_csv('./crawling_data/crawling_data.csv'.format(category[i]), index=False)
driver.close()