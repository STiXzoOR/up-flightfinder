from app import app
from flask import render_template


@app.errorhandler(403)
def access_denied(e):
    return render_template("403.html"), 403


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template("500.html"), 500

@app.errorhandler(503)
def server_maintenance(e):
    return render_template("error/503.html"), 503
