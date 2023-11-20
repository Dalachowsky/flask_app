
import os, io, subprocess
import werkzeug
from flask import Flask, render_template, request, Response, send_file
from random import randint

from .robobo_app import robobo
from .dh_solver_app import dh_solver_app

app = Flask(__name__)

app.register_blueprint(robobo, url_prefix="/polibuda/robobo")
app.register_blueprint(dh_solver_app, url_prefix="/polibuda/dh_solver")

class ad:

    def __init__(self, path: str, width: str):
        self.path = '/static/ads/' + path
        self.width = width

    def getHTML(self):
        return f'<img src={self.path} width={self.width} style="margin: 20px">'

ads = [
    ad('lecina.jpg', width='60%'),
    ad('lecina2.jpg', width='60%'),
    ad('jachas.jpg', width='auto'),
    ad('holownianos.jpg', width='auto'),
    ad('niedogrzany.jpeg', width='auto'),
    ad('memtzen.png', width='auto'),
]

@app.context_processor
def addBanner():
    try:
        users = int(open('/tmp/active_users', 'r').read())
        banner = ""
        if users > 1:
            banner = ""
            banner += r"<div style='position: fixed; bottom: 0; left: 0; background-color: orange; width: 100%;'>"
            banner += r"Uwaga admin na obiekcie. Strona może sie rozjebać w każdym momencie."
            banner += r"</div>"
        return dict(banner=banner)
    except Exception:
        return dict(banner="")


@app.route('/robotics/ad')
def ad():
    return send_file( os.getcwd() + ads[randint(0, len(ads) - 1)].path, mimetype='image/gif')

@app.route('/polibuda')
def robotics():
    return render_template('robotics.html')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)