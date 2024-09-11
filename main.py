import os
import argon2
import random
import string
import requests
from urllib import parse
from functools import wraps
from flask_mysqldb import MySQL
from flask_session import Session
from urllib import request as requestt
from xml.etree.ElementTree import Element, SubElement, tostring
from flask import Flask, redirect, render_template, request, url_for, session, jsonify, Response

app = Flask(__name__)

app.secret_key = 'task_flow'

app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

app.config['MYSQL_HOST'] = "mysql"
app.config['MYSQL_USER'] = "webuser"
app.config['MYSQL_PASSWORD'] = "webpass"
app.config['MYSQL_DB'] = "di_internet_technologies_project"

mysql = MySQL(app)
ph = argon2.PasswordHasher()

def is_logged_in():
    return 'logged_in' in session

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_logged_in():
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    theme_mode = session.get('theme_mode', 'light')
    return render_template('index.html', theme_mode=theme_mode)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['Name']
        surname = request.form['Surname']
        username = request.form['Username']
        email = request.form['Email'].lower()
        password = request.form['password']
        key = request.form['Key']
        coockies = True  
        hashed_password = ph.hash(password)

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users (name, surname, username, email, password, notification_key, coockies) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                    (name, surname, username, email, hashed_password, key, coockies))
        
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
        cur.close()  

        if user:
            stored_password = user[4]  
            try:
                ph.verify(stored_password, password)
                
                session['user_id'] = user[0]
                session['logged_in'] = True
                session['username'] = user[2]
                
                session['theme_mode'] = 'dark' if user[6] else 'light' 
                print("Session details after login:", session)

                return redirect(url_for('home'))
            except argon2.exceptions.VerifyMismatchError:
                return render_template('login.html', error='Invalid email or password.')

        return render_template('login.html', error='Invalid email or password.')  
    
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
    return render_template('home.html', theme_mode=session.get('theme_mode', 'light'))

def send_notification(key, title, message):
    data = parse.urlencode({'key': key, 'title': title, 'msg': message, 'event': ''}).encode()
    req = requestt.Request("https://api.simplepush.io/send", data=data)
    requestt.urlopen(req)

@app.route('/submit_task', methods=['POST'])
@login_required
def submit_task():
    try:
        data = request.get_json()  
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        title = data.get('title')
        content = data.get('content')
        username = session.get('username')

        if not title or not content:
            return jsonify({'error': 'Title and content are required'}), 400

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO tasks (Title, Content, Status, username) VALUES (%s, %s, %s, %s)",
                    (title, content, 'todo', username))
        mysql.connection.commit()

        
        cur.execute("SELECT notification_key FROM users WHERE username = %s", (username,))
        user = cur.fetchone()
        cur.close()

        if user:
            key = user[0]
            send_notification(key, 'New Task Created', title)

        return jsonify({'success': True})

    except Exception as e:
        app.logger.error(f"Error in submit_task: {e}")
        return jsonify({'error': 'An error occurred while submitting the task'}), 500

@app.route('/tasks', methods=['GET'])
@login_required
def get_tasks():
    user_id = session['user_id']
    username = session['username']

    cur = mysql.connection.cursor()
    cur.execute(
        """
        SELECT Taskid, Title, Content, Status, CreatedAt, assigned_to, assigned, username
        FROM tasks
        WHERE username = %s OR assigned_to = %s AND assigned = %s
        ORDER BY CreatedAt DESC
        """, (username, username, 1)
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

@app.route('/update_task_status', methods=['POST'])
@login_required
def update_task_status():
    data = request.get_json()
    if data:
        task_id = data.get('task_id')
        new_status = data.get('status')

        cur = mysql.connection.cursor()
        cur.execute("UPDATE tasks SET Status = %s WHERE TaskID = %s", (new_status, task_id))
        mysql.connection.commit()
        cur.close()
        
        return jsonify({'success': True})
    return jsonify({'error': 'Invalid data'}), 400


@app.route('/search_tasks', methods=['GET'])
@login_required
def search_tasks():
    query = request.args.get('query', '')
    status = request.args.get('status', '')
    user_id = session['username']
    
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
    elif query == "":
        cur.execute(
            """
            SELECT Taskid, Title, Content, Status, CreatedAt, assigned_to, assigned, username
            FROM tasks 
            """, 
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
    old_username = session['username']  
    email = request.form.get('change-email')
    name = request.form.get('change-name')
    surname = request.form.get('change-surname')
    password = request.form.get('change-password')
    new_username = request.form.get('change-username')  

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
    
    if new_username:
        cur.execute("UPDATE users SET username = %s WHERE name = %s", (new_username, user_id))
        cur.execute("UPDATE tasks SET assigned_to = %s WHERE assigned_to = %s", (new_username, old_username))
        
        cur.execute("UPDATE tasks SET username = %s WHERE username = %s", (new_username, old_username))
        
        
        session['username'] = new_username
        session['user_id'] = user_id

    mysql.connection.commit()
    cur.close()

    return jsonify({'success': True})


@app.route('/delete_account', methods=['POST'])
@login_required
def delete_account():
    chars = string.ascii_letters + string.digits
    username = session.get('username')
    new_username = ''.join(random.choice(chars) for _ in range(4))


    if not username:
        app.logger.error('No username found in session.')
        return jsonify({'success': False, 'error': 'User not logged in'}), 400

    try:
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM users WHERE name = %s", (username,))
        cur.execute("UPDATE tasks SET username = %s WHERE username = %s", (new_username, username))
        cur.execute("UPDATE tasks SET assigned_to = %s WHERE assigned_to = %s", (new_username, username))

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
    user_id = session.get('username')
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
    
    xml_str = tostring(root, encoding='utf-8', method='xml')
    
    response = Response(xml_str, content_type='application/xml')
    response.headers['Content-Disposition'] = 'attachment; filename=user_data.xml'
    
    return response

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
    title = data.get('title')

    cur = mysql.connection.cursor()
    cur.execute("SELECT username FROM users WHERE username = %s", (username,))
    user = cur.fetchone()
    if not user:
        cur.close()
        return jsonify({'success': False, 'error': 'Invalid username'}), 400

    try:
        cur.execute(
            "UPDATE tasks SET assigned_to = %s, assigned = %s WHERE TaskID = %s", (username, 1, task_id))
        mysql.connection.commit()

        cur.execute("SELECT notification_key FROM users WHERE username = %s", (username,))
        assigned_user = cur.fetchone()

        if assigned_user:
            key = assigned_user[0]
            result = send_notification(key, 'A task Assigned to you', title)
            # if result is None:
            #     return jsonify({'success': False, 'error': 'Notification failed'}), 500
            
    except Exception as e:
        mysql.connection.rollback()
        cur.close()
        return jsonify({'success': False, 'error': str(e)}), 500
    
    cur.close()
    return jsonify({'success': True})


@app.route('/toggle_theme', methods=['POST'])
@login_required
def toggle_theme():
    user_id = session['user_id']
    current_mode = session.get('theme_mode', 'light')
    
    new_mode = 'dark' if current_mode == 'light' else 'light'
    session['theme_mode'] = new_mode

    cur = mysql.connection.cursor()
    cur.execute("UPDATE users SET theme_mode = %s WHERE id = %s", (new_mode == 'dark', user_id))
    mysql.connection.commit()
    cur.close()

    return jsonify({'success': True, 'theme_mode': new_mode})


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
    app.debug = False
    app.run()
