import time
from random import choice
from string import ascii_uppercase

from bs4 import BeautifulSoup
from selenium import webdriver
import os
import json
import re
import requests

from selenium.webdriver.chrome.service import Service


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
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
DRIVER_BIN = os.path.join(PROJECT_ROOT, "chromedriver")
domain_prefix = "https://www.tripadvisor.com.vn"

searched_page_urls = [
    # "https://www.tripadvisor.com.vn/Search?q=%C4%91%C3%A0%20n%E1%BA%B5ng&searchSessionId=000822b055e36922.ssid&sid=272A290281CB431FBB66B75B9DEB7B341682093771184&blockRedirect=true&ssrc=m&isSingleSearch=true&geo=1&o={0}",
    # "https://www.tripadvisor.com.vn/Search?q=nha%20trang&searchSessionId=000822b055e36922.ssid&sid=FE038E2301404C21891BA4CBFD01EF171682315847299&blockRedirect=true&ssrc=m&isSingleSearch=true&geo=1&o={0}",
    # "https://www.tripadvisor.com.vn/Search?q=ninh%20b%C3%ACnh&searchSessionId=000822b055e36922.ssid&sid=922AF968352C43848579E50530CD7E5F1682933858128&blockRedirect=true&ssrc=m&isSingleSearch=true&geo=1&o={0}",
    # "https://www.tripadvisor.com.vn/Search?q=h%E1%BB%93&searchSessionId=000822b055e36922.ssid&sid=922AF968352C43848579E50530CD7E5F1682934000755&blockRedirect=true&ssrc=m&isSingleSearch=true&geo=293925&o={0}",
    # "https://www.tripadvisor.com.vn/Search?q=%C4%91%C3%A0&searchSessionId=000822b055e36922.ssid&sid=9D1084172F784712ACADD3EEDD5F2A0A1682942939951&blockRedirect=true&ssrc=m&isSingleSearch=true&geo=15334653&o={0}",
    # "https://www.tripadvisor.com.vn/Search?q=h%C3%A0%20n%E1%BB%99i&searchSessionId=000822b055e36922.ssid&sid=9D1084172F784712ACADD3EEDD5F2A0A1682942990310&blockRedirect=true&ssrc=m&isSingleSearch=true&geo=1&o={0}",
    # "https://www.tripadvisor.com.vn/Search?q=ph%C3%BA%20qu%E1%BB%91c&searchSessionId=000822b055e36922.ssid&sid=9D1084172F784712ACADD3EEDD5F2A0A1682943049801&blockRedirect=true&ssrc=m&isSingleSearch=true&geo=1&o={0}",
    "https://www.tripadvisor.com.vn/Search?q=H%C3%A0%20Giang&searchSessionId=000822b055e36922.ssid&sid=12F5B71BCF6C4580BA5345EF272826371683524657316&blockRedirect=true&ssrc=m&isSingleSearch=true&geo=1&o={0}"
]


def get_geo_hotel(page_url):
    geo_data = dict()
    hotel_id_pattern = r"d(\d+?)-"
    hotel_matched = re.findall(hotel_id_pattern, page_url)
    hotel_id = hotel_matched[0]

    params = {
        "rn": 1,
        "rc": "Hotel_Review",
        "stayDates": "2023_5_7_2023_5_8",
        "guestInfo": "1_2",
        "placementName": "Hotel_Review_MapDetail_Anchor",
        "currency": "VND",
    }

    response = requests.get(f"https://www.tripadvisor.com.vn/data/1.0/mapsEnrichment/hotel/{hotel_id}", params=params, headers=get_header(req_header))
    if response.status_code == 200:
        geo_data = {
            "latitude": response.json()["hotels"][0]['location']['geoPoint']['latitude'],
            "longitude": response.json()["hotels"][0]['location']['geoPoint']['longitude']
        }

    return geo_data


def get_hotel_name(page_url):
    page_data = dict()

    try:
        hotel_images = []
        chrome_executable = Service(executable_path=DRIVER_BIN, log_path='NUL')
        driver = webdriver.Chrome(service=chrome_executable)
        driver.get(page_url)
        time.sleep(2)
        page = driver.page_source
        soup = BeautifulSoup(page, 'html.parser')

        images_boxes = soup.find_all("img", {"class": "_Q t _U s l KSVvt"})
        for images_box in images_boxes:
            image_url = images_box["src"]
            if image_url:
                image_url = image_url.replace("w=100", "w=1200")
                hotel_images.append(image_url)
        location_box = soup.find("div", {"class": "gZwVG H3 f u ERCyA"})
        location_text = location_box.find("span", {"class": "fHvkI PTrfg"}).text
        name_box = soup.find("h1", {"class": "QdLfr b d Pn"})
        hotel_name = name_box.text
        room_number_box = soup.find_all("div", {"class": "IhqAp Ci"})[-1]
        room_number = room_number_box.text

        page_data["location"] = location_text
        page_data["name"] = hotel_name
        page_data["geo_data"] = get_geo_hotel(page_url)
        page_data["room_number"] = room_number
        if hotel_images:
            page_data["images"] = hotel_images
    except Exception as e:
        print(e)
        print(f"Error when fetch url: {page_url}")

    return page_data


def create_format_url_string(url: str):
    review_str = "-Reviews"
    index = url.find(review_str)
    index += len(review_str)
    return url[:index] + "{0}" + url[index:]


def get_single_page_content(raw_url, file_name):
    metadata = dict()
    page_offset = 0
    is_next = True
    max_tried = 5
    count_tried = 0
    review_data = []
    page_content = dict()
    if "Hotel_Review" not in raw_url:
        return

    while is_next:
        url = ""
        try:
            driver = webdriver.Chrome(executable_path=DRIVER_BIN)
            # Use options to have your selenium headless
            offset_str = f"-or{str(page_offset)}" if page_offset else ""
            url = raw_url.format(offset_str)
            driver.get(url)

            page = driver.page_source
            soup = BeautifulSoup(page, 'html.parser')
            metadata["hotel"] = {
                "name": soup.find("h1", {"id": "HEADING"}).text,
                "location": soup.find("span", {"class": "fHvkI PTrfg"}).text,
            }

            reviews = soup.find_all("div", {"class": "YibKl MC R2 Gi z Z BB pBbQr"})
            print(f"page offset: {page_offset}: {len(reviews)}...")
            for idx, _review in enumerate(reviews):
                review_rating_box = _review.find(
                    "div", {"data-test-target": "review-rating"})
                review_rating_box = review_rating_box.contents[0]
                trim_len = len("bubble_")
                review_rating = review_rating_box["class"][1][trim_len]
                location_box = _review.find("span", {"class": "default LXUOn small"})
                review_title = _review.find("div", {"data-test-target": "review-title"})
                review_title = review_title.find("span").contents[0].text
                review_content = _review.find(
                    "span", {"class": "QewHA H4 _a"}).contents[0].text
                review_data.append({
                    "name": _review.find("a", {"class": "ui_header_link uyyBf"}).text,
                    "avatar": "",
                    "review_rating": review_rating,
                    "review_title": review_title,
                    "review_content": review_content,
                    "reviewer_location": location_box.contents[-1].text if location_box else "dumpxxx"
                })

            page_offset += 5
            next_button = soup.find("a", {"class": "ui_button nav next primary"})
            disabled_next_button = soup.find("a", {"class": "ui_button nav next primary disabled"})
            is_next = next_button and not disabled_next_button
        except Exception as e:
            print(e)
            print("Error with url: ", url)
            count_tried += 1
            is_next = count_tried < max_tried
            page_offset += 5

        hotel_page_url = raw_url.format("")
        page_content = get_hotel_name(hotel_page_url)

    with open(f'{file_name}.json', 'w', encoding='utf-8') as file:
        print(f"Fetched page: {raw_url} with {str(len(review_data))} reviews")
        json.dump(dict(content=review_data, hotel=page_content), file, ensure_ascii=False)


def get_file_name_from_url(url):
    import re
    file_name = ""

    pattern = r"https://www.tripadvisor\.com\.vn/(.*?)\.html"
    matches = re.findall(pattern, url)
    if matches:
        file_name = matches[0]

    return file_name or ''.join(choice(ascii_uppercase) for i in range(12))


def get_all_page_url_with_searched_page_url(search_page_url):
    is_next = True
    step = 30
    offset = 30
    all_page_urls = []

    try:
        while is_next:
            real_page_url = search_page_url.format(offset)
            chrome_executable = Service(executable_path=DRIVER_BIN, log_path='NUL')
            driver = webdriver.Chrome(service=chrome_executable)
            driver.get(real_page_url)
            time.sleep(3)

            page = driver.page_source
            soup = BeautifulSoup(page, 'html.parser')

            preview_object_containers = soup.find_all("div", {"class": "ui_columns is-mobile result-content-columns"})
            for preview_object_container in preview_object_containers:
                try:
                    preview_title = preview_object_container.find("div", {"class": "result-title"})
                    _page_url = preview_title["onclick"][50:]
                    _url_pattern = r"/(.*?)\'"
                    matches = re.findall(_url_pattern, _page_url)
                    _page_url = matches[0]
                    all_page_urls.append(_page_url)
                except Exception as e:
                    pass

            print(f"Fetched {len(all_page_urls)} urls ...")
            next_button = soup.find("a", {"class": "ui_button nav next primary"})
            disabled_next_button = soup.find("a", {"class": "ui_button nav next primary disabled"})

            is_next = next_button and not disabled_next_button and len(all_page_urls) <= 53
            offset += step
    except Exception as e:
        print(e)

    return all_page_urls


for idx, search_page_url in enumerate(searched_page_urls):
    all_page_urls = get_all_page_url_with_searched_page_url(search_page_url)
    print(f">>>>> Found {str(len(all_page_urls))} url: ")
    print(all_page_urls)
    # with open(f'searched_page_{idx}.json', 'w', encoding='utf-8') as file:
    #     json.dump(dict(urls=all_page_urls), file, ensure_ascii=False)

    # Fetching page 22 with url: Hotel_Review-g15295685-d13980353-Reviews-Vinpearl_Resort_Golf_Nam_Hoi_An-Binh_Minh_Quang_Nam_Province.html
    # all_page_urls = ["Hotel_Review-g298085-d6370235-Reviews-Premier_Village_Danang_Resort_Managed_by_Accor-Da_Nang.html", "Attraction_Review-g298085-d5531576-Reviews-Lady_Buddha-Da_Nang.html", "Hotel_Review-g298085-d9874032-Reviews-Serene_Beach_Hotel-Da_Nang.html", "Attraction_Review-g298085-d6612108-Reviews-Dragon_Bridge-Da_Nang.html", "Attraction_Review-g298085-d454980-Reviews-The_Marble_Mountains-Da_Nang.html", "Attraction_Review-g298085-d24111506-Reviews-Santa_Spa-Da_Nang.html", "Hotel_Review-g298085-d20063843-Reviews-HAIAN_Riverfront_Hotel_Danang-Da_Nang.html", "Hotel_Review-g298085-d2179507-Reviews-Danang_Marriott_Resort_Spa-Da_Nang.html", "Hotel_Review-g298085-d14794498-Reviews-Ruby_Light_Hotel_by_NNT_Hotel_Collection-Da_Nang.html", "Hotel_Review-g298085-d19453440-Reviews-Muong_Thanh_Luxury_Song_Han_Hotel-Da_Nang.html", "Hotel_Review-g15296807-d6668057-Reviews-FIVITEL_King_Hotel-My_An_Da_Nang.html", "Hotel_Review-g298085-d6161470-Reviews-Fivitel_Boutique_Da_Nang-Da_Nang.html", "Hotel_Review-g298085-d3236066-Reviews-Brilliant_Hotel-Da_Nang.html", "Hotel_Review-g298085-d24948586-Reviews-Wink_Hotel_Danang_Centre-Da_Nang.html", "Hotel_Review-g298085-d13297744-Reviews-Nhu_Minh_Plaza_Danang_Hotel-Da_Nang.html", "Attraction_Review-g298085-d7687457-Reviews-My_Khe_Beach-Da_Nang.html", "Hotel_Review-g298085-d15142242-Reviews-Eden_Hotel_Danang-Da_Nang.html", "Hotel_Review-g298085-d14058690-Reviews-Balcona_Hotel_Da_Nang-Da_Nang.html", "Hotel_Review-g298085-d13084590-Reviews-New_Orient_Hotel-Da_Nang.html", "Hotel_Review-g298085-d13326393-Reviews-Sheraton_Grand_Danang_Resort_Convention_Center-Da_Nang.html", "Hotel_Review-g298085-d1732187-Reviews-Pullman_Danang_Beach_Resort-Da_Nang.html", "Attraction_Review-g298085-d18114312-Reviews-Oani_Spa-Da_Nang.html", "Hotel_Review-g298085-d9570796-Reviews-Ana_Maison_Boutique_Hotel-Da_Nang.html", "Hotel_Review-g298085-d24073544-Reviews-Nesta_Hotel_Da_Nang-Da_Nang.html", "Hotel_Review-g298085-d1575735-Reviews-One_Opera_Danang_Hotel-Da_Nang.html", "Hotel_Review-g298085-d15327970-Reviews-Rosamia_Da_Nang_Hotel-Da_Nang.html", "Hotel_Review-g298085-d2340470-Reviews-Hyatt_Regency_Danang_Resort_Spa-Da_Nang.html", "Hotel_Review-g298085-d24102969-Reviews-Cozy_Danang_Boutique_Hotel-Da_Nang.html", "Restaurant_Review-g298085-d24985405-Reviews-Cardi_Pizzeria_Bach_Dang-Da_Nang.html", "Hotel_Review-g298085-d17732168-Reviews-Minh_Boutique-Da_Nang.html", "Hotel_Review-g298085-d8299463-Reviews-Palmier_Hotel_Apartment-Da_Nang.html", "Restaurant_Review-g298085-d17760929-Reviews-Bep_Cuon_Da_Nang-Da_Nang.html", "Hotel_Review-g298085-d15153595-Reviews-TMS_Hotel_Da_Nang_Beach-Da_Nang.html", "Hotel_Review-g298085-d8300044-Reviews-Golden_Star_Hotel-Da_Nang.html", "Hotel_Review-g298085-d12579296-Reviews-Cocobay_Danang_Boutique_Hotels-Da_Nang.html", "Hotel_Review-g298085-d14094174-Reviews-DLG_Hotel-Da_Nang.html", "Hotel_Review-g298085-d9702684-Reviews-Hadana_Boutique_Hotel-Da_Nang.html", "Hotel_Review-g298085-d19482545-Reviews-Daisy_Boutique_Hotel_Apartment-Da_Nang.html", "Hotel_Review-g298085-d12117671-Reviews-Adaline_Hotel_Suite-Da_Nang.html", "Hotel_Review-g298085-d1198755-Reviews-Da_Nang_Riverside_Hotel-Da_Nang.html", "Hotel_Review-g298085-d7891016-Reviews-Samdi_Hotel-Da_Nang.html", "Hotel_Review-g298085-d7932663-Reviews-Vanda_Hotel-Da_Nang.html", "Hotel_Review-g298085-d24863133-Reviews-Golden_Lotus_Grand_Da_Nang-Da_Nang.html", "Attraction_Review-g298085-d13084698-Reviews-Silk_Spa_Da_Nang-Da_Nang.html", "Hotel_Review-g298085-d7760658-Reviews-Fusion_Suites_Danang_Beach-Da_Nang.html", "Attraction_Review-g298085-d11674427-Reviews-Herbal_Spa-Da_Nang.html", "Hotel_Review-g298085-d11779930-Reviews-Sofia_Suite_Hotel_Spa_Danang-Da_Nang.html", "Hotel_Review-g298085-d8147265-Reviews-Galavina_Danang_Hotel-Da_Nang.html", "Attraction_Review-g298085-d454979-Reviews-Da_Nang_Museum_of_Cham_Sculpture-Da_Nang.html", "Hotel_Review-g298085-d12710754-Reviews-Eco_Green_Boutique_Hotel-Da_Nang.html", "Hotel_Review-g298085-d11895549-Reviews-Luxtery_Hotel-Da_Nang.html", "Hotel_Review-g298085-d12676316-Reviews-Central_Hotel_Spa-Da_Nang.html", "Hotel_Review-g298085-d12391393-Reviews-SEN_Boutique_Hotel-Da_Nang.html", "Hotel_Review-g293925-d20411635-Reviews-La_Vela_Saigon_Hotel-Ho_Chi_Minh_City.html", "Hotel_Review-g298085-d12268599-Reviews-Grandvrio_City_Danang_by_Route_Inn_Group-Da_Nang.html", "Hotel_Review-g298085-d17695824-Reviews-Ocean_View_Hotel_Da_Nang-Da_Nang.html", "Hotel_Review-g298085-d14969237-Reviews-Seashore_Hotel_Apartment-Da_Nang.html", "Hotel_Review-g298085-d12123736-Reviews-Alani_Hotel_Spa-Da_Nang.html", "Hotel_Review-g298085-d12970369-Reviews-Haka_Hotel_Apartment-Da_Nang.html", "Hotel_Review-g298085-d21015072-Reviews-Golden_Lotus_Hotel-Da_Nang.html", "Hotel_Review-g298085-d16820992-Reviews-The_Code_Hotel_Spa-Da_Nang.html", "Hotel_Review-g298085-d23976746-Reviews-Draco_Hotel_Suites-Da_Nang.html", "Hotel_Review-g298085-d12442254-Reviews-Dylan_Hotel_Da_Nang-Da_Nang.html", "Hotel_Review-g293928-d15353581-Reviews-Vinpearl_Sealink_Nha_Trang-Nha_Trang_Khanh_Hoa_Province.html", "Hotel_Review-g298085-d14800987-Reviews-Aria_Grand_Da_Nang_Hotel_Apartments-Da_Nang.html", "Hotel_Review-g298085-d4346231-Reviews-Eden_Plaza_Da_Nang_Hotel-Da_Nang.html", "Hotel_Review-g298085-d15521854-Reviews-Grand_Cititel_Danang_Hotel-Da_Nang.html", "Hotel_Review-g15339118-d14932943-Reviews-Grand_Gold_Hotel-Tho_Quang_Son_Tra_Peninsula_Da_Nang.html", "Hotel_Review-g17786366-d18207115-Reviews-Maximilan_Danang_Beach_Hotel-Son_Tra_Peninsula_Da_Nang.html", "Hotel_Review-g298085-d6609499-Reviews-Melia_Danang_Beach_Resort-Da_Nang.html", "Hotel_Review-g298085-d3914006-Reviews-Orchid_Hotel-Da_Nang.html", "Hotel_Review-g298085-d21020893-Reviews-Canvas_Danang_Beach_Hotel-Da_Nang.html", "Hotel_Review-g298085-d4870701-Reviews-Happy_Day_Hotel_Da_Nang-Da_Nang.html", "Hotel_Review-g298085-d12722484-Reviews-Touch_Danang_Hostel-Da_Nang.html", "Hotel_Review-g298085-d12829336-Reviews-Gemma_Hotel-Da_Nang.html", "Hotel_Review-g19779171-d23169144-Reviews-Radisson_Hotel_Danang-Phuoc_My_Son_Tra_Peninsula_Da_Nang.html", "Attraction_Review-g298085-d15588293-Reviews-Danang_Green_Travel-Da_Nang.html", "Hotel_Review-g298085-d12646017-Reviews-Raon_Danang_Beach-Da_Nang.html", "Hotel_Review-g298085-d13846812-Reviews-Altara_Suites-Da_Nang.html", "Hotel_Review-g298085-d15225205-Reviews-Grand_Sunrise_Boutique_Hotel-Da_Nang.html", "Hotel_Review-g298085-d12221349-Reviews-Grand_Sunrise_3_Hotel-Da_Nang.html", "Hotel_Review-g298085-d13228168-Reviews-Lamuno_Hotel-Da_Nang.html", "Hotel_Review-g298085-d7787047-Reviews-Diamond_Sea_Hotel-Da_Nang.html", "Hotel_Review-g298085-d14016792-Reviews-Greenery_Hotel-Da_Nang.html", "Hotel_Review-g298085-d10181933-Reviews-Mercure_Danang_French_Village_Bana_Hills_Hotel-Da_Nang.html", "Attraction_Review-g298085-d7021088-Reviews-SKY36-Da_Nang.html", "Attraction_Review-g298085-d12273530-Reviews-Da_Nang_Catheral-Da_Nang.html", "Hotel_Review-g15296807-d19730171-Reviews-Senorita_Boutique_Hotel-My_An_Da_Nang.html", "Hotel_Review-g298085-d8431339-Reviews-Cicilia_Hotels_Spa-Da_Nang.html", "Hotel_Review-g15296807-d19254969-Reviews-Sofiana_My_Khe_Hotel_Spa-My_An_Da_Nang.html", "Hotel_Review-g19779171-d7389185-Reviews-Royal_Family_Hotel-Phuoc_My_Son_Tra_Peninsula_Da_Nang.html", "Hotel_Review-g11909288-d3504912-Reviews-Angsana_Lang_Co_Vietnam-Cu_Du_Loc_Vinh_Phu_Loc_District_Thua_Thien_Hue_Province.html", "Hotel_Review-g298085-d10255974-Reviews-FIVITEL_Queen-Da_Nang.html", "Hotel_Review-g298085-d8462721-Reviews-Le_House_Boutique_Hotel-Da_Nang.html", "Hotel_Review-g298085-d19935841-Reviews-Santa_Luxury_Hotel-Da_Nang.html", "Hotel_Review-g298085-d7787334-Reviews-Green_House_Hotel-Da_Nang.html", "Hotel_Review-g298085-d10182530-Reviews-Golden_Light_Hotel-Da_Nang.html", "Attraction_Review-g298085-d19417690-Reviews-Da_Nang_Travel_Car_Company-Da_Nang.html", "Hotel_Review-g298085-d13964367-Reviews-Parze_Ocean_Hotel_Spa-Da_Nang.html", "Hotel_Review-g298085-d21510279-Reviews-Chi_House_Danang_Hotel_Apartment-Da_Nang.html", "Hotel_Review-g298085-d12250113-Reviews-Le_Hoang_Beach_Hotel-Da_Nang.html", "Hotel_Review-g298085-d16952134-Reviews-Roliva_Hotel_Apartment_Danang-Da_Nang.html", "Hotel_Review-g19779171-d17591909-Reviews-Hai_Trieu_Hotel-Phuoc_My_Son_Tra_Peninsula_Da_Nang.html", "Hotel_Review-g298085-d14016789-Reviews-Rosetta_Hotel_Apartment-Da_Nang.html", "Attraction_Review-g298085-d12976292-Reviews-Maison_Spa_Da_Nang-Da_Nang.html", "Hotel_Review-g298085-d7403837-Reviews-Sofia_Boutique_Hotel_Da_Nang-Da_Nang.html", "Attraction_Review-g298085-d17546936-Reviews-Panda_Spa-Da_Nang.html", "Hotel_Review-g298086-d23019691-Reviews-Centara_Mirage_Resort_Mui_Ne-Phan_Thiet_Binh_Thuan_Province.html", "Hotel_Review-g298085-d10151876-Reviews-OYO_157_Centre_Hotel-Da_Nang.html", "Hotel_Review-g298085-d16917089-Reviews-Golden_Line_Danang_Hotel-Da_Nang.html", "Hotel_Review-g19935676-d10170259-Reviews-Mai_Boutique_Villa-An_Hai_Bac_Son_Tra_Peninsula_Da_Nang.html", "Hotel_Review-g298085-d9809627-Reviews-Da_nang_Han_River_Hotel-Da_Nang.html", "Hotel_Review-g19779171-d14025941-Reviews-Four_Points_by_Sheraton_Danang-Phuoc_My_Son_Tra_Peninsula_Da_Nang.html", "Restaurant_Review-g298085-d6961132-Reviews-Banh_xeo_Ba_Duong-Da_Nang.html", "Hotel_Review-g298085-d10049985-Reviews-Valentine_Hotel-Da_Nang.html", "Hotel_Review-g15296807-d11891076-Reviews-Yarra_Ocean_Suites_Danang-My_An_Da_Nang.html", "Hotel_Review-g298085-d1823746-Reviews-TIA_Wellness_Resort_Spa_Inclusive-Da_Nang.html", "Hotel_Review-g298085-d10175116-Reviews-Lucky_Bee_Homestay-Da_Nang.html", "Attraction_Review-g298085-d6372004-Reviews-Charm_Spa-Da_Nang.html", "Attraction_Review-g298085-d8090733-Reviews-Han_River_Bridge-Da_Nang.html", "Hotel_Review-g298085-d12250036-Reviews-The_Han_Hotel-Da_Nang.html", "Restaurant_Review-g298085-d13810289-Reviews-Thia_G-Da_Nang.html", "Hotel_Review-g298085-d6697462-Reviews-Sanouva_Danang_Hotel-Da_Nang.html", "Hotel_Review-g298085-d12596649-Reviews-Lis_Hotel-Da_Nang.html", "Hotel_Review-g298085-d12238939-Reviews-Little_Flower_Homestay-Da_Nang.html", "Hotel_Review-g298085-d3750946-Reviews-LEGEND_Boutique_Hotel-Da_Nang.html", "Hotel_Review-g298085-d12417548-Reviews-Danang_Moment_Boutique_Serviced_Apartment-Da_Nang.html", "Hotel_Review-g298085-d21041406-Reviews-M_Boutique_Danang-Da_Nang.html", "Hotel_Review-g298085-d10317572-Reviews-Danaciti_Hotel-Da_Nang.html", "Hotel_Review-g298085-d15300519-Reviews-Monsieur_Diesel_Hotel_Danang-Da_Nang.html", "Hotel_Review-g298085-d12730279-Reviews-Pavilion_Hotel_Danang-Da_Nang.html", "Hotel_Review-g298085-d23276595-Reviews-M_Suite_Danang-Da_Nang.html", "Hotel_Review-g298085-d12458667-Reviews-Mandila_Beach_Hotel_Danang-Da_Nang.html", "Hotel_Review-g298085-d14929076-Reviews-Lahome_Apartment_And_Villa-Da_Nang.html", "Hotel_Review-g298085-d15186970-Reviews-Jolia_Hotel_Apartment-Da_Nang.html", "Hotel_Review-g298086-d3478132-Reviews-The_Cliff_Resort_Residences-Phan_Thiet_Binh_Thuan_Province.html", "Attraction_Review-g298085-d24193508-Reviews-Santa_Spa-Da_Nang.html", "Hotel_Review-g19779171-d3240170-Reviews-Star_Hotel_Da_Nang-Phuoc_My_Son_Tra_Peninsula_Da_Nang.html", "Hotel_Review-g293928-d7305361-Reviews-Muong_Thanh_Luxury_Nha_Trang_Hotel-Nha_Trang_Khanh_Hoa_Province.html", "Hotel_Review-g17786366-d12295273-Reviews-Brilliant_Majestic_Villa_Hotel-Son_Tra_Peninsula_Da_Nang.html", "Hotel_Review-g298085-d15746947-Reviews-Pandora_Boutique_Da_Nang-Da_Nang.html", "Hotel_Review-g298085-d17484084-Reviews-CN_Palace_Boutique_Hotel_Spa-Da_Nang.html", "Hotel_Review-g17786366-d23333380-Reviews-Nguyen_Gia_Hotel-Son_Tra_Peninsula_Da_Nang.html", "Hotel_Review-g298085-d3210927-Reviews-Sun_Moon_Hotel_Hostel-Da_Nang.html", "Hotel_Review-g298085-d17379315-Reviews-The_Memory_Danang-Da_Nang.html", "Hotel_Review-g17786366-d10627716-Reviews-Star_City_Riverside_Hotel_By_Haviland-Son_Tra_Peninsula_Da_Nang.html", "Hotel_Review-g298085-d24838643-Reviews-Alan_Sea_Hotel_Danang-Da_Nang.html", "Hotel_Review-g298085-d8132288-Reviews-Jazz_Hotel-Da_Nang.html", "Hotel_Review-g298085-d3222457-Reviews-Fansipan_Danang_Hotel-Da_Nang.html", "Hotel_Review-g298085-d12222354-Reviews-Nam_Anh_Hotel-Da_Nang.html"]
    for _idx, page_url in enumerate(all_page_urls):
        # if _idx >= 22:
        #     break
        print(f"=== Fetching page {_idx} with url: {page_url} ===")
        page_url = domain_prefix + "/" + page_url
        page_url = create_format_url_string(page_url)
        file_name = get_file_name_from_url(page_url)

        get_single_page_content(page_url, file_name)
