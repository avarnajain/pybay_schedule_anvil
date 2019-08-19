import anvil.server
anvil.server.connect("A3G66GH2YYGOJCGH4Y7PN2AM-PSGS3J3JYESQHKKS")

import anvil.server
from bs4 import BeautifulSoup
import requests
import re
import time
import pprint
from requests import ConnectionError
from anvil.tables import app_tables
from datetime import datetime

@anvil.server.callable
def get_article_body(url):
    """Call all functions needed to extract p tag text from article urls
    returns a dictionary with the following format:
    {
        "day": {
            "date": date,
            time: [
                {
                    "title": title,
                    "speaker": speaker,
                    "room": room,
                    "duration": duration,
                    "description": descri            
                }
            ]
        }
    }
    """
    bs = fetch_article(url)
    if (bs):
        full_html_str = find_events(bs)
    else:
        return []
    return full_html_str

@anvil.server.callable
def fetch_article(url):
    """given the url, fetch the news article and parse html"""
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")
    except ConnectionError:
        soup = None
    return soup

@anvil.server.callable
def find_events(soup):
    """find all p elements and join together into one string"""
    text_list = []
    counter = 0
    event_dict = {}
    for tag in soup.find_all("div", {"class": "sch-day"}):
        day = find_text(str(tag.find("h2", {"class": "sch-day-title"})))
        date = datetime.strptime(day, "%b. %d, %Y").date()
        timeslots = tag.find_all("div", {"class": "sch-timeslots", "class": "sch-timeslot"})
        event_dict[day] = {"date": date}
        for timeslot in timeslots:
            time = find_text(str(timeslot.find("h3")))
            t = format_time(time)
            t = datetime.strptime(t, "%H:%M")
            event_dict[day][time] = []
            slots = timeslot.find_all("div", {"class": "sch-timeslot-slot"})
            for slot in slots:
                title = format_tag(str(slot.find("h4")))
                speaker = find_text(str(slot.find("p", {"class": "sch-speaker"})))
                room = find_text(str(slot.find("p", {"class": "sch-room"})))
                duration = find_text(str(slot.find("p", {"class": "sch-duration"})))
                description = format_tag(str(slot.find("div", {"class": "sch-description"})))
                event_dict[day][time].append({
                                        'time': t,
                                        'title': title,
                                        'speaker': speaker,
                                        'room': room,
                                        'duration': duration,
                                        'description': description
                                        })
        special_slots = tag.find_all("div", {"class": "sch-timeslot-special"})
        for timeslot in special_slots:
            time = find_text(str(timeslot.find("h3")))
            t = format_time(time)
            t = datetime.strptime(t, "%H:%M")
            if time not in event_dict[day].keys():
                event_dict[day][time] = []
            d = timeslot.find("div", {"class": "sch-timeslot-custom"})
            title = format_tag(str(d.find("p")))
            if title:
                event_dict[day][time].append({
                                        'time': t,
                                        'title': title,
                                        'speaker': "",
                                        'room': "",
                                        'duration': "",
                                        'description': ""
                                    })
               
    # for key in event_dict.keys():
    #     for k in event_dict[key].keys():
    #         if k != "date":
    #             sort_by_time(event_dict[key][k][0])
    # for key in event_dict.keys():
    #     for k in event_dict[key].keys():
    #         if k != "date":
    #             for l in event_dict[key][k][0].keys():
    #                 if l == "time":
    #                     print(event_dict[key][k][0][l].time())
    return event_dict

@anvil.server.callable
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
    return formatted_str

@anvil.server.callable
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

# @anvil.server.callable
# def sort_by_time(event):
#     datetime = event['time']
#     time = datetime.time()
#     return time

@anvil.server.callable
def format_time(t):
    l = t.split(" ")
    hl = l[0].split(":")
    hour = int(hl[0])
    minute = "0"
    if len(hl)==2:
        minute = hl[1]
    if l[1] == "a.m.":
        if hour < 10 and len(minute)<2:
            time = "0{}:0{}".format(hour, minute)
        elif hour < 10:
            time = "0{}:{}".format(hour, minute)
        else:
            time = "{}:{}".format(hour, minute)
    else:
        if hour == 12:
            time = "{}:{}".format(hour, minute)
        else:
            time = "{}:{}".format(hour+12, minute)
    return time

# if __name__ == "__main__":
#     print(get_article_body('https://pybay.com/schedule/'))
anvil.server.wait_forever()
