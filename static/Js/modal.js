document.addEventListener("DOMContentLoaded", function() {
    var modal = document.getElementById("taskModal");
    var btn = document.getElementById("openModalBtn");
    var span = document.getElementsByClassName("close")[0];
    var titleInput = document.getElementById("taskTitle");
    var contentInput = document.getElementById("taskContent");

    btn.onclick = function() {
        modal.style.display = "block";
        titleInput.value = "";
        contentInput.value = "";
    }

    span.onclick = function() {
        modal.style.display = "none";
    }

    window.onclick = function(event) {
        if (event.target == modal) {
            modal.style.display = "none";
        }
    }

    function addMoveToInProgressButton(task) {
        var button = document.createElement("button");
        button.textContent = "Mark as In Progress";
        button.classList.add("move-to-in-progress-btn");
        button.onclick = function() {
            moveTaskToInProgress(task);
        };
        task.appendChild(button);
    }

    function moveTaskToInProgress(task) {
        var inProgressColumn = document.getElementById("inProgress");
        task.querySelector(".move-to-in-progress-btn").remove();
        inProgressColumn.appendChild(task);
    }

    function addMoveToDoneButton(task) {
        var button = document.createElement("button");
        button.textContent = "Mark as Done";
        button.classList.add("move-to-done-btn");
        button.onclick = function() {
            moveTaskToDone(task);
        };
        task.appendChild(button);
    }

    function moveTaskToDone(task) {
        var doneColumn = document.getElementById("done");
        task.querySelector(".move-to-done-btn").remove();
        doneColumn.appendChild(task);
    }

    function addCreationDateTime(task) {
        var dateTime = new Date().toLocaleString();
        var span = document.createElement("span");
        span.textContent = "Created: " + dateTime;
        span.classList.add("task-date");
        task.appendChild(span);
    }

    document.getElementById("taskForm").addEventListener("submit", function(event) {
        event.preventDefault();
        var title = titleInput.value;
        var content = contentInput.value;

        fetch('/submit_task', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                title: title,
                content: content
            }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                var task = document.createElement("div");
                task.classList.add("task");
                task.innerHTML = "<h3>" + title + "</h3><p>" + content + "</p>";

                var editBtn = document.createElement("button");
                editBtn.textContent = "Edit Task";
                editBtn.classList.add("edit-btn");
                editBtn.onclick = function() {
                    openEditModal(task, task.querySelector("h3").textContent, task.querySelector("p").textContent);
                };
                task.appendChild(editBtn);

                var deleteBtn = document.createElement("button");
                deleteBtn.textContent = "Delete Task";
                deleteBtn.classList.add("delete-btn");
                deleteBtn.onclick = function() {
                    task.remove();
                };
                task.appendChild(deleteBtn);

                addMoveToInProgressButton(task);
                addMoveToDoneButton(task);
                addCreationDateTime(task);

                var todoColumn = document.getElementById("todo");
                todoColumn.appendChild(task);

                modal.style.display = "none";
            } else {
                console.error('Error saving task:', data.error);
            }
        })
        .catch((error) => {
            console.error('Error:', error);
        });
    });

    function openEditModal(task, title, content) {
        var editModal = document.getElementById("editModal");
        var editTitleInput = document.getElementById("editTaskTitle");
        var editContentInput = document.getElementById("editTaskContent");

        editModal.task = task;
        editModal.originalTitle = title;
        editModal.originalContent = content;

        if (editModal.editedTitle && editModal.editedContent) {
            editTitleInput.value = editModal.editedTitle;
            editContentInput.value = editModal.editedContent;
        } else {
            editTitleInput.value = title;
            editContentInput.value = content;
        }

        editModal.style.display = "block";
    }

    document.getElementById("editModal").addEventListener("click", function(event) {
        if (event.target && event.target.classList.contains("move-to-in-progress-btn")) {
            var task = event.target.parentNode;
            moveTaskToInProgress(task);
        }
    });

    document.getElementById("editTaskForm").addEventListener("submit", function(event) {
        event.preventDefault();

        var editModal = document.getElementById("editModal");
        var task = editModal.task;
        var titleInput = document.getElementById("editTaskTitle");
        var contentInput = document.getElementById("editTaskContent");
        var title = titleInput.value;
        var content = contentInput.value;

        editModal.originalTitle = title;
        editModal.originalContent = content;
        editModal.editedTitle = title;
        editModal.editedContent = content;

        task.querySelector("h3").textContent = title;
        task.querySelector("p").textContent = content;

        editModal.style.display = "none";
    });

    document.getElementById("editCloseBtn").addEventListener("click", function() {
        var editModal = document.getElementById("editModal");
        editModal.editedTitle = null;
        editModal.editedContent = null;
        editModal.style.display = "none";
    });
});

// Load tasks script

document.addEventListener("DOMContentLoaded", function() {
    // Fetch tasks from the server and display them
    function loadTasks() {
        fetch('/tasks')
            .then(response => response.json())
            .then(data => {
                data.forEach(task => {
                    var taskElement = createTaskElement(task.id, task.title, task.content, task.status, task.created_at);
                    if (task.status === 'todo') {
                        document.getElementById("todo").appendChild(taskElement);
                    } else if (task.status === 'in progress') {
                        document.getElementById("inProgress").appendChild(taskElement);
                    } else if (task.status === 'done') {
                        document.getElementById("done").appendChild(taskElement);
                    }
                });
            })
            .catch(error => console.error('Error fetching tasks:', error));
    }

    // Helper function to create a task element
    function createTaskElement(id, title, content, status, createdAt) {
        var task = document.createElement("div");
        task.classList.add("task");
        task.setAttribute("data-id", id);
        task.innerHTML = `<h3>${title}</h3><p>${content}</p><p><small>Created At: ${createdAt}</small></p>`;

        var editBtn = document.createElement("button");
        editBtn.textContent = "Edit Task";
        editBtn.classList.add("edit-btn");
        editBtn.onclick = function() {
            openEditModal(task, title, content);
        };
        task.appendChild(editBtn);

        var deleteBtn = document.createElement("button");
        deleteBtn.textContent = "Delete Task";
        deleteBtn.classList.add("delete-btn");
        deleteBtn.onclick = function() {
            task.remove();
        };
        task.appendChild(deleteBtn);

        if (status === 'todo') {
            addMoveToInProgressButton(task);
        } else if (status === 'in progress') {
            addMoveToDoneButton(task);
        }

        return task;
    }

    function addMoveToInProgressButton(task) {
        var button = document.createElement("button");
        button.textContent = "Mark as In Progress";
        button.classList.add("move-to-in-progress-btn");
        button.onclick = function() {
            moveTaskToInProgress(task);
        };
        task.appendChild(button);
    }

    function moveTaskToInProgress(task) {
        var inProgressColumn = document.getElementById("inProgress");
        task.querySelector(".move-to-in-progress-btn").remove();
        inProgressColumn.appendChild(task);
    }

    function addMoveToDoneButton(task) {
        var button = document.createElement("button");
        button.textContent = "Mark as Done";
        button.classList.add("move-to-done-btn");
        button.onclick = function() {
            moveTaskToDone(task);
        };
        task.appendChild(button);
    }

    function moveTaskToDone(task) {
        var doneColumn = document.getElementById("done");
        task.querySelector(".move-to-done-btn").remove();
        doneColumn.appendChild(task);
    }

    function openEditModal(task, title, content) {
        var editModal = document.getElementById("editModal");
        var editTitleInput = document.getElementById("editTaskTitle");
        var editContentInput = document.getElementById("editTaskContent");

        editModal.task = task;
        editTitleInput.value = title;
        editContentInput.value = content;

        editModal.style.display = "block";
    }

    // Load tasks when the page is loaded
    loadTasks();

    // Handle adding new tasks
    document.getElementById("taskForm").addEventListener("submit", function(event) {
        event.preventDefault();
        var title = document.getElementById("taskTitle").value;
        var content = document.getElementById("taskContent").value;

        fetch('/submit_task', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                title: title,
                content: content
            }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                var task = createTaskElement(data.id, title, content, 'todo', new Date().toISOString().slice(0, 19).replace('T', ' '));
                document.getElementById("todo").appendChild(task);
                document.getElementById("taskModal").style.display = "none";
            } else {
                console.error('Error saving task:', data.error);
            }
        })
        .catch(error => console.error('Error:', error));
    });
});
