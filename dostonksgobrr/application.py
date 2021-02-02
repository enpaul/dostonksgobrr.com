import os

import flask

from dostonksgobrr import calendar

APPLICATION = flask.Flask(__name__)

try:
    import flask_minify
except ImportError:
    pass
else:
    flask_minify.minify(app=APPLICATION, html=True, js=True, cssless=True)


ENV_META_TAGS: str = "STONKS_META_TAGS"

DEFAULT_META_TAGS: str = (
    "stocks,nyse,stonks,brr,trade,trading,market,hours,open,api,programatic,json"
)

ENV_BASE_URL: str = "STONKS_BASE_URL"

DEFAULT_BASE_URL: str = "/"


@APPLICATION.route("/")
def index():
    return flask.render_template(
        "index.html.j2",
        status=calendar.is_market_open(),
        next_bell=f"{calendar.next_bell().isoformat()}+00:00",
        meta_tags=os.getenv(ENV_META_TAGS, DEFAULT_META_TAGS).split(","),
        url_base=os.getenv(ENV_BASE_URL, DEFAULT_BASE_URL),
        url_style=flask.url_for("static", filename="style.css"),
    )


@APPLICATION.route("/data.json")
def data():
    return flask.jsonify(
        {
            "is-market-open": calendar.is_market_open(),
            "next-bell": f"{calendar.next_bell().isoformat()}+00:00",
        }
    )
