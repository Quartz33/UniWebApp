import sys

from flask import Flask, render_template, request, redirect, url_for, flash, session, make_response
from flask_mysqldb import MySQL
from flask_bcrypt import Bcrypt

app = Flask('__name__')
bcrypt = Bcrypt(app)
app.secret_key = 'many random bytes'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'crudapplication'

mysql = MySQL(app)


@app.route('/')
def home():
    if 'username' in session:
        return render_template('home.html', username=session['username'], isAdmin=session['isAdmin'])
    else:
        return render_template('home.html')


@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor()
        cursor.execute(f"select username,password, isAdmin from tbl_users where username ='{username}'")
        user = cursor.fetchone()
        cursor.close()
        if user and password == user[1]:
            session['username'] = user[0]
            session['isAdmin'] = user[2]

            return redirect(url_for('home'))
        else:
            return render_template('login.html', error='Invalid username or password')
    else:
        return render_template('login.html')


@app.route('/logout')
def logout():
        session.pop('username', None )
        session.pop('isAdmin', None )
        return redirect(url_for('home'))

@app.route('/default')
def default():
    cur = mysql.connection.cursor()
    cur.execute("SELECT u.id, u.username, j.name AS job_name, u.firstName, u.surname, u.email, u.phone FROM tbl_users u INNER JOIN job j ON u.jobID = j.jobID;")
    data = cur.fetchall()
    cur.execute("SELECT job.name, job.jobID FROM job;")
    jobs = cur.fetchall()
    cur.close()
    return render_template('default.html', users=data, jobs=jobs)


@app.route('/insert', methods=['POST','GET'])
def insert():
    if request.method == "POST":
        flash("Data Inserted Successfully")
        firstName = request.form['firstName']
        username = request.form['username']
        surname = request.form['surname']
        password = request.form['password']
        email = request.form['email']
        phone = request.form['phone']
        job_name = request.form.get('job')
        jobid = request.form['job']
        flash('Job', jobid)
        # Hash the password
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        # Get the cursor
        cur = mysql.connection.cursor()

        cur.execute("SELECT jobID from job where name=%s", (job_name,))
        jobID = cur.fetchone()

        #If the job exists, proceed
        #if existing_job:
        #    job_id = existing_job[0]
        #else:
        #    flash("Job does not exist")
        #    return redirect(url_for('default'))

        # Insert the user into the 'users' table
        cur.execute("INSERT INTO tbl_users(username, firstName, surname, password, email, phone, jobID) VALUES (%s, %s, %s, %s, %s, %s, %s)", (username, firstName, surname, hashed_password, email, phone, '1'))
        mysql.connection.commit()

        # Close the cursor
        cur.close()

        return redirect(url_for('default'))


@app.route('/update',methods=['POST','GET'])
def update():

    if request.method == 'POST':
        id_data = request.form['id']
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        job = request.form['job']
        cur = mysql.connection.cursor()
        cur.execute("""
               UPDATE users
               SET name=%s, email=%s, phone=%s
               WHERE id=%s
            """, (name, email, phone, id_data, job))
        flash("Data Updated Successfully")
        mysql.connection.commit()
        return redirect(url_for('Index'))

if __name__ == '__main__':
    app.run(debug=True)