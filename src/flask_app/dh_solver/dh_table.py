
import csv
from numpy import deg2rad

class dh_entry:

    def __init__(self, a: float = 0, d: float = 0, alpha: float = 0, theta: float = 0):
        self.a = float(a)
        self.d = float(d)
        self.alpha = deg2rad(float(alpha))
        self.theta = deg2rad(float(theta))

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

