from app import app, restricted, create_connection, get_customer_id, set_session_user, clear_session_user
from flask import render_template, session, request, redirect, flash, url_for
from flask_bcrypt import generate_password_hash as gen_pw_hash
from flask_bcrypt import check_password_hash as chk_pw_hash
from datetime import datetime
import urllib.parse

@app.route('/sign-in.html')
def sign_in():
    has_next = request.args.get('next') is not None
    return render_template('sign-in.html', has_next=has_next)

@app.route('/sign-in.html', methods=["POST"])
def sign_in_post():
    email = request.form.get('email')
    password = request.form.get('password')
    next_url = request.args.get('next')

    cnx = create_connection()
    cursor = cnx.cursor()
    cursor.execute('SELECT customer_id, first_name, last_name, password, customer_type FROM customer WHERE email=%s', (email))
    result = cursor.fetchone()
    cursor.close()
    cnx.close()
    
    if result is None:
        flash("The user does not exist!", 'error')
        return redirect(url_for('sign_in', next=next_url))
    
    if not chk_pw_hash(result['password'], password):
        flash("You have entered a wrong password!", 'error')
        return redirect(url_for('sign_in', next=next_url))
    
    info = {
        'customer_id': result['customer_id'],
        'email': email,
        'customer_type': result['customer_type'],
        'first_name': result['first_name'],
        'last_name': result['last_name'],
        'full_name': '{fname} {lname}'.format(fname=result['first_name'], lname=result['last_name'])
    }

    set_session_user(info)
    
    return redirect(urllib.parse.quote(next_url) if next_url is not None else url_for('index'))

@app.route('/sign-up.html')
def sign_up():
    has_next = request.args.get('next') is not None
    return render_template('sign-up.html', has_next=has_next)

@app.route('/sign-up.html', methods=["POST"])
def sign_up_post():
    form = request.form

    first_name = form.get('firstName')
    last_name = form.get('lastName')
    mobile = form.get('mobile')
    gender = form.get('gender')
    email = form.get('email')
    password = gen_pw_hash(form.get('password'))
    next_url = request.args.get('next')
    current_date = datetime.now().date()

    cnx = create_connection()
    cursor = cnx.cursor()
    cursor.execute('SELECT * FROM customer WHERE email=%s', (email))
    result = cursor.fetchone()
    cursor.close()

    if result is not None:
        flash("The user already exists", 'error')
        return redirect(url_for('sign_up', next=next_url))
    
    cursor = cnx.cursor()
    cursor.execute('SELECT COUNT(*) as next_id FROM customer')
    customer_id = int(cursor.fetchone()['next_id'])
    cursor.close()
    
    ins = """
    INSERT INTO customer (customer_id, first_name, last_name, email, password, mobile, gender, joined_date, status, customer_type) 
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, "Active", "USER")
    """

    cursor = cnx.cursor()
    cursor.execute(ins, (customer_id, first_name, last_name, email, password, mobile, gender, current_date))
    cursor.close()
    cnx.commit()
    cnx.close()

    info = {
        'customer_id': customer_id,
        'email': email,
        'customer_type': 'USER',
        'first_name': first_name,
        'last_name': last_name,
        'full_name': '{fname} {lname}'.format(fname=first_name, lname=last_name)
    }

    set_session_user(info)

    return redirect(urllib.parse.quote(next_url) if next_url is not None else url_for('index'))

@app.route('/sign-out.html')
@restricted(access_level='USER')
def sign_out():
    clear_session_user()
    return redirect(url_for('index'))

@app.route('/user-profile.html')
@restricted(access_level='USER')
def profile():
    cnx = create_connection()

    user_query = """
    SELECT first_name, last_name, email, mobile, gender, DATE_FORMAT(joined_date, "%%d %%b %%Y") as joined_date
    FROM customer
    WHERE customer_id=%s
    """

    cursor = cnx.cursor()
    cursor.execute(user_query, (session['customer_id']))
    user_info = cursor.fetchone()
    cursor.close()
    cnx.close()

    return render_template('user-profile.html', user_info=user_info)

@app.route('/edit-info', methods=["POST"])
@restricted(access_level='USER')
def edit_info():
    form = request.form
    first_name = form.get('firstName')
    last_name = form.get('lastName')
    mobile = form.get('mobile')

    query = """
    UPDATE customer 
    SET first_name=%s, last_name=%s, mobile=%s 
    WHERE customer_id=%s and email=%s
    """

    cnx = create_connection()
    cursor = cnx.cursor()
    cursor.execute(query, (first_name, last_name, mobile, session['customer_id'], session['email']))
    cursor.close()
    cnx.commit()
    cnx.close()

    flash('Profile updated successfully', 'success')
    return redirect(url_for('profile'))

@app.route('/change-password', methods=["POST"])
@restricted(access_level='USER')
def change_password():
    form = request.form
    current_password = form.get('currentPassword')
    new_password = gen_pw_hash(form.get('newPassword'))
    customer_id = get_customer_id()

    query = """
    SELECT password 
    FROM customer 
    WHERE customer_id=%s
    """

    cnx = create_connection()
    cursor = cnx.cursor()
    cursor.execute(query, (customer_id))
    db_password = cursor.fetchone()['password']
    cursor.close()
    
    if not chk_pw_hash(db_password, current_password):
        cnx.close()
        flash('You have entered a wrong password!', 'error')
        return redirect(url_for('profile'))

    query = """
    UPDATE customer 
    SET password=%s 
    WHERE customer_id=%s and email=%s
    """

    cursor = cnx.cursor()
    cursor.execute(query, (new_password, session['customer_id'], session['email']))
    cursor.close()
    cnx.commit()
    cnx.close()

    return redirect(url_for('sign_out'))

@app.route('/delete-account', methods=["POST"])
@restricted(access_level='USER')
def delete_account():
    form = request.form
    current_password = form.get('currentDeletePassword')
    customer_id = get_customer_id()

    query = """
    SELECT password 
    FROM customer 
    WHERE customer_id=%s
    """

    cnx = create_connection()
    cursor = cnx.cursor()
    cursor.execute(query, (customer_id))
    db_password = cursor.fetchone()['password']
    cursor.close()
    
    if not chk_pw_hash(db_password, current_password):
        cnx.close()
        flash('You have entered a wrong password!', 'error')
        return redirect(url_for('profile'))
    
    query = """
    DELETE FROM customer 
    WHERE customer_id=%s and email=%s
    """

    cursor = cnx.cursor()
    cursor.execute(query, (customer_id, session['email']))
    cursor.close()
    cnx.commit()
    cnx.close()

    return redirect(url_for('sign_out'))