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

#Establishing database connection
app.config['MYSQL_HOST'] = "mysql"
app.config['MYSQL_USER'] = "webuser"
app.config['MYSQL_PASSWORD'] = "webpass"
app.config['MYSQL_DB'] = "di_internet_technologies_project"

# Initialize MySQL connection
mysql = MySQL(app)

# Initialize Argon2 Password Hasher for password security
ph = argon2.PasswordHasher()

# Check if the user is logged in by verifying the session
def is_logged_in():
    return 'logged_in' in session

# Wrapper to enforce login requirements on routes
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_logged_in():
            # Redirect to login if not authenticated
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Route for index/info page
@app.route('/')
def index():
    theme_mode = session.get('theme_mode', 'light')
    return render_template('index.html', theme_mode=theme_mode)

# Route for user registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Get form data from request
        name = request.form['Name']
        surname = request.form['Surname']
        username = request.form['Username']
        email = request.form['Email'].lower()
        password = request.form['password']
        key = request.form['Key']
        coockies = True 
        # Hash the password using Argon2
        hashed_password = ph.hash(password)

        # Insert new user data into the database
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users (name, surname, username, email, password, notification_key, coockies) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                    (name, surname, username, email, hashed_password, key, coockies))
        
        # Commit the transaction
        mysql.connection.commit()
        cur.close()

        # Redirect to login page after registration
        return redirect(url_for('login'))
   
    return render_template('register.html')

# Route for user login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['Email'].lower()
        # Get password from form
        password = request.form['password']

        # Retrieve user info from the database based on email
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cur.fetchone()
        cur.close()  

        if user:
            # Get the stored hashed password
            stored_password = user[4]  
            try:
                # Verify the entered password with the stored one
                ph.verify(stored_password, password)
                
                # Set session variables for the logged-in user
                session['user_id'] = user[0]
                session['logged_in'] = True
                session['username'] = user[2]

                # Set theme mode based on user's preference in the database
                session['theme_mode'] = 'dark' if user[6] else 'light' 
                print("Session details after login:", session)

                # Redirect to home page
                return redirect(url_for('home'))
            except argon2.exceptions.VerifyMismatchError:
                # If password verification fails, display error message
                return render_template('login.html', error='Invalid email or password.')

        return render_template('login.html', error='Invalid email or password.')  
    
    return render_template('login.html')

# Route for user logout
@app.route('/logout', methods=['POST'])
# Requires login
@login_required
def logout():
    # Clear session data
    session.clear()
    # Redirect to home page
    return redirect(url_for('index'))

# Route for user profile page 
@app.route('/Templates/Profile.html')
# Requires login
@login_required
def profile():
    return render_template('Profile.html')

# Route for home page
@app.route('/Templates/index.html')
@login_required
def about():
    return render_template('index.html')

# Route for home page
@app.route('/Templates/home.html')
@login_required
def home():
    return render_template('home.html', theme_mode=session.get('theme_mode', 'light'))

# Function to send notifications using SimplePush API
def send_notification(key, title, message):
    data = parse.urlencode({'key': key, 'title': title, 'msg': message, 'event': ''}).encode()
    req = requestt.Request("https://api.simplepush.io/send", data=data)
    requestt.urlopen(req)

# Route to submit a task
@app.route('/submit_task', methods=['POST'])
@login_required
def submit_task():
    try:
        # Get task data from request
        data = request.get_json()  
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        # Extract task details from the data
        title = data.get('title')
        content = data.get('content')
        username = session.get('username')

        if not title or not content:
            return jsonify({'error': 'Title and content are required'}), 400
        # Insert the task into the tasks table
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO tasks (Title, Content, Status, username) VALUES (%s, %s, %s, %s)",
                    (title, content, 'todo', username))
        mysql.connection.commit()

        # Send notification if task is successfully created
        cur.execute("SELECT notification_key FROM users WHERE username = %s", (username,))
        user = cur.fetchone()
        cur.close()

        # Notify the user
        if user:
            key = user[0]
            send_notification(key, 'New Task Created', title)

        return jsonify({'success': True})

    except Exception as e:
        app.logger.error(f"Error in submit_task: {e}")
        return jsonify({'error': 'An error occurred while submitting the task'}), 500

# Route to retrieve all tasks
@app.route('/tasks', methods=['GET'])
@login_required
def get_tasks():
    user_id = session['user_id']
    username = session['username']

    # Retrieve tasks for the user or tasks assigned to them
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

    # Create a list of task dictionaries
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
    # Return tasks as JSON response
    return jsonify(task_list)

# Route to update task status
@app.route('/update_task_status', methods=['POST'])
@login_required
def update_task_status():
    data = request.get_json()
    if data:
        task_id = data.get('task_id')
        new_status = data.get('status')

        # Update task status in the database
        cur = mysql.connection.cursor()
        cur.execute("UPDATE tasks SET Status = %s WHERE TaskID = %s", (new_status, task_id))
        mysql.connection.commit()
        cur.close()
        
        return jsonify({'success': True})
    return jsonify({'error': 'Invalid data'}), 400

# Route to search tasks
@app.route('/search_tasks', methods=['GET'])
@login_required
def search_tasks():
    # Get search query
    query = request.args.get('query', '')

    # Get task status filter
    status = request.args.get('status', '')
    user_id = session['username']
    
    cur = mysql.connection.cursor()
    
    # Perform search query based on user input (query and/or status)
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

    # Create task list for JSON response
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

# Route for updating user account information
@app.route('/update_account', methods=['POST'])
@login_required  # This route requires the user to be logged in
def update_account():
    # Getting user details from the session
    user_id = session['user_id']  # Retrieve user ID from session
    old_username = session['username']  # Retrieve current username from session
    
    # Getting updated information from the form
    email = request.form.get('change-email')  # New email from form
    name = request.form.get('change-name')  # New name from form
    surname = request.form.get('change-surname')  # New surname from form
    password = request.form.get('change-password')  # New password from form
    new_username = request.form.get('change-username')  # New username from form

    # Establish a cursor to interact with the database
    cur = mysql.connection.cursor()
    
    # If the user provided a new email, update the email in the database
    if email:
        cur.execute("UPDATE users SET email = %s WHERE name = %s", (email, user_id))
    
    # If the user provided a new name, update the name in the database
    if name:
        cur.execute("UPDATE users SET name = %s WHERE name = %s", (name, user_id))
    
    # If the user provided a new surname, update the surname in the database
    if surname:
        cur.execute("UPDATE users SET surname = %s WHERE name = %s", (surname, user_id))
    
    # If the user provided a new password, hash it and update it in the database
    if password:
        hashed_password = ph.hash(password)  # Hash the new password
        cur.execute("UPDATE users SET password = %s WHERE name = %s", (hashed_password, user_id))
    
    # If the user provided a new username, update the username in the users and tasks tables
    if new_username:
        # Update the username in the users table
        cur.execute("UPDATE users SET username = %s WHERE username = %s", (new_username, old_username))
        
        # Update the assigned_to field in tasks where the old username was assigned
        cur.execute("UPDATE tasks SET assigned_to = %s WHERE assigned_to = %s", (new_username, old_username))
        
        # Update the username field in tasks where the old username created the task
        cur.execute("UPDATE tasks SET username = %s WHERE username = %s", (new_username, old_username))
        
        # Update the session with the new username
        session['username'] = new_username
        session['user_id'] = user_id  # Keep the user ID the same

    # Commit the changes to the database
    mysql.connection.commit()
    
    # Close the cursor
    cur.close()

    # Return a success response as JSON
    return jsonify({'success': True})

# Route to handle account deletion
@app.route('/delete_account', methods=['POST'])
@login_required  # Ensures the user must be logged in to access this route
def delete_account():
    # Generate a new random username using a combination of letters and digits (4 characters long)
    name = session.get('user_id')
    chars = string.ascii_letters + string.digits  # Define allowed characters (letters and digits)
    username = session.get('username')  # Get the current username from the session
    new_username = ''.join(random.choice(chars) for _ in range(4))  # Generate new random username

    # Check if the username is available in session
    if not username:
        # Log an error and return a failure response if no username found in session
        app.logger.error('No username found in session.')
        return jsonify({'success': False, 'error': 'User not logged in'}), 400  # HTTP 400: Bad Request

    try:
        # Establish a cursor to interact with the database
        cur = mysql.connection.cursor()

        # Delete the user from the 'users' table
        cur.execute("DELETE FROM users WHERE name = %s", (name,))

        # Update the 'tasks' table, replacing the user's username in the 'username' field with the generated one
        cur.execute("UPDATE tasks SET username = %s WHERE username = %s", (new_username, username))

        # Update the 'tasks' table, replacing the user's username in the 'assigned_to' field with the generated one
        cur.execute("UPDATE tasks SET assigned_to = %s WHERE assigned_to = %s", (new_username, username))

        # Commit the changes to the database
        mysql.connection.commit()

        # Close the cursor
        cur.close()

        # Clear the session after account deletion
        session.clear()

        # Log that the user was successfully deleted
        app.logger.info(f'User {username} deleted successfully.')

        # Return a success response
        return jsonify({'success': True})

    except Exception as e:
        # Log any error that occurs during the deletion process
        app.logger.error(f"Error deleting user {username}: {e}")
        # Return a failure response if an exception occurs, with an error message
        return jsonify({'success': False, 'error': 'An error occurred'}), 500  # HTTP 500: Internal Server Error


# Route to allow a user to download their task data as an XML file
@app.route('/user_data', methods=['POST'])
@login_required  # Ensures that only logged-in users can access this route
def download_data():
    user_id = session.get('username')  # Get the logged-in user's username from the session
    cur = mysql.connection.cursor()  # Create a cursor for database operations

    # Fetch tasks that either belong to the user or are assigned to the user and marked as assigned
    cur.execute(
        """
        SELECT Taskid, Title, Content, Status, CreatedAt, assigned_to, assigned, username
        FROM tasks
        WHERE username = %s OR assigned_to = %s AND assigned = %s
        ORDER BY CreatedAt DESC
        """, (user_id, user_id, 1)
    )

    tasks = cur.fetchall()  # Get all the results from the query
    cur.close()  # Close the cursor

    # Create XML structure for tasks
    root = Element('Tasks')  # Root element of the XML

    for task in tasks:
        task_elem = SubElement(root, 'Task')  # Create a 'Task' element for each task
        SubElement(task_elem, 'ID').text = str(task[0])  # Add task ID
        SubElement(task_elem, 'Title').text = task[1]  # Add task title
        SubElement(task_elem, 'Content').text = task[2]  # Add task content
        SubElement(task_elem, 'Status').text = task[3]  # Add task status
        SubElement(task_elem, 'CreatedAt').text = task[4].strftime("%Y-%m-%d %H:%M:%S")  # Add task creation date
        SubElement(task_elem, 'AssignedTo').text = task[5]  # Add task's assigned user
        SubElement(task_elem, 'Assigned').text = str(task[6])  # Add task assignment status
        SubElement(task_elem, 'Username').text = task[7]  # Add the task's creator username

    # Convert XML to string format
    xml_str = tostring(root, encoding='utf-8', method='xml')

    # Create a response object to return the XML file
    response = Response(xml_str, content_type='application/xml')
    response.headers['Content-Disposition'] = 'attachment; filename=user_data.xml'  # Define the file name

    return response  # Send the XML file as a response


# Route to edit a task's title and content
@app.route('/edit_task', methods=['POST'])
@login_required  # Requires login to access
def edit_task():
    data = request.get_json()  # Get JSON data from the request
    if data:
        task_id = data.get('task_id')  # Get task ID from the request data
        new_title = data.get('title')  # Get the new title
        new_content = data.get('content')  # Get the new content

        cur = mysql.connection.cursor()  # Create a cursor for database operations
        cur.execute("UPDATE tasks SET Title = %s, Content = %s WHERE TaskID = %s", (new_title, new_content, task_id))  # Update the task
        mysql.connection.commit()  # Commit the changes
        cur.close()  # Close the cursor

        return jsonify({'success': True})  # Return success response
    return jsonify({'error': 'Invalid data'}), 400  # Return error if data is invalid


# Route to delete a task
@app.route('/delete_task', methods=['POST'])
@login_required  # Requires login
def delete_task():
    data = request.get_json()  # Get JSON data from the request
    if data:
        task_id = data.get('task_id')  # Get the task ID to delete

        cur = mysql.connection.cursor()  # Create a cursor
        cur.execute("DELETE FROM tasks WHERE TaskID = %s", (task_id,))  # Delete the task by ID
        mysql.connection.commit()  # Commit changes
        cur.close()  # Close the cursor

        return jsonify({'success': True})  # Return success response
    return jsonify({'error': 'Invalid data'}), 400  # Return error if data is invalid


# Route to assign a task to a specific user
@app.route('/assign_to', methods=['POST'])
@login_required  # Requires login
def assign_to():
    data = request.json  # Get JSON data
    task_id = data.get('task_id')  # Get task ID
    username = data.get('username')  # Get the username to assign the task to
    title = data.get('title')  # Get task title for notification purposes

    cur = mysql.connection.cursor()  # Create cursor
    cur.execute("SELECT username FROM users WHERE username = %s", (username,))  # Check if the user exists
    user = cur.fetchone()
    if not user:
        cur.close()  # Close cursor if user does not exist
        return jsonify({'success': False, 'error': 'Invalid username'}), 400  # Return error

    try:
        # Update the task with the new assignee and set it as assigned
        cur.execute(
            "UPDATE tasks SET assigned_to = %s, assigned = %s WHERE TaskID = %s", (username, 1, task_id)
        )
        mysql.connection.commit()  # Commit changes

        # Fetch notification key for the assigned user
        cur.execute("SELECT notification_key FROM users WHERE username = %s", (username,))
        assigned_user = cur.fetchone()

        # If user has a notification key, send a notification
        if assigned_user:
            key = assigned_user[0]
            result = send_notification(key, 'A task Assigned to you', title)  # Send notification

    except Exception as e:
        mysql.connection.rollback()  # Rollback in case of error
        cur.close()  # Close the cursor
        return jsonify({'success': False, 'error': str(e)}), 500  # Return error message

    cur.close()  # Close cursor after success
    return jsonify({'success': True})  # Return success


# Route to toggle between dark and light themes
@app.route('/toggle_theme', methods=['POST'])
@login_required  # Requires login
def toggle_theme():
    user_id = session['user_id']  # Get user ID from session
    current_mode = session.get('theme_mode', 'light')  # Get current theme mode (default is 'light')

    # Toggle theme mode
    new_mode = 'dark' if current_mode == 'light' else 'light'
    session['theme_mode'] = new_mode  # Update session with new mode

    cur = mysql.connection.cursor()  # Create cursor
    cur.execute("UPDATE users SET theme_mode = %s WHERE id = %s", (new_mode == 'dark', user_id))  # Update user's theme mode in DB
    mysql.connection.commit()  # Commit changes
    cur.close()  # Close cursor

    return jsonify({'success': True, 'theme_mode': new_mode})  # Return success and new theme mode


# Route to search for users by username (for use in task assignment)
@app.route('/search_users', methods=['GET'])
@login_required  # Requires login
def search_users():
    query = request.args.get('query', '')  # Get search query from the request
    cur = mysql.connection.cursor()  # Create cursor
    cur.execute("SELECT username FROM users WHERE username LIKE %s", (f'%{query}%',))  # Search for users matching the query
    users = cur.fetchall()  # Fetch matching users
    cur.close()  # Close cursor
    return jsonify([user[0] for user in users])  # Return list of matching usernames


# Run the app
if __name__ == '__main__':
    app.debug = False  # Set debug mode to False for production
    app.run()  # Run the Flask application