
from typing import Tuple, List
from math import *
import matplotlib.pyplot as plt

from latex2mathml.converter import convert as mathml

class robobo_arc:

    def __init__(self, \
        R: float,
        delta: float,
        a = None,
        A: float = 0.01,
        I: float = 0.1):

        self.R = R
        self.delta = delta
        self.A = A
        self.I = I

        self.beta = acos(R / (R+A))
        print(f"a = {a}")
        if a is None:
            self.alpha_suspected = acos((R-I)/(R+A))
            self._a = (delta - 2*self.beta)/(2*self.alpha_suspected)
            self.a = ceil(self._a) if not (self._a).is_integer() else self._a
        else:
            self.a = a
        self.alpha = (delta - 2*self.beta)/(2*self.a)

    def getPoints(self) -> List[Tuple[float, float]]:
        points = [self.getPoint(n) for n in range(0,self.a+1)]
        points.insert(0, (self.R, 0.0))
        points.append((cos(self.delta)*self.R, sin(self.delta)*self.R))
        return points

    def getPoint(self, n: int) -> Tuple[float, float]:
        return ((self.R + self.A)*cos(self.getGamma(n)), (self.R + self.A)*sin(self.getGamma(n)))

    def getGamma(self, n: int):
        if n == self.a+1:
            return self.delta
        return self.beta + n*2*self.alpha

    def getMathML(self):
        res = ""
        #res += "1.Kąt pierwszego i ostatniego odcinka<br>\n"
        res += mathml(f"\\beta = arccos(\\frac{{R}}{{R+A}}) = {round(degrees(self.beta), 2)}^{{\\circ}}") + "<br>"
        try:
            res += mathml(f"\\alpha = arccos(\\frac{{R-I}}{{R+A}}) = {round(degrees(self.alpha_suspected), 2)}^{{\\circ}}") + "<br>"
            res += mathml(f"a_{{th}} = \\frac{{\\delta-2\\beta}}{{2\\alpha}} = {round(self._a, 2)}") + "<br>"
        except AttributeError:
            pass
        res += mathml(f"a = {self.a}") + "<br>"
        res += mathml(f"\\alpha_{{rz}} = \\frac{{\\delta - 2\\beta}}{{2a}} = {round(degrees(self.alpha), 2)}^{{\\circ}}") + "<br>"
        res += '<table border="1px solid black">\n'
        res += "<tr><td>l.p</td><td>&gamma; [&deg;]</td><td>P</td></tr>\n"
        for n in range(0,self.a+2):
            res += "<tr>\n"
            res += f"<td>{n}</td>\n"
            res += f"<td>{round(degrees(self.getGamma(n)), 2)}</td>"
            res += f"<td>({', '.join([str(round(i, 2)) for i in self.getPoint(n)])})</td>"
            res += "</tr>\n"
        res += "</table>"

        return res

    def getPlot(self):
        fig = plt.figure()
        ax = fig.add_subplot(111)

        points = self.getPoints()
        x, y = zip(*points)
        ax.plot(x, y, "b")
        ax.plot(x, y, "+")
        ax.plot()

        #ax.set_xlim(-10, 80)
        #ax.set_ylim(-10, 80)
        ax.axhline(0, color='black', linewidth=.5)
        ax.axvline(0, color='black', linewidth=.5)
        ax.grid(True)

        fig.set_facecolor(color='aliceblue')
        ax.set_facecolor(color='aliceblue')

        return fig

class robobo_solver:

    def __init__(self, \
        P: Tuple[float, float],
        alpha: float,
        L: float,
        R: float,
        delta: float,
        a = None,
        A: float = 0.01,
        I: float = 0.1):

        self.P = P
        self.alpha = radians(alpha)
        self.L = L
        self.R = R
        self.delta = radians(delta)
        self.A = A
        self.I = I

        if a is not None:
            self.arc = robobo_arc(self.R, self.delta, a=a)
        else:
            self.arc = robobo_arc(self.R, self.delta)

        self.mathMLString = ""

    def generateArcPlot(self):
        return self.arc.getPlot()

if __name__ == "__main__":
    solver = robobo_solver((0,0), 30, 100, 100, 100) 
    print(solver.arc.getMathML())