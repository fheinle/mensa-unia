#!/usr/bin/env python
# -*- coding:utf-8 -*-

""" parse Augsburg's mensa schedule 

yes this is ugly. Just look at the following imports."""

from datetime import datetime
import subprocess
import re

WEEKDAYS = ['Montag', 'Dienstag', 'Mittwoch', 'Donnerstag', 'Freitag']

UNI_CURRENT_WEEK = 'http://web.studentenwerk-augsburg.de/verpflegung/_uni-aktuelle-woche.php'
UNI_NEXT_WEEK = 'http://web.studentenwerk-augsburg.de/verpflegung/_uni-naechste-woche.php'

SPEISE_RE = re.compile(
    '(?:\s|\*)* (?P<gericht>.*) (?P<Preis>\d,\d\d \/ \d,\d\d)'
)
ADDITIVES_RE = re.compile('(\d+)')
ADDITIVES_CLEAN_RE = re.compile('\(\d+\s?(,\s?\d+)*?\)\s*')
DATE_RE = re.compile('\d{2}.+\d{2}.+\d{4}')

def replace_umlauts(name):
    umlauts = {'ä':'&auml;', 'Ä':'&Auml;',
               'ö':'&ouml;', 'Ö':'&Ouml;',
               'ü':'&uuml;', 'Ü':'&Uuml;',
               'ß':'&szlig'
              }
    for umlaut, representation in umlauts.iteritems():
        name = name.replace(umlaut, representation)
    return name

def _fetch_mensa_schedule(url):
    '''fetch mensa schedule from their website

    yes, we're calling w3m in dump mode instead of parsing HTML
    but they keep changing their unparsable HTML code anyway.'''
    website_dump = subprocess.Popen(
        ['w3m', '-dump', url],
        stdout=subprocess.PIPE)
    return website_dump.communicate()[0]

def _isolate_day(dump, day_of_week):
    '''isolate single days and their dishes from other days

    because the HTML structure isn't hierarchival unfortunately.'''
    if not day_of_week == 'Freitag':
        next_day = WEEKDAYS[WEEKDAYS.index(day_of_week) + 1]
    else:
        next_day = 'T&auml;glich'
    that_day = dump[dump.find(day_of_week):dump.find(next_day)]
    return that_day

def _get_dishes_for_day(day_menu):
    '''get a dictionary of dishes from a string that spans a day's menu'''
    dishes_that_day = SPEISE_RE.findall(day_menu)
    dishes = []
    dish_id = 0
    for dish, price in dishes_that_day:
        dish_id += 1
        additives = ADDITIVES_RE.findall(dish)
        date = DATE_RE.findall(day_menu)[0].replace('..', '.')
        if dish.strip().endswith('und'):
            lines = day_menu.splitlines()
            for line in lines:
                if line.strip().startswith(dish):
                    dish = "%s %s" % (
                        dish.strip(),
                        lines[lines.index(line) + 1].strip()
                    )
        dishes.append({
             'name':replace_umlauts(ADDITIVES_CLEAN_RE.sub('', dish).strip()),
             'price_student':price.split('/')[0].strip(),
             'price_emloyee':price.split('/')[1].strip(),
             'additives':[int(additive) for additive in additives],
             'date':datetime.strptime(date, '%d.%m.%Y'),
             'id':dish_id,
        })
    return dishes

def get_mensa_schedule(url):
    '''get a given week's mensa schedule. 

    takes different mensa urls (Uni, FH, different weeks, etc)'''
    dishes = {}
    website_dump = _fetch_mensa_schedule(url)
    for day_of_week in WEEKDAYS:
        that_day = _isolate_day(website_dump, day_of_week)
        dishes[day_of_week] = _get_dishes_for_day(that_day)
    return dishes

def main():
    '''prints this week's schedule in mensa/uni'''
    print "Speiseplan dieser Woche:"
    mensa_schedule = get_mensa_schedule(UNI_CURRENT_WEEK)
    for day_of_week in WEEKDAYS:
        print day_of_week
        print '---------'
        for dish in mensa_schedule[day_of_week]:
            print dish['date']
            print '''%(name)s
    Studenten: %(stud)s Angestellte: %(empl)s''' % {
        'name':dish['name'],
        'stud':dish['price_student'],
        'empl':dish['price_emloyee']

        }
        print

if __name__ == '__main__':
    import yaml
    current_file = open('current.yaml', 'w')
    current_file.write(yaml.dump(get_mensa_schedule(UNI_CURRENT_WEEK), Dumper=yaml.Dumper))
    next_file = open('next.yaml', 'w')
    next_file.write(yaml.dump(get_mensa_schedule(UNI_NEXT_WEEK), Dumper=yaml.Dumper))
    current_file.close()
    next_file.close()
