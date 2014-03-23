# -*- coding: utf-8 -*-
import textwrap
import yaml

from core.tests import TestCase
from .. import data


class RouteTrainsTestCase(TestCase):

    def setUp(self):
        self.raw_data = yaml.safe_load(
          textwrap.dedent('''
            ---
              data: null
              value: 
                - 
                  category: 0
                  from: 
                    date: 1395610740
                    station: "Київ-Пасажирський"
                    src_date: "2014-03-23 23:39:00"
                    station_id: "2200001"
                  till: 
                    date: 1395626940
                    station: "Кам`янець-Подільський"
                    src_date: "2014-03-24 04:09:00"
                    station_id: "2200300"
                  num: "173П"
                  model: 0
                  types: 
                    - 
                      places: 1
                      letter: "С1"
                      title: "Сидячий першого класу"
                    - 
                      places: 246
                      letter: "С2"
                      title: "Сидячий другого класу"
                - 
                  category: 0
                  from: 
                    date: 1395611100
                    station: "Київ-Пасажирський"
                    src_date: "2014-03-23 23:45:00"
                    station_id: "2200001"
                  till: 
                    date: 1395629880
                    station: "Хмельницький"
                    src_date: "2014-03-24 04:58:00"
                    station_id: "2200300"
                  num: "187К"
                  model: 0
                  types: 
                    - 
                      places: 19
                      letter: "С1"
                      title: "Сидячий першого класу"
                    - 
                      places: 426
                      letter: "С2"
                      title: "Сидячий другого класу"
              error: false''')
        )
        self.data = data.RouteTrains(self.raw_data)

    def test_valid(self):
        self.assertEqual(len(self.data), 2)
        self.assertEqual(self.data.seats_count, 692)
        self.assertEqual(self.data[0].seats_count, 247)
        self.assertEqual(self.data[0].station_from.date.day, 23)
        self.assertEqual(len(self.data[0]), 2)
        self.assertEqual(self.data[0][0].name, u'С1')
        self.assertEqual(self.data[0][0].seats_count, 1)
        self.assertEqual(self.data[0][1].seats_count, 246)
