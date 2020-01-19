from app import (
    app,
    restricted,
    redirect_when,
    check_unconfirmed,
    create_connection,
    get_customer_id,
    get_customer_type,
    set_session_user,
    clear_session_user,
    user_is_confirmed,
    get_user_fullname,
    generate_token,
    confirm_token,
    send_email_mailgun,
    send_confirm_account_email,
    send_reset_password_email,
)
from flask import render_template, session, request, redirect, flash, url_for, jsonify
from flask_bcrypt import generate_password_hash as gen_pw_hash
from flask_bcrypt import check_password_hash as chk_pw_hash
from datetime import datetime
import urllib.parse
import os


@app.route("/sign-in.html")
@redirect_when(_type="USER")
def sign_in():
    has_next = request.args.get("next") is not None
    return render_template("sign-in.html", has_next=has_next)


@app.route("/sign-in.html", methods=["POST"])
@redirect_when(_type="USER")
def sign_in_post():
    email = request.form.get("email")
    password = request.form.get("password")
    next_url = request.args.get("next")

    query = """
    SELECT customer_id, first_name, last_name, password, customer_type 
    FROM customer 
    WHERE email=%s
    """

    cnx = create_connection()
    cursor = cnx.cursor()
    cursor.execute(query, (email))
    result = cursor.fetchone()
    cursor.close()
    cnx.close()

    if result is None:
        flash("The user does not exist!", "error")
        return redirect(url_for("sign_in", next=next_url))

    if not chk_pw_hash(result["password"], password):
        flash("You have entered a wrong password!", "error")
        return redirect(url_for("sign_in", next=next_url))

    if not user_is_confirmed(email):
        session["next_url"] = next_url
        resend_confirmation()

        flash(
            "Your account needs to be confirmed first. A new email has been sent!",
            "error",
        )
        return redirect(url_for("unconfirmed"))

    full_name = "{fname} {lname}".format(
        fname=result["first_name"], lname=result["last_name"]
    )
    info = {
        "customer_id": result["customer_id"],
        "email": email,
        "customer_type": result["customer_type"],
        "first_name": result["first_name"],
        "last_name": result["last_name"],
        "full_name": full_name,
    }

    set_session_user(info)

    return redirect(
        urllib.parse.quote(next_url) if next_url is not None else url_for("index")
    )


@app.route("/sign-up.html")
@redirect_when(_type="USER")
def sign_up():
    has_next = request.args.get("next") is not None
    return render_template("sign-up.html", has_next=has_next)


@app.route("/sign-up.html", methods=["POST"])
@redirect_when(_type="USER")
def sign_up_post():
    use_mailgun = os.getenv("MAILGUN_ENABLED", False) == "True"
    form = request.form

    first_name = form.get("firstName")
    last_name = form.get("lastName")
    mobile = form.get("mobile")
    gender = form.get("gender")
    email = form.get("email")
    password = gen_pw_hash(form.get("password"))
    next_url = request.args.get("next")
    current_date = datetime.now().date()

    cnx = create_connection()
    cursor = cnx.cursor()
    cursor.execute("SELECT * FROM customer WHERE email=%s", (email))
    result = cursor.fetchone()
    cursor.close()

    if result is not None:
        flash("The user already exists", "error")
        return redirect(url_for("sign_up", next=next_url))

    cursor = cnx.cursor()
    cursor.execute("SELECT COUNT(*) as next_id FROM customer")
    customer_id = int(cursor.fetchone()["next_id"])
    cursor.close()

    query = """
    INSERT INTO customer (customer_id, first_name, last_name, email, password, mobile, gender, joined_date, status, customer_type) 
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, "USER")
    """

    cursor = cnx.cursor()
    cursor.execute(
        query,
        (
            customer_id,
            first_name,
            last_name,
            email,
            password,
            mobile,
            gender,
            current_date,
            "Unconfirmed" if use_mailgun else "Confirmed",
        ),
    )
    cursor.close()

    if use_mailgun:
        cnx.commit()
        cnx.close()

        response = send_confirm_account_email(email=email, next_url=next_url)

        return redirect(url_for("unconfirmed", email=email, next=next_url))

    full_name = "{fname} {lname}".format(fname=first_name, lname=last_name)
    info = {
        "customer_id": customer_id,
        "email": email,
        "customer_type": "USER",
        "first_name": first_name,
        "last_name": last_name,
        "full_name": full_name,
    }

    set_session_user(info)

    cnx.commit()
    cnx.close()

    return redirect(
        urllib.parse.quote(next_url) if next_url is not None else url_for("index")
    )


@app.route("/sign-out.html")
@restricted(access_level="USER")
def sign_out():
    clear_session_user()
    return redirect(url_for("index"))


@app.route("/user-profile.html")
@restricted(access_level="USER")
def profile():
    cnx = create_connection()

    query = """
    SELECT first_name, last_name, email, mobile, gender, DATE_FORMAT(joined_date, "%%d %%b %%Y") as joined_date
    FROM customer
    WHERE customer_id=%s
    """

    cursor = cnx.cursor()
    cursor.execute(query, (session["customer_id"]))
    user_info = cursor.fetchone()
    cursor.close()
    cnx.close()

    return render_template("user-profile.html", user_info=user_info)


@app.route("/edit-info", methods=["POST"])
@restricted(access_level="USER")
def edit_info():
    form = request.form
    first_name = form.get("firstName")
    last_name = form.get("lastName")
    mobile = form.get("mobile")

    query = """
    UPDATE customer 
    SET first_name=%s, last_name=%s, mobile=%s 
    WHERE customer_id=%s and email=%s
    """

    cnx = create_connection()
    cursor = cnx.cursor()
    cursor.execute(
        query, (first_name, last_name, mobile, session["customer_id"], session["email"])
    )
    cursor.close()
    cnx.commit()
    cnx.close()

    flash("Profile updated successfully", "success")
    return redirect(url_for("profile"))


@app.route("/change-password", methods=["POST"])
@restricted(access_level="USER")
def change_password():
    form = request.form
    current_password = form.get("currentPassword")
    new_password = gen_pw_hash(form.get("newPassword"))
    customer_id = get_customer_id()

    query = """
    SELECT password 
    FROM customer 
    WHERE customer_id=%s
    """

    cnx = create_connection()
    cursor = cnx.cursor()
    cursor.execute(query, (customer_id))
    db_password = cursor.fetchone()["password"]
    cursor.close()

    if not chk_pw_hash(db_password, current_password):
        cnx.close()
        flash("You have entered a wrong password!", "error")
        return redirect(url_for("profile"))

    query = """
    UPDATE customer 
    SET password=%s 
    WHERE customer_id=%s and email=%s
    """

    cursor = cnx.cursor()
    cursor.execute(query, (new_password, session["customer_id"], session["email"]))
    cursor.close()
    cnx.commit()
    cnx.close()

    return redirect(url_for("sign_out"))


@app.route("/delete-account", methods=["POST"])
@restricted(access_level="USER")
def delete_account():
    form = request.form
    current_password = form.get("currentDeletePassword")
    customer_id = get_customer_id()

    query = """
    SELECT password 
    FROM customer 
    WHERE customer_id=%s
    """

    cnx = create_connection()
    cursor = cnx.cursor()
    cursor.execute(query, (customer_id))
    db_password = cursor.fetchone()["password"]
    cursor.close()

    if not chk_pw_hash(db_password, current_password):
        cnx.close()
        flash("You have entered a wrong password!", "error")
        return redirect(url_for("profile"))

    query = """
    DELETE FROM customer 
    WHERE customer_id=%s and email=%s
    """

    cursor = cnx.cursor()
    cursor.execute(query, (customer_id, session["email"]))
    cursor.close()
    cnx.commit()
    cnx.close()

    return redirect(url_for("sign_out"))


@app.route("/unconfirmed.html")
@check_unconfirmed(by="email")
def unconfirmed():
    return render_template("unconfirmed.html", email=request.args.get("email"))


@app.route("/confirm?token=<token>")
@check_unconfirmed(by="token")
def confirm_email(token=""):
    next_url = request.args.get("next")
    email = confirm_token(token)

    # if not email:
    #     flash("The confirmation link is invalid or has expired.", "error")
    #     return redirect(url_for("index"))

    query = """
    UPDATE customer
    SET status="Confirmed"
    WHERE email=%s
    """

    cnx = create_connection()
    cursor = cnx.cursor()
    cursor.execute(query, (email))
    cursor.close()
    cnx.commit()
    cnx.close()

    recipient = "{fullname} <{email}>".format(
        fullname=get_user_fullname(email), email=email,
    )

    data = {
        "recipient": recipient,
        "subject": "Welcome on board!",
        "template": "welcome",
        "action_url": url_for("sign_in", _external=True),
    }

    response = send_email_mailgun(data=data)
    flash("Your account has been confirmed. Thanks!", "success")

    return redirect(url_for("sign_in", next=next_url))


@app.route("/resend", methods=["GET"])
@check_unconfirmed(by="email")
def resend_confirmation():
    email = request.args.get("email")
    next_url = request.args.get("next")
    message = "A new confirmation email has been sent."

    send_confirm_account_email(email=email, next_url=next_url)

    return jsonify(message=message)


@app.route("/forgot-password.html")
def forgot_password():
    return render_template("forgot-password.html")


@app.route("/forgot-password.html", methods=["POST"])
def forgot_password_post():
    use_mailgun = os.getenv("MAILGUN_ENABLED") == "True"
    email = request.form.get("email")

    full_name = get_user_fullname(email=email)

    if full_name is None:
        flash("The user does not exist!", "error")
        return redirect(url_for("sign_up"))

    if get_customer_type() == "USER":
        clear_session_user()

    token = generate_token(email)

    if use_mailgun:
        response = send_reset_password_email(email=email, token=token)

        flash("An email was sent with instructions to reset your password!", "success")
        return redirect(url_for("index"))

    return redirect(url_for("reset_password", token=token))


@app.route("/reset-password?token=<token>", methods=["GET", "POST"])
def reset_password(token=""):
    use_mailgun = os.getenv("MAILGUN_ENABLED") == "True"
    email = confirm_token(token)

    if not email:
        flash(
            "The reset link is invalid or has expired!", "error",
        )
        return redirect(url_for("index"))

    if request.method == "GET":
        return render_template("reset-password.html")

    password = gen_pw_hash(request.form.get("password"))

    query = """
    UPDATE customer 
    SET password=%s 
    WHERE email=%s
    """

    cnx = create_connection()
    cursor = cnx.cursor()
    cursor.execute(query, (password, email))
    cursor.close()
    cnx.commit()
    cnx.close()

    if use_mailgun:
        recipient = "{fullname} <{email}>".format(
            fullname=get_user_fullname(email), email=email,
        )

        data = {
            "recipient": recipient,
            "subject": "Your password has been updated!",
            "template": "updated_password",
            "action_url": url_for("sign_in", _external=True),
        }

        response = send_email_mailgun(data=data)

    flash("Your password has been updated! Please sign in.", "success")

    return redirect(url_for("sign_in"))
