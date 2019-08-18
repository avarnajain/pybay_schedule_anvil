from bs4 import BeautifulSoup, NavigableString
import requests
import re
import time
import pprint
from requests import ConnectionError

def get_article_body(url):
    """Call all functions needed to extract p tag text from article urls"""
    bs = fetch_article(url)
    if (bs):
        full_html_str = find_events(bs)
    else:
        return []
    return full_html_str

def fetch_article(url):
    """given the url, fetch the news article and parse html"""
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")
    except ConnectionError:
        soup = None
    return soup

def find_events(soup):
    """find all p elements and join together into one string"""
    text_list = []
    counter = 0
    event_dict = {}
    for tag in soup.find_all("div", {"class": "sch-day"}):
        day = find_text(str(tag.find("h2", {"class": "sch-day-title"})))
        timeslots = tag.find_all("div", {"class": "sch-timeslots", "class": "sch-timeslot"})
        event_dict[day] = {}
        for timeslot in timeslots:
            time = find_text(str(timeslot.find("h3")))
            event_dict[day][time] = []
            slots = timeslot.find_all("div", {"class": "sch-timeslot-slot"})
            for slot in slots:
                title = format_tag(str(slot.find("h4")))
                speaker = find_text(str(slot.find("p", {"class": "sch-speaker"})))
                room = find_text(str(slot.find("p", {"class": "sch-room"})))
                duration = find_text(str(slot.find("p", {"class": "sch-duration"})))
                description = format_tag(str(slot.find("div", {"class": "sch-description"})))
                event_dict[day][time].append({
                                        'title': title,
                                        'speaker': speaker,
                                        'room': room,
                                        'duration': duration,
                                        'description': description
                                        })
               
    for key in event_dict.keys():
        for k in event_dict[key].keys():
            for item in event_dict[key][k]:
                print(key)
                print(k)
                print(item['title'])
                print(item['speaker'])
                print(item['room'])
                print(item['duration'])
                print(item['description'])
                print('_______')


def format_tag(html_string):
    """format p element strings from beautiful soup"""
    text_str = ''
    counter = -1
    for character in html_string:
        counter+=1
        if character == '>':
            text = find_text(html_string, counter)
            text_str+=text
    formatted_str = re.sub(' +', ' ', text_str).replace('\n', '')
    formatted_str.replace('&amp;apos', "'")
    # print('_____', formatted_str, '\n')
    return formatted_str

def find_text(html_string, start_from=0):
    """find and extract text strings within html tags"""
    try:
        start_index = html_string.index('>', start_from) + 1
        stop_index = html_string.index('<', start_index)
        result = html_string[start_index:stop_index]
        if "\t" in result or '@media' in result:
            return ""
        return result
    except ValueError:
        return ""

if __name__ == "__main__":
    get_article_body('https://pybay.com/schedule/')
