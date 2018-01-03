
import time
from urllib.request import urlopen
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import Select

driver = webdriver.Firefox()
list=[]
full_list = []
f = open('crawl_g_prod_prm20.txt', 'a')
f2 = open('crawl_g_prod_gen20.txt', 'a')




def prod_crawl(url):
    driver.get(url)####상품 상세 있는 부분이 자바스크립트라 urlopen으로 하면 실행이 안되어 빈칸임. 이게 최선인가..?
    time.sleep(5)

    soup2 = BeautifulSoup(driver.page_source, 'lxml')
    list = []
    prod = soup2.find('h1','itemtit').getText() #상품명
    price = soup2.find('strong','price_real').getText() # 세일가격


    tmp = prod+'\t'+price+'\n'
    print(tmp)
    #f.write(tmp)

    #/html/body/div[6]/div[2]/div[1]/ul/li[2]/a 리뷰 탭 클릭
    driver.execute_script("window.scrollTo(0, 500);")
    click = driver.find_element_by_xpath('//html/body/div[6]/div[2]/div[1]/ul/li[2]').click()
    time.sleep(4)
    soup2 = BeautifulSoup(driver.page_source, 'lxml')

    # 프리미엄 리뷰 테이블
    p_review = soup2.find('table', 'tb_comment tb_premium').find_all('tr')
    p_total = soup2.find('span', 'pagetotal').find('em').getText()
    for p in range(1, int(p_total)):
        print('------------------', p, 'page')
        try:        #값 없을경우 넘어
            for i in range(0, len(p_review)):
                # p_review = soup2.find('table', 'tb_comment tb_premium').find_all('tr')
                review_tit = p_review[i].find('p', 'comment-tit').getText().replace("\n"," ")
                option_tit = p_review[i].find('p', 'pd-tit').getText()
                review_detail = p_review[i].find('p', 'con').getText().replace("\n", " ")
                #print(review_detail)
                # 이미지 없는 경우
                try:
                    review_img = p_review[i].find('a', 'uxelayer_ctrl').find('img').get('src')
                except AttributeError:
                    review_img = ''
                    pass
                write_info = p_review[i].find('dl', 'writer-info').find_all('dd')
                uid = write_info[0].getText()
                reg_date = write_info[1].getText()
                click_cnt = write_info[2].getText()

                review_wr(review_tit, option_tit, review_detail, review_img, uid, reg_date, click_cnt)

            # 다음페이지.....다른 방법 없나?
            if ((p) % 10 == 0):  # 다음 10개
                next = driver.find_element_by_class_name('board_pagenation')
                driver.execute_script("window.scrollTo(0, 1500);")
                ppage = next.find_element_by_link_text('다음').click()  # 10page씩 이동
            else:
                next = driver.find_element_by_class_name('board_pagenation')
                page_num = str(p + 1)
                driver.execute_script("window.scrollTo(0, 1500);")
                a = next.find_element_by_link_text(page_num).click()

            time.sleep(4)
            # 페이지 변경 후 reload
            soup2 = BeautifulSoup(driver.page_source, 'lxml')
            p_review = soup2.find('table', 'tb_comment tb_premium').find_all('tr')
        except AttributeError:
            break
    # 프리미엄 리뷰


    #일반리뷰
    driver.execute_script("window.scrollTo(0, 2500);")
    g_review = soup2.find('table', 'tb_comment tb_comment_common').find_all('tr')
    g_total = soup2.find('div','board_pagenationwrap').find('span','pagetotal').find('em').getText()
    for p in range(1,1000):
        for i in range(0, len(g_review)):
            rec = g_review[i].find('span','rec').getText()
            delivery = g_review[i].find('span','dev').getText()
            option_tit = g_review[i].find('p', 'pd-tit').getText()
            review_detail = g_review[i].find('p', 'con').getText(strip=True).replace("\n"," ")

            write_info = g_review[i].find('dl', 'writer-info').find_all('dd')
            uid = write_info[0].getText()
            reg_date = write_info[1].getText()
            review_wr2(rec,delivery, option_tit, review_detail, uid, reg_date)
        # 다음페이지.....다른 방법 없나?
        if ((p) % 10 == 0):  # 다음 10개
            next = driver.find_element_by_id('text-pagenation-wrap').find_element_by_class_name('board_pagenation')
            driver.execute_script("window.scrollTo(0, 2350);")
            ppage = next.find_element_by_link_text('다음').click()  # 10page씩 이동
            print('------------------', p, 'page')
        else:
            next = driver.find_element_by_id('text-pagenation-wrap').find_element_by_class_name('board_pagenation')
            page_num = str(p + 1)
            driver.execute_script("window.scrollTo(0, 2350);")
            a = next.find_element_by_link_text(page_num).click()

        time.sleep(2)
        # 페이지 변경 후 reload
        soup2 = BeautifulSoup(driver.page_source, 'lxml')
        g_review = soup2.find('table', 'tb_comment tb_comment_common').find_all('tr')


def review_wr(review_tit, option_tit, review_detail, review_img, uid, reg_date, click_cnt):
    list = []
    list.append(review_tit)
    list.append(option_tit)
    list.append(review_detail)
    list.append(review_img)
    list.append(uid)
    list.append(reg_date)
    list.append(click_cnt)
    f.write('\t'.join(list))
    f.write('\n')


def review_wr2(rec,delivery, option_tit, review_detail, uid, reg_date):
    list = []
    list.append(rec)
    list.append(delivery)
    list.append(option_tit)
    list.append(review_detail)
    list.append(uid)
    list.append(reg_date)
    f2.write('\t'.join(list))
    f2.write('\n')

#url ='http://item.gmarket.co.kr/Item?goodscode=231941110' #f 치렝스
#url ='http://item.gmarket.co.kr/Item?goodscode=165003300&pos_shop_cd=SH&pos_class_cd=111111111&pos_class_kind=T&search_keyword=' #f2 청바지
#url = 'http://item.gmarket.co.kr/detailview/Item.asp?goodscode=868469393' #f3 니트
#url= 'http://item.gmarket.co.kr/detailview/Item.asp?goodscode=212004014' #f4 니트
#url='http://item.gmarket.co.kr/Item?goodscode=627247117' #f5
#url ='http://item.gmarket.co.kr/Item?goodscode=798416412' #f6
#url='http://item.gmarket.co.kr/detailview/Item.asp?goodscode=826303672' #f7
#url ='http://item.gmarket.co.kr/Item?goodscode=511008587' #f8
#url='http://item.gmarket.co.kr/Item?goodscode=301110076' #f9
#url='http://item.gmarket.co.kr/Item?goodscode=946176130' #f10
#url='http://item.gmarket.co.kr/Item?goodscode=226919468' #f11
#url='http://item.gmarket.co.kr/Item?goodscode=125749989' #f12
#url='http://item.gmarket.co.kr/Item?goodscode=841755269' #f13
#url='http://item.gmarket.co.kr/Item?goodscode=755821853'#f14
#url='http://item.gmarket.co.kr/Item?goodscode=628153284' #f15
#url='http://item.gmarket.co.kr/detailview/Item.asp?goodscode=201653087' #f16
#url17='http://item.gmarket.co.kr/detailview/Item.asp?goodscode=659582055' #f17
#url='http://item.gmarket.co.kr/detailview/Item.asp?goodscode=189842449' #18
#url='http://item.gmarket.co.kr/Item?goodscode=215673140' #스위트바니
#url2='http://item.gmarket.co.kr/Item?goodscode=587779477' #떳다그녀
#url3='http://item.gmarket.co.kr/Item?goodscode=929105077' #겨울바지
#url4='http://item.gmarket.co.kr/Item?goodscode=502114157' #코코리
#url5='http://item.gmarket.co.kr/Item?goodscode=212004014'
#url6='http://item.gmarket.co.kr/Item?goodscode=630991355'
#url7='http://item.gmarket.co.kr/Item?goodscode=166096293' #수면잡옷
#url8='http://item.gmarket.co.kr/Item?goodscode=924900551'
#url9='http://item.gmarket.co.kr/Item?goodscode=533546720' #유아복
#url10='http://item.gmarket.co.kr/Item?goodscode=896527720' 
#url11='http://item.gmarket.co.kr/Item?goodscode=776582823' #마담의류
url='http://item.gmarket.co.kr/Item?goodscode=798416412'
url2='http://item.gmarket.co.kr/Item?goodscode=948932277'
url3='http://item.gmarket.co.kr/Item?goodscode=860855455'
url4='http://item.gmarket.co.kr/Item?goodscode=125749989'
url5='http://item.gmarket.co.kr/Item?goodscode=932044429'
url6='http://item.gmarket.co.kr/Item?goodscode=969437920'
url7='http://item.gmarket.co.kr/Item?goodscode=727408363'
url8='http://item.gmarket.co.kr/Item?goodscode=734492742'

print(url)
prod_crawl(url)
print(url2)
prod_crawl(url2)
print(url3)
prod_crawl(url3)
print(url4)
prod_crawl(url4)
print(url5)
prod_crawl(url5)
print(url6)
prod_crawl(url6)
print(url7)
prod_crawl(url7)
print(url8)
prod_crawl(url8)

f.close()
f2.close()


