
from .dh_table import dh_table, dh_entry
import numpy as np
from math import cos, sin
import pylatex as pytx
import matplotlib.pyplot as plt
from scipy.spatial.transform import Rotation as R

def dh_get_rotation(dh_matrix: np.matrix):
    res = []
    for i in range(0,3):
        res.append(dh_matrix.A[i][:3])
    return np.matrix(res)

def print_coords(ax: plt.Axes, x, y, z, r: R = None, scale=10):
    if r is not None:
        x_v = r.apply([1*scale, 0, 0])
        y_v = r.apply([0, 1*scale, 0])
        z_v = r.apply([0, 0, 1*scale])
    else:
        x_v = [1*scale, 0, 0]
        y_v = [0, 1*scale, 0]
        z_v = [0, 0, 1*scale]

    ax.quiver(x, y, z, *x_v).set_color("r")
    ax.quiver(x, y, z, *y_v).set_color("g")
    ax.quiver(x, y, z, *z_v)

def mathmlMatrix(self, matrix: list):
    res = "[<mtable>"
    for row in matrix.A:
        res += "<mtr>"
        for c in row:
            if isinstance(c, str):
                res += f"<mtd>{c}</mtd>\n"
            else:
                res += f"<mtd>{round(c, 2)}</mtd>\n"
        res += "</mtr>"
    res += "</mtable>]"

class dh_transition:

    def __init__(self, idx: int, entry: dh_entry):
        self.dh_entry = entry
        self._idx = idx

        # Rotate theta
        self._rot_theta = np.matrix([ \
            [cos(entry.theta), -sin(entry.theta), 0, 0], \
            [sin(entry.theta), cos(entry.theta), 0, 0 ], \
            [0, 0, 1, 0], \
            [0, 0, 0, 1] \
            ])

        # Translate d
        self._trans_d = np.matrix([\
            [1, 0, 0, 0], \
            [0, 1, 0, 0], \
            [0, 0, 1, entry.d], \
            [0, 0, 0, 1] \
            ])

        # Translate a
        self._trans_a = np.matrix([\
            [1, 0, 0, entry.a], \
            [0, 1, 0, 0], \
            [0, 0, 1, 0], \
            [0, 0, 0, 1] \
            ])

        # Rotate alpha
        self._rot_alpha = np.matrix([\
            [1, 0, 0, 0], \
            [0, cos(entry.alpha), -sin(entry.alpha), 0],\
            [0, sin(entry.alpha), cos(entry.alpha), 0],\
            [0, 0, 0, 1] \
            ])

        self._matrix = self._rot_theta * self._trans_d * self._trans_a * self._rot_alpha

    @property
    def matrix(self):
        return self._matrix

    def latex(self, doc: pytx.Document):
        with doc.create(pytx.Alignat(numbering=False, escape=False)) as agn:
            sym = [f"T_{self._idx} = "]
            if self.dh_entry.theta != 0:
                sym.append( \
                    pytx.Matrix(np.matrix([\
                        [1, 0, 0, 0], \
                        [0, 0, 0, 0], \
                        [0, 0, 0, 0], \
                        [0, 0, 0, 1] \
                        ]))
                    )
            agn.extend(sym)
            
        with doc.create(pytx.Alignat(numbering=False, escape=False)) as agn:
            agn.extend([\
            f"T_{self._idx} = ", \
            pytx.Matrix(self._rot_theta.round(2), mtype="b"),\
            pytx.Matrix(self._trans_d.round(2), mtype="b"),\
            pytx.Matrix(self._trans_a.round(2), mtype="b"),\
            pytx.Matrix(self._rot_alpha.round(2), mtype="b"),\
            ])
        with doc.create(pytx.Alignat(numbering=False, escape=False)) as agn:
            agn.extend([f"T_{self._idx} = ", \
            pytx.Matrix(self.matrix.round(2), mtype="b"),\
            ])

class dh_solver:

    def __init__(self, params: dh_table):
        self.params = params

        self._transitions = []

        self.recalculate()

    def recalculate(self):
        for i, entry in enumerate(self.params):
            self._transitions.append(dh_transition(i+1, entry))

        self.result = 1

        for t in self._transitions:
            self.result *= t.matrix

    def generate_latex(self):
        doc = pytx.Document(\
            geometry_options={"lmargin=2cm"}
            )
        with doc.create(pytx.Section("Title")):
            for t in self._transitions:
                t.latex(doc)
            with doc.create(pytx.Alignat(numbering=False, escape=False)) as agn:
                agn.extend([f"T =", pytx.Matrix(result.round(2), mtype="b")])

        doc.generate_pdf('full')

    def generate_mathml(self):
        res = ""
        def mathmlMatrix(name: str, matrix):
            res = ""
            res += '<math xmlns="http://www.w3.org/1998/Math/MathML">\n'
            res += "<mrow>\n"
            if '_' in name:
                name = name.split('_', 1)
                res += f"<msub><mi>{name[0]}</mi><mi>{name[1]}</mi></msub>"
            else:
                res += f"<mi>{name}</mi>"
            res += "<mo>=</mo>\n"
            res += "<mo>[</mo><mtable>\n"
            for row in matrix.A:
                res += "<mtr>\n"
                for c in row:
                    res += f"<mtd>{round(c, 2)}</mtd>\n"
                res += "</mtr>\n"
            res += "</mtable><mo>]</mo>\n"
            res += "</mrow>\n"
            res +="</math><br>\n\n" 
            return res
        for i, t in enumerate(self._transitions):
            res += mathmlMatrix(f"T_{i+1}", t.matrix)
        
        res += "<br>Macierz wynikowa:<br>"
        res += mathmlMatrix("T", self.result)
        return res

    def generate_plot(self):
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')

        point = [0, 0, 0]
        points = [point]
        text_points = []
        T = 1
        for i, t in enumerate(self._transitions):
            T *= t.matrix
            point_next = [ \
                T.A[0][3],
                T.A[1][3],
                T.A[2][3],
            ]
            if point != point_next:
                points.append(point_next)
                # q = ax.quiver(*point, \
                #     *[point_next[i] - point[i] for i in range(0,3)])
                text_points.append(ax.text(*point_next, f"{i+1}"))

                rot_matrix = dh_get_rotation(T)
                angles = R.from_matrix(rot_matrix)
            else:
                text_prev = text_points[-1].get_text()
                text_points[-1].set_text(f"{text_prev},{i+1}")
            point = point_next
        print(f"points: {points}")
        print(f"points {[row[0] for row in points]}")
        print(f"points {[row[1] for row in points]}")
        print(f"points {[row[1] for row in points]}")
        ax.plot3D( \
            [row[0] for row in points], \
            [row[1] for row in points], \
            [row[2] for row in points], \
            "r"
            )
        #ax.quiver(0, 0, 0, self.result.A[0][0], self.result.A[0][1], self.result.A[0][2])

        rot_matrix = dh_get_rotation(self.result)
        angles = R.from_matrix(rot_matrix)

        # Auto scale
        h_max = 10
        h_min = -10
        z_max = 10
        for p in points:
            print(f"Point {p}")
            h_max = p[0] if p[0] > h_max else h_max
            h_min = p[0] if p[0] < h_min else h_min
            h_max = p[0] if p[0] > h_max else h_max
            h_min = p[1] if p[1] < h_min else h_min
            h_max = p[1] if p[1] > h_max else h_max
            h_max = p[2] if p[2] > z_max else h_max
        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        lim_scale = 0.25
        ax.set_xlim([h_min+h_min*lim_scale, h_max+h_max*lim_scale])
        ax.set_ylim([h_min+h_min*lim_scale, h_max+h_max*lim_scale])
        ax.set_zlim([0, h_max+h_max*lim_scale])

        # Print coordinate markers
        point_prev = None
        coords_scale = abs((h_max-h_min)*0.15)
        r = 1
        print(f"scale: {coords_scale}")
        for i, p in enumerate(points):
            print(f"p: {p}")
            if point_prev != p:
                print(i)
                try: 
                    r *= self._transitions[i-1].matrix[:3,:3]
                    print_coords(ax, *p, 
                        r=R.from_matrix(r),
                        scale=coords_scale)
                except Exception as e:
                    print_coords(ax, *p, 
                        scale=coords_scale)
            point_prev = p

        ax.text(0, 0, 0, "(0,0)")
        fig.set_facecolor(color='aliceblue')
        ax.set_facecolor(color='aliceblue')

        return fig

if __name__ == "__main__":
    table = dh_table("./data.csv")
    solver = dh_solver(table)
    solver.generate_latex()
    solver.generate_plot().show()
