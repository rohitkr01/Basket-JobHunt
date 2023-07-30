from flask import Flask, render_template, request, jsonify,redirect, url_for, session

from chat import get_response

from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
  
  
app = Flask(__name__)
  
  
app.secret_key = 'xyzsdfg'
  
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '@Rohit$4331&'
app.config['MYSQL_DB'] = 'user-system'
  
mysql = MySQL(app)
  

@app.route('/')
def home():
    if 'loggedin' in session:
        return render_template('user.html')
    return render_template('home.html')


@app.route('/login', methods =['GET', 'POST'])
def login():
    if 'loggedin' in session:
        return redirect(url_for('home'))
    else:
        mesage = ''
        if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
            email = request.form['email']
            password = request.form['password']
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM user WHERE email = % s AND password = % s', (email, password, ))
            user = cursor.fetchone()
            if user:
                session['loggedin'] = True
                session['userid'] = user['userid']
                session['name'] = user['name']
                session['email'] = user['email']
                mesage = 'Logged in successfully !'

                return redirect(url_for('home'))
            else:
                mesage = 'Please enter correct email / password !'
        return render_template('login.html', mesage = mesage)
  
@app.route('/logout')
def logout():
    if 'loggedin' in session:
        session.pop('loggedin', None)
        session.pop('userid', None)
        session.pop('email', None)
        return redirect(url_for('login'))
    return redirect(url_for('home'))

  
@app.route('/register', methods =['GET', 'POST'])
def register():
    if 'loggedin' in session:
        return redirect(url_for('home'))
    else:
        mesage = ''
        if request.method == 'POST' and 'name' in request.form and 'password' in request.form and 'email' in request.form :
            userName = request.form['name']
            password = request.form['password']
            email = request.form['email']
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM user WHERE email = % s', (email, ))
            account = cursor.fetchone()
            if account:
                mesage = 'Account already exists !'
            elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
                mesage = 'Invalid email address !'
            elif not userName or not password or not email:
                mesage = 'Please fill out the form !'
            else:
                cursor.execute('INSERT INTO user VALUES (NULL, % s, % s, % s)', (userName, email, password, ))
                mysql.connection.commit()
                mesage = 'You have successfully registered !'
                return redirect(url_for('login'))
        elif request.method == 'POST':
            mesage = 'Please fill out the form !'
        return render_template('register.html', mesage = mesage)




@app.route('/jobs')
def all_jobs():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM job')
        jobs = cursor.fetchall()
        return render_template('jobs.html', jobs=jobs)
    return redirect(url_for('login'))



# Chatbot response data fetching
@app.post("/predict")
def predict():
    text = request.get_json().get("message")
    response = get_response(text)
    message = {"answer": response}
    return jsonify(message)

# ending of chatbot response data fetching

    
if __name__ == "__main__":
    app.run(debug=True)