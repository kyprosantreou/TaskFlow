from flask import Flask, redirect, render_template, request, url_for, session, jsonify,Response
from flask_mysqldb import MySQL
from flask_session import Session
import argon2
from functools import wraps
import random
import string
from xml.etree.ElementTree import Element, SubElement, tostring, ElementTree
import io
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Set the secret key to enable session usage
app.secret_key = 'task_flow'

# Configure Flask-Session to use filesystem (You can also configure it to use other options like Redis)
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = os.getenv("user")
app.config['MYSQL_PASSWORD'] = os.getenv("password")
app.config['MYSQL_DB'] = 'testing'

mysql = MySQL(app)
ph = argon2.PasswordHasher()

def is_logged_in():
    return 'logged_in' in session

# Define a decorator function to check if the user is logged in
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_logged_in():
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    print(session)
    theme_mode = session.get('theme_mode', 'light')
    return render_template('index.html', theme_mode=theme_mode)

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        name = request.form['Name']
        surname = request.form['Surname']
        username = request.form['Username']
        email = request.form['Email'].lower()
        password = request.form['password']
        hashed_password = ph.hash(password)
        cur = mysql.connection.cursor()

        cur.execute("INSERT INTO users (name, surname, username, email, password) VALUES (%s, %s, %s, %s, %s)",
                    (name, surname, username, email, hashed_password))
        
        mysql.connection.commit()
        cur.close()

        return redirect(url_for('login'))
   
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['Email'].lower()
        password = request.form['password']
        cur = mysql.connection.cursor()

        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cur.fetchone()

        if user:
            stored_password = user[4]  
            try:
                ph.verify(stored_password, password)
                
                session['user_id'] = user[0]
                session['logged_in'] = True
                
                session['theme_mode'] = request.form.get('theme_mode', 'light')

                return render_template('home.html')
            except argon2.exceptions.VerifyMismatchError:
                return render_template('login.html', error='Invalid email or password.')

        cur.close()

    return render_template('login.html')

@app.route('/logout', methods=['POST'])
@login_required
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/Templates/Profile.html')
@login_required
def profile():
    return render_template('Profile.html')

@app.route('/Templates/index.html')
@login_required
def about():
    return render_template('index.html')

@app.route('/Templates/home.html')
@login_required
def home():
    print(session)
    return render_template('home.html')

@app.route('/submit_task', methods=['POST'])
@login_required
def submit_task():
    data = request.get_json()
    if data:
        title = data.get('title')
        content = data.get('content')
        user_id = session['user_id']
        
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO tasks (Title, Content, Status, username) VALUES (%s, %s, %s, %s)",
                    (title, content, 'todo', user_id))
        mysql.connection.commit()
        cur.close()

        return jsonify({'success': True})
    return jsonify({'error': 'Invalid data'}), 400

@app.route('/tasks', methods=['GET'])
@login_required
def get_tasks():
    user_id = session['user_id']
    cur = mysql.connection.cursor()
    cur.execute(
        """
        SELECT Taskid, Title, Content, Status, CreatedAt, assigned_to, assigned, username
        FROM tasks
        WHERE username = %s OR assigned_to = %s AND assigned = %s
        ORDER BY CreatedAt DESC
        """, (user_id, user_id, 1)
    )

    tasks = cur.fetchall()
    cur.close()

    task_list = []
    for task in tasks:
        task_list.append({
            'id': task[0],
            'title': task[1],
            'content': task[2],
            'status': task[3],
            'created_at': task[4].strftime("%Y-%m-%d %H:%M:%S"),
            'assigned_to': task[5],
            'assigned': task[6],
            'username': task[7]
        })

    return jsonify(task_list)

@app.route('/search_tasks', methods=['GET'])
@login_required
def search_tasks():
    query = request.args.get('query', '')
    status = request.args.get('status', '')
    user_id = session['user_id']
    
    cur = mysql.connection.cursor()
    
    if query and status:
        cur.execute("""
            SELECT Taskid, Title, Content, Status, CreatedAt, assigned_to, assigned, username
            FROM tasks
            WHERE (Title LIKE %s OR Status = %s) AND (username = %s OR assigned_to = %s AND assigned = %s)
            ORDER BY CreatedAt DESC
        """, (f'%{query}%', status, user_id, user_id, 1))
    elif query:
        cur.execute("""
            SELECT Taskid, Title, Content, Status, CreatedAt, assigned_to, assigned, username
            FROM tasks
            WHERE Title LIKE %s AND (username = %s OR assigned_to = %s AND assigned = %s)
            ORDER BY CreatedAt DESC
        """, (f'%{query}%', user_id, user_id, 1))
    elif status:
        cur.execute("""
            SELECT Taskid, Title, Content, Status, CreatedAt, assigned_to, assigned, username
            FROM tasks
            WHERE Status = %s AND (username = %s OR assigned_to = %s AND assigned = %s)
            ORDER BY CreatedAt DESC
        """, (status, user_id, user_id, 1))
    elif query == "" :
        cur.execute(
            """
            SELECT Taskid, Title, Content, Status, CreatedAt, assigned_to, assigned, username
            FROM tasks
            WHERE username = %s OR assigned_to = %s AND assigned = %s
            ORDER BY CreatedAt DESC
            """, (user_id, user_id, 1)
        )
    else:
        return jsonify({'error': 'No search parameters provided'}), 400

    tasks = cur.fetchall()
    cur.close()

    task_list = []
    for task in tasks:
        task_list.append({
            'id': task[0],
            'title': task[1],
            'content': task[2],
            'status': task[3],
            'created_at': task[4].strftime("%Y-%m-%d %H:%M:%S"),
            'assigned_to': task[5],
            'assigned': task[6],
            'username': task[7]
        })

    return jsonify(task_list)

@app.route('/update_account', methods=['POST'])
@login_required
def update_account():
    user_id = session['user_id']
    email = request.form.get('change-email')
    name = request.form.get('change-name')
    surname = request.form.get('change-surname')
    password = request.form.get('change-password')
    username = request.form.get('change-username')

    cur = mysql.connection.cursor()
    
    if email:
        cur.execute("UPDATE users SET email = %s WHERE name = %s", (email, user_id))
    
    if name:
        cur.execute("UPDATE users SET name = %s WHERE name = %s", (name, user_id))
    
    if surname:
        cur.execute("UPDATE users SET surname = %s WHERE name = %s", (surname, user_id))
    
    if password:
        hashed_password = ph.hash(password)
        cur.execute("UPDATE users SET password = %s WHERE name = %s", (hashed_password, user_id))
    
    if username:
        cur.execute("UPDATE users SET username = %s WHERE name = %s", (username, user_id))
    
    mysql.connection.commit()
    cur.close()

    return jsonify({'success': True})

@app.route('/delete_account', methods=['POST'])
@login_required
def delete_account():
    chars = string.ascii_letters + string.digits
    username = session.get('user_id')
    new_username = ''.join(random.choice(chars) for _ in range(4))


    if not username:
        app.logger.error('No username found in session.')
        return jsonify({'success': False, 'error': 'User not logged in'}), 400

    try:
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM users WHERE name = %s", (username,))
        cur.execute("UPDATE tasks SET username = %s WHERE username = %s", (new_username, username))
        mysql.connection.commit()
        cur.close()
        
        session.clear()
        app.logger.info(f'User {username} deleted successfully.')
        
        return jsonify({'success': True})
    except Exception as e:
        app.logger.error(f"Error deleting user {username}: {e}")
        return jsonify({'success': False, 'error': 'An error occurred'}), 500

@app.route('/user_data', methods=['POST'])
@login_required
def download_data():
    user_id = session.get('user_id')
    cur = mysql.connection.cursor()
    cur.execute(
        """
        SELECT Taskid, Title, Content, Status, CreatedAt, assigned_to, assigned, username
        FROM tasks
        WHERE username = %s OR assigned_to = %s AND assigned = %s
        ORDER BY CreatedAt DESC
        """, (user_id, user_id, 1)
    )

    tasks = cur.fetchall()
    cur.close()

    # Create XML structure
    root = Element('Tasks')
    
    for task in tasks:
        task_elem = SubElement(root, 'Task')
        SubElement(task_elem, 'ID').text = str(task[0])
        SubElement(task_elem, 'Title').text = task[1]
        SubElement(task_elem, 'Content').text = task[2]
        SubElement(task_elem, 'Status').text = task[3]
        SubElement(task_elem, 'CreatedAt').text = task[4].strftime("%Y-%m-%d %H:%M:%S")
        SubElement(task_elem, 'AssignedTo').text = task[5]
        SubElement(task_elem, 'Assigned').text = str(task[6])
        SubElement(task_elem, 'Username').text = task[7]
    
    # Convert XML to string
    xml_str = tostring(root, encoding='utf-8', method='xml')
    
    # Create a response object
    response = Response(xml_str, content_type='application/xml')
    response.headers['Content-Disposition'] = 'attachment; filename=user_data.xml'
    
    return response


@app.route('/update_task_status', methods=['POST'])
def update_task_status():
    data = request.json
    task_id = data.get('task_id')
    new_status = data.get('status')
    print(f"Updating task {task_id} to status {new_status}")  # Debugging line

    # Ensure status is a valid value
    if new_status not in ['todo', 'inProgress', 'done']:
        return jsonify({'success': False, 'error': 'Invalid status value'})

    # Update the database
    cur = mysql.connection.cursor()
    cur.execute("UPDATE tasks SET Status = %s WHERE Taskid = %s", (new_status, task_id))
    mysql.connection.commit()
    cur.close()

    return jsonify({'success': True})

@app.route('/edit_task', methods=['POST'])
@login_required
def edit_task():
    data = request.get_json()
    if data:
        task_id = data.get('task_id')
        new_title = data.get('title')
        new_content = data.get('content')
        
        cur = mysql.connection.cursor()
        cur.execute("UPDATE tasks SET Title = %s, Content = %s WHERE TaskID = %s", (new_title, new_content, task_id))
        mysql.connection.commit()
        cur.close()
        
        return jsonify({'success': True})
    return jsonify({'error': 'Invalid data'}), 400


@app.route('/delete_task', methods=['POST'])
@login_required
def delete_task():
    data = request.get_json()
    if data:
        task_id = data.get('task_id')
        
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM tasks WHERE TaskID = %s", (task_id,))
        mysql.connection.commit()
        cur.close()
        
        return jsonify({'success': True})
    return jsonify({'error': 'Invalid data'}), 400

@app.route('/assign_to', methods=['POST'])
@login_required
def assign_to():
    data = request.json
    task_id = data.get('task_id')
    username = data.get('username')

    # Validate username
    cur = mysql.connection.cursor()
    cur.execute("SELECT username FROM users WHERE username = %s", (username,))
    user = cur.fetchone()
    if not user:
        cur.close()
        return jsonify({'success': False, 'error': 'Invalid username'}), 400

    # Update the database
    try:
        cur.execute(
            "UPDATE tasks SET assigned_to = %s, assigned = %s WHERE TaskID = %s",(username, 1, task_id))
        mysql.connection.commit()
    except Exception as e:
        mysql.connection.rollback()
        cur.close()
        return jsonify({'success': False, 'error': str(e)}), 500
    
    cur.close()
    return jsonify({'success': True})

@app.route('/search_users', methods=['GET'])
@login_required
def search_users():
    query = request.args.get('query', '')
    cur = mysql.connection.cursor()
    cur.execute("SELECT username FROM users WHERE username LIKE %s", (f'%{query}%',))
    users = cur.fetchall()
    cur.close()
    return jsonify([user[0] for user in users])

if __name__ == '__main__':
    app.debug = True
    app.run()
