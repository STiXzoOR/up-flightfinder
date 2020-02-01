from flask import render_template, request, redirect, url_for
from app import app
import urllib.parse


@app.route("/guest/guest-detected.html")
def guest_detected():
    return render_template("guest/guest-detected.html")


@app.route("/guest/guest-detected.html", methods=["POST"])
def guest_detected_post():
    form = request.form

    next_url = request.args.get("next")
    btn_state = form.get("btnState")
    if btn_state == "guest":
        return redirect(urllib.parse.quote(next_url))
    elif btn_state == "sign_in":
        return redirect(url_for("sign_in", next=next_url))
    else:
        return redirect(url_for("sign_up", next=next_url))

