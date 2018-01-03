import time
from urllib.request import urlopen
from bs4 import BeautifulSoup
from selenium import webdriver

driver = webdriver.Firefox()
list=[]
full_list = []
#f = open('test_crawl.txt', 'w')
f = open('crawl_cabagge_uid.txt','w')


def prod_crawl(url):
    driver.get(url)####상품 상세 있는 부분이 자바스크립트라 urlopen으로 하면 실행이 안되어 빈칸임. 이게 최선인가..?
    time.sleep(5)
    #prod_html = urlopen(url)
    #soup2 = BeautifulSoup(prod_html, "lxml")
    soup2 = BeautifulSoup(driver.page_source, 'lxml')
    list = []
    #cat = soup2.find('div', 'divCat1').getText()  # 과일
    prod = soup2.find('h1', 'detail-type').getText()  # 햇사레 복숭아
    origin = soup2.find('p', 'country').getText()  # 원산지
    star = soup2.find('div', 's-total').find('em', 'score').getText()    # 9.3
    #count = soup2.find('div', 's-total').find('em', 'reviewCnt').getText()  # 4,538
    print(prod, origin,star)
    #print(prod, star)
    tmp = prod+'\t'+origin+'\t'+star+'\n'
    f.write(tmp)


    review1 = soup2.find_all('tr', 'tblfaq')
    review2 = soup2.find_all('tr', 'tblfaq-cont')
   # b_chk = soup2.find('tr','tblfaq best')
    for pp in range(1,300):
        time.sleep(3)
        for p in range(1,10):
            print('------------------',p,'page')
            page = driver.find_element_by_xpath('//*[@id="pagingDiv"]/div/span/a[' + format(p) + ']').click()   #페이지 이동
            time.sleep(5)
            soup2 = BeautifulSoup(driver.page_source, 'lxml')
            review1 = soup2.find_all('tr', 'tblfaq')
            review2 = soup2.find_all('tr', 'tblfaq-cont')
            if(pp == 1) & (p == 1):
                for i in range(len(review1)):
                    score = review1[i].find('td','in-star').getText(strip=True)
                    score = score.split('/')[0].strip()
                    title = review1[i].find('td', 'subject').getText(strip=True)
                    ##1010 사용자/지점/작성일 추가
                    uid = review1[i].contents[7].contents[0]
                    try:
                        store = review1[i].contents[9].contents[0]
                    except IndexError:
                        store = ""
                        pass
                    wr_date = review1[i].contents[11].contents[0]
                    price = review2[i].find('p','sfaction-price').getText(strip=True)
                    delivery = review2[i].find('p','sfaction-del').getText(strip=True)
                    quality = review2[i].find('p','sfaction-qual').getText(strip=True)
                    contents = review2[i].find('div','faq-comm').getText(strip=True)
                    print(score,title, price,delivery,quality,contents,uid,store,wr_date)
                    review_wr(score,title,price,delivery,quality,contents,uid,store,wr_date)
            else:
                for i in range(3,len(review1)):
                    score = review1[i].find('td','in-star').getText(strip=True)
                    score = score.split('/')[0].strip()
                    title = review1[i].find('td', 'subject').getText(strip=True)
                    ##1010 사용자/지점/작성일 추가
                    uid = review1[i].contents[7].contents[0]
                    try:
                        store = review1[i].contents[9].contents[0]
                    except IndexError:
                        store = ""
                        pass
                    wr_date = review1[i].contents[11].contents[0]
                    price = review2[i].find('p','sfaction-price').getText(strip=True)
                    delivery = review2[i].find('p','sfaction-del').getText(strip=True)
                    quality = review2[i].find('p','sfaction-qual').getText(strip=True)
                    contents = review2[i].find('div','faq-comm').getText(strip=True)
                    print(score,title, price,delivery,quality,contents,uid,store,wr_date)
                    review_wr(score,title,price,delivery,quality,contents,uid,store,wr_date)

        if(pp == 1):
            ppage = driver.find_element_by_xpath('//*[@id="pagingDiv"]/div/a[1]').click() #10page씩 이동
            time.sleep(5)
        elif(pp == 2):
            ppage = driver.find_element_by_xpath('//*[@id="pagingDiv"]/div/a[2]').click()
            time.sleep(5)
        elif(pp > 2):
            ppage = driver.find_element_by_xpath('//*[@id="pagingDiv"]/div/a[3]').click()
            time.sleep(5)
    time.sleep(3)
    #10page씩 이동

def review_wr(score,title,price,delivery,quality,contents,uid,store,wr_date):
    list = []
    list.append(score)
    list.append(title)
    list.append(price)
    list.append(delivery)
    list.append(quality)
    list.append(contents)
    list.append(uid)
    list.append(store)
    list.append(wr_date)
    full_list.append(list)
    f.write('\t'.join(list))
    f.write('\n')


#서울우유1L url ='http://www.lottemart.com/product/ProductDetail.do?ProductCD=8801115114154&CategoryID=C001001600090001&SITELOC=undefined&socialSeq=&koostYn=N'
#서울우유 2.3L url='http://www.lottemart.com/product/ProductDetail.do?ProductCD=8801115111054&CategoryID=C001001600090001&SITELOC=undefined&socialSeq=&koostYn=N'
#서울우유 목장url='http://www.lottemart.com/product/ProductDetail.do?ProductCD=8801115114260&CategoryID=C001001600090001&SITELOC=undefined&socialSeq=&koostYn=N'

#무 url ='http://www.lottemart.com/product/ProductDetail.do?ProductCD=0430000015429&CategoryID=C001001200050001&SITELOC=undefined&socialSeq=&koostYn=N'
#양배추
url='http://www.lottemart.com/product/ProductDetail.do?ProductCD=0430000007905&CategoryID=C001001200050001&SITELOC=undefined&socialSeq=&koostYn=N'
#감자 url='http://www.lottemart.com/product/ProductDetail.do?ProductCD=2399610000004&CategoryID=C001001200010002&SITELOC=undefined&socialSeq=&koostYn=N'
#당근 url='http://www.lottemart.com/product/ProductDetail.do?ProductCD=0400590300007&CategoryID=C001001200010004&SITELOC=undefined&socialSeq=&koostYn=N'
#키위 url='http://www.lottemart.com/product/ProductDetail.do?ProductCD=0400351770001&CategoryID=C001001300040002&SITELOC=undefined&socialSeq=&koostYn=N'
#포도2 url='http://www.lottemart.com/product/ProductDetail.do?ProductCD=0400150040008&CategoryID=C001001300150001&SITELOC=undefined&socialSeq=&koostYn=N'
#포도 url='http://www.lottemart.com/product/ProductDetail.do?ProductCD=0400316670001&CategoryID=C001001300150001&SITELOC=undefined&socialSeq=&koostYn=N'
#사과 url='http://www.lottemart.com/product/ProductDetail.do?ProductCD=0400634390001&CategoryID=C001001300010001&SITELOC=undefined&socialSeq=&koostYn=N'
#귤url='http://www.lottemart.com/product/ProductDetail.do?ProductCD=0400216480007&CategoryID=C001001300020001&SITELOC=undefined&socialSeq=&koostYn=N'
#삼겹살2url='http://www.lottemart.com/product/ProductDetail.do?ProductCD=2485300000000&CategoryID=C001001400040002&SITELOC=undefined&socialSeq=&koostYn=N'
#삼겹살 url='http://www.lottemart.com/product/ProductDetail.do?ProductCD=2560010000004&CategoryID=C001001400040001&SITELOC=undefined&socialSeq=&koostYn=N'
#시금치2url ='http://www.lottemart.com/product/ProductDetail.do?ProductCD=0400609030000&CategoryID=C001001200070001&SITELOC=undefined&socialSeq=&koostYn=N'
#시금치 url='http://www.lottemart.com/product/ProductDetail.do?ProductCD=0400626210003&CategoryID=C001001200070001&SITELOC=undefined&socialSeq=&koostYn=N'
#깻잎 url='http://www.lottemart.com/product/ProductDetail.do?ProductCD=0400311300002&CategoryID=C001001200080001&SITELOC=undefined&socialSeq=&koostYn=N'
#바나나2 url ='http://www.lottemart.com/product/ProductDetail.do?ProductCD=0400521590002&CategoryID=C001001300080001&SITELOC=undefined&socialSeq=&koostYn=N'
#바나나 url ='http://www.lottemart.com/product/ProductDetail.do?ProductCD=0400450390001&CategoryID=C001001300080001&SITELOC=undefined&socialSeq=&koostYn=N'
#쌀url = 'http://www.lottemart.com/product/ProductDetail.do?ProductCD=8808836973855&CategoryID=C001001100010001&SITELOC=undefined&socialSeq=&koostYn=N'
#고구마 url = 'http://www.lottemart.com/product/ProductDetail.do?ProductCD=0400304770003&CategoryID=C001001200010001&SITELOC=undefined&socialSeq=&koostYn=N'
#감자 url2 = 'http://www.lottemart.com/product/ProductDetail.do?ProductCD=2399610000004&CategoryID=C001001200010002&SITELOC=undefined&socialSeq=&koostYn=N'
print(url)
prod_crawl(url)
f.close()

