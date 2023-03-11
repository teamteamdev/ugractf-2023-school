import hmac
import sys
from base64 import b64encode
from io import BytesIO
from random import choice

from flask import Flask, request, session, render_template, redirect, url_for, send_file
from flask_limiter import Limiter
from kyzylborda_lib.secrets import get_flag

from captcha import generate

secret = b'N6LW-BlhbF0oMOvJ-A1xvYsY357vzWB9CCf_nvnRkmivbUCap1CF5Q'

with open('words.txt') as f:
    words = list(map(str.strip, f))

def get_word() -> str:
    return choice(words)


def calc_price(number: int) -> int:
    static_cashes = [400, 200, 100, 50, 25]
    if number <= len(static_cashes):
        return static_cashes[number - 1]
    return 1


def text2id(text: str, token: str) -> str:
    id_ = hmac.digest(b''.join([secret, token.encode()]), text.encode(), 'sha256')
    return ''.join(f'{c:02x}' for c in id_)


def check_captcha(answer: str, id: str, token: str) -> bool:
    return text2id(answer, token) == id


def make_app():
    app = Flask(__name__)
    app.secret_key = secret

    limiter = Limiter(
            lambda: session.get('token', 'nothing'),
            app=app,
            storage_uri='memcached://memcached:11211',
    )

    @app.errorhandler(429)
    def no_more_captcha(e):
        return send_file('templates/error.html')

    @app.route("/favicon.ico")
    def favicon():
        return send_file('favicon.ico')

    @app.route("/<token>/", methods=["GET"])
    @limiter.limit('5 per 5 minutes')
    def index(token):
        if session.get('token') != token:
            session.clear()
        session['token'] = token

        text = get_word()

        cid = text2id(text, token)
        buf = BytesIO()
        generate(text).save(buf, format="PNG")
        based = b64encode(buf.getvalue()).decode()

        count = session.get('count', 0)
        cash = session.get('cash', 0)
        flag = None
        if cash >= 10_00:
            flag = get_flag(token)
        cash = f'{cash // 100}.{cash % 100:02}'

        return render_template('index.html',
                               url=f'/{token}/{cid}/',
                               image=f'data:image/png;base64,{based}',
                               count=count,
                               cash=cash,
                               flag=flag)

    @app.route("/<token>/<cid>/", methods=["POST"])
    def verify(token, cid):
        answer = request.form['answer']
        if 'count' not in session:
            session['count'] = 0
            session['cash'] = 0
        if check_captcha(answer, cid, token):
            session['count'] += 1
            session['cash'] += calc_price(session['count'])
        return redirect(url_for('index', token=token))


    return app
