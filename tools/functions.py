from bs4 import BeautifulSoup
from youtube_search import YoutubeSearch
import youtube_dl
import requests
import datetime
import timestring
import calendar
import os


def current_time():
    time = datetime.datetime.today().strftime("%H:%M").split(':')
    hours = int(time[0])
    minutes = int(time[1])
    if(hours<12):
        answer = f"it's {hours}:{minutes} am"
    else:
        answer = f"it's {hours-12}:{minutes} pm"
    return answer


def day_of_the_week():
    my_date = datetime.date.today()
    answer = f"it's {calendar.day_name[my_date.weekday()]}"
    return answer


def current_date():
    date = datetime.date.today()
    month = date.month
    day = date.day
    year = date.year
    print(day)
    month = calendar.month_name[int(month)]
    if(day in range(1,4)):
        if(day == 1):
            day = 'first'
        elif(day == 2):
            day = 'second'
        elif(day == 3):
            day = 'third'
    else:
        day = f"{day}th"

    answer = f"it's the {day} of {month} {year}"

    return answer


def get_city_name(city: str):
    """
    Функция, которая получает айди города на сайте погоды ббс
    :param city: Название города
    :return: Айди города, Название города
    """
    URL = f"https://locator-service.api.bbci.co.uk/" \
          f"locations?api_key=AGbFAKx58hyjQScCXIYrxuEwJh2W2cmv" \
          f"&stack=aws" \
          f"&locale=en" \
          f"&filter=international" \
          f"&place-types=settlement%2Cairport%2Cdistrict" \
          f"&order=importance" \
          f"&s={city}" \
          f"&a=true" \
          f"&format=json"

    request = requests.get(URL)
    answer = request.json()

    count = answer['response']['results']['totalResults']

    if(count >0):
        city = answer['response']['results']['results'][0]
        print(city['name'])
        print(city)
        return city['id'], city['name']
    else:
        return None, None


def get_description_weather(city):
    """
    Функция которая определяет описание погоды в городе
    :param city: Название города
    :return: Описание погоды
    """
    id, name = get_city_name(city)
    if(id is None):
        print('Нет города')
        return False
    request = requests.get(f'https://www.bbc.com/weather/{id}')

    soup = BeautifulSoup(request.text, 'html.parser')

    temps = soup.find_all('span', {'class': 'wr-value--temperature'})
    current_temp = temps[0].span.text
    tomorrow_temp = temps[1].span.text

    decsription = soup.find('div', {'class':'wr-day__weather-type-description wr-js-day-content-weather-type-description wr-day__content__weather-type-description--opaque'}).text
    print(decsription)

    return decsription


def get_temperature(city):
    """
        Функция которая определяет температуру в городе
        :param city: Название города
        :return: Температуру в формате: сегодня в городе 228 градусов
        """
    id, name = get_city_name(city)
    if (id is None):
        print('Нет города')
        return False
    request = requests.get(f'https://www.bbc.com/weather/{id}')

    soup = BeautifulSoup(request.text, 'html.parser')

    temps = soup.find_all('span', {'class': 'wr-value--temperature'})
    current_temp = temps[0].span.text
    tomorrow_temp = temps[1].span.text


    date = soup.find_all('span', {'class': 'wr-date'})[0].text

    return f'{date} in {name} {current_temp}'

def get_news():
    """Функция возвращающая два списка: заголовки новостей и ссылки на них"""
    request = requests.get('https://www.bbc.com/news')

    soup = BeautifulSoup(request.text, 'html.parser')

    headers = soup.find_all('a', {'class': 'gs-c-promo-heading gs-o-faux-block-link__overlay-link gel-pica-bold nw-o-link-split__anchor'})

    response = []
    links = []

    for header in headers:
        response.append(header.text)
        if("https" in header['href']):
            links.append(f"{header['href']}")
        else:
            links.append(f"https://www.bbc.com/news{header['href']}")

    return response, links

def get_youtube_music(query: str, music_directory):
    results = YoutubeSearch(query, max_results=5).to_dict() # Первые 5 видосов по запросу

    first_song = results[0] # Первая песня (словарь там много ключей)
    print(first_song)

    directory = music_directory
    file_name = f"{len(os.listdir(directory))+1}"

    ydl_opts = { # Настройки для скачивания
        'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}],
        'outtmpl': music_directory + f'/{file_name}.%(ext)s',
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([f"https://www.youtube.com/watch?v={first_song['id']}"])


    file_name = f"{music_directory}/{file_name}.mp3"

    return file_name


def get_seconds_from_date(date: str):
    future = timestring.Date(date).date
    print(future)
    delta = future - datetime.datetime.now()
    return delta.days * 86400 + delta.seconds


def search_ebay(item: str):
    """
    Функция, которая ищет заголовки товара на ebay
    :param item: Товар
    :return: Список заголовков
    """
    URL = f"https://www.ebay.co.uk/sch/i.html?_nkw={item}"

    print(URL)
    request = requests.get(URL)
    soup = BeautifulSoup(request.text, 'html.parser')

    headers = soup.find_all('div', {
        'class': 's-item__info clearfix'})

    response = []
    links = []
    prices = []

    for header in headers:
        response.append(header.h3.text)
        links.append(header.a['href'])
        prices.append(header.find('span', {'class':'s-item__price'}).text)
    return response, links, prices


def get_description_ebay(url: str):
    request = requests.get(url)

    soup = BeautifulSoup(request.text, 'html.parser')

    table = soup.find('div', {'class': 'itemAttr'})

    labels = table.find_all('td', {'class': 'attrLabels'})[1:]
    texts = table.find_all('td', {'width': '50.0%'})[1:]

    print(labels[0].text)
    print(texts[0].text)
    response = ''
    for i in range(len(labels)):
        label = labels[i].text
        label = label.replace('\n', '')
        label = label.replace('\t', '')
        response += label
        text = texts[i].text
        text = text.replace('\n', '')
        text = text.replace('\t', '')
        response += text
        response += '.'
    response = response[1:]
    return response
