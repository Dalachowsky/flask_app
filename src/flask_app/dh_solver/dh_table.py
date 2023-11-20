
import csv
from numpy import deg2rad

class dh_entry:

    def __init__(self, a: float = 0, d: float = 0, alpha: float = 0, theta: float = 0):
        self.variables = {}
        try:
            self.a = float(a)
        except ValueError:
            self.a = 0
            self.variables['a'] = str(a)
        try:
            self.d = float(d)
        except ValueError:
            self.d = 0
            self.variables['d'] = str(d)
        try:
            self.alpha = deg2rad(float(alpha))
        except ValueError:
            self.alpha = 0
            self.variables['alpha'] = str(alpha)
        try:
            self.theta = deg2rad(float(theta))
        except ValueError:
            self.theta = 0
            self.variables['theta'] = str(theta)

class dh_table:

    def __init__(self, path: str = None, data: str = None):
        
        self._entries = []

        if path != None and data != None:
            raise AttributeError("Cannot specify data and path at the same time")
        if path != None:
            print("Reading file")
            data = open(path, 'r')
        else:
            print(f"Data: {data}")

        reader = csv.DictReader(data.splitlines())  
        for i, row in enumerate(reader):
            print(row)
            try:
                self._entries.append(dh_entry(**row))
            except TypeError as e:
                print("Format error")
                raise(e)

        if path != None:
            data.close()

    def __getitem__(self, i: int) -> dh_entry:
        return self._entries[i]

