from flask import Flask, render_template, request
from jitvm import run_code


def make_app():
    app = Flask(__name__)

    @app.route("/<token>/", methods=["GET", "POST"])
    def index(token):
        if request.method == "GET":
            return render_template("index.html")
        form = request.form

        code = str(form["code"])
        input = [int(x) for x in str(form["input"]).split()]

        return run_code(code, input)

    return app
