import requests
from bs4 import BeautifulSoup
import csv
import os


URL = input('Введите URL: ').strip()
HEADERS = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/90.0.4430.212 Safari/537.36', 'accept': '*/*'}
FILE = 'KTY_products.csv'


# ----------- Блок получения HTML кода -----------
def get_html(url, params=None):
    r = requests.get(url, headers=HEADERS, params=params)
    return r


# ----------- Блок получения кол-ва страниц -----------
def get_pages_count(html):
    pages = []
    soup = BeautifulSoup(html.text, 'html.parser')
    try:
        paginations = soup.find('ul', class_='text-center').find_all('a')
        for pagination in paginations:
            if pagination.get_text(strip=True) != '':
                pages.append(pagination.get_text(strip=True))
        return int(pages[-1])
    except AttributeError:
        return 1


# ----------- Блок получения контента -----------
def get_content(html):
    product = []
    soup = BeautifulSoup(html.text, 'html.parser')
    items = soup.find_all('article', class_='product-miniature')
    for item in items:
        prices = item.find('span', class_='product-price').get_text()
        cost = ''
        for i in prices:
            if i.isdigit():
                cost += i
        link = item.find('div', class_='h3 product-title').find('a').get('href')
        product.append({
            'category': item.find('div', class_='product-category-name').get_text(strip=True),
            'brand': item.find('div', class_='product-brand').get_text(strip=True),
            'title': item.find('div', class_='h3 product-title').get_text(strip=True),
            'price': cost,
            'link': link,
            'photo': safe_photo(link),
                        })
    return product


# ----------- Блок получения фото -----------
def safe_photo(link):
    photo = ''
    html = get_html(link)
    soup = BeautifulSoup(html.text, 'html.parser')
    items = soup.find_all('a', class_='js-easyzoom-trigger')
    for item in items:
        if photo != '':
            photo += ',' + item.get('href')
        else:
            photo += item.get('href')
        photo = photo.strip()
    return photo


# ----------- Блок сохранения файла -----------
def safe_file(items, path):
    with open(path, 'w', newline='') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(['Категория', 'Бренд', 'Название', 'Стоимость', 'Ссылка на товар', 'Ссылка на фото'])
        for item in items:
            writer.writerow([item['category'], item['brand'], item['title'],
                             item['price'], item['link'], item['photo']])


# ----------- Основной блок обработки -----------
def parse():
    product = []
    html = get_html(URL)
    if html.status_code == 200:
        pages_count = get_pages_count(html)
        for page in range(1, pages_count + 1):
            print(f'Парсинг страницы {page} из {pages_count}')
            html = get_html(URL, params={'page': page})
            product.extend(get_content(html))

        safe_file(product, FILE)
        print(f'Парсинг успешно завершен. Общее кол-во позиций: {len(product)}.')
        os.startfile(FILE)
    else:
        print('Ошибка...')


parse()
