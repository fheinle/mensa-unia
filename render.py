#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
""" mensa planer """

import yaml
from string import Template
import os

DATA = yaml.load(open('current.yaml', 'r'))

WEEKDAYS = ['Montag', 'Dienstag', 'Mittwoch', 'Donnerstag', 'Freitag']

ADDITIVES = {
    1:'mit Farbstoff', 2:'mit Geschmacksverstärker', 3:'mit Konservierungsstoff',
    4:'mit Antioxidationsmittel', 5:'geschwefelt', 6:'geschwärzt', 7:'gewachst',
    8:'mit Phosphat', 9:'mit Süßungsmittel', 10:'enthält eine Phenylalaninquelle',
    11:'kann bei übermäßigem Verkehr abführend wirken', 12:'Schweinefleisch',
    13:'aus kontrolliert biologischem Anbau', 14:'mit Alkohol', 15:'Rindfleisch',
    16:'gentechnisch verändert',
}
def render_day(weekday):
    day_template = Template(open('templates/day.html', 'r').read())
    dish_template = Template(open('templates/dish.html', 'r').read())
    detail_template = Template(open('templates/detail.html', 'r').read())
    base_template = Template(open('templates/base.html', 'r').read())
    dishes = []
    dish_id = 0
    for dish in DATA[weekday]:
        dish_id += 1
        dishes.append(dish_template.substitute(
                        weekday=weekday, id=dish_id,
                        name=dish['name'], price=dish['price_student']
                     )
        )
        additives = []
        for additive in dish['additives']:
            additives.append('<li>%s</li>' % ADDITIVES[additive])
        detail_file = open('output/days/%s-%s.html' % (weekday, dish_id), 'w')
        detail_file.write(
            base_template.substitute(
                title="Details",
                content=detail_template.substitute(additives="\n".join(additives),
                    name=dish['name'], price_student=dish['price_student'],
                                       price_employee=dish['price_emloyee'])
        ))
        detail_file.close()
    return day_template.substitute(weekday=weekday, day="\n".join(dishes))

def render():
    base_template = Template(open('templates/base.html', 'r').read())
    week = []
    for weekday in WEEKDAYS:
        week.append(render_day(weekday))
    return base_template.substitute(title="Mensa Uni", content="\n".join(week))

if __name__ == '__main__':
    if not os.path.isdir('output'):
        os.makedirs('output/days')
    output = open('output/mensa.html', 'w')
    output.write(render())
