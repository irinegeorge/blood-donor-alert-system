import pymysql

from flask import Flask, render_template, request, redirect, session

from flask_bcrypt import Bcrypt

app = Flask(__name__)

app.secret_key = "blooddonorsecret"

bcrypt = Bcrypt(app)

def get_db_connection():

    return pymysql.connect(
        host='localhost',
        user='bloodadmin',
        password='blood123',
        database='blood_donor_alert'
    )

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register', methods=['GET','POST'])
def register():

    if request.method == 'POST':

        name = request.form['name']
        blood = request.form['blood']
        location = request.form['location']
        phone = request.form['phone']
        email = request.form['email']
        password = request.form['password']

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        connection = get_db_connection()
        cur = connection.cursor()

        cur.execute("""
        INSERT INTO users(name,blood_group,location,phone,email,password)
        VALUES(%s,%s,%s,%s,%s,%s)
        """,(name,blood,location,phone,email,hashed_password))

        connection.commit()
        connection.close()

        return redirect('/login')

    return render_template('register.html')

@app.route('/login', methods=['GET','POST'])
def login():

    if request.method == 'POST':

        email = request.form['email']
        password = request.form['password']

        connection = get_db_connection()
        cur = connection.cursor()

        cur.execute("SELECT * FROM users WHERE email=%s",(email,))

        user = cur.fetchone()

        connection.close()

        if user:

            if bcrypt.check_password_hash(user[6], password):

                session['user'] = user[1]

                return redirect('/dashboard')

        return "Invalid Login"

    return render_template('login.html')


@app.route('/dashboard')
def dashboard():

    connection = get_db_connection()

    cur = connection.cursor()

    cur.execute("SELECT * FROM users")

    donors = cur.fetchall()

    cur.execute("SELECT COUNT(*) FROM users")

    total_donors = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM emergency_requests")

    total_requests = cur.fetchone()[0]

    connection.close()

    return render_template(
        'dashboard.html',
        donors=donors,
        total_donors=total_donors,
        total_requests=total_requests
    )

@app.route('/search', methods=['GET','POST'])
def search():

    donors = []

    if request.method == 'POST':

        blood = request.form['blood']

        connection = get_db_connection()

        cur = connection.cursor()

        cur.execute("SELECT * FROM users WHERE blood_group=%s",(blood,))

        donors = cur.fetchall()

        connection.close()

    return render_template('search.html', donors=donors)

@app.route('/emergency', methods=['GET','POST'])
def emergency():

    if request.method == 'POST':

        patient = request.form['patient']
        hospital = request.form['hospital']
        blood = request.form['blood']
        contact = request.form['contact']

        connection = get_db_connection()

        cur = connection.cursor()

        cur.execute("""
        INSERT INTO emergency_requests(patient_name,hospital,blood_group,contact)
        VALUES(%s,%s,%s,%s)
        """, (patient, hospital, blood, contact))

        connection.commit()

        connection.close()

        return "Emergency Request Submitted Successfully"

    return render_template('emergency.html')

@app.route('/logout')
def logout():

    session.clear()

    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)