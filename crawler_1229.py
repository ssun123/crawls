# -*coding :utf-8-*-
#exe 파일 생성용
from datetime import datetime
import arrow
import requests
from bs4 import BeautifulSoup
from time import sleep
import re
import psycopg2 as pg

from requests import HTTPError

def main():
    #cur = dbcon()
    detailed_dict = load_data()
    detailed_dict2 = crawling_naver(detailed_dict)
   # export_excel(detailed_dict2)

nowDate = arrow.utcnow().to('Asia/Seoul').format('YYYY-MM-DD_HH')

###db관련 추가 1228
#db connect
def dbcon():
    host = '211.41.186.135'
    db = 'ghs_db'
    user = 'metashopping'
    pwd = 'apxktyvld1!'
    conn = pg.connect(host=host, database=db, user=user, password=pwd)
    #cur = conn.cursor()
    return conn

#카테고리 매핑 필요한 상품 db select -> dict에 저장
def load_data():
    conn = dbcon()
    cur = conn.cursor()
    selectStmt="select channelno, itemcode, productname from schema_ghs.shopping_table_batch where category1_mapping='';" #main_yn필드 확인되면 추가
    cur.execute(selectStmt)  # 상품DB내 매핑 안된것
    EPG_data = cur.fetchall()
    EPG_data_len = len(EPG_data)
    id = 1
    detailed_dict = {}
    for i in range(0, EPG_data_len):
        data = EPG_data[i]
        ch_no = data[0]
        prod_name = data[2]
        prod_id = data[1]

        detailed_dict[i] = {
            'ch_no': ch_no,
            'detailed_product_name': prod_name,
            'prod_id': prod_id
        }

    print(detailed_dict)
    conn.close()
    return detailed_dict

#크롤링 카테고리 db 업데이트
def update_db(res):
    conn = dbcon()
    cur = conn.cursor()
    for i in range(0,len(res)):
        if(res[i].get('categories4') != None):  #category정보 4까지 있는경우
            updateStmt = "update schema_ghs.shopping_table_batch " \
                         "set category1_mapping = %s, category2_mapping  = %s, category3_mapping = %s,category4_mapping = %s " \
                         "where channelno = %s and itemcode = %s and category3_mapping ='';"
            cur.execute(updateStmt, (res[i].get('categories1'), res[i].get('categories2'), res[i].get('categories3'), res[i].get('categories4'), res[i].get('ch_no'),res[i].get('prod_id')))
            print(updateStmt, res[i].get('categories1'), res[i].get('categories2'), res[i].get('categories3'), res[i].get('ch_no'), res[i].get('prod_id'))
        elif(res[i].get('categories1') != None):
             updateStmt = "update schema_ghs.shopping_table_batch " \
                 "set category1_mapping = %s, category2_mapping  = %s, category3_mapping = %s "\
                 "where channelno = %s and itemcode = %s and category3_mapping='';"
             cur.execute(updateStmt,(res[i].get('categories1'),res[i].get('categories2'),res[i].get('categories3'),res[i].get('ch_no'),res[i].get('prod_id')))
             print(updateStmt,(res[i].get('categories1'),res[i].get('categories2'),res[i].get('categories3'),res[i].get('ch_no'),res[i].get('prod_id')))

    conn.commit()
    conn.close()

def crawling_naver(detailed_dict):
    # 상품 명 중에서 제외할 단어 리스트로 나열
    except_word = ['[본품론칭이후최다구성]','◆16FW 신상 바로 그 느낌!◆',' 백화점 인기상품 긴급물량★','★전 고객 조건없이 5개 용량★','인하_',
                   '[오직 방송중에만 상담예약 가능]','★프리미엄 커튼/블라인드의 명가 벽창호★','★런칭가 159,000원★','★17년 SS 최신상★',
                   '★공식수입원 정품★','★백화점 판매동일 모델 사운드 바 증정★','시중동일모델 최저가 보상/차액의 100% 보상★','★TV상품★',
                   '★무료체험 14일★','★3/1 특집전 총4천만원 상당 행운찬스★','*14회방송매진*방송동일*★크림6개최다구성★','★2017년 최신상★',
                   '★전 성분 100% 자연유래★','★여배우들의 뷰티템! 먹는 콜라겐★','(방송에서만 구성)','(상시 구성)','ver2','_프로모션','(리_방송)',
                   '17년 봄 팬츠 최신상품 // ','★17년 봄 팬츠 최신상품!★','★4회 방송 모두 완판! 방송중에만 특별한 가격★','♥17신상, 백화점 인기물량, 스타일업♥',
                   '★GS 단독구성★ ','★백화점 동일 상품, 백화점 판매가 239,000원★','*14회방송매진*방송동일*','[영국아두나]','(TV_직_3만원할인)',
                   '★GS단독 사은품 러셀홉스 브펙퍼스트 세트★','★TV상품★','방송 동일조건 !!',' GS단독','★2017 마지막 생방송★','★방송동일조건★[AMing]','★최초2만원인하★',
                   '★여배우들의 뷰티템! 먹는 콜라겐 돌풍★','★파이널 최저가! 막바지 물량!★','(방송에서만 구성)','(미리주문)','(단품)','[단품]','(직)','★16FW 최신상★',
                   '[고객감사5만원↓]','★최저가! 단 59,000원!!!★','★1/2일 월요일 07시15분 마지막 생방송!!!★','★최초2만원인하★','디자이너가 선택한 NEW소재!',
                   '★2017년 봄신상★','런칭 사은품 책장 25일에만 드려요~','★방송동일조건★','[TV홈쇼핑]','(방송중)','(TV방송)','(TV)','_직택','(TV_직매입)','(1만원 인하)',
                   '_1만원인하',' (특약)','(TV방송_직)','(TV_기습)','[17년 최신상! 핫트렌드]','_50프로 할인','_특약','_무료체험15일',' 방송단독구성_조건변경',
                   '(직_리2)','(1-1)','(형성)','★2017년 여름 신상품★','17년 최신상','★2017 봄신상★','★2017년 봄신상★','★17SS 최신상★','_구성변경','★방송중 6만원세일! ',
                   '_직매입','(방송_정률)','세일','(TV_리뉴얼/직매)','(전용의자증정)','(TV_방송_직)',' ver1','5차','(TV_방송)','_15봉',' 5종+사은품','(16+6평형)','(무료체험 2매)',
                   '(18+6평형)','(18평형)','(TV기습)','(TV_초특가)','점보특대형','대형','(방송)','5차','(TV_2만원할인)','_직택배','(방송_직_1+1)','(1+1)','_일시불4천원',' _세일',
                   '더블구성','(직)','기본구성','5팩','34팩_직택배','직매입_','(TV_형성)','[여름SALE3만원인하!]','_최대','(직매입)','(직_리2)','(TV_방_직)','(TV_특)','(TV_방송)',
                   '_배송','(특대형)','+사은품','(TV_5만원할인)','_1만인하','_사은품 추가','_ARS3천원',' ★여름에빛나는매력★','(특약)','(사은품변경_정액)','(혼합형)','2017','(TV_수정)',
                   '_직택배','_방송최저가','_더블구성','_기본구성','슈퍼특대형','특대형','_SALE','_최저가찬스','_직','(3차)','_최다구성','(방송중)','34팩','(TV_방_특)','(80매)','_10만원인하',
                   '(TV_혼합)','기본세트','3종 세트','15마리','(사은품 포함)','12박스','_프로모션 강화','(프리미엄팩)','(기본팩)','(방송_세일)','역대최저가!','(기습초특가)','(직_리3)',
                   '(혼합형)','_사은품변경','직_','프리미엄팩','기본팩','(단독특가)','(TV_직_초특가)','_1만원할인','(2017)','(퀸)','(킹)','(슈퍼싱글)','패키지5차','1세트',' 쿨 ',' 선샤인 ','_컬러변경',
                   '[일시불 할인]','(11월 한정)','GS MY SHOP 특별 런칭','★GS 단 하나 맥주효모★','★대박구성★','★17 FW 신상★','★2만원인하★','★GS단독/무10/월9천원대로 9종풀세트 소장★','★방송동일상품★',
                   '★2017년 FW 신상품★','★방송중10만원SALE★','★김장준비 풀세트★','★11/12 방송중10만원SALE★','★2018 gs마이샵 론칭특가!★',''
                   ]
#'★[가-핳]+.★'
    for (k, v) in detailed_dict.items():
        #start_date= v['start_date']
        #end_date = v['end_date']
        detailed_product_name = v['detailed_product_name']
        if k ==500:
            sleep(500);

        if not detailed_product_name:
            continue
        for word in except_word:
            detailed_product_name=detailed_product_name.replace(word, '')
            # re.sub("[0-9]종", "", detailed_product_name)
            # re.sub("총 [0-9]통","",detailed_product_name)
            #detailed_product_name = re.sub("[0-9*]병|[0-9*]통|[0-9*]종|[0-9*]세트|0-9*]포|0-9*]개|0-9*]팩|0-9*]개월|[0-9*]롤", "",detailed_product_name)
            detailed_product_name = re.sub("\(.*?\)", "", detailed_product_name)
            detailed_product_name = re.sub("\[.*?\]", "", detailed_product_name)


        try:
            targetUrl = "http://shopping.naver.com/search/all.nhn"
            response = requests.get(targetUrl, params={
                'query': detailed_product_name,
                'frm': 'NVSHATC',
            })
            response.raise_for_status()
            sleep(4)
        except HTTPError as e:
            return None

        # soup 객체에 넣기
        # 여러개의 div중 첫번째 div 뽑아오기
        # <div class = "info">
        #   <a href = "/category/category.nhn?cat_id=[0-9]*" 중 title 뽑아오기
        soup = BeautifulSoup(response.text, "lxml")
        first_div = soup.find('div', {'class': 'info'})
        detailed_dict[k]['categories'] = []
        if first_div:
            items = first_div.findAll('a', {'class': re.compile('cat_id_[0-9]+')})
            if items:
                item = items[-1]
                categories = item['title'].split(" > ")
                #item의 마지막 categories까지 뽑아오기위해 append(item.text)
                categories.append(item.text)
                #print(categories)

                a = ",".join(categories)
                categories1=a.split(',')[0]
                detailed_dict[k]['categories1']=categories1
                categories2=a.split(',')[1]
                detailed_dict[k]['categories2']=categories2
                try:
                    categories3=a.split(',')[2]
                    detailed_dict[k]['categories3']=categories3
                except:
                    pass
                try:
                    categories4=a.split(',')[3]
                    detailed_dict[k]['categories4']=categories4
                except:
                    pass
                detailed_dict[k]['categories'] = categories
            else:
                print('categories info is empty')
        else:
            print('first_div is empty')

        print(detailed_dict[k])
        #print(detailed_dict[k].get('categories'))

    update_db(detailed_dict)
    return detailed_dict

def export_excel(detailed_dict2):
    with open(nowDate+'_epg.csv', 'w') as f:
        for (k, v) in detailed_dict2.items():
            ch_no= v['ch_no']
            detailed_product_name = v['detailed_product_name']
            categories1=str(v.get('categories1') or "")
            categories2=str(v.get('categories2') or "")
            categories3=str(v.get('categories3') or "")
            try:
                categories4=(v.get('categories4') or "")
            except:
                pass
            prod_id = v['prod_id']
            f.write(ch_no+'{'+detailed_product_name+'{'+categories1+'{'+categories2+'{'+categories3+'{'+categories4+'{'+str(prod_id)+'{'+'\n')


if __name__ == '__main__':
    main()