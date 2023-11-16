from .dh_solver.dh_solver import dh_solver as solver
from .dh_solver.dh_table import dh_table
from .robobo.robobo import robobo_solver

from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

import os, io
import werkzeug
from flask import Flask, render_template, request, Response

app = Flask(__name__)

@app.route('/robotics')
def robotics():
    return render_template('robotics.html')

@app.route('/robotics/dh_solver')
def dh_solver_get():
    return render_template('upload.html', fields_count=1)

def dh_get_solver_from_query(args) -> solver:
    data = "theta,d,a,alpha\n"

    for i in range(int(args.get("joints_count"))):
        data += args.get(f"theta{i}") + ',' 
        data += args.get(f"d{i}") + ',' 
        data += args.get(f"a{i}") + ',' 
        data += args.get(f"alpha{i}") + '\n'
    params = dh_table(data=data)
    slvr = solver(params)
    return slvr

@app.route('/robotics/dh_solver/plot')
def dh_solver_plot():
    slvr = dh_get_solver_from_query(request.args)

    figure = slvr.generate_plot()
    output = io.BytesIO()
    FigureCanvas(figure).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')

@app.route('/robotics/dh_solver', methods=['POST'])
def dh_solver_post():
    print(request.form)

    fields_count = int(request.form["fields_count"])

    if request.form["submit_button"] == "send":
        f = request.files['file']
        data = f.stream.read().decode()
        params = dh_table(data=data)
        slvr = solver(params)
        slvr.generate_plot().savefig("tmpfig")
        os.remove("tmpfig")

    prev_fields = {}
    for i in range(0, fields_count):
        prev_fields[f"theta{i}"] = request.form[f"theta{i}"]
        prev_fields[f"a{i}"] = request.form[f"a{i}"]
        prev_fields[f"d{i}"] = request.form[f"d{i}"]
        prev_fields[f"alpha{i}"] = request.form[f"alpha{i}"]

    if request.form["submit_button"] == "+":
        fields_count += 1
    if request.form["submit_button"] == "-" and \
        fields_count > 1:
        try:
            prev_fields.pop(f"theta{fields_count}")
            prev_fields.pop(f"d{fields_count}")
            prev_fields.pop(f"a{fields_count}")
            prev_fields.pop(f"alpha{fields_count}")
        except KeyError:
            pass
        fields_count -= 1
    if request.form["submit_button"] == "Oblicz":
        def getField(request, param, i):
            try:
                return int(request.form[f"{param}{i}"])
            except ValueError:
                return 0

            theta = []
            a = []
            d = []
            alpha = []

        query = ""
        csv = "theta,d,a,alpha\n"
        for i in range(0, fields_count):
            query += f"theta{i}={getField(request, 'theta', i)}&"
            query += f"d{i}={getField(request, 'd', i)}&"
            query += f"a{i}={getField(request, 'a', i)}&"
            query += f"alpha{i}={getField(request, 'alpha', i)}&"
            csv += f"{getField(request, 'theta', i)},"
            csv += f"{getField(request, 'd', i)},"
            csv += f"{getField(request, 'a', i)},"
            csv += f"{getField(request, 'alpha', i)}\n"

        query += f"joints_count={fields_count}"
        params = dh_table(data=csv)
        slvr = solver(params)

        return render_template('upload.html', \
            fields_count = fields_count, \
            plot_query = query, \
            prev_fields = prev_fields, \
            matrices=slvr.generate_mathml())

    return render_template('upload.html', fields_count = fields_count, prev_fields = prev_fields)

@app.route('/robotics/robobo')
def robobo():
    return render_template('robobo.html', x=0, y=0, n=0, delta=0, alpha=0, L=0, R=0)

@app.route('/robotics/robobo/plot')
def robobo_plot():

    args = dict(request.args)
    print(f"Plot args: {args}")
    if 'n' in args and int(args['n']) > 0:
        n = int(args['n'])
    else: 
        n = None
    args = {k: float(v) for k,v in args.items()}
    slvr = robobo_solver((args['x'],args['y']), args['alpha'], args['L'], args['R'], args['delta'], a=n)   

    figure = slvr.generateArcPlot()
    output = io.BytesIO()
    FigureCanvas(figure).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')

@app.route('/robotics/robobo', methods=['POST'])
def robobo_post():

    x = 0
    y = 0
    try:
        x = float(request.form['x'])
    except ValueError:
        pass
    try:
        y = float(request.form['y'])
    except ValueError:
        pass
    try:
        alpha = float(request.form['alpha'])
    except ValueError:
        alpha = 0.0
    try:
        L = float(request.form['L'])
        if L == 0:
            raise ValueError
    except ValueError:
        return "Error: L = 0"
    try:
        R = float(request.form['R'])
        if R == 0:
            raise ValueError
    except ValueError:
        return "Error: R = 0"
    try:
        delta = float(request.form['delta'])
        if delta == 0:
            raise ValueError
    except ValueError:
        return "Error: &delta; = 0"
    try:
        a = int(request.form['n'])
    except Exception as e:
        a = None

    if request.form['submit_button'] == 'Oblicz':
        a = 0
        slvr = robobo_solver((x,y), alpha, L, R, delta)   
    elif request.form['submit_button'] == 'Oblicz dla n':
        slvr = robobo_solver((x,y), alpha, L, R, delta, a=a)   
    print(f"a = {a}")
    return render_template('robobo.html', x=x, y=y, R=R, L=L, n=a, delta=delta, alpha=alpha, mathml=slvr.arc.getMathML())

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)