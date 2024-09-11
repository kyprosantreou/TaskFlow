USE di_internet_technologies_project;

CREATE TABLE IF NOT EXISTS users (
    name VARCHAR(255) NOT NULL,
    surname VARCHAR(255) NOT NULL,
    username VARCHAR(255) NOT NULL,     
    email VARCHAR(255) PRIMARY KEY,
    password VARCHAR(255) NOT NULL,
    coockies BOOLEAN,
    notification_key VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS tasks (
    TaskID INT AUTO_INCREMENT PRIMARY KEY,
    Title VARCHAR(255) NOT NULL,
    Content TEXT,
    Status ENUM('todo', 'inprogress', 'done') DEFAULT 'todo',
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    username VARCHAR(255),
    assigned_to VARCHAR(255),
    assigned TINYINT
);
