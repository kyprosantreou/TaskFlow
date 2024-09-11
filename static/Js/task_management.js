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

    var editModal = document.getElementById("editModal");
    var editCloseBtn = document.getElementById("editCloseBtn");

    editCloseBtn.onclick = function() {
        editModal.style.display = "none";
    }

    window.onclick = function(event) {
        if (event.target == modal) {
            modal.style.display = "none";
        } else if (event.target == editModal) {
            editModal.style.display = "none";
        } else if (event.target == assignModal) {
            closeAssignModal();
        }
    }

    function addMoveToInProgressButton(task) {
        var button = document.createElement("button");
        button.textContent = "Mark as In Progress";
        button.classList.add("move-to-in-progress-btn");
        button.onclick = function() {
            var taskId = task.getAttribute('data-id');  
            var newStatus = 'inProgress';  
            console.log("Marking task as In Progress. Task ID:", taskId);  
            fetch('/update_task_status', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    task_id: taskId,
                    status: newStatus
                }),
            })
            .then(response => response.json())
            .then(data => {
                console.log("Response from server:", data);  // Debugging
                if (data.success) {
                    moveTaskToInProgress(task);
                } else {
                    console.error('Error updating task status:', data.error);
                }
            })
            .catch(error => console.error('Error:', error));
        };
        task.appendChild(button);
    }
    

    function moveTaskToInProgress(task) {
        var inProgressColumn = document.getElementById("inProgress");
        task.querySelector(".move-to-in-progress-btn").remove();
        addMoveToDoneButton(task);
        inProgressColumn.appendChild(task);
    }

    function addMoveToDoneButton(task) {
        var button = document.createElement("button");
        button.textContent = "Mark as Done";
        button.classList.add("move-to-done-btn");
        button.onclick = function() {
            var taskId = task.getAttribute('data-id');  
            fetch('/update_task_status', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    task_id: taskId,
                    status: 'done'
                }),
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    moveTaskToDone(task);
                } else {
                    console.error('Error updating task status:', data.error);
                }
            })
            .catch(error => console.error('Error:', error));
        };
        task.appendChild(button);
    }

    function moveTaskToDone(task) {
        var doneColumn = document.getElementById("done");
        task.querySelector(".move-to-done-btn").remove();
        doneColumn.appendChild(task);
    }


    
    function addMoveToAssignButton(task) {
        var button = document.createElement("button");
        button.textContent = "Assign to";
        button.classList.add("move-to-assign-btn");
        button.onclick = function() {
            openAssignModal(task);
        };
        task.appendChild(button);
    }


    function openAssignModal(task) {
        var assignModal = document.getElementById("assignModal");
        assignModal.task = task;
        assignModal.style.display = "block";
        
        var errorMsg = document.getElementById("assignErrorMsg");
        if (errorMsg) {
            errorMsg.remove();
        }

        var title = task.querySelector("h3").textContent; 
        console.log("Task Title:", title);

        var taskTitleElement = document.getElementById("taskTitle"); 
        taskTitleElement.value = title; 
    }

    
    function showAssignErrorMessage(message) {
        var errorMsg = document.getElementById("assignErrorMsg");
        if (!errorMsg) {
            errorMsg = document.createElement("p");
            errorMsg.id = "assignErrorMsg";
            errorMsg.style.color = "red";
            var form = document.getElementById("assignTaskForm");
            form.insertBefore(errorMsg, form.firstChild);
        }
        errorMsg.textContent = message;
    }
    
      var assignModal = document.getElementById("assignModal");
      var assignModalCloseBtn = document.querySelector("#assignModal .close");
  
      
      function closeAssignModal() {
          assignModal.style.display = "none"; 
      }
  
      
      assignModalCloseBtn.onclick = closeAssignModal;
  
      
      window.onclick = function(event) {
          if (event.target === assignModal) {
              closeAssignModal();
          }
      }

    document.getElementById("assignTaskForm").addEventListener("submit", function(event) {
    event.preventDefault();
    
    var assignModal = document.getElementById("assignModal");
    var task = assignModal.task;

    var title = task.querySelector("h3").textContent;
    var username = document.getElementById("assignUsername").value;

    console.log("Assigning task '" + title + "' to " + username);

    fetch('/assign_to', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            task_id: task.getAttribute('data-id'),
            username: username,
            title: title 
        }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            updateTaskAssignedTo(task, username);
            closeAssignModal();
        } else {
            showAssignErrorMessage(data.error || 'An error occurred');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showAssignErrorMessage('An error occurred while assigning the task. Please try again.');
    });
});

    
    function searchUsers() {
        var query = document.getElementById("assignUsername").value;
        fetch(`/search_users?query=${query}`)
            .then(response => response.json())
            .then(users => {
                var userList = document.getElementById("userList");
                userList.innerHTML = '';
                users.forEach(user => {
                    var li = document.createElement("li");
                    li.textContent = user;
                    userList.appendChild(li);
                });
            })
            .catch(error => console.error('Error:', error));
    }

    function updateTaskAssignedTo(task, username) {
        var assignedText = task.querySelector("p:last-child");
        if (assignedText) {
            assignedText.textContent = "Assigned To: " + username;
        } else {
            var span = document.createElement("span");
            span.textContent = "Assigned To: " + username;
            span.classList.add("task-assigned");
            
        }
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
                var task = createTaskElement(data.id, title, content, 'todo', new Date().toISOString().slice(0, 19).replace('T', ' '));
                document.getElementById("todo").appendChild(task);
                modal.style.display = "none";
            } else {
                console.error('Error saving task:', data.error);
            }
        })
        .catch(error => console.error('Error:', error));
    });

    function openEditModal(task, title, content) {
        var editModal = document.getElementById("editModal");
        var editTitleInput = document.getElementById("editTaskTitle");
        var editContentInput = document.getElementById("editTaskContent");

        editModal.task = task;
        editModal.taskId = task.getAttribute('data-id');
        editTitleInput.value = title;
        editContentInput.value = content;

        editModal.style.display = "block";
    }

    document.getElementById("editTaskForm").addEventListener("submit", function(event) {
        event.preventDefault();

        var editModal = document.getElementById("editModal");
        var task = editModal.task;
        var taskId = editModal.taskId;
        var titleInput = document.getElementById("editTaskTitle");
        var contentInput = document.getElementById("editTaskContent");
        var title = titleInput.value;
        var content = contentInput.value;

        fetch('/edit_task', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                task_id: taskId,
                title: title,
                content: content
            }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                task.querySelector("h3").textContent = title;
                task.querySelector("p").textContent = content;
                editModal.style.display = "none";
            } else {
                console.error('Error updating task:', data.error);
            }
        })
        .catch(error => console.error('Error:', error));
    });



    function createTaskElement(id, title, content, status, createdAt, assigned_to,username) {
        var task = document.createElement("div");
        task.classList.add("task");
        task.setAttribute("data-id", id);
        task.innerHTML = `<h3>${title}</h3><p>${content}</p><p><small>Created At: ${createdAt}</small></p><p><small>Created from: ${username}</small></p><p><small>Assigned To: ${assigned_to}</small></p>`;
    
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
            var taskId = task.getAttribute('data-id');  
            fetch('/delete_task', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    task_id: taskId
                }),
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    task.remove();
                } else {
                    console.error('Error deleting task:', data.error);
                }
            })
            .catch(error => console.error('Error:', error));
        };
        task.appendChild(deleteBtn);
    
        if (status === 'todo') {
            addMoveToInProgressButton(task);
            addMoveToAssignButton(task);
        } else if (status === 'inprogress') {
            addMoveToDoneButton(task);
            addMoveToAssignButton(task);
        }
    
        return task;
    }
    
    function searchTasks() {
        var title = searchTitle.value;
        var status = searchStatus.value;
    
        fetch(`/search_tasks?query=${title}&status=${status}`)
            .then(response => response.json())
            .then(tasks => {
                var todoColumn = document.getElementById("todo");
                var inProgressColumn = document.getElementById("inProgress");
                var doneColumn = document.getElementById("done");
    
                todoColumn.innerHTML = '';
                inProgressColumn.innerHTML = '';
                doneColumn.innerHTML = '';
    
                tasks.forEach(task => {
                    var taskElement = createTaskElement(task.id, task.title, task.content, task.status, task.created_at, task.assigned_to, task.username);
                    if (task.status === 'todo') {
                        todoColumn.appendChild(taskElement);
                    } else if (task.status === 'inprogress') {
                        inProgressColumn.appendChild(taskElement);
                    } else if (task.status === 'done') {
                        doneColumn.appendChild(taskElement);
                    }
                });
            })
            .catch(error => console.error('Error:', error));
    }

    searchBtn.onclick = searchTasks;

    function loadTasks() {
        fetch('/tasks')
            .then(response => response.json())
            .then(data => {
                data.forEach(task => {
                    var taskElement = createTaskElement(task.id, task.title, task.content, task.status, task.created_at,task.assigned_to,task.username);
                    if (task.status === 'todo') {
                        document.getElementById("todo").appendChild(taskElement);
                    } else if (task.status === 'inprogress') {
                        document.getElementById("inProgress").appendChild(taskElement);
                    } else if (task.status === 'done') {
                        document.getElementById("done").appendChild(taskElement);
                    }
                });
            })
            .catch(error => console.error('Error fetching tasks:', error));
    }

    loadTasks();
});
