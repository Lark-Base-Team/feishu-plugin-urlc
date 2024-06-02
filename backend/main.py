from datetime import datetime
from typing import Dict, List
from flask import Flask, abort, redirect, render_template, request, jsonify
from urlc.models import ShortLink
from urlc.database import db_session

import os, sys

import mmh3
import base62

from loguru import logger

logger.remove()
logger.add(sys.stderr, format="{time} {level} {message}", level="INFO")


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
    =>res 3YmGBU
    """
    res = None
    try:
        m = mmh3.hash(long_url.encode("utf-8"), signed=False)
        res = base62.encode(m)
    except Exception as e:
        print(f"generate_short_url error: {e}")
    return res


def shorten_url_to_db(long_url: str) -> str:
    """缩短链接并插入到数据库中"""
    if not long_url:
        return ""
    short_url = generate_short_url(long_url)
    if not short_url:
        return f"generate_short_url failed, input longurl: {long_url}"
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

    return short_url


@app.route("/api/shorten_urls", methods=["POST"])
def batch_shorten_url():
    """接收处理long url列表
    body: 待处理url
    field_value_list:
    [
        {
            "record_id": "recm2bS5GV",
            "text": "https://juejin.cn/post/7057083730686377997"
        }, ...
    ]
    """
    logger.debug(f"req url: {request.host_url}")
    host_url = request.host_url

    if request.method != "POST":
        return
    long_urls: List[Dict] = request.get_json()
    if (not long_urls) or ("field_value_list" not in long_urls.keys()):
        return jsonify({"code": 1000, "msg": "need param field_value_list"})

    data_list = []
    try:
        for d in long_urls.get("field_value_list"):
            if not ("record_id" in d.keys() and "text" in d.keys()):
                continue
            cur_url: str = d["text"]
            shortened_res = f"{cur_url}生成失败"
            if (
                cur_url
                and isinstance(cur_url, str)
                and any((cur_url.startswith("http://"), cur_url.startswith("https://")))
            ):
                shortened_res = host_url + shorten_url_to_db(d["text"])
            else:
                shortened_res = "请输入http://或者https://开头的网址"

            cur_res = {"record_id": d["record_id"], "text": shortened_res}
            data_list.append(cur_res)

    except Exception as e:
        logger.error(f"shorten_urls error, process {long_urls}, {e}")
        return jsonify(
            {"code": 2000, "msg": f"转换失败, {long_urls}, {e}", "data": data_list}
        )

    return jsonify({"code": 0, "msg": "success", "data": data_list})


@app.route("/api/shorten_url", methods=["POST"])
def shorten_url():
    """接收处理单个long url
    form['long_url']: 待处理url
    """
    logger.debug(f"req url: {request.host_url}")
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

    return jsonify({"code": 0, "msg": "success", "short_url": host_url + short_url})


@app.route("/<string:short_key>", methods=["GET"])
def redirect_source_url(short_key):
    """传入短链后重定向到到原链接"""
    logger.debug(f"req url: {request.url}")
    sl: ShortLink = ShortLink.query.filter_by(short_key=short_key).first()
    if not sl:
        abort(404)
    source_url: str = sl.source_url
    while source_url.endswith(DULPLICATED):
        source_url = source_url.removesuffix(DULPLICATED)
    return redirect(location=source_url, code=301)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True, ssl_context="adhoc")
    # app.run(host="0.0.0.0", port=8080, debug=True)
