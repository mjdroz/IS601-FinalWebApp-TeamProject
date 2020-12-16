from typing import List, Dict
import simplejson as json
from flask import Flask, request, Response, redirect, abort, session, flash
from flask import render_template
from flaskext.mysql import MySQL
from pymysql.cursors import DictCursor
from werkzeug.security import check_password_hash, generate_password_hash
from flask_mail import Mail, Message
import os
import random

app = Flask(__name__)
mysql = MySQL(cursorclass=DictCursor)
picFolder = os.path.join('static', 'images')

#email setup
mail_settings = {
    "MAIL_SERVER": 'smtp.gmail.com',
    "MAIL_PORT": 465,
    "MAIL_USE_TLS": False,
    "MAIL_USE_SSL": True,
    "MAIL_USERNAME": os.environ['MAIL_USERNAME'],
    "MAIL_PASSWORD": os.environ['MAIL_PASSWORD']
}

app.config.update(mail_settings)
mail = Mail(app)

app.config['UPLOAD_FOLDER'] = picFolder
app.config['SECRET_KEY'] = os.environ['SECRET_KEY']
app.config['MYSQL_DATABASE_HOST'] = 'db'
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'root'
app.config['MYSQL_DATABASE_PORT'] = 3306
app.config['MYSQL_DATABASE_DB'] = 'citiesData'
mysql.init_app(app)

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == ('POST'):
        cursor = mysql.get_db().cursor()
        username = request.form['username']
        password = request.form['password']
        sql_query = ('SELECT * FROM users u WHERE u.username = %s')
        userData = (username,)
        cursor.execute(sql_query, userData)
        try:
            if username == os.environ['ADMIN_USER']:
                if password == os.environ['ADMIN_PASS']:
                    session["user"] = username
                    return redirect("/home", code=302)
            result = cursor.fetchall()
            hash_pass = result[0]['passwordHash']
            confirmed = result[0]['confirmed']
            if check_password_hash(hash_pass, password):
                if confirmed == "yes":
                    session["user"] = username
                    return redirect("/home", code=302)
            else:
                flash("Login Failed. Try Again.", "danger")
        except IndexError:
            flash("Account Not Confirmed. Please Register an Account and Confirm Your Email!", "danger")
    return render_template('login.html')

@app.route('/logout')
def logout():
    if "user" in session:
        flash("You have been logged out.", "info")
    session.pop("user", None)
    return redirect('/', code=302)

@app.route('/register', methods=['GET'])
def register_get():
    title = "Registration"
    return render_template('register.html', title=title)

@app.route('/register', methods=['POST'])
def register_post():
    cursor = mysql.get_db().cursor()
    hash_pass = generate_password_hash(str(request.form['password']), "sha256")
    sql_insert_query = """INSERT INTO users (username, email, passwordHash, confirmed) VALUES (%s,%s,%s,%s)"""
    confirmed = "no"
    inputData = (request.form['username'], request.form['email'], hash_pass, confirmed)
    cursor.execute(sql_insert_query, inputData)
    mysql.get_db().commit()
    session['user'] = request.form['username']
    session['email'] = request.form['email']
    session['code'] = generate_password_hash(str(session), "sha256")
    msg = Message(subject="Mike and Stanley's Website Confirmation Code",
                  sender=app.config.get("MAIL_USERNAME"),
                  recipients=[session['email']],
                  body="Thank you for signing up to our website. "
                       "Please find the confirmation code below and enter that on the confirmation page.\n\n"
                       "Confirmation Code: " +
                       session['code'])
    mail.send(msg)
    return redirect("/confirm", code=302)

@app.route('/confirm', methods=['GET', 'POST'])
def confirm_email():
    if request.method == ('POST'):
        cursor = mysql.get_db().cursor()
        code = request.form['code']
        if code == session['code']:
            sql_update_query = """UPDATE users u SET u.confirmed = %s WHERE u.username = %s """
            confirmed = "yes"
            inputData = (confirmed, session['user'])
            cursor.execute(sql_update_query, inputData)
            mysql.get_db().commit()
            flash("Your email has been verified. Thank you.", "success")
            return redirect('/', code=302)
        else:
            flash("The code you entered and the code sent to your email are not the same. Please retry!", "danger")
    return render_template('confirm.html')

@app.route('/home', methods = ['GET'])
def index():
    if "user" in session:
        user = {'username': session["user"]}
    else:
        user = {'username': 'This didnt work'}
    title = "Home"
    return render_template('index.html', title=title, user=user)

@app.route('/records', methods=['GET'])
def records():
    if "user" in session:
        user = {'username': session["user"]}
    else:
        user = {'username': 'This didnt work'}
    cursor = mysql.get_db().cursor()
    cursor.execute('SELECT * FROM tblCitiesImport')
    result = cursor.fetchall()
    return render_template('records.html', title='Records', user=user, cities=result)

@app.route('/teampage', methods=['GET'])
def teampage():
    teamPic_michael = os.path.join(app.config['UPLOAD_FOLDER'], 'BackgroundPic.jpg')
    teamPic_stanley = os.path.join(app.config['UPLOAD_FOLDER'], 'DSC_0928.jpg')
    return render_template('teampage.html', title='Team Page', michael=teamPic_michael, stanley=teamPic_stanley)

@app.route('/profile', methods=['GET'])
def profile():
    if session["user"] == os.environ['ADMIN_USER']:
        return render_template('admin-profile.html', title='Admin Profile', user=os.environ['ADMIN_USER'])
    else:
        if "user" in session:
            user = {'username': session["user"]}
        else:
            user = {'username': 'This didnt work'}
        cursor = mysql.get_db().cursor()
        cursor.execute('SELECT username, email FROM users WHERE username=%s', session["user"])
        result = cursor.fetchall()
        return render_template('profile-page.html', title='Profile Page', user=user, profile=result[0])

@app.route('/profile-edit', methods=['GET'])
def edit_profile_get():
    if "user" in session:
        user = {'username': session["user"]}
    else:
        user = {'username': 'This didnt work'}
    cursor = mysql.get_db().cursor()
    cursor.execute('SELECT username, email FROM users WHERE username=%s', session["user"])
    result = cursor.fetchall()
    return render_template('profile-edit.html', title='Edit Profile', user=user, profile=result[0])


@app.route('/profile-edit', methods=['POST'])
def edit_profile_post():
    cursor = mysql.get_db().cursor()
    inputData = (request.form.get('username'), request.form.get('email'), session["user"])
    sql_update_query = """UPDATE users u SET u.username = %s, u.email = %s WHERE u.username = %s """
    cursor.execute(sql_update_query, inputData)
    mysql.get_db().commit()
    cursor.execute('SELECT username FROM users WHERE username=%s', request.form.get('username'))
    new_username = cursor.fetchone()['username']
    session["user"] = new_username
    return redirect("/profile", code=302)


@app.route('/new-password', methods=['GET', 'POST'])
def new_pass():
    if "user" in session:
        user = {'username': session["user"]}
    else:
        user = {'username': 'This didnt work'}
    if request.method == ('POST'):
        cursor = mysql.get_db().cursor()
        hash_pass = generate_password_hash(str(request.form['password']), "sha256")
        inputData = (hash_pass, session["user"])
        sql_update_query = """UPDATE users u SET u.passwordHash = %s WHERE u.username = %s """
        cursor.execute(sql_update_query, inputData)
        mysql.get_db().commit()
        flash("You have successfully changed your password. Please log back in!", "info")
        return redirect("/logout", code=302)
    return render_template('password.html', title='Password Change', user=user)

@app.route('/view/<int:city_id>', methods=['GET'])
def record_view(city_id):
    cursor = mysql.get_db().cursor()
    cursor.execute('SELECT * FROM tblCitiesImport WHERE id=%s', city_id)
    result = cursor.fetchall()
    return render_template('view.html', title='View Form', city=result[0])


@app.route('/edit/<int:city_id>', methods=['GET'])
def form_edit_get(city_id):
    cursor = mysql.get_db().cursor()
    cursor.execute('SELECT * FROM tblCitiesImport WHERE id=%s', city_id)
    result = cursor.fetchall()
    return render_template('edit.html', title='Edit Form', city=result[0])


@app.route('/edit/<int:city_id>', methods=['POST'])
def form_update_post(city_id):
    cursor = mysql.get_db().cursor()
    inputData = (request.form.get('fldName'), request.form.get('fldLat'), request.form.get('fldLong'),
                 request.form.get('fldCountry'), request.form.get('fldAbbreviation'),
                 request.form.get('fldCapitalStatus'), request.form.get('fldPopulation'), city_id)
    sql_update_query = """UPDATE tblCitiesImport t SET t.fldName = %s, t.fldLat = %s, t.fldLong = %s, t.fldCountry = 
    %s, t.fldAbbreviation = %s, t.fldCapitalStatus = %s, t.fldPopulation = %s WHERE t.id = %s """
    cursor.execute(sql_update_query, inputData)
    mysql.get_db().commit()
    return redirect("/records", code=302)

@app.route('/cities/new', methods=['GET'])
def form_insert_get():
    return render_template('new.html', title='New City Form')


@app.route('/cities/new', methods=['POST'])
def form_insert_post():
    cursor = mysql.get_db().cursor()
    inputData = (request.form.get('fldName'), request.form.get('fldLat'), request.form.get('fldLong'),
                 request.form.get('fldCountry'), request.form.get('fldAbbreviation'),
                 request.form.get('fldCapitalStatus'), request.form.get('fldPopulation'))
    sql_insert_query = """INSERT INTO tblCitiesImport (fldName,fldLat,fldLong,fldCountry,fldAbbreviation,fldCapitalStatus,fldPopulation) VALUES (%s,%s, %s,%s, %s,%s, %s)"""
    cursor.execute(sql_insert_query, inputData)
    mysql.get_db().commit()
    return redirect("/records", code=302)


@app.route('/delete/<int:city_id>', methods=['POST'])
def form_delete_post(city_id):
    cursor = mysql.get_db().cursor()
    sql_delete_query = """DELETE FROM tblCitiesImport WHERE id = %s """
    cursor.execute(sql_delete_query, city_id)
    mysql.get_db().commit()
    return redirect("/records", code=302)



@app.route('/api/v1/cities', methods=['GET'])
def api_browse() -> str:
    cursor = mysql.get_db().cursor()
    cursor.execute('SELECT * FROM tblCitiesImport')
    result = cursor.fetchall()
    json_result = json.dumps(result);
    resp = Response(json_result, status=200, mimetype='application/json')
    return resp


@app.route('/api/v1/cities/<int:city_id>', methods=['GET'])
def api_retrieve(city_id) -> str:
    cursor = mysql.get_db().cursor()
    cursor.execute('SELECT * FROM tblCitiesImport WHERE id=%s', city_id)
    result = cursor.fetchall()
    json_result = json.dumps(result);
    resp = Response(json_result, status=200, mimetype='application/json')
    return resp


@app.route('/api/v1/cities/<int:city_id>', methods=['PUT'])
def api_edit(city_id) -> str:
    cursor = mysql.get_db().cursor()
    content = request.json
    inputData = (content['fldName'], content['fldLat'], content['fldLong'],
                 content['fldCountry'], content['fldAbbreviation'],
                 content['fldCapitalStatus'], content['fldPopulation'],city_id)
    sql_update_query = """UPDATE tblCitiesImport t SET t.fldName = %s, t.fldLat = %s, t.fldLong = %s, t.fldCountry = 
        %s, t.fldAbbreviation = %s, t.fldCapitalStatus = %s, t.fldPopulation = %s WHERE t.id = %s """
    cursor.execute(sql_update_query, inputData)
    mysql.get_db().commit()
    resp = Response(status=200, mimetype='application/json')
    return resp


@app.route('/api/v1/cities', methods=['POST'])
def api_add() -> str:

    content = request.json

    cursor = mysql.get_db().cursor()
    inputData = (content['fldName'], content['fldLat'], content['fldLong'],
                 content['fldCountry'], content['fldAbbreviation'],
                 content['fldCapitalStatus'], request.form.get('fldPopulation'))
    sql_insert_query = """INSERT INTO tblCitiesImport (fldName,fldLat,fldLong,fldCountry,fldAbbreviation,fldCapitalStatus,fldPopulation) VALUES (%s, %s,%s, %s,%s, %s,%s) """
    cursor.execute(sql_insert_query, inputData)
    mysql.get_db().commit()
    resp = Response(status=201, mimetype='application/json')
    return resp


@app.route('/api/v1/cities/<int:city_id>', methods=['DELETE'])
def api_delete(city_id) -> str:
    cursor = mysql.get_db().cursor()
    sql_delete_query = """DELETE FROM tblCitiesImport WHERE id = %s """
    cursor.execute(sql_delete_query, city_id)
    mysql.get_db().commit()
    resp = Response(status=200, mimetype='application/json')
    return resp


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)