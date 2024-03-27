from datetime import datetime
from flask import Flask, abort, redirect, render_template, request, jsonify
from urlc.models import ShortLink
from urlc.database import db_session

import os, sys

import mmh3
import base62

from loguru import logger

logger.remove()
logger.add(sys.stderr, format="{time} {level} {message}", level="DEBUG")


DULPLICATED = "DULPLICATED888"

app = Flask(__name__)


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()


@app.route("/")
def index():
    return render_template("dist/index.html")


@app.route("/ping")
def ping_pong():
    return "pong"


def generate_short_url(long_url):
    """e.g.
    url: https://juejin.cn/post/7057083730686377997
    res 3YmGBU
    """
    res = None
    try:
        m = mmh3.hash(long_url.encode("utf-8"), signed=False)
        res = base62.encode(m)
    except Exception as e:
        print(f"generate_short_url error: {e}")
    return res


@app.route("/api/shorten_url", methods=["POST"])
def shorten_url():
    """
    form['long_url']: 待处理url
    """
    logger.debug(f'req url: {request.host_url}')
    host_url = request.host_url

    if request.method != "POST":
        return
    long_url = request.form.get("long_url")
    if not long_url:
        return jsonify({"code": 1000, "msg": "need param long_url"})

    short_url = generate_short_url(long_url)
    if not short_url:
        return jsonify({"code": 1000, "msg": "param long_url invalid, change one"})
    sl: ShortLink = ShortLink.query.filter_by(short_key=short_url).first()
    logger.debug(f"short_url: {short_url}, long_url: {long_url}")
    if not sl:
        new_sl = ShortLink(
            short_key=short_url, source_url=long_url, created_time=datetime.now()
        )
        db_session.add(new_sl)
        db_session.commit()
        logger.debug("add new url")
    else:
        if sl.source_url.encode("utf-8") == long_url.encode("utf-8"):
            logger.debug("it exits, return")
        else:
            # hash冲突
            logger.warning("hash DULPLICATED!!!")
            new_long_url = long_url + DULPLICATED
            short_url = generate_short_url(new_long_url)
            new_sl = ShortLink(
                short_key=short_url,
                source_url=new_long_url,
                created_time=datetime.now(),
            )
            db_session.add(new_sl)
            db_session.commit()

    return jsonify({"code": 0, "msg": "success", "short_url": host_url+short_url})


@app.route("/<string:short_key>", methods=["GET"])
def redirect_source_url(short_key):
    """传入短连后重定向到到原链接"""
    logger.debug(f'req url: {request.url}')
    sl: ShortLink = ShortLink.query.filter_by(short_key=short_key).first()
    if not sl:
        abort(404)
    source_url: str = sl.source_url
    while source_url.endswith(DULPLICATED):
        source_url = source_url.removesuffix(DULPLICATED)
    return redirect(location=source_url, code=301)


if __name__ == "__main__":
    # app.run(host="0.0.0.0", port=8080, debug=True, ssl_context='adhoc')
    app.run(host="0.0.0.0", port=8080, debug=True)
