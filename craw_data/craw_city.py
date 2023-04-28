import requests
from bs4 import BeautifulSoup


link = 'https://thanhthinhbui.com/zipcode/'


def soup_for_link(link):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36"}

    draw_r1 = requests.get(link, headers=headers)
    coverpage_drawn = draw_r1.content
    soap_drawn = BeautifulSoup(coverpage_drawn, 'html5lib')
    return soap_drawn


def table_data_text(table):
    def rowgetDataText(tr, coltag='td'):  # td (data) or th (header)
        return [td.get_text(strip=True) for td in tr.find_all(coltag)]
    rows = []
    trs = table.find_all('tr')
    trs = trs[1:]

    for tr in trs:  # for every table row
        rows.append(rowgetDataText(tr, 'td'))  # data row
    return rows


def get_data_for_city():
    main_page = soup_for_link(link)
    table = main_page.find('table')
    row = table_data_text(table)
    return row





