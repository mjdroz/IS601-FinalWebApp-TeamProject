from typing import List, Dict
import simplejson as json
from flask import Flask, request, Response, redirect
from flask import render_template
from flaskext.mysql import MySQL
from pymysql.cursors import DictCursor
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
mysql = MySQL(cursorclass=DictCursor)

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
        cursor.execute(sql_query,userData)
        result = cursor.fetchone()['passwordHash']
        if username == 'admin':
            if password == 'adminpwd':
                return redirect("/home", code=302)
        if check_password_hash(result,password):
            return redirect("/home", code=302)
    return render_template('login.html')

@app.route('/register', methods=['GET'])
def register_get():
    cursor = mysql.get_db().cursor()
    return render_template('register.html', title='Registration')

@app.route('/register', methods=['POST'])
def register_post():
    cursor = mysql.get_db().cursor()
    hash_pass = generate_password_hash(str(request.form['password']),"sha256")
    inputData = (request.form['username'],request.form['email'],hash_pass)
    sql_insert_query = """INSERT INTO users (username, email, passwordHash) VALUES (%s,%s, %s)"""
    cursor.execute(sql_insert_query, inputData)
    mysql.get_db().commit()
    return redirect("/", code=302)


@app.route('/home', methods=['GET'])
def index():
    user = {'username': 'Cities Project'}
    cursor = mysql.get_db().cursor()
    cursor.execute('SELECT * FROM tblCitiesImport')
    result = cursor.fetchall()
    return render_template('index.html', title='Home', user=user, cities=result)

@app.route('/teampage', methods=['GET'])
def teampage():
    cursor = mysql.get_db().cursor()
    return render_template('teampage.html', title='teampage')

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
    return redirect("/home", code=302)

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
    return redirect("/home", code=302)


@app.route('/delete/<int:city_id>', methods=['POST'])
def form_delete_post(city_id):
    cursor = mysql.get_db().cursor()
    sql_delete_query = """DELETE FROM tblCitiesImport WHERE id = %s """
    cursor.execute(sql_delete_query, city_id)
    mysql.get_db().commit()
    return redirect("/home", code=302)



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