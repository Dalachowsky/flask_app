
from .robobo.robobo import robobo_solver, robobo_arc

from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

import io
from flask import Blueprint, render_template, request, Response
from math import radians

robobo = Blueprint('robobo', __name__, template_folder='templates')

@robobo.route('/')
def robobo_get():
    return render_template('robobo.html', x=0, y=0, n=0, delta=0, alpha=0, L=0, R=0)

@robobo.route('/plot_arc')
def robobo_plot_arc():

    args = dict(request.args)
    print(f"Plot args: {args}")
    if 'n' in args and int(args['n']) > 0:
        n = int(args['n'])
    else: 
        n = None
    args = {k: float(v) for k,v in args.items()}
    slvr = robobo_arc(R=args['R'], delta=radians(args['delta']), a=n)   

    figure = slvr.getPlot()
    output = io.BytesIO()
    FigureCanvas(figure).print_png(output)

    return Response(output.getvalue(), mimetype='image/png')

@robobo.route('/plot')
def robobo_plot():
    args = dict(request.args)
    print(f"Plot args: {args}")
    if 'n' in args and int(args['n']) > 0:
        n = int(args['n'])
    else: 
        n = None
    args = {k: float(v) for k,v in args.items()}
    slvr = robobo_solver(
        P=(args['x'], args['y']),
        alpha=args['alpha'],
        L=args['L'],
        R=args['R'],
        delta=args['delta']
    )

    figure = slvr.generatePlot()
    output = io.BytesIO()
    FigureCanvas(figure).print_png(output)

    return Response(output.getvalue(), mimetype='image/png')

@robobo.route('/', methods=['POST'])
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
        slvr = robobo_arc(R, radians(delta))   
    elif request.form['submit_button'] == 'Oblicz dla n':
        slvr = robobo_arc(R, radians(delta), a=a)   
    print(f"a = {a}")
    return render_template('robobo.html', x=x, y=y, R=R, L=L, n=a, delta=delta, alpha=alpha, mathml=slvr.getMathML())
