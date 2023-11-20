
from .dh_solver.dh_solver import dh_solver as solver
from .dh_solver.dh_table import dh_table

from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

import io
from flask import Blueprint, render_template, request, Response

dh_solver_app = Blueprint('dh_solver', __name__, template_folder='templates')

@dh_solver_app.route('/')
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

@dh_solver_app.route('/plot')
def dh_solver_plot():
    slvr = dh_get_solver_from_query(request.args)

    figure = slvr.generate_plot()
    output = io.BytesIO()
    FigureCanvas(figure).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')

@dh_solver_app.route('/', methods=['POST'])
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
