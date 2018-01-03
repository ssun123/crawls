import time
from urllib.request import urlopen
from bs4 import BeautifulSoup
from selenium import webdriver

#url ='http://swindow.naver.com/itemdetail/2246038656?inflow=wdl'
#prod_html = urlopen(url)
#soup2 = BeautifulSoup(prod_html, "lxml")
def crawl_prods():
    f = open('/home/ysong/PycharmProjects/shoppingmall_crawl/crawl_dept_url_total_1129_.txt', 'r')
    f_wr = open('crawl_naver_deptwindow_goods_1129.txt','w')
    read_url = f.readline()#한줄씩
    list = []
    cnt = 0
    while read_url:
        list = []
        prod_url = read_url.split(',')[1]  # 상품 url
        cate_name = read_url.split(',')[0]  # 상품카테고리명
        prod_html = urlopen(prod_url) #상품페이지
        soup2 = BeautifulSoup(prod_html, "lxml")
        list.append(cate_name)
        #카테고리, 상점명, 상품명, 가격
        try:
            cate = soup2.find('h3', 'breadcrumb').getText(strip=True)  # 네이버쇼핑 > 백화점윈도 > 현대백화점 > 중동점 > 럭키슈에뜨
            store_name = soup2.find('span', 'store').getText()  # 럭키슈에뜨
            prod_name = soup2.find('h3', 'title').getText()  # 벨슬리브스트라이프니트풀오버니트 LFWAW17420
            prod_price = soup2.find('div', 'detail_name').find('strong', 'price').getText()  # 282,000원

            list.append(store_name), list.append(prod_name), list.append(prod_price), list.append(cate), list.append(read_url.strip())
            main_img = soup2.find('img', 'common_img_center').get('src')
            # print(main_img)  # 메인이미지
            list.append(main_img)

            #상세정보 10개까지만 저장
            info_title = soup2.find('dl', 'info_list').find_all('dt', 'info_title')
            info_desc = soup2.find('dl', 'info_list').find_all('dd', 'info_desc')
            for i in range(0,10):
                if(i < len(info_title)):
                    info = info_title[i].getText()+':'+info_desc[i].getText()
                else:
                    info=''
               # print(info)
                list.append(info)
            #브랜드,모델명,원산지, 성별, 핏, 디테일, 소매기장,사이즈/사이즈(하의),총기장,등록일..화장품은 또 다름(사용시간, 형태, 사용효과 등)
            #상품 태그 없는 경우도 존재함
            try:
                tag_list = soup2.find('ul', 'tag_list').getText(strip=True)
                #print(tag_list)
                list.append(tag_list)
            except AttributeError:
                tag_list=''
                pass


            #본문내 설명
            desc_text = soup2.find_all('p', 'se_textarea')
            text= ''
            for i in range(0,len(desc_text)):
                text = text+desc_text[i].getText(strip=True)
            #print(text)
            list.append(text)
            #본문내 이미지
            img_list = soup2.find_all('a', 'se_mediaArea')
            for i in range(0,len(img_list)):
               # print(img_list[i].find('img').get('src'))
                list.append(img_list[i].find('img').get('src'))

            f_wr.write('\t'.join(list))
            f_wr.write('\n')
        except AttributeError:
            pass
        read_url=f.readline() #다음상품
        cnt = cnt+1
        if(cnt/3000 == 0):
            print(store_name, prod_name, prod_price)
            time.sleep(300)



    f.close()
    f_wr.close()

crawl_prods()