import json
import os
import re

import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service


def get_header(req_header: str):
    header_settings = dict()
    for _line in req_header.split("\n"):
        if _line:
            item = _line.split(": ")
            header_settings[item[0]] = item[1]

    return header_settings


req_header = """
accept: */*
accept-encoding: gzip, deflate, br
accept-language: en-US,en;q=0.9
cookie: TAUnique=%1%enc%3AhZfZr2KWSOzmJiLD2PDlMDCQxVpYWx29GBOH21GdfltQ7hkA15SYJg%3D%3D; TASSK=enc%3AAG94dB0CBfPiOE3UTiX4obJv8HnSk4msfwPAF3PZn6v3TELCTHKG45V056%2BzPOxrGd3s2UXOXdjf%2F2qPQ7yX1qNeevAlaMaDbpJeslIt2DWZp%2BdXqeP46mU%2FHS1eQx6Wyg%3D%3D; TATrkConsent=eyJvdXQiOiIiLCJpbiI6IkFMTCJ9; TART=%1%enc%3AKQVDKAxiMUoWQ3Jc%2FlWoCRlXdDW9LqG78srxJvACqG9utSKSevkefl2Kd76e7cg1lyRpkes7zLo%3D; TADCID=C_qdQJvlNQzu526uABQCXdElnkGETRW-Svh01l3nWnUKgLVUEUpOxIJebDUkPY40khh9XRrgDwjIcxGhe_brXDhJnrbBU6O0sbk; TAAUTHEAT=DpLSwnzH9ToAapxnABQCnPHiQaRASfmTxbKSWaoBQjThgKMEgROJPiETYr5g1FzE-uViKciBXKrh2v33fWvPu0oRYopFJk5jX4gTSDwSA1jo4Yh_MpQfpmwzz6mdtHSL95rD8iktvaLuZUUJxlLbrxlhS9xNn0QHJpwle-SL-IzXnzbjiZfr__FwXbA9TpN-OcCR-0_cFA0ZoMJfGQ5r_Kel4eiSQ-4SosD_FOvx; TATravelInfo=V2*AY.2023*AM.5*AD.7*DY.2023*DM.5*DD.8*A.2*MG.-1*HP.2*FL.3*DSM.1682237984563*RS.1; PMC=V2*MS.27*MD.20230413*LD.20230423; PAC=AJB21_c5Zq4OHFTx2FvJRbWFqx7Yz5xO2j5UWTqUOZKe7aEmYEez-alQ1Q-ZZFekNZLgXQn7WZilz5fd6krV4R2TMZdIww4iMWOEpI5baut5QQGWGTa-I9QH47cpNdGknZpLrHlaJtbk4AtBXAWNNgwyxBIyX_teznGsHNIsztBnghxpNd3Ykhy3wgAgALIcxpOamVZ5IsuJtzc3bYakkam8uWBNCGZkAaNEeDda1_5I1os1f7qlFrzebaDJgwX36HaTomWboBqnifYjGyVyOTU%3D; ServerPool=B; VRMCID=%1%V1*id.10568*llp.%2FHotel_Review-g293925-d20411635-Reviews-La_Vela_Saigon_Hotel-Ho_Chi_Minh_City%5C.html*e.1682869718378; TASID=BEFAB9E72A124EB19F4D4EEB164275FE; TAReturnTo=%1%%2FHotel_Review-g293925-d20411635-Reviews-La_Vela_Saigon_Hotel-Ho_Chi_Minh_City.html; ak_bmsc=C7D03C020D44592FDE426A1CD1CF74A3~000000000000000000000000000000~YAAQJQ/TF+dTsKCHAQAA8IzNrhOiv4WOOKDqDxB8E3put+DZsGypvwcJl4/UkMQE6CI9dvIc0GCB4vAZeSlby3hc2Quv+FuDECloqt3TIPWrF1KpwvWQPSlVvTinjYREUQoD6tjPpmzfjrVs/t8dqloU4zHdYo/SMzt/XnG43YWe3xyU5zhaMV2lBCHLeLyS+FClRkSWs9dUZPml52xXskUeJub0Gm+sB1vEcVpd+RYthykXG4QqFFFCunMmC+hy8KmubnPymYfklDrv3+X9OS4aOvWPujLEm71gMz8s0X8JkTBc1V5IZiLG42csIr+lRaZRe6j4qlX1Tb0vxa3eT2pSWioxC8Bss8UwzGUjuL6nEThPzXdp184VOka2khu2IJoEC/LDqYPXXJLpM5xrnWZOqw==; roybatty=TNI1625!AO1OaeLy0epv2c5VHWoZi8M8lMbKpeMQeeyhEyqS%2BEfhyuI9SLgYRGFQXDWuLHjHNkmzAbkVPx%2F8VP0OSC17JBaBCKEoPNDHsqiIr2wudxF54CRiZfeBdZSG8%2F6uAJGLLuAJUerZEjsmwnai7V60jc%2BH1n2FqkuDLs7yQeYkh9Td%2C1; datadome=5AeRYBWMkii0OolVrIrQzfi8DKt7VIy3tsPWglDVRFbiRpgyjP8gd4CH6~OjgOPRQ6EdiIj3zNgyChztIEb8J_opHV935BPdO1vIsvyvNK6tsP6ROE9iMwA0wTsFnKjb; TASession=V2ID.BEFAB9E72A124EB19F4D4EEB164275FE*SQ.7*LS.DemandLoadAjax*HS.recommended*ES.popularity*DS.5*SAS.popularity*FPS.oldFirst*TS.05CF65BF8C8FC6BD4C8D8EC594C48F41*LF.vi*FA.1*DF.0*TRA.true*LD.20411635*EAU.8; TAUD=LA-1681400889003-1*RDD-1-2023_04_14*HC-88765909*VRC-88765910*HDD-837096006-2023_05_07.2023_05_08.1*LD-864041869-2023.5.7.2023.5.8*LG-864041871-2.1.F.; SRT=%1%enc%3AKQVDKAxiMUoWQ3Jc%2FlWoCRlXdDW9LqG78srxJvACqG9utSKSevkefl2Kd76e7cg1lyRpkes7zLo%3D; __vt=TRc7A5bcZH_oQ5qiABQCwDrKuA05TCmUEEd0_4-PPCTp8W5xCsjRnYaMVBEY9Jqlmtdrivb-o6E35FhVKul7VlVO5fnUzQAqMxnEYbODCI3r-innk8Ltg7KAzzdirIbSh-z4slzChWq-mAotCe61pPC5UxQP0EP9YOfY9heODKwe7RrOIdEZd2a_nmx6lwZlpJU6OnDpeil0dQ; bm_sv=87AB7AC25E536D19D2D4A78C42D4C723~YAAQJQ/TF3epsKCHAQAAnpfgrhNIU0pAS8z6GHP5eja8ETpP/FJ22kZ88hjJomWWxXQve4J6UnM2ePeXjjVEJTydhE/AsF7xMZtsQUOcP4vPJYqMJ51kw3ugwOVU4EqXFH95ujWX5HmOpiTZrRvr4mFVpUqVvp0ZP3NsxCsQq/modGHwpYl/u0BLFgOCLrRN4HJMal4qqkyyBMg67DxoxibR12b3xuIDZlnm7K0vJN2jjpOPYEUlb4Vn69ZwHbI37fsN+p4wJibt~1
referer: https://www.tripadvisor.com.vn/Hotel_Review-g293925-d20411635-Reviews-La_Vela_Saigon_Hotel-Ho_Chi_Minh_City.html
sec-ch-device-memory: 8
sec-ch-ua: "Chromium";v="112", "Google Chrome";v="112", "Not:A-Brand";v="99"
sec-ch-ua-arch: "x86"
sec-ch-ua-full-version-list: "Chromium";v="112.0.5615.138", "Google Chrome";v="112.0.5615.138", "Not:A-Brand";v="99.0.0.0"
sec-ch-ua-mobile: ?0
sec-ch-ua-model: ""
sec-ch-ua-platform: "Windows"
sec-fetch-dest: empty
sec-fetch-mode: cors
sec-fetch-site: same-origin
user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36
"""
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
DRIVER_BIN = os.path.join(PROJECT_ROOT, "chromedriver")
domain_prefix = "https://www.tripadvisor.com.vn"


def get_hotel_images(page_url):
    images = []

    try:
        chrome_executable = Service(executable_path=DRIVER_BIN, log_path='NUL')
        driver = webdriver.Chrome(service=chrome_executable)
        driver.get(page_url)
        # driver.execute_script("window.scrollTo(0, 500)")
        time.sleep(2)
        page = driver.page_source
        soup = BeautifulSoup(page, 'html.parser')

        images_boxes = soup.find_all("img", {"class": "_Q t _U s l KSVvt"})
        for images_box in images_boxes:
            image_url = images_box["src"]
            if image_url:
                image_url = image_url.replace("w=100", "w=1200")
                images.append(image_url)

    except Exception as e:
        print(e)
        print(f"Error when fetch url: {page_url}")

    return images


all_page = os.listdir()
total_pages = len(all_page)

for idx, file_name in enumerate(all_page):
    print(f"Progressing idx: {idx}/{total_pages}")
    if file_name.endswith(".json"):
        url = domain_prefix + "/" + file_name.replace(".json", ".html")
        url = url.format("")
        print(f"Crawling the hotel info url: {url}")
        with open(file_name, "r+", encoding='utf-8') as file:
            content = json.loads(file.read())
            hotel_images = get_hotel_images(url)
            if hotel_images:
                content["hotel"]["images"] = hotel_images
                file.seek(0)
                json.dump(content, file, ensure_ascii=False, indent=4)
                file.truncate()
            print("Done!")
