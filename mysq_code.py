import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

try:
    mydb = mysql.connector.connect(
        host="localhost",
        user=os.getenv("user"),
        password=os.getenv("password"),
        database="testing",
    )
    cursor = mydb.cursor()

    # Create the users table if it doesn't exist
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        name VARCHAR(255) NOT NULL,
        surname VARCHAR(255) NOT NULL,
        username VARCHAR(255) NOT NULL,     
        email VARCHAR(255) PRIMARY KEY,
        password VARCHAR(255) NOT NULL,
        coockies BOOLEAN,
        notification_key VARCHAR(255)
    );
    ''')

    # Create the Tasks table if it doesn't exist
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Tasks (
        TaskID INT AUTO_INCREMENT PRIMARY KEY,
        Title VARCHAR(255) NOT NULL,
        Content TEXT,
        Status ENUM('todo', 'inprogress', 'done') DEFAULT 'todo',
        CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        username VARCHAR(255),
        assigned_to VARCHAR(255),
        assigned TINYINT
    );
    ''')

    mydb.commit()

except mysql.connector.Error as err:
    print("MySQL Error: {}".format(err))
