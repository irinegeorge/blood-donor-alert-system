from flask import Flask, render_template, request, redirect, session
import pymysql

app = Flask(__name__)

app.secret_key = 'blooddonor'

# MYSQL CONNECTION
connection = pymysql.connect(
    host='localhost',
    user='root',
    password='irine4131',
    database='blooddonor'
)

# HOME PAGE
@app.route('/')
def home():
    return render_template('index.html')

# REGISTER PAGE
@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        blood_group = request.form['blood_group']
        city = request.form['city']
        phone = request.form['phone']
        availability = request.form['availability']

        cursor = connection.cursor()

        sql = """
        INSERT INTO users
        (name, email, password, blood_group, city, phone, availability)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """

        values = (
            name,
            email,
            password,
            blood_group,
            city,
            phone,
            availability
        )

        cursor.execute(sql, values)

        connection.commit()

        cursor.close()

        return redirect('/login')

    return render_template('register.html')

# LOGIN PAGE
@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        email = request.form['email']
        password = request.form['password']

        cursor = connection.cursor()

        sql = """
        SELECT * FROM users
        WHERE email=%s AND password=%s
        """

        values = (email, password)

        cursor.execute(sql, values)

        user = cursor.fetchone()

        cursor.close()

        if user:
            session['user'] = email
            return redirect('/dashboard')

        else:
            return 'Invalid Email or Password'

    return render_template('login.html')

# DASHBOARD
@app.route('/dashboard')
def dashboard():

    if 'user' in session:
        return render_template('dashboard.html')

    return redirect('/login')

# BLOOD REQUEST PAGE
@app.route('/request', methods=['GET', 'POST'])
def request_blood():

    if request.method == 'POST':

        patient_name = request.form['patient_name']
        blood_group = request.form['blood_group']
        hospital = request.form['hospital']
        city = request.form['city']
        contact = request.form['contact']
        urgency = request.form['urgency']

        cursor = connection.cursor()

        sql = """
        INSERT INTO emergency_request
        (patient_name, blood_group, hospital, city, contact, urgency)
        VALUES (%s, %s, %s, %s, %s, %s)
        """

        values = (
            patient_name,
            blood_group,
            hospital,
            city,
            contact,
            urgency
        )

        cursor.execute(sql, values)

        connection.commit()

        cursor.close()

        return '''
        <script>
            alert("Blood Request Submitted Successfully");
            window.location="/dashboard";
        </script>
        '''

    return render_template('request.html')

# SEARCH DONOR
@app.route('/search', methods=['GET', 'POST'])
def search():

    donors = []

    if request.method == 'POST':

        blood_group = request.form['blood_group']

        cursor = connection.cursor()

        sql = "SELECT * FROM users WHERE blood_group=%s"

        cursor.execute(sql, (blood_group,))

        donors = cursor.fetchall()

        cursor.close()

    return render_template('search.html', donors=donors)


# ADMIN PANEL
@app.route('/admin')
def admin():

    cursor = connection.cursor()

    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()

    cursor.execute("SELECT * FROM emergency_request")
    requests = cursor.fetchall()

    cursor.close()

    return render_template(
        'admin.html',
        users=users,
        requests=requests
    )


@app.route('/logout')
def logout():

    session.pop('user', None)

    return redirect('/login')

# RUN APPLICATION
if __name__ == '__main__':
    app.run(debug=True)