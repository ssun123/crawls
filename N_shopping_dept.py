import time
from urllib.request import urlopen
from bs4 import BeautifulSoup
from selenium import webdriver
#import naver_shopping_goods as ns


driver = webdriver.Firefox()
list=[]
f_cateurl = open('naver_dept_cateurl.txt') # 백화점 윈도우 카테고리 url
cate = f_cateurl.readline()
f = open('crawl_dept_url_total_1129_2.txt','a')# 백화점 카테고리내 상품 url저장

while cate:
    cate_url = cate.split(',')[1]   # 카테고리별 url
    cate_name = cate.split(',')[0]  # 카테고리명
    print(cate_name, cate_url)
    driver.get(cate_url)
    time.sleep(5)

    soup = BeautifulSoup(driver.page_source, 'lxml')
    prod_list = soup.find_all('li','_NEW_ITEM_LAYOUT')
    prod_len = len(prod_list)
    print(prod_len)
    #prod_tmp_url = prod_list[prod_len-1].find('a').get('href')

    #Infinite scroll
    SCROLL_PAUSE_TIME = 3

    # Get scroll height
    last_height = driver.execute_script("return document.body.scrollHeight")
    prev_prod = 0
    while True:
        # Scroll down to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Wait to load page
        time.sleep(SCROLL_PAUSE_TIME)

        #20개씩 prod url저장
        soup = BeautifulSoup(driver.page_source, 'lxml')
        prod_list = soup.find_all('li', '_NEW_ITEM_LAYOUT')
        prod_len = len(prod_list)

        if (prod_list[prev_prod].find('a').get('href') == prod_list[prev_prod-20].find('a').get('href')):    #페이지 끝 체크 마지막에 계속 같은 상품 가르켜서.
            break

        for i in range(prev_prod,prod_len):
            prod_tmp_url = prod_list[i].find('a').get('href')
            prod_url = 'http://swindow.naver.com/'+prod_tmp_url
            list.append(prod_url)
            #print(cate_name+', '+prod_url)
            f.write(cate_name+', '+prod_url+'\n')

        prev_prod = prod_len # 마지막 위치 저장

        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if (new_height == last_height):
            break
        last_height = new_height

    cate = f_cateurl.readline() # 다음카테고리

######스타일윈도######
#cate_url='http://swindow.naver.com/style/style/list?query=11005001' #상의
#cate_url='http://swindow.naver.com/style/style/list?query=11005002' #아우터
#cate_url='http://swindow.naver.com/style/style/list?query=11005003' #원피스
f_cateurl.close()
f.close()

ns.crawl_prods()
