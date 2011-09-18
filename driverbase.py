import pickle
import csv

class DriverBase(object):

    def __init__(self, filename=None):
        self.filename = filename
        try:
            f = open(self.filename, 'rb')
            self.driver_dict = pickle.load(f)
            f.close()
        except IOError:
            self.driver_dict = {}
    
    def get_driver(self, tabnum):
        return self.driver_dict.get(tabnum, None)

    def add_driver(self, tabnum, name): 
        self.driver_dict[tabnum] = name

    def load_drivers(self, filename):
        f = open(filename)
        r = csv.reader(f, delimiter=';')
        for row in r:
            self.driver_dict[row[0]] = row[1]

    def save(self):
        f = open(self.filename, 'wb')
        pickle.dump(self.driver_dict, f)
        f.close()
