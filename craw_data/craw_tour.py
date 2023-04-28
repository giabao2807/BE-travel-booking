import requests
import json
import random
import os
from bs4 import BeautifulSoup


link = 'https://www.vietnambooking.com/du-lich-trong-nuoc.html'

pages = [i for i in range(1, 11)]
link_page = [(link + '/' + str(page)) for page in pages]
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))


def soup_for_link(link):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36"}

    draw_r1 = requests.get(link, headers=headers)
    coverpage_drawn = draw_r1.content
    soap_drawn = BeautifulSoup(coverpage_drawn, 'html5lib')
    return soap_drawn


def get_detail_item(item, detail_link):
    page = soup_for_link(detail_link)
    group_image = page.find('div', {'id': 'owl-slider-tour-single-feature'})
    images = [] if not group_image else group_image.find_all('img')
    link_images = [img['src'].replace('\n', '') for img in images]
    item['images'] = link_images
    item['city'] = page.find(
        'table', {'class': 'tlb-info-tour'}).find_all('td')[0].get_text(strip=True)
    item['description'] = str(page.find(
        'div', {'class': 'single-box-excerpt'}))
    group = page.find_all('div', {'class': "panel panel-tour-product"})
    item['schedule_content'] =str(group[0].find(
        'div', {"class": "panel-collapse collapse in"}).find_all('div')[0])
    item['note'] = str(group[2].find(
        'div', {"class": "panel-collapse collapse in"}).find_all('div')[0])
    item['num_review'] = str(random.randint(1, 1000))
    item['group_size'] = str(random.randint(10, 30))
    return item


def get_detail_tour_for_page(list_item):
    list_rs = []
    for idx, item in enumerate(list_item):
        item_data = dict()
        image = item.find('div', {'class': 'box-img'})
        content = item.find('div', {'class': 'box-content'})
        if not image or not content:
            continue
        item_data['cover_image'] = image.find('a').find('img')['src']
        item_data['name'] = content.find('h3', {'class':'title-h3'}).get_text(strip=True)
        item_data['link_detail'] = content.find(
            'h3', {'class': 'title-h3'}).find('a').get_attribute_list('href')[0]
        item_data['total_days'] = content.find('table').find_all(
            'td')[1].get_text(strip=True)
        price_content = content.find(
            'div', {'class': 'box-price-promotion-tour'})
        item_data['price'] = price_content.find('del').get_text(
            strip=True) if price_content.find('del') else price_content.find(
            'span').get_text(strip=True)
        item_data = get_detail_item(item_data, item_data['link_detail'])
        list_rs.append(item_data)
    return list_rs


list_tour = []
for idx, page in enumerate(link_page):
    print(f"Crawling ... page {idx}: {page}")
    main_page = soup_for_link(page)
    list_item = main_page.find(
        'div', {'class': 'category-box-list-default-inner'}).find('ul').find_all("li")
    real_items = []
    for item in list_item:
        if len(item.find_all('div')) != 0:
            real_items.append(item)
    rs = get_detail_tour_for_page(real_items)
    list_tour.extend(rs)
    print(f"Done!")

with open(PROJECT_ROOT + 'tour_data.txt', 'w', encoding='utf-8') as f:
    json.dump(list_tour, f, ensure_ascii=False)
