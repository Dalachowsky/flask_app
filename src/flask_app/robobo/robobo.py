
from typing import Tuple, List
from math import *
import matplotlib.pyplot as plt
from numpy import sign

from latex2mathml.converter import convert as mathml

class robobo_arc:

    def __init__(self, \
        R: float,
        delta: float,
        a = None,
        A: float = 0.01,
        I: float = 0.1,
        centerPoint = (0,0),
        startPoint = None,
        lineAlpha = None):

        self.R = R
        self.delta = delta
        self.A = A
        self.I = I
        self.centerPoint = centerPoint
        self.lineAlpha = lineAlpha
        if startPoint is not None:
            self.startPoint = startPoint
        else:
            self.startPoint = (self.centerPoint[0] + self.R, self.centerPoint[1])

        self.beta = acos(R / (R+A))
        self.alpha_suspected = 0
        if a is None:
            self.alpha_suspected = acos((R-I)/(R+A))
            self._a = (abs(delta) - 2*self.beta)/(2*self.alpha_suspected)
            self.a = ceil(self._a) if not (self._a).is_integer() else self._a
        else:
            self.a = a
        self.alpha = (abs(delta) - 2*abs(self.beta))/(2*self.a)

    def getPoints(self) -> List[Tuple[float, float]]:
        points = [self.getPoint(n) for n in range(0,self.a+3)]
        return points

    def getPoint(self, n: int) -> Tuple[float, float]:
        if n == 0:
            return self.startPoint

        if self.lineAlpha is None:
            if n == self.a + 2:
                return ((self.R)*cos(self.getGamma(n)), (self.R)*sin(self.getGamma(n)))
            else:
                return ((self.R + self.A)*cos(self.getGamma(n)), (self.R + self.A)*sin(self.getGamma(n)))
        else:
            if n == self.a + 2:
                return (
                    (self.R)*cos(self.getGamma(n) - pi + self.lineAlpha) + self.centerPoint[0], 
                    (self.R)*sin(self.getGamma(n) - pi + self.lineAlpha) + self.centerPoint[1]
                    )
            else:
                return (
                    (self.R + self.A)*cos(self.getGamma(n) - pi + self.lineAlpha) + self.centerPoint[0], 
                    (self.R + self.A)*sin(self.getGamma(n) - pi + self.lineAlpha) + self.centerPoint[1]
                    )

    def getGamma(self, n: int):
        if n == 0:
            return 0
        if n == self.a+2:
            return self.delta
        return sign(self.delta) * (self.beta + (n-1)*2*self.alpha)

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
        res += mathml(f"PK = (Rcos(\\delta), Rsin(\\delta))") + '<br>'
        res += '<table border="1px solid black">\n'
        res += "<tr><td>l.p</td><td>&gamma;=</td><td>&gamma; [&deg;]</td><td>P =</td><td>P</td></tr>\n"
        for n, point in enumerate(self.getPoints()):
            if n == 0:
                lp = "PS"
                gamma_eq = "0"
                p_eq = "(R,0)"
            elif n == self.a + 2:
                lp = "PK"
                gamma_eq = f"&delta; = {round(degrees(self.delta))}"
                p_eq = mathml(f"(Rcos(\\delta),Rsin(\\delta))")
            else:
                lp = n - 1
                gamma_eq = mathml(f"\\beta + {n}\\gamma = {round(degrees(self.beta), 2)} + {round(degrees(2*self.getGamma(n)), 2)}")
                p_eq = mathml(f"(Rcos(\\gamma_{{{n-1}}}), Rsin(\\gamma_{{{n-1}}}))")
            res += "<tr>\n"
            res += f"<td>{lp}</td>\n"
            res += f"<td>{gamma_eq}</td>"
            res += f"<td>{round(degrees(self.getGamma(n)), 2)}</td>"
            res += f"<td>{p_eq}</td>"
            res += f"<td>({', '.join([str(round(i, 2)) for i in point])})</td>"
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
        self.a = a

        self.mathMLString = ""

    def generatePlot(self):

        fig = plt.figure()
        ax = fig.add_subplot(111)

        points = []
        points.append(self.P)
        points.append( 
            (self.P[0] + self.L*cos(self.alpha), 
            (self.P[1] + self.L*sin(self.alpha)))
            )

        # Find arc center point
        arcCenterPoint = (
            points[-1][0] + (self.R * cos(self.alpha)),
            points[-1][1] + (self.R * sin(self.alpha))
        )
        ax.plot(arcCenterPoint[0], arcCenterPoint[1], '+r')
        ax.text(
            arcCenterPoint[0], 
            arcCenterPoint[1], 
            f"({round(arcCenterPoint[0])}, {round(arcCenterPoint[1])})")

        arc = robobo_arc(self.R, self.delta, centerPoint=arcCenterPoint, startPoint=points[-1], lineAlpha=self.alpha)

        points += arc.getPoints()

        ax.plot(*zip(*points))
        ax.plot(*zip(*points), '+r')

        ax.axvline(0)
        ax.axhline(0)


        plt.axis('Scaled')
        ax.grid(True, which='both')
        fig.set_facecolor('aliceblue')
        ax.set_facecolor('aliceblue')

        return fig

if __name__ == "__main__":
    solver = robobo_solver((0,0), 45, 100, 100, 90) 
    solver.generatePlot().show()
    plt.show()