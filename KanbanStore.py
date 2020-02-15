#!/usr/bin/env python3

import csv


class KanbanEntry:

    fieldnames = ['status', 'tag', 'description', 'history', 'date']

    def __init__(self, values, index):
        self.values = values
        self.index = index
        self.values['id'] = index

    def __getitem__(self, key):
        return self.values[key]



class KanbanStore:

    def __init__(self, csv_path):
        self.csv_path = csv_path

    def entries(self):
        with open(self.csv_path,"r") as f:
            r = csv.DictReader(f)
            i = 1
            for e in r:
                yield KanbanEntry(e, i)
                i += 1

    def read(self):
        pass

    def write(self):
        pass




