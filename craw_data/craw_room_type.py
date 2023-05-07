import os
from selenium import webdriver
import re
import io
import requests
from bs4 import BeautifulSoup
import json
import time
import random
from collections import defaultdict


link = 'https://www.agoda.com/oriental-danang/hotel/all/da-nang-vn.html?locale=en-us&ckuid=fdedba03-4477-452c-b8e2-e0518e1022c5&prid=0&currency=VND&correlationId=10e7ea96-5365-4632-8824-b99bc1a13501&analyticsSessionId=-3552745395782370614&pageTypeId=7&realLanguageId=1&languageId=1&origin=VN&cid=1899796&userId=fdedba03-4477-452c-b8e2-e0518e1022c5&whitelabelid=1&loginLvl=0&storefrontId=3&currencyId=78&currencyCode=VND&htmlLanguage=en-us&cultureInfoName=en-us&machineName=hk-acmweb-2007&trafficGroupId=2&sessionId=rldkjqkrbmolaz45h1jnejhx&trafficSubGroupId=133&aid=284594&useFullPageLogin=true&cttp=4&isRealUser=true&mode=production&browserFamily=Chrome&checkIn=2023-05-06&checkOut=2023-05-07&rooms=1&adults=4&childs=1&childages=-1&priceCur=VND&los=1&textToSearch=Oriental%20Danang&productType=-1&travellerType=1&familyMode=off'


def get_header(req_header: str):
    header_settings = dict()
    for _line in req_header.split("\n"):
        if _line:
            item = _line.split(": ")
            header_settings[item[0]] = item[1]

    return header_settings


req_header = """
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/111.0
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8
Accept-Language: vi-VN,vi;q=0.8,en-US;q=0.5,en;q=0.3
Accept-Encoding: gzip, deflate, br
Connection: keep-alive
Cookie: TADCID=RhTex--PzakBu6nTABQCXdElnkGETRW-Svh01l3nWnTZ5iCtUlW3mhACiJQeHA9q9qPqLSwneSqiwEQwVbsx-qUwPvQhkVbipFs; TAUnique=%1%enc%3AWBQ%2FL%2FWn1ATmJiLD2PDlMDCQxVpYWx299gkE2QZj4cZ8nEhsIHY1Kw%3D%3D; TASSK=enc%3AAI89fd1cjtyCoV3jBKdwNStCWJtedPvz0oBSrweMSFKxMIgUuRGJ3Xm9CxzkDPr%2BVelRpxlC8D1%2BwfcHoT%2BsDXnebWRDIomHZ7zFLdTNAiK%2BdXF5rTHllDCUx2XHkkIhUw%3D%3D; PMC=V2*MS.83*MD.20230413*LD.20230414; TART=%1%enc%3AHTUPUBLJNa77nO7vdNFeO%2BHn8lNras4k7D1cT%2FQWNr6tYTFmrrH9Jq6g%2B8smg1a4O%2FCgneS8vfk%3D; PAC=APrQnBUsolzlkiy8vIwdyk82vhjMnABbzhqCNoe7bXzsXrkGjBVhlYkOHSqe6EHiHrmMvj826ItT0GZNFp896YKzCLuuXqzsllSuflcE8jpCpLck233-wAgr_agzQvHt3ecBIrR8oxM5tjOkhSOfbJHfoLSOvfU1aFw9z3iWIjxEXWs_VZ5WxtPv0LjANizxtXYbw-qS_U-z-hcocdReWJEFuA4RI25cu_vHE_znlV5YJjiXphn3VPAjMIyIsuNsszvj5_2dJOzQLXrwNBYD58M%3D; TATravelInfo=V2*AY.2023*AM.4*AD.23*DY.2023*DM.4*DD.24*A.2*MG.-1*HP.2*FL.3*DSM.1681402942795*RS.1; TAUD=LA-1681402969814-1*RDD-1-2023_04_14*HDD-88479369-2023_04_23.2023_04_24.1*LG-88492422-2.1.F.*LD-88492423-.....; datadome=48rrncotA8zm1calWCjBfbe9iljwwWDuwfK00gFU_g-Z6bmCmSDC~gdT_qNTn56OlnGIC3E2yJD0InVlX09C0yi1QLs~73KPLa7PcDY0Bm8tr1xXepLEJlK8eURosqrG; TATrkConsent=eyJvdXQiOiIiLCJpbiI6IkFMTCJ9; _pbjs_userid_consent_data=3524755945110770; _lc2_fpi=28c87295fd99--01gxxpv6k9k780sw9js022exyr; __gads=ID=827df69fb8d72ddb:T=1681402996:S=ALNI_Mb2vSRsyK9IT9j6EXS6MVQ1VKPcxw; __gpi=UID=00000bf442b1bd70:T=1681402996:RT=1681402996:S=ALNI_MaTMv6KSlKc_x4Cys9UDNUQiToZGg; _lr_env_src_ats=false; TAAUTHEAT=vLnYiQMDSM22RrZuABQCnPHiQaRASfmTxbKSWaoBQjSw5voHa0W0IoDcVqMnQW_XXVBzUpXopn6YuzZznsGJYrWqrxkGvwLX_zCA2sZFgmN3fdhBA276GErRjhiNxS3l11M4v-cjKYbQjBpDUs_6aWiJXF71XTrt0pjnI-NLnSuo8ON-TpbGPP8fpwVLl0QZh42FxPV9GtOhgvXQOInF37_ekqvMOkUVyQLQk_bq; __vt=QozSuoCoD1oz8QTPABQCwDrKuA05TCmUEEd0_4-PPCS3hpYyWhW8DTq3u2gTOZS7AjEm8vYd0UYbjER1F_DJnwWJ_biwudflpHlvJuepRbHIpTVH0vOCvZS-47SQOZbnV5vqFxPmbNuomisYw0UdqQhKv8RxjPM9KyHMJgQfx-j4ub-xjliZygFRt9PA1yOCB7bETBnKCbBA40U; BEPIN=%1%18780b3558a%3Bweb165a.a.tripadvisor.com%3A30023%3B; TASession=V2ID.281D9B08763C44D28A5D5F4A7C4BCD27*SQ.3*LS.DemandLoadAjax*HS.recommended*ES.popularity*DS.5*SAS.popularity*FPS.oldFirst*TS.05CF65BF8C8FC6BD4C8D8EC594C48F41*LF.vi*FA.1*DF.0*TRA.true*LD.13813357*EAU.8; SRT=TART_SYNC; ServerPool=A; TASID=281D9B08763C44D28A5D5F4A7C4BCD27; TAReturnTo=%1%%2FHotel_Review-g293928-d13813357-Reviews-Melia_Vinpearl_Nha_Trang_Empire-Nha_Trang_Khanh_Hoa_Province.html; ak_bmsc=396C870E09387E9F7AB83FD25740AAEC~000000000000000000000000000000~YAAQxPEoF78pSFyHAQAATFizgBNuZDNH4D79FGI3WHYpJv5DZQS6hxMevtI1subVtHOsfMmPsA9qHR1b8qugWkLPNJuy3W/11u1vJjWlt4zRyt9CGoQXOjnPHo9aqugeoT1E3sAQ+VS2Pbkn0WKHFF/dzrZ8IjuFCwht7E0XyJFdfaYxBOt7EcDTJmJks+Cnq488hHNJrXUJemr2kmIj6qUCnEy+eIHYAZSE4UjkbOyAC5PcHWz4ftlNoMt28XQDieIcPUGWWheFwQUfUGm70ILkNuikgabMs7rbN7JgZWIB5BriK79c99TJx2Shon6IwSxZgm/LDiCIFfouWJ0jieL9w311EBHJ4r5BiOdaYJ+I83khdeW9qJp+26i10lRCfDOVEoow1LWZI3Fso3Oets9EyA==; roybatty=TNI1625!AAo%2FL1AnzYNcLBM04mXQISYACuNs%2FNkkrkDQw9yxX1oUeXAUKtnD%2FzVN87N6b9uBDVY6YQZj0V3YpOnLT4l6cvTSiWor4zDsj%2Be4l1dH0v9pfrJahEgzS1CStDrr99goOhgmX0IJiaLa4vpMTEIjuMFMwIyzJHpeplpgysMBiGs2%2C1; bm_sv=FA657ADBE5F956727C2B3899E48F53D0~YAAQxPEoF24uSFyHAQAA1YmzgBPrrphlor9JVb7djP0HP//mNFlJvnGej8bLUMYqEdtNBBtShj6lCHzLQ0/bjkI/sJ/8YAjATAzGGDSXLVr3rh3KPX37QLrISM8ixUUvITo5iYLvfv30LmTGt3AWb4HfpZOyHXg7QBVEfh7lg9PNKCjPeRab4LQsP2lhMnKapRK+3a3k0LGAEi/sjPiNBxOiCmdcX6VHg6uZEq5SCc1D8rv58GAVAP1bxsY6GMtwxnQMyG+XmuM=~1
Upgrade-Insecure-Requests: 1
Sec-Fetch-Dest: document
Sec-Fetch-Mode: navigate
Sec-Fetch-Site: cross-site
Pragma: no-cache
Cache-Control: no-cache
TE: trailers
"""

metadata = dict()
url = "https://www.agoda.com/oriental-danang/hotel/all/da-nang-vn.html?locale=en-us&ckuid=fdedba03-4477-452c-b8e2-e0518e1022c5&prid=0&currency=VND&correlationId=10e7ea96-5365-4632-8824-b99bc1a13501&analyticsSessionId=-3552745395782370614&pageTypeId=7&realLanguageId=1&languageId=1&origin=VN&cid=1899796&userId=fdedba03-4477-452c-b8e2-e0518e1022c5&whitelabelid=1&loginLvl=0&storefrontId=3&currencyId=78&currencyCode=VND&htmlLanguage=en-us&cultureInfoName=en-us&machineName=hk-acmweb-2007&trafficGroupId=2&sessionId=rldkjqkrbmolaz45h1jnejhx&trafficSubGroupId=133&aid=284594&useFullPageLogin=true&cttp=4&isRealUser=true&mode=production&browserFamily=Chrome&checkIn=2023-05-06&checkOut=2023-05-07&rooms=1&adults=4&childs=1&childages=-1&priceCur=VND&los=1&textToSearch=Oriental%20Danang&productType=-1&travellerType=1&familyMode=off"
list_url = [
    "https://www.agoda.com/oriental-danang/hotel/all/da-nang-vn.html?locale=en-us&ckuid=fdedba03-4477-452c-b8e2-e0518e1022c5&prid=0&currency=VND&correlationId=10e7ea96-5365-4632-8824-b99bc1a13501&analyticsSessionId=-3552745395782370614&pageTypeId=7&realLanguageId=1&languageId=1&origin=VN&cid=1899796&userId=fdedba03-4477-452c-b8e2-e0518e1022c5&whitelabelid=1&loginLvl=0&storefrontId=3&currencyId=78&currencyCode=VND&htmlLanguage=en-us&cultureInfoName=en-us&machineName=hk-acmweb-2007&trafficGroupId=2&sessionId=rldkjqkrbmolaz45h1jnejhx&trafficSubGroupId=133&aid=284594&useFullPageLogin=true&cttp=4&isRealUser=true&mode=production&browserFamily=Chrome&checkIn=2023-05-06&checkOut=2023-05-07&rooms=1&adults=4&childs=1&childages=-1&priceCur=VND&los=1&textToSearch=Oriental%20Danang&productType=-1&travellerType=1&familyMode=off",
    'https://www.agoda.com/sala-danang-beach-hotel/hotel/da-nang-vn.html?finalPriceView=1&isShowMobileAppPrice=false&cid=-1&numberOfBedrooms=&familyMode=false&adults=2&children=0&rooms=1&maxRooms=0&checkIn=2023-05-9&isCalendarCallout=false&childAges=&numberOfGuest=0&missingChildAges=false&travellerType=-1&showReviewSubmissionEntry=false&currencyCode=VND&isFreeOccSearch=false&isCityHaveAsq=false&los=1&searchrequestid=8fcc6700-97d3-497d-a65e-87aa640900dd',
    'https://www.agoda.com/grand-sunrise-boutique-hotel_2/hotel/da-nang-vn.html?finalPriceView=1&isShowMobileAppPrice=false&cid=-1&numberOfBedrooms=&familyMode=false&adults=2&children=0&rooms=1&maxRooms=0&isCalendarCallout=false&childAges=&numberOfGuest=0&missingChildAges=false&travellerType=-1&showReviewSubmissionEntry=false&currencyCode=VND&isFreeOccSearch=false&isCityHaveAsq=false&los=1&searchrequestid=8fcc6700-97d3-497d-a65e-87aa640900dd&checkin=2023-05-12',
    'https://www.agoda.com/haian-beach-hotel-spa/hotel/da-nang-vn.html?finalPriceView=1&isShowMobileAppPrice=false&cid=-1&numberOfBedrooms=&familyMode=false&adults=2&children=0&rooms=1&maxRooms=0&isCalendarCallout=false&childAges=&numberOfGuest=0&missingChildAges=false&travellerType=-1&showReviewSubmissionEntry=false&currencyCode=VND&isFreeOccSearch=false&isCityHaveAsq=false&los=1&searchrequestid=8fcc6700-97d3-497d-a65e-87aa640900dd&checkin=2023-05-11',
    'https://www.agoda.com/peninsula-hotel-h35038730/hotel/da-n-ng-vn.html?finalPriceView=1&isShowMobileAppPrice=false&cid=-1&numberOfBedrooms=&familyMode=false&adults=2&children=0&rooms=1&maxRooms=0&checkIn=2023-05-9&isCalendarCallout=false&childAges=&numberOfGuest=0&missingChildAges=false&travellerType=-1&showReviewSubmissionEntry=false&currencyCode=VND&isFreeOccSearch=false&isCityHaveAsq=false&los=1&searchrequestid=8fcc6700-97d3-497d-a65e-87aa640900dd',
    'https://www.agoda.com/balcona-hotel-da-nang/hotel/da-nang-vn.html?finalPriceView=1&isShowMobileAppPrice=false&cid=-1&numberOfBedrooms=&familyMode=false&adults=2&children=0&rooms=1&maxRooms=0&checkIn=2023-05-9&isCalendarCallout=false&childAges=&numberOfGuest=0&missingChildAges=false&travellerType=-1&showReviewSubmissionEntry=false&currencyCode=VND&isFreeOccSearch=false&isCityHaveAsq=false&los=1&searchrequestid=8fcc6700-97d3-497d-a65e-87aa640900dd',
]
# Use options to have your selenium headless
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
DRIVER_BIN = os.path.join(PROJECT_ROOT, "chromedriver")

driver = webdriver.Chrome(executable_path=DRIVER_BIN)

hotel_room_type = defaultdict(list)
for indx, url in enumerate(list_url):
    driver.get(url)
    time.sleep(5)
    list_rs = []

    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    room_types = soup.find_all('div', {"class": "MasterRoom"})
    for type in room_types:
        try:
            name = type.find(
                'span', {'data-selenium': "masterroom-title-name"}).get_text(strip=True)
            images = type.find_all('img')
            link_images = ['https:'+image['src'] for image in images]

            animest = type.find_all('li', {"class": "MasterRoom-amenitiesItem"})
            square = animest[2].find('div', {
                                    "class": "MasterRoom-amenitiesTitle"}).get_text(strip=True).replace('Room size: ', "")
            beds = animest[1].find('div', {"class": "MasterRoom-amenitiesTitle"}).get_text(strip=True)
            children = random.randint(0, 3)
            adults = random.randint(2, 4)
            price = type.find('div', {'class': 'CrossedOutPrice'}).get_text(
                strip=True).replace("₫ ", "").replace(",", "")
            description = type.find('div', {
                                    'class': 'ChildRoomsList-room-featurebucket ChildRoomsList-room-featurebucket-Benefits'})
            rs = {
                "name": name,
                "images": link_images,
                "square": square,
                'beds': beds,
                'children': children,
                'adults': adults,
                "price": price,
                'description': str(description)
            }

            list_rs.append(rs)
        except:
            continue
    hotel_room_type[indx] = list_rs


with open('room_type.txt', 'w', encoding='utf-8') as f:
    json.dump(hotel_room_type, f, ensure_ascii=False)
