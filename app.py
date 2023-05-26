from flask import Flask, render_template, request, redirect, url_for, session, flash
import psycopg2
import re

app = Flask(__name__)
app.config['SECRET_KEY'] = 'thisissecret'

conn = psycopg2.connect(
    "postgres://accounts:BPqY8JN9DAufCtYdBDbi3qo815EKdqwi@dpg-choafmg2qv295pruiqe0-a.oregon-postgres.render.com/alchemy_zyif")


# http://localhost:5000/pythonlogin/ - the following will be our login page, which will use both GET and POST requests
@app.route('/')
@app.route('/pythonlogin/', methods=['GET', 'POST'])
def login():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        # Check if account exists using MySQL
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM accounts WHERE username = %s AND password = %s', (username, password,))
        account = cursor.fetchone()
        # If account exists in accounts table in out database
        if account:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            # session['id'] = account['id']
            # session['username'] = account['username']
            session['id'] = account[0]
            session['username'] = account[1]
            # Redirect to home page
            return redirect(url_for('home'))
        else:
            # Account doesn't exist or username/password incorrect
            msg = 'Incorrect username/password!'
    return render_template('index.html', msg='')


# http://localhost:5000/python/logout - this will be the logout page
@app.route('/pythonlogin/logout')
def logout():
    # Remove session data, this will log the user out
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    # Redirect to login page
    return redirect(url_for('login'))


# http://localhost:5000/pythinlogin/register - this will be the registration page, we need to use both GET and POST requests
@app.route('/pythonlogin/register', methods=['GET', 'POST'])
def register():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        # Check if account exists using MySQL
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM accounts WHERE username = %s', (username,))
        account = cursor.fetchone()
        # If account exists show error and validation checks
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
            # Account doesn't exist and the form data is valid, now insert new account into accounts table
            cursor.execute('INSERT INTO accounts(username, password, email) VALUES ( %s, %s, %s)',
                           (username, password, email,))
            conn.commit()
            msg = 'You have successfully registered!'
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    # Show registration form with message (if any)
    return render_template('register.html', msg=msg)


# http://localhost:5000/pythinlogin/home - this will be the home page, only accessible for loggedin users
@app.route('/pythonlogin/home')
def home():
    # Check if user is loggedin
    if 'loggedin' in session:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM blog')
        post = cursor.fetchall()
        # User is loggedin show them the home page
        return render_template('home.html', username=session['username'], post=post)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))


# http://localhost:5000/pythinlogin/profile - this will be the profile page, only accessible for loggedin users
@app.route('/pythonlogin/profile')
def profile():
    # Check if user is loggedin
    if 'loggedin' in session:
        # We need all the account info for the user so we can display it on the profile page
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM accounts WHERE username = %s', (session['id'],))
        account = cursor.fetchone()
        # Show the profile page with account info
        return render_template('profile.html', account=account)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))


@app.route('/addpost', methods=['POST', 'GET'])
def addpost():
    if 'loggedin' in session and request.method == 'POST':
        print(session['id'])
        title = request.form.get('title')
        content = request.form.get('content')
        author = request.form.get('author')
        date = request.form.get('date')
        imglink = request.form.get('imglink')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO blog(title,content,author,datetime,imglink) VALUES (%s ,%s, %s, %s,%s)',
                       (title, content, author, date, imglink))
        conn.commit()
        flash('Created Successfully', None)
        return redirect(url_for('home'))
    return render_template('addpost.html')


@app.route('/editpost/<int:id>', methods=['POST', 'GET'])
def editpost(id):
    cursor = conn.cursor()
    cursor.execute("SELECT*FROM blog where id=%s", (id,))
    editdata = cursor.fetchone()
    return render_template('editpost.html', post=editdata)


@app.route('/delete/<int:id>', methods=['POST', 'GET'])
def deletepost(id):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM blog where id=%s", (id,))
    conn.commit()
    return redirect(url_for('home'))


@app.route('/update/<int:id>', methods=['POST', 'GET'])
def updatepost(id):
    title = request.form.get('title')
    content = request.form.get('content')
    author = request.form.get('author')
    imglink = request.form.get('imglink')
    cursor = conn.cursor()
    cursor.execute("UPDATE blog SET title=%s,content=%s,author=%s,imglink=%s WHERE id=%s",
                   (title, content, author, imglink, id))
    conn.commit()
    return redirect(url_for('home'))


@app.route('/view/<int:id>', methods=['POST', 'GET'])
def view(id):
    cursor = conn.cursor()
    cursor.execute("SELECT*FROM blog where id=%s", (id,))
    post = cursor.fetchone()
    return render_template('view.html', post=post)


if __name__ == '__main__':
    app.run(debug=True)
