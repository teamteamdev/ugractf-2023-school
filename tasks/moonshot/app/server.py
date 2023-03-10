from flask import Flask, render_template, request
from jitvm import run_code
import time


def make_app():
    app = Flask(__name__)

    @app.route("/<token>/", methods=["GET", "POST"])
    def index(token):
        if request.method == "GET":
            return render_template("index.html")
        form = request.form

        code = str(form["code"])
        input = [int(x) for x in str(form["input"]).split()]

        """
        You have: 2 moondists
        You want: lightseconds
            * 2.5644408
            / 0.38994857
        """
        time.sleep(2.5)

        return run_code(code, input)

    return app
