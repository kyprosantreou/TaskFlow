# TaskFlow Web Application

TaskFlow is a Dockerized web-based task management application designed to simplify task organization and collaboration. Built with Flask, MySQL, and other modern technologies, it includes features like user authentication, task assignment, and customizable themes.

## Features

### User Authentication
- Secure registration and login with **Argon2** password hashing.
- Session-based authentication.
- Update user details or delete accounts securely.

### Task Management
- Create, update, delete, and search tasks.
- Assign tasks to specific users.
- Export tasks as **XML files**.

### Notifications
- Get task-related updates through the **SimplePush API**.

### Themes
- Toggle between light and dark modes with settings saved per user.

### User Search
- Quickly find users for task assignment using the search feature.

## Dockerized Setup

### Prerequisites
- Docker installed on your machine.
- Docker Compose installed.

### Installation and Deployment

1. Clone the repository:
    ```bash
    git clone https://github.com/yourusername/taskflow.git
    cd taskflow
    ```

2. Build and start the Docker containers:
    ```bash
    docker-compose up --build
    ```

3. Access the application in your web browser at:
    ```
    http://127.0.0.1:5000
    ```

---
