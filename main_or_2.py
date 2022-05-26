import requests
from bs4 import BeautifulSoup
import os.path
import time
from random import randrange
import csv
import random
from datetime import datetime


def get_articles(url):
    user, prox = agent_or_prox_random()
    s = requests.Session()
    req = s.get(url=url, headers=user, proxies=prox)
    src = req.text
    print("Искусственная задержка чтобы не забанили")
    time.sleep(randrange(5, 8))

    if not os.path.exists("data"):
        os.mkdir("data")
    soup = BeautifulSoup(src, 'lxml')
    # возьмем номер последней страницы из пагиниции
    try:
        # print("2")
        pagination_count = int(soup.find('ul', class_='pg').find_all('a')[-1].text)
        print(pagination_count, "*************")
    except:
        pagination_count = 2
        # print("3")


    # изменим ссылку для переходов по пагинациям
    url2 = url + "Y2l0eT18cmVnaW9uPXxjb3VudHJ5PXxtZXRrYT18c29ydD0x/"

    # пройдемся по всем страницам
    airticles_urls_list = []
    for page in range(1, pagination_count + 1):
        # print("4")
        # ограничим сбор ссылок для безопасности
        if page > 20:
            print("Угроза блокировки, нельзя парсить больше. Сохраняю данные")
            break
        user, prox = agent_or_prox_random()
        s = requests.Session()
        response = s.get(url = url2 + str(page) + '/', headers=user, proxies=prox)
        print("Искусственная задержка чтобы не забанили")
        time.sleep(random.randint(4, 7))
        soup = BeautifulSoup(response.text, 'lxml')
        #сохраним страницы сайта
        with open(f"data/glav_index{page}.html", "w", encoding='utf-8') as file:
            file.write(response.text)

        return pagination_count + 1

def collect_data(pages_count):
    cur_date = datetime.now().strftime("%d_%m_%Y")
    # пишем заголовки
    with open(f"file_{cur_date}.csv", "w", encoding="cp1251", newline="") as file:
        writer = csv.writer(file, delimiter=';')

        writer.writerow(
            (
            "Название товара",
            "Цена",
            "Описание",
            "Мини изображение",
            "Контактное лицо",
            "Адрес",
            "Телефон",
            "Ссылка на товар",
            "Email",
            "Информация о компании"
            )
        )

    for page in range(1, pages_count):
        # открываем сохраненные страницы
        with open(f"data/glav_index{page}.html", encoding='utf-8') as file:
            src = file.read()

        soup = BeautifulSoup(src, "lxml")

        # тег на каждый товар
        items_cards = soup.find_all("div", class_='line')
        # соберем информацию
        data = []
        for item in items_cards:
            article_title = item.find('div', class_='wrapper').find('div', class_='tovar').find('a').text.strip()
            article_title = encod_work(article_title)
            print(article_title)
            # print(item)
            try:
                article_price = item.find('div', class_='price').text.strip()
                article_price = encod_work(article_price)
                print(article_price)
            except:
                article_price = "Цена не указана"
                print(article_price)
            article_opis = item.find('div', class_='text').text.replace("\n", "").strip()
            article_opis = encod_work(article_opis)
            print(article_opis)
            try:
                article_img = item.find('div', class_='photo').find('img').get('src').strip()
                article_img = encod_work(article_img)
                start = article_img.startswith("h")
                if not start:
                    article_img = "https://agroserver.ru" + article_img
            except:
                article_img = 'Фото нет'
            print(article_img)

            article_contact_lic = item.find('div', class_='wrapper').find('div', class_='blwr org_block').find('a', class_='personal_org_menu ajs').text.strip()
            article_contact_lic = encod_work(article_contact_lic)
            print(article_contact_lic)

            article_location = item.find('div', class_='bl geo').text.strip()
            article_location = encod_work(article_location)
            print(article_location)

            try:
                article_phone = item.find('div', class_='bl phone phone2').text.strip().replace(" ", "")
                article_phone = encod_work(article_phone)
            except:
                article_phone = "Телефон не указан"
            print(article_phone)

            # ссылка на товар
            art_urls = "https://agroserver.ru" + item.find('div', class_='wrapper').find('div', class_='th').find('a').get('href').strip()
            art_urls = encod_work(art_urls)
            print(art_urls)

            try:
                article_email = item.find('div', class_='bl ico_mail').find('a').get('href')
                article_email = 'https://agroserver.ru' + article_email
                article_email = encod_work(article_email)
                print("email", article_email)
            except:
                article_email = 'Продавец не указал email'
                print(article_email)

            try:
                inform_company = item.find('div', class_='wr').find_all('div')[1].find('a').get('href').strip()
                inform_company = 'https://agroserver.ru' + inform_company
                inform_company = encod_work(inform_company)
                print(inform_company)
            except:
                inform_company = "Продавец не указал данные"
                print(inform_company)

            data.append(
                {
                    "article_title": article_title,
                    "article_price": article_price,
                    "article_opis": article_opis,
                    "article_img": article_img,
                    "article_contact_lic": article_contact_lic,
                    "article_location": article_location,
                    "article_phone": article_phone,
                    "art_urls": art_urls,
                    "article_email": article_email,
                    "inform_company": inform_company
                }
            )
            try:
                with open(f"file_{cur_date}.csv", "a", encoding="cp1251", newline="") as file:
                    writer = csv.writer(file, delimiter=';')

                    writer.writerow(
                        (
                            article_title,
                            article_price,
                            article_opis,
                            article_img,
                            article_contact_lic,
                            article_location,
                            article_phone,
                            art_urls,
                            article_email,
                            inform_company
                        )
                    )
            except:
                continue

        print(f"[INFO] Обработана страница {page}/{pages_count}")


def agent_or_prox_random():
    # меняем прокси и юзер агент
    proxies1 = {"https": "http://46.3.182.240:8000"}
    proxies2 = {"https": "http://45.10.249.8:8000"}
    proxies3 = {"https": "http://45.10.251.116:8000"}
    proxies5 = {"https": "http://45.10.248.187:8000"}
    proxies6 = {"https": "http://46.3.182.109:8000"}

    user_agent1 = {"accept": "*/*", "accept-encoding": "gzip, deflate, br", "accept-language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7", "content-type": "application/x-www-form-urlencoded", "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.80 Safari/537.36"}
    user_agent2 = {"accept": "*/*", "accept-encoding": "gzip, deflate, br", "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.80 Safari/537.36"}
    user_agent3 = {"accept": "*/*", "accept-language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7", "User-Agent": "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.80 Safari/537.36"}
    user_agent5 = {"accept": "*/*", "accept-encoding": "gzip, deflate, br", "accept-language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7", "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:96.0) Gecko/20100101 Firefox/96.0"}
    user_agent6 = {"accept": "*/*", "accept-encoding": "gzip, deflate, br", "accept-language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7", "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:91.0) Gecko/20100101 Firefox/91.0"}


    proxies = [[proxies1, user_agent1], [proxies2, user_agent2], [proxies3, user_agent3], [proxies5, user_agent5], [proxies6, user_agent6]]

    proxii = random.choice(proxies)

    user = proxii[1]
    prox = proxii[0]

    return user, prox

def encod_work(encod):
    # исправляем ошибки в кодировке
    rep = ["\u20bd", "\xb3", "\xb2", "\xd8", "\u2011", "\xe9", "\xed", "\u25ba", "\u2103", "\uff08", "\uff09", "\u2714", "\u0130", "\u0131", "\xdc", "\xfc", "\u015f"]
    for item in rep:
        if item in encod:
            encod = encod.replace(item, "")
    return encod

def main():
    url = input("Вставь ссылку: ")
    collect_data(pages_count=get_articles(url))

if __name__ == '__main__':
    main()