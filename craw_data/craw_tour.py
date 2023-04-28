import requests
import json
from bs4 import BeautifulSoup


link = 'https://www.vietnambooking.com/du-lich-trong-nuoc.html'

pages = [i for i in range(2, 30)]
link_page = [(link + '/' + str(page)) for page in pages]


def soup_for_link(link):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36"}

    draw_r1 = requests.get(link, headers=headers)
    coverpage_drawn = draw_r1.content
    soap_drawn = BeautifulSoup(coverpage_drawn, 'html5lib')
    return soap_drawn


def table_data_text(table):
    def row_get_data_text(tr, coltag='td'):  # td (data) or th (header)
        return [td.get_text(strip=True) for td in tr.find_all(coltag)]
    rows = []
    trs = table.find_all('tr')
    trs = trs[1:]

    for tr in trs:  # for every table row
        rows.append(row_get_data_text(tr, 'td'))  # data row
    return rows


def get_detail_item(item, detail_link):
    page = soup_for_link(detail_link)
    item['city'] = page.find(
        'table', {'class': 'tlb-info-tour'}).find_all('td')[0].get_text(strip=True)
    item['description'] = page.find('div', {'class': 'single-box-excerpt'})
    group = page.find_all('div', {'class': "panel panel-tour-product"})
    item['schedule_content'] = str(group[0].find(
        'div', {"class": "panel-collapse collapse in"}))
    item['note'] = str(group[2].find(
        'div', {"class": "panel-collapse collapse in"}))
    item['num_review'] = range(1,1000)
    return item


def get_detail_tour_for_page(real_items):
    list_rs = []
    for item in list_item:
        item_data = dict()
        image = item.find('div', {'class': 'box-img'})
        content = item.find('div', {'class': 'box-content'})
        if not image or not content:
            continue
        item_data['image'] = image.find('a').get_attribute_list('href')[0]
        item_data['name'] = content.find('h3', {'class':'title-h3'}).get_text(strip=True)
        item_data['link_detail'] = content.find(
            'h3', {'class': 'title-h3'}).find('a').get_attribute_list('href')[0]
        item_data['total_days'] = content.find('table').find_all(
            'td')[1].get_text(strip=True)
        item_data['price'] = content.find(
            'div', {'class': 'box-price-promotion-tour'}).find('del').get_text(strip=True)
        item_data = get_detail_item(item_data, item_data['link_detail'])
        list_rs.append(item_data)
    return list_rs


# main_page = soup_for_link(link)
# list_item = main_page.find(
#     'div', {'class': 'category-box-list-default-inner'}).find('ul').find_all("li")
#
# real_items = []
# for item in list_item:
#     if len(item.find_all('div'))!= 0:
#         real_items.append(item)
#
# list_tour = get_detail_tour_for_page(real_items)
list_tour = []
for page in link_page:
    main_page = soup_for_link(link)
    list_item = main_page.find(
        'div', {'class': 'category-box-list-default-inner'}).find('ul').find_all("li")
    real_items = []
    for item in list_item:
        if len(item.find_all('div')) != 0:
            real_items.append(item)
    rs = get_detail_tour_for_page(real_items)
    list_tour.extend(rs)

with open('tour_data.txt', 'w') as f:
    json.dump(list_tour, f)
