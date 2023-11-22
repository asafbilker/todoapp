document.addEventListener("DOMContentLoaded", function () {
    // Registration Form
    var registrationForm = document.getElementById('registration-form');
    var registrationSuccessMessage = document.getElementById('registration-success-message');
    var registrationErrorMessage = document.getElementById('registration-error-message');

    if (registrationForm) {
        registrationForm.addEventListener('submit', function (event) {
            event.preventDefault();

            var formData = new FormData(registrationForm);
            fetch('/register', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    registrationErrorMessage.textContent = '';
                    registrationErrorMessage.style.display = 'none';
                    registrationSuccessMessage.textContent = 'Successfully registered! Redirecting to login page...';
                    registrationSuccessMessage.style.display = 'block';
                    setTimeout(function () {
                        registrationSuccessMessage.style.display = 'none';
                        window.location.href = data.redirect;
                    }, 2000);
                }
                else if (data.yesUserE) {
                    registrationErrorMessage.textContent = 'Username already exists. Please choose a different username.';
                    registrationErrorMessage.style.display = 'block';
                }
            });
        });
    }

    // Login Form
    var loginForm = document.getElementById('login-form');
    var loginSuccessMessage = document.getElementById('login-success-message');
    var loginErrorMessageUser = document.getElementById('login-error-message-user');
    var loginErrorMessagePassword = document.getElementById('login-error-message-password');

    if (loginForm) {
        loginForm.addEventListener('submit', function (event) {
            event.preventDefault();

            var formData = new FormData(loginForm);
            fetch('/login', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.loggedIn) {
                    resetErrorMessages();
                    loginSuccessMessage.textContent = 'Successfully logged in! Redirecting to home page...';
                    loginSuccessMessage.style.display = 'block';
                    setTimeout(function () {
                        loginSuccessMessage.style.display = 'none';
                        window.location.href = data.redirect;
                    }, 2000);
                }
                else if (data.passE) {
                    displayErrorMessage(loginErrorMessagePassword, 'Incorrect password. Please try again.');
                }
                else if (data.userE) {
                    displayErrorMessage(loginErrorMessageUser, 'Incorrect username. Please try again.');
                }
            });
        });
    }

    // Function to handle mark complete button clicks
    function handleMarkCompleteButtonClick(button) {
        button.addEventListener('click', function () {
            var taskElement = button.closest('.task');
            if (taskElement) {
                var taskId = taskElement.dataset.taskId;
                var completed = !button.classList.contains('completed');

                // Update the UI
                button.classList.toggle('completed', completed);
                taskElement.classList.toggle('done', completed);

                // Update the button text based on the current state of the task
                button.textContent = completed ? 'Mark as Uncompleted' : 'Mark as Completed';

                // Send a request to the server to update the task
                updateTaskInDatabase(taskId, completed);
            }
        });
    }

    // Toggle Form
    var toggleForm = document.getElementById('toggle-form');
    if (toggleForm) {
        toggleForm.addEventListener('submit', function (event) {
            event.preventDefault();

            var taskId = toggleForm.getAttribute('action').split('/').pop();
            var formData = new FormData(toggleForm);

            fetch(`/toggle_task/${taskId}`, {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    updateUIForCompletedTasks(data.completed);
                }
            });
        });
    }

    // Handle mark as completed button clicks
    var markCompleteButtons = document.querySelectorAll('.mark-complete-button');
    markCompleteButtons.forEach(handleMarkCompleteButtonClick);

    // Function to update the task in the database
    function updateTaskInDatabase(taskId, completed) {
        fetch('/toggle_task', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({taskId, completed})
        })
        .then(response => response.json())
    }

    // Helper function to update the UI for completed tasks
    function updateUIForCompletedTasks(completedTaskIds) {
        completedTaskIds.forEach(function(taskId) {
            var taskElement = document.querySelector(`.task[data-task-id="${taskId}"]`);
            var markCompleteButton = taskElement.querySelector('.mark-complete-button');
            if (taskElement) {
                taskElement.classList.toggle('done');
                markCompleteButton.classList.toggle('completed');
                updateTaskInDatabase(taskId, markCompleteButton.classList.contains('completed'));
            }
        });
    }

    // Helper function to reset error messages
    function resetErrorMessages() {
        loginErrorMessageUser.textContent = '';
        loginErrorMessageUser.style.display = 'none';
        loginErrorMessagePassword.textContent = '';
        loginErrorMessagePassword.style.display = 'none';
    }

    // Helper function to display error messages
    function displayErrorMessage(element, message) {
        resetErrorMessages();
        element.textContent = message;
        element.style.display = 'block';
    }
});
