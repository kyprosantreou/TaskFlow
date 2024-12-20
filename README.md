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
    https://github.com/kyprosantreou/TaskFlow.git
    cd TaskFlow
    ```

2. Build and start the Docker containers:
    ```bash
    docker-compose up --build
    ```

3. Access the application in your web browser at:
    ```
    http://127.0.0.1:5000
    ```
## Demo 
![TaskFlow Demo 1](Demo/1.gif) 
![TaskFlow Demo 2](Demo/(2).gif) 
![TaskFlow Demo 3](Demo/(3).gif) 
![TaskFlow Demo 4](Demo/(4).gif) 
![TaskFlow Demo 5](Demo/(5).gif) 
![TaskFlow Demo 6](Demo/(6).gif) 
![TaskFlow Demo 7](Demo/(7).gif)

## Collaborators 
- [Kypros Andreou](https://github.com/kyprosantreou)
- [Eleni Giannouchou](https://github.com/ElenaGiannouchou)
- [Panayiotis Kleanthous](https://github.com/KPanais)

---
